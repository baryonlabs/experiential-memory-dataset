#!/usr/bin/env python3
"""LLM-as-judge scorer for Condition E run output.

Reads a results JSON produced by `scripts/run_condition_e.py` and scores
each task response against the rubric in `evaluation/rubric.md`. Uses
Claude as a blind judge: the judge sees only the task and the response,
not the condition label or memory source.

Output: results/<run_id>-scored.json with per-task 1-5 scores plus a
summary mean. The summary mean is the metric autoresearch optimizes.

Usage:
  export ANTHROPIC_API_KEY=...
  python scripts/score_responses.py results/condition-E-run-<ts>.json
  python scripts/score_responses.py --judge-model claude-sonnet-4-5 ...
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]
    # Lazy: only required for --backend api; --backend claude-code uses subprocess.

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUBRIC = REPO_ROOT / "evaluation" / "rubric.md"

JUDGE_PROMPT = """\
You are a blind evaluator of an AI development assistant's response to a
single task. Score the response 1–5 against the rubric below. Be strict
but fair. Do not award high scores for verbosity alone.

Rubric:

{rubric}

Task:

{task}

Response:

{response}

Output exactly one line in this format:

SCORE: <integer 1-5>
REASON: <one short sentence>
"""

SCORE_RE = re.compile(r"^\s*SCORE\s*:\s*([1-5])\b", re.MULTILINE)
REASON_RE = re.compile(r"^\s*REASON\s*:\s*(.+?)\s*$", re.MULTILINE)


def judge_one_via_api(
    client,
    rubric: str,
    task: str,
    response: str,
    model: str,
) -> tuple[int | None, str]:
    msg = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": JUDGE_PROMPT.format(
                    rubric=rubric, task=task, response=response
                ),
            }
        ],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return _parse_judge_text(text)


def judge_one_via_claude_code(
    rubric: str,
    task: str,
    response: str,
    model: str,
    timeout_seconds: int = 120,
) -> tuple[int | None, str]:
    prompt = JUDGE_PROMPT.format(rubric=rubric, task=task, response=response)
    cmd = [
        "claude",
        "-p", prompt,
        "--no-session-persistence",
        "--model", model,
        "--output-format", "json",
        "--tools", "",  # strictly disable all tools — judge is pure text in/out
        "--permission-mode", "bypassPermissions",
    ]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout_seconds
        )
    except subprocess.TimeoutExpired:
        return None, f"(judge timeout after {timeout_seconds}s)"
    if proc.returncode != 0:
        return None, f"(claude exit {proc.returncode}: {proc.stderr[:200]})"
    try:
        out = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        return None, f"(judge JSON parse: {e})"
    return _parse_judge_text(out.get("result", ""))


def _parse_judge_text(text: str) -> tuple[int | None, str]:
    score_m = SCORE_RE.search(text)
    reason_m = REASON_RE.search(text)
    score = int(score_m.group(1)) if score_m else None
    reason = reason_m.group(1) if reason_m else text.strip()[:200]
    return score, reason


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("results_json", type=Path)
    ap.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    ap.add_argument(
        "--backend",
        choices=["claude-code", "api"],
        default="claude-code",
        help="Judge backend. 'claude-code' uses local CLI (subscription auth, no API key). 'api' uses Anthropic SDK.",
    )
    ap.add_argument(
        "--judge-model",
        default=None,
        help="Model alias. Defaults: 'sonnet' (claude-code) or 'claude-sonnet-4-6' (api).",
    )
    ap.add_argument("--output", type=Path, default=None)
    args = ap.parse_args()

    if not args.results_json.exists():
        sys.exit(f"results file not found: {args.results_json}")
    if not args.rubric.exists():
        sys.exit(f"rubric not found: {args.rubric}")

    if args.judge_model is None:
        args.judge_model = "sonnet" if args.backend == "claude-code" else "claude-sonnet-4-6"

    data = json.loads(args.results_json.read_text(encoding="utf-8"))
    rubric = args.rubric.read_text(encoding="utf-8")

    client = None
    if args.backend == "api":
        if anthropic is None:
            sys.exit("Install for --backend api: pip install anthropic")
        client = anthropic.Anthropic()

    scored = []
    for r in data["results"]:
        if args.backend == "claude-code":
            score, reason = judge_one_via_claude_code(
                rubric=rubric,
                task=r["task"],
                response=r.get("response", ""),
                model=args.judge_model,
            )
        else:
            score, reason = judge_one_via_api(
                client=client,
                rubric=rubric,
                task=r["task"],
                response=r.get("response", ""),
                model=args.judge_model,
            )
        scored.append(
            {
                "task_id": r["task_id"],
                "score": score,
                "reason": reason,
                "tool_call_count": r.get("tool_call_count"),
                "input_tokens": r.get("input_tokens"),
                "output_tokens": r.get("output_tokens"),
                "wall_seconds": r.get("wall_seconds"),
            }
        )
        print(f"  {r['task_id']}: {score} — {reason[:80]}", file=sys.stderr)

    valid_scores = [s["score"] for s in scored if s["score"] is not None]
    summary = {
        "run_id": data.get("run_id"),
        "condition": data.get("condition"),
        "eval_backend": data.get("backend"),
        "eval_model": data.get("model"),
        "judge_backend": args.backend,
        "judge_model": args.judge_model,
        "task_count": len(scored),
        "scored_count": len(valid_scores),
        "mean_score": (
            round(sum(valid_scores) / len(valid_scores), 3)
            if valid_scores
            else None
        ),
        "min_score": min(valid_scores) if valid_scores else None,
        "max_score": max(valid_scores) if valid_scores else None,
        "scored": scored,
    }

    out_path = (
        args.output
        or args.results_json.with_name(args.results_json.stem + "-scored.json")
    )
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(
        f"\nMean score: {summary['mean_score']}  (n={summary['scored_count']})\n"
        f"Wrote {out_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
