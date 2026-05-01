# Autoresearch Integration

Scaffolding for plugging this fork into [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) so an autonomous agent can iteratively optimize the LLM-Wiki structure.

## What Gets Optimized

The wiki is the *training target*. autoresearch's agent modifies it (within fidelity constraints) and observes the effect on the taskset score. Allowed modifications:

| Target | Allowed | Forbidden |
|---|---|---|
| `wiki/CLAUDE.md` (operating rules) | Yes — schema, ingest/query/lint procedures | — |
| `wiki/index.md` (catalog) | Yes — clustering, ordering, columns | — |
| `wiki/pages/*.md` front-matter | Yes — `summary`, `tags`, `related` | Cannot remove `source:` field |
| `wiki/pages/*.md` body — wiki-only sections | Yes — inline cross-ref links, `## Related` block, parenthetical notes that don't break source sentences | — |
| `wiki/pages/*.md` body — source content | **No** | Editing source-derived sentences (lint enforces) |
| Splitting / merging pages | Yes (with corresponding `index.md` update) | Cannot drop content covered by an existing source file |
| `synthetic-memory/` (sources) | **No** | Forbidden — these are the immutable ground truth |
| `taskset.md`, `evaluation/rubric.md` | **No** | Forbidden — changing these contaminates the comparison |

The fidelity lint (`scripts/lint_fidelity.py`) enforces "no source content edits" automatically before each evaluation.

## Loss Function

autoresearch expects "lower is better" (matching `val_bpb` in the original). We define:

```
loss = 1.0 - (mean_rubric_score - 1) / 4
```

So a perfect mean of 5.0 → loss = 0.0; baseline mean of 3.0 → loss = 0.5; worst mean of 1.0 → loss = 1.0.

The LLM-as-judge scorer (`scripts/score_responses.py`) produces the rubric scores used in this formula.

## Cycle

1. **Mutate**: Agent edits one or more allowed targets.
2. **Lint**: `scripts/lint_fidelity.py` rejects edits that break source fidelity. If lint fails, the cycle aborts and reverts.
3. **Evaluate**: `scripts/run_condition_e.py` runs the full taskset (15 questions) against the modified wiki. Wall-clock budget ≈ 5 min on `claude-opus-4-5` with `max_tool_calls=40`.
4. **Score**: `scripts/score_responses.py` (LLM-as-judge) yields per-task 1–5 scores and a mean.
5. **Decide**: autoresearch keeps or discards the change based on whether `loss` improved over the prior best.

`autoresearch/run_experiment.sh` performs steps 2–4 in one invocation and prints the final loss to stdout.

## Bootstrapping

Before running the optimization loop:

1. Establish baseline: run Condition E on the current hand-curated wiki (the state in this repo) and record the loss.
2. Establish ceiling: run Condition C (Hybrid) — already in the parent paper. Hybrid scored 4.95/5 → loss ≈ 0.012. autoresearch should not exceed this.
3. Establish floor: run Condition D (Baseline) — scored 3.30/5 → loss ≈ 0.425. autoresearch should never produce a worse loss.

If autoresearch's best run beats the hand-curated baseline by a non-trivial margin (e.g., loss drops by ≥ 0.05) on a held-out task subset, that's the headline finding for the v2 paper.

## Setup

See `autoresearch/program.md` for the agent's instructions and `autoresearch/run_experiment.sh` for the experiment wrapper. The actual integration with karpathy/autoresearch requires:

```bash
git clone https://github.com/karpathy/autoresearch /tmp/autoresearch
cd /tmp/autoresearch
# Configure autoresearch to point its `program.md` and `run_experiment.sh`
# at this repo's autoresearch/ directory.
```

The detailed wiring depends on autoresearch's runtime conventions, which are tracked separately as the project evolves. This scaffolding establishes the *interface* (mutable targets, loss function, cycle) so autoresearch's runner can drive it.

## Risks and Guardrails

- **Reward hacking via lint bypass**: The agent might try to delete `source:` fields or split pages to avoid fidelity checks. The lint rejects these. A periodic manual review of `wiki/log.md` is recommended.
- **Judge collusion**: Using the same model family for both the agent and the LLM-as-judge can create biased optimism. Cross-check periodically with a different judge model (e.g., switch from `claude-sonnet-4-5` to a different vendor's judge).
- **Overfitting to the 15-task set**: Hold out a sub-batch of tasks (e.g., 3 of 15) from the optimization loop and use only for final reporting.
- **Wall-clock cost**: Each cycle = 1 lint + 15 task runs (with tool calls) + 15 judge calls. Budget realistically ≈ $1-3 per cycle on Opus, $0.20-0.50 on Sonnet.
