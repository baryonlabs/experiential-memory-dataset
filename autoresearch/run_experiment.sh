#!/usr/bin/env bash
# autoresearch/run_experiment.sh
#
# One experiment cycle: lint -> eval -> score -> emit loss.
#
# Exit codes:
#   0  — cycle completed, loss printed to stdout
#   1  — fidelity lint failed (abort cycle, revert in caller)
#   2  — eval or score step failed
#
# Environment:
#   AR_BACKEND          eval backend: "claude-code" (default, uses subscription)
#                                     or "api" (uses ANTHROPIC_API_KEY)
#   AR_MODEL            default: opus      (claude-code) | claude-opus-4-7 (api)
#   AR_JUDGE_MODEL      default: sonnet    (claude-code) | claude-sonnet-4-6 (api)
#   AR_MAX_TOOL_CALLS   default: 40        (api backend only)
#   AR_TIMEOUT          default: 600       (claude-code backend, per-task seconds)
#
# When AR_BACKEND=claude-code (default), eval uses the local `claude` CLI
# and bills against your Pro/Max subscription. Make sure ANTHROPIC_API_KEY
# is unset, otherwise it takes precedence and bills the API instead.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

BACKEND="${AR_BACKEND:-claude-code}"

if [[ "$BACKEND" == "claude-code" ]]; then
  MODEL="${AR_MODEL:-opus}"
  JUDGE_MODEL="${AR_JUDGE_MODEL:-sonnet}"
  TIMEOUT="${AR_TIMEOUT:-600}"
else
  MODEL="${AR_MODEL:-claude-opus-4-7}"
  JUDGE_MODEL="${AR_JUDGE_MODEL:-claude-sonnet-4-6}"
  MAX_TOOL_CALLS="${AR_MAX_TOOL_CALLS:-40}"
fi

echo "[1/3] fidelity lint" >&2
if ! python3 scripts/lint_fidelity.py >/tmp/ar-lint.log 2>&1; then
  echo "FIDELITY LINT FAILED" >&2
  cat /tmp/ar-lint.log >&2
  exit 1
fi

echo "[2/3] run Condition E (backend=$BACKEND, model=$MODEL)" >&2
if [[ "$BACKEND" == "claude-code" ]]; then
  RESULTS_JSON=$(python3 scripts/run_condition_e_via_claude_code.py \
    --model "$MODEL" \
    --timeout "$TIMEOUT" 2>&1 | tee /tmp/ar-run.log | \
    grep -oE 'results/condition-E-claudecode-[^[:space:]]+\.json' | tail -1)
else
  RESULTS_JSON=$(python3 scripts/run_condition_e.py \
    --model "$MODEL" \
    --max-tool-calls "$MAX_TOOL_CALLS" 2>&1 | tee /tmp/ar-run.log | \
    grep -oE 'results/condition-E-run-[^[:space:]]+\.json' | tail -1)
fi

if [[ -z "${RESULTS_JSON:-}" || ! -f "$RESULTS_JSON" ]]; then
  echo "EVAL STEP FAILED" >&2
  cat /tmp/ar-run.log >&2
  exit 2
fi

echo "[3/3] score with judge=$JUDGE_MODEL" >&2
python3 scripts/score_responses.py \
  --judge-model "$JUDGE_MODEL" \
  "$RESULTS_JSON" >/tmp/ar-score.log 2>&1 || {
  echo "SCORE STEP FAILED" >&2
  cat /tmp/ar-score.log >&2
  exit 2
}

SCORED_JSON="${RESULTS_JSON%.json}-scored.json"
MEAN_SCORE=$(python3 -c "import json,sys; d=json.load(open('$SCORED_JSON')); print(d['mean_score'])")

# loss = 1 - (mean - 1) / 4
LOSS=$(python3 -c "m=$MEAN_SCORE; print(round(1 - (m - 1) / 4, 4))")

echo "mean_score=$MEAN_SCORE  loss=$LOSS  results=$RESULTS_JSON  scored=$SCORED_JSON" >&2

# autoresearch reads stdout for the metric.
echo "$LOSS"
