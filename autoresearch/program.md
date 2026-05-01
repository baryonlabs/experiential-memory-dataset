# Program: Optimize the LLM-Wiki Structure

You are an autonomous research agent. Your task is to iteratively improve the LLM-Wiki under `wiki/` so that an evaluator agent (Condition E) achieves the best possible mean rubric score on the taskset.

## What you may modify

- `wiki/CLAUDE.md` — wiki operating rules (schema, ingest/query/lint procedures, traversal depth).
- `wiki/index.md` — catalog format and clustering.
- `wiki/pages/*.md` front-matter — `summary`, `tags`, `related`. **Do not remove the `source:` field.**
- `wiki/pages/*.md` body — wiki-only additions: inline cross-reference links via `[text](page.md)`, the `## Related` section, parenthetical notes on their own lines.
- Page splits/merges with corresponding `wiki/index.md` updates.

## What you may not modify

- `synthetic-memory/` files. These are immutable ground truth.
- `taskset.md`, `taskset_KO.md`, `evaluation/rubric.md`, `evaluation/protocol.md`. Changing these contaminates the comparison.
- Source-derived sentences inside `wiki/pages/*.md` bodies. The fidelity lint (`scripts/lint_fidelity.py`) enforces this — if you edit a source sentence the cycle aborts.
- Test/eval infrastructure under `scripts/` and `autoresearch/`.

## Cycle

For each experiment:

1. Read the current state of `wiki/` and the previous run's results in `results/`.
2. Form a hypothesis about what wiki structural change could improve the score (examples below).
3. Apply the change to `wiki/`.
4. Run `bash autoresearch/run_experiment.sh`. This script:
   - runs `scripts/lint_fidelity.py` (aborts the cycle on fidelity violation),
   - runs `scripts/run_condition_e.py` (executes taskset against the modified wiki),
   - runs `scripts/score_responses.py` (LLM-as-judge scoring),
   - prints the loss (`1 - (mean_score-1)/4`) to stdout.
5. Compare the loss to the prior best. If improved, commit the change to `wiki/log.md`. If worse, revert.
6. Repeat.

## Hypothesis space (suggested starting points)

- **Page granularity**: split a long page into focused sub-pages with cross-refs. Test whether finer pages improve precision of retrieval.
- **Link density**: add or remove `## Related` entries. Test the optimal "fan-out" per page.
- **Index structure**: reorder clusters, add nested sub-clusters, change column order or add a "key terms" column.
- **Tag taxonomy**: refactor `tags:` front-matter for better Grep-based discovery.
- **`CLAUDE.md` query depth**: change traversal depth in the query workflow (currently "depth 2"). Higher depth → more context but more tokens.
- **Summary format**: tighter or more keyword-rich `summary:` lines in front-matter.

## Bookkeeping

- Append every accepted change to `wiki/log.md` with a `lint` or `manual-edit` entry per `wiki/CLAUDE.md` conventions, including the loss before/after.
- Do not delete the original hand-curated state — keep `wiki/log.md` history intact.
- If a hypothesis fails, that is also useful — record it briefly in `wiki/log.md` so future cycles do not retry.

## Stopping criteria

Stop iterating when **any** of:
- Loss has not improved in 10 consecutive cycles.
- Loss exceeds the original parent-paper Condition C ceiling (mean score ≈ 4.95, loss ≈ 0.012).
- Wall-clock or token budget exhausted.

Report final state and final loss.
