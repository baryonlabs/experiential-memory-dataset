#!/usr/bin/env python3
"""Run Condition E via the local `claude` CLI (subscription auth, no API key).

Mirrors `scripts/run_condition_e.py` but uses Claude Code's headless mode
(`claude -p`) as the runtime, so calls bill against the user's Pro/Max
subscription rather than per-token API spend.

For each task:
  - Spawn `claude -p` as a subprocess with:
      * --no-session-persistence (fresh, isolated session)
      * --system-prompt <soul-spec>
      * --add-dir <wiki-dir> (tool access scoped to wiki/)
      * --allowedTools "Read,Glob,Grep" (deny everything else)
      * --model opus (or user-specified)
      * --output-format json (parseable result + token usage)
      * --permission-mode bypassPermissions (no interactive prompts)
  - Capture the JSON output and aggregate.

Output format matches `run_condition_e.py` so `score_responses.py` works
on results from either backend.

Usage:
  # Confirm the agent's claude CLI is logged in via subscription:
  unset ANTHROPIC_API_KEY      # subscription only takes precedence when key is unset
  claude auth                  # check / log in if needed

  python scripts/run_condition_e_via_claude_code.py --dry-run         # verify
  python scripts/run_condition_e_via_claude_code.py --task IR-1       # 1 task
  python scripts/run_condition_e_via_claude_code.py                   # all 20

Trade-offs vs the API backend:
  + No per-token cost (subscription flat fee)
  + No SDK install needed (uses local claude CLI)
  - Subject to subscription rate limits (5-hour rolling window on Max)
  - Per-call wall-clock includes Claude Code's startup overhead (~2-5s)
  - `claude -p` aggregates internal tool calls; we don't get per-tool-call
    granularity in the output (use --output-format stream-json + parsing
    if granular traces are needed)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_WIKI = REPO_ROOT / "wiki"
DEFAULT_SOUL = REPO_ROOT / "soul-spec-anonymized" / "SOUL.md"
DEFAULT_TASKSET = REPO_ROOT / "taskset.md"
RESULTS_DIR = REPO_ROOT / "results"

# Reuse the parser from the API-backend script.
sys.path.insert(0, str(Path(__file__).parent))
from run_condition_e import parse_taskset, CONDITION_E_PROMPT_TEMPLATE  # noqa: E402


def build_claude_cmd(
    prompt: str,
    soul_spec: str,
    wiki_dir: Path,
    model: str,
    timeout_seconds: int,
) -> list[str]:
    return [
        "claude",
        "-p", prompt,
        "--no-session-persistence",
        "--system-prompt", soul_spec,
        "--add-dir", str(wiki_dir.resolve()),
        # `--tools` is the strict whitelist of *available* tools. The
        # agent literally cannot see anything else. We deliberately do
        # NOT use `--allowedTools` here (that flag only auto-approves
        # permissions for tools that are already available, which under
        # `--permission-mode bypassPermissions` would still let Bash and
        # everything else through — contaminating the LLM-Wiki vs RAG
        # comparison since Bash can replicate Read/Glob/Grep behavior in
        # ways that are not part of the LLM-Wiki retrieval method).
        "--tools", "Read,Glob,Grep",
        "--model", model,
        "--output-format", "stream-json",
        "--verbose",
        "--permission-mode", "bypassPermissions",
    ]


def _progress(started: float, msg: str) -> None:
    elapsed = time.time() - started
    print(f"      [{elapsed:5.1f}s] {msg}", file=sys.stderr, flush=True)


def run_one_task_via_claude_code(
    task_id: str,
    task_text: str,
    soul_spec: str,
    wiki_dir: Path,
    model: str,
    timeout_seconds: int,
) -> dict:
    """Run one task via `claude -p` with stream-json output, printing
    live progress (tool calls, response chunks) to stderr as events arrive.
    """
    import threading

    prompt = CONDITION_E_PROMPT_TEMPLATE.format(task=task_text)
    cmd = build_claude_cmd(prompt, soul_spec, wiki_dir, model, timeout_seconds)

    started = time.time()
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        cwd=REPO_ROOT,
    )

    # Watchdog: kill the subprocess if it exceeds the timeout. The reading
    # loop exits naturally when the pipe closes.
    done = threading.Event()
    timed_out = {"flag": False}

    def watchdog() -> None:
        if not done.wait(timeout=timeout_seconds):
            timed_out["flag"] = True
            try:
                proc.kill()
            except Exception:
                pass

    threading.Thread(target=watchdog, daemon=True).start()

    response_text = ""
    tool_calls: list[dict] = []
    final_usage: dict = {}
    session_id: str | None = None
    stop_reason: str | None = None

    try:
        for line in proc.stdout or []:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = evt.get("type")
            if etype == "system" and evt.get("subtype") == "init":
                session_id = evt.get("session_id")
                _progress(started, f"init  session={(session_id or '?')[:8]}  model={evt.get('model', model)}")
            elif etype == "assistant":
                msg = evt.get("message", {})
                for block in msg.get("content", []):
                    btype = block.get("type")
                    if btype == "tool_use":
                        name = block.get("name", "?")
                        inp = block.get("input", {}) or {}
                        detail = (
                            inp.get("path")
                            or inp.get("pattern")
                            or inp.get("file_path")
                            or inp.get("command")
                            or inp.get("query")
                            or ""
                        )
                        _progress(started, f"→ {name}({str(detail)[:60]})")
                        tool_calls.append({"name": name, "input": inp})
                    elif btype == "text":
                        text = block.get("text", "")
                        if text:
                            response_text += text
                            preview = " ".join(text.split())[:80]
                            if preview:
                                _progress(started, f"← {preview}{'…' if len(text) > 80 else ''}")
            elif etype == "user":
                # tool_result echoed back; suppress to keep output compact
                pass
            elif etype == "result":
                stop_reason = evt.get("stop_reason")
                final_usage = evt.get("usage", {}) or {}
                final_text = evt.get("result")
                if final_text:
                    response_text = final_text
                _progress(
                    started,
                    f"done  stop={stop_reason}  in={final_usage.get('input_tokens', 0)} "
                    f"out={final_usage.get('output_tokens', 0)}",
                )
            elif etype == "error":
                _progress(started, f"ERROR {evt.get('message', evt)}")
    finally:
        done.set()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    wall = round(time.time() - started, 2)

    if timed_out["flag"]:
        return {
            "task_id": task_id,
            "task": task_text,
            "response": f"(timeout after {timeout_seconds}s)",
            "error": "timeout",
            "wall_seconds": wall,
            "model": model,
            "backend": "claude-code",
        }

    if proc.returncode != 0:
        stderr = proc.stderr.read() if proc.stderr else ""
        return {
            "task_id": task_id,
            "task": task_text,
            "response": response_text or "(claude CLI exited non-zero)",
            "error": stderr[:1000],
            "returncode": proc.returncode,
            "wall_seconds": wall,
            "model": model,
            "backend": "claude-code",
        }

    return {
        "task_id": task_id,
        "task": task_text,
        "response": response_text,
        "session_id": session_id,
        "input_tokens": final_usage.get("input_tokens", 0),
        "output_tokens": final_usage.get("output_tokens", 0),
        "cache_creation_input_tokens": final_usage.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": final_usage.get("cache_read_input_tokens", 0),
        "stop_reason": stop_reason,
        "tool_calls": tool_calls,
        "tool_call_count": len(tool_calls),
        "wall_seconds": wall,
        "model": model,
        "backend": "claude-code",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--wiki-dir", type=Path, default=DEFAULT_WIKI)
    ap.add_argument("--soul", type=Path, default=DEFAULT_SOUL)
    ap.add_argument("--taskset", type=Path, default=DEFAULT_TASKSET)
    ap.add_argument("--task", help="Run only this task ID (e.g., IR-1)")
    ap.add_argument(
        "--model",
        default="opus",
        help="Model alias or full name. 'opus' = latest Opus on subscription.",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Per-task wall-clock timeout in seconds (default 600 = 10 min).",
    )
    ap.add_argument("--output", type=Path, default=None)
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the claude CLI command that would be invoked, without running.",
    )
    args = ap.parse_args()

    for path, label in [
        (args.wiki_dir, "wiki dir"),
        (args.soul, "soul spec"),
        (args.taskset, "taskset"),
    ]:
        if not path.exists():
            sys.exit(f"{label} not found: {path}")

    if not args.dry_run:
        # Best-effort sanity check; doesn't fail on missing claude (some
        # contexts wrap it). User sees clear error from subprocess later.
        if not _claude_in_path():
            print(
                "WARNING: 'claude' CLI not found in PATH. "
                "Install Claude Code: https://docs.claude.com/en/docs/claude-code",
                file=sys.stderr,
            )
        if os.environ.get("ANTHROPIC_API_KEY"):
            print(
                "NOTE: ANTHROPIC_API_KEY is set; it takes precedence over the "
                "subscription. `unset ANTHROPIC_API_KEY` if you want to bill "
                "against your Pro/Max subscription instead.",
                file=sys.stderr,
            )

    soul_spec = args.soul.read_text(encoding="utf-8")
    tasks = parse_taskset(args.taskset)
    if args.task:
        tasks = [(tid, t) for tid, t in tasks if tid == args.task]
        if not tasks:
            sys.exit(f"task {args.task} not found in {args.taskset}")

    if args.dry_run:
        print(f"Would run {len(tasks)} task(s) via local `claude` CLI:")
        for tid, body in tasks:
            preview = body.split("\n", 1)[0]
            if len(preview) > 80:
                preview = preview[:77] + "..."
            print(f"  {tid}: {preview}")
        # Show the command shape for the first task as a sanity check.
        sample_prompt = CONDITION_E_PROMPT_TEMPLATE.format(task=tasks[0][1])
        sample_cmd = build_claude_cmd(
            sample_prompt[:60] + "...(truncated)",
            soul_spec[:40] + "...(truncated)",
            args.wiki_dir,
            args.model,
            args.timeout,
        )
        print("\nSample command (truncated for display):")
        print("  " + " \\\n    ".join(repr(x) if " " in x else x for x in sample_cmd))
        print(f"\nTimeout per task: {args.timeout}s. Model: {args.model}.")
        print("(--dry-run: no claude invocations made)")
        return 0

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = (
        args.output or RESULTS_DIR / f"condition-E-claudecode-{timestamp}.json"
    )

    results: list[dict] = []
    for task_id, task_text in tasks:
        print(f"  running {task_id} ...", file=sys.stderr, flush=True)
        result = run_one_task_via_claude_code(
            task_id=task_id,
            task_text=task_text,
            soul_spec=soul_spec,
            wiki_dir=args.wiki_dir,
            model=args.model,
            timeout_seconds=args.timeout,
        )
        results.append(result)
        if result.get("error"):
            print(
                f"    {task_id}: ERROR — {result['error'][:120]}",
                file=sys.stderr,
            )
        else:
            print(
                f"    {task_id}: {result.get('input_tokens', 0)} in / "
                f"{result.get('output_tokens', 0)} out, "
                f"{result.get('wall_seconds', 0)}s",
                file=sys.stderr,
            )

    summary = {
        "run_id": timestamp,
        "condition": "E",
        "backend": "claude-code",
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


def _claude_in_path() -> bool:
    from shutil import which
    return which("claude") is not None


if __name__ == "__main__":
    sys.exit(main())
