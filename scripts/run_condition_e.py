#!/usr/bin/env python3
"""Run Condition E (LLM-Wiki retrieval) over the taskset and record responses.

For each task in taskset.md, spawns a fresh Claude API session with:
  - System prompt: the anonymized Soul Spec.
  - User prompt: the Condition E spawn prompt (from spawn-prompts.md) with
    the task appended.
  - Tools: Read, Glob, Grep — sandboxed to the wiki/ directory.

Output: results/condition-E-run-<timestamp>.json containing the full
conversation, tool-call traces, token usage, and runtime per task. This
file feeds the rubric scorer (see evaluation/rubric.md) and the autoresearch
loop (autoresearch/run_experiment.sh).

Usage:
  export ANTHROPIC_API_KEY=...
  python scripts/run_condition_e.py                       # all tasks
  python scripts/run_condition_e.py --task IR-1           # single task
  python scripts/run_condition_e.py --wiki-dir wiki       # default
  python scripts/run_condition_e.py --model claude-opus-4-5
  python scripts/run_condition_e.py --max-tool-calls 30

Requires: anthropic >= 0.39 (tool use), Python >= 3.10.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import anthropic
except ImportError:
    sys.exit("Install: pip install anthropic")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WIKI = REPO_ROOT / "wiki"
DEFAULT_SOUL = REPO_ROOT / "soul-spec-anonymized" / "SOUL.md"
DEFAULT_TASKSET = REPO_ROOT / "taskset.md"
RESULTS_DIR = REPO_ROOT / "results"

# Tool definitions for the Claude API tool-use protocol.
TOOLS = [
    {
        "name": "Read",
        "description": (
            "Read the contents of a file inside the wiki directory. "
            "Path is resolved relative to the wiki root."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relative path inside wiki/"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "Glob",
        "description": (
            "List files inside the wiki directory matching a glob pattern "
            "(e.g., 'pages/*.md'). Returns matching paths relative to wiki root."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern, e.g., 'pages/*.md'"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "Grep",
        "description": (
            "Search for a regex pattern across files in the wiki directory. "
            "Returns matching lines with their file path."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex pattern"},
                "path_glob": {
                    "type": "string",
                    "description": "Optional glob to restrict files (default 'pages/*.md')",
                },
            },
            "required": ["pattern"],
        },
    },
]


def safe_resolve(wiki_root: Path, rel: str) -> Path | None:
    """Resolve `rel` under `wiki_root`. Reject path-traversal attempts."""
    resolved = (wiki_root / rel).resolve()
    try:
        resolved.relative_to(wiki_root.resolve())
    except ValueError:
        return None
    return resolved


def tool_read(wiki_root: Path, path: str) -> str:
    target = safe_resolve(wiki_root, path)
    if target is None:
        return f"ERROR: path '{path}' is outside the wiki directory"
    if not target.exists():
        return f"ERROR: '{path}' not found"
    if not target.is_file():
        return f"ERROR: '{path}' is not a regular file"
    return target.read_text(encoding="utf-8")


def tool_glob(wiki_root: Path, pattern: str) -> str:
    matches: list[str] = []
    for p in wiki_root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(wiki_root))
        if fnmatch.fnmatch(rel, pattern):
            matches.append(rel)
    matches.sort()
    return "\n".join(matches) if matches else "(no matches)"


def tool_grep(wiki_root: Path, pattern: str, path_glob: str = "pages/*.md") -> str:
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"ERROR: invalid regex: {e}"
    out: list[str] = []
    for p in wiki_root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(wiki_root))
        if not fnmatch.fnmatch(rel, path_glob):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                out.append(f"{rel}:{i}:{line.rstrip()}")
                if len(out) >= 200:
                    out.append("(truncated at 200 hits)")
                    return "\n".join(out)
    return "\n".join(out) if out else "(no matches)"


def dispatch_tool(wiki_root: Path, name: str, params: dict) -> str:
    if name == "Read":
        return tool_read(wiki_root, params["path"])
    if name == "Glob":
        return tool_glob(wiki_root, params["pattern"])
    if name == "Grep":
        return tool_grep(
            wiki_root,
            params["pattern"],
            params.get("path_glob", "pages/*.md"),
        )
    return f"ERROR: unknown tool '{name}'"


def parse_taskset(taskset_path: Path) -> list[tuple[str, str]]:
    """Extract (task_id, task_text) pairs from taskset.md.

    Tasks are identified by a heading or marker like '## IR-1', '## CT-3', etc.
    Returns the body text under each heading as the task content.
    """
    text = taskset_path.read_text(encoding="utf-8")
    pattern = re.compile(r"^##\s+([A-Z]{2}-\d+)\b(.*)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    tasks: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        task_id = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        # Include the heading line so the task text is self-contained.
        header_rest = m.group(2).strip()
        full = (f"## {task_id} {header_rest}".rstrip() + "\n\n" + body).strip()
        tasks.append((task_id, full))
    return tasks


CONDITION_E_PROMPT_TEMPLATE = """\
You are an AI development assistant. Before answering the question below,
first read CLAUDE.md (the wiki operating rules) and index.md (the catalog).
For the question, identify relevant pages by tag/summary in index.md, read
those pages in full from pages/, and follow `## Related` links transitively
up to depth 2 when relevant. Cite the page (e.g., [page#section]) for each
factual claim.

Use only the Read / Glob / Grep tools provided. Do not rely on prior
knowledge that isn't grounded in the wiki.

When ready, give your final answer as plain prose (no tool call).

Task:

{task}
"""


def run_one_task(
    client: anthropic.Anthropic,
    wiki_root: Path,
    soul_spec: str,
    task_id: str,
    task_text: str,
    model: str,
    max_tool_calls: int,
) -> dict:
    user_prompt = CONDITION_E_PROMPT_TEMPLATE.format(task=task_text)

    messages: list[dict] = [{"role": "user", "content": user_prompt}]
    tool_call_log: list[dict] = []
    total_input = 0
    total_output = 0
    started = time.time()

    for step in range(max_tool_calls + 1):
        resp = client.messages.create(
            model=model,
            max_tokens=4096,
            system=soul_spec,
            tools=TOOLS,
            messages=messages,
        )
        total_input += resp.usage.input_tokens
        total_output += resp.usage.output_tokens

        # Append assistant message verbatim (including any tool_use blocks).
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            final_text = "".join(
                b.text for b in resp.content if getattr(b, "type", "") == "text"
            )
            return {
                "task_id": task_id,
                "task": task_text,
                "response": final_text,
                "tool_calls": tool_call_log,
                "tool_call_count": len(tool_call_log),
                "input_tokens": total_input,
                "output_tokens": total_output,
                "wall_seconds": round(time.time() - started, 2),
                "model": model,
                "stop_reason": resp.stop_reason,
            }

        if resp.stop_reason != "tool_use":
            return {
                "task_id": task_id,
                "task": task_text,
                "response": "(unexpected stop reason)",
                "stop_reason": resp.stop_reason,
                "input_tokens": total_input,
                "output_tokens": total_output,
            }

        # Execute every tool_use block requested.
        tool_results = []
        for block in resp.content:
            if getattr(block, "type", "") != "tool_use":
                continue
            result = dispatch_tool(wiki_root, block.name, block.input)
            tool_call_log.append(
                {"name": block.name, "input": block.input, "output_preview": result[:200]}
            )
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return {
        "task_id": task_id,
        "task": task_text,
        "response": "(max tool calls exceeded)",
        "tool_calls": tool_call_log,
        "tool_call_count": len(tool_call_log),
        "input_tokens": total_input,
        "output_tokens": total_output,
        "wall_seconds": round(time.time() - started, 2),
        "model": model,
        "stop_reason": "max_tool_calls",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--wiki-dir", type=Path, default=DEFAULT_WIKI)
    ap.add_argument("--soul", type=Path, default=DEFAULT_SOUL)
    ap.add_argument("--taskset", type=Path, default=DEFAULT_TASKSET)
    ap.add_argument("--task", help="Run only this task ID (e.g., IR-1)")
    ap.add_argument("--model", default="claude-opus-4-5")
    ap.add_argument("--max-tool-calls", type=int, default=40)
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    if not args.wiki_dir.exists():
        sys.exit(f"wiki dir not found: {args.wiki_dir}")
    if not args.soul.exists():
        sys.exit(f"soul spec not found: {args.soul}")
    if not args.taskset.exists():
        sys.exit(f"taskset not found: {args.taskset}")

    soul_spec = args.soul.read_text(encoding="utf-8")
    tasks = parse_taskset(args.taskset)
    if args.task:
        tasks = [(tid, t) for tid, t in tasks if tid == args.task]
        if not tasks:
            sys.exit(f"task {args.task} not found in {args.taskset}")

    client = anthropic.Anthropic()
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = args.output or RESULTS_DIR / f"condition-E-run-{timestamp}.json"

    results: list[dict] = []
    for task_id, task_text in tasks:
        print(f"  running {task_id} ...", file=sys.stderr, flush=True)
        result = run_one_task(
            client=client,
            wiki_root=args.wiki_dir,
            soul_spec=soul_spec,
            task_id=task_id,
            task_text=task_text,
            model=args.model,
            max_tool_calls=args.max_tool_calls,
        )
        results.append(result)
        print(
            f"    {task_id}: {result.get('tool_call_count', 0)} tool calls, "
            f"{result.get('input_tokens', 0)} in / {result.get('output_tokens', 0)} out, "
            f"{result.get('wall_seconds', 0)}s",
            file=sys.stderr,
            flush=True,
        )

    summary = {
        "run_id": timestamp,
        "condition": "E",
        "model": args.model,
        "wiki_dir": str(args.wiki_dir.relative_to(REPO_ROOT)),
        "task_count": len(results),
        "total_input_tokens": sum(r.get("input_tokens", 0) for r in results),
        "total_output_tokens": sum(r.get("output_tokens", 0) for r in results),
        "total_wall_seconds": round(sum(r.get("wall_seconds", 0) for r in results), 2),
        "results": results,
    }
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
