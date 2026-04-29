# RAG vs LLM-Wiki — Experimental Design Extension

**Status**: Proposal / PoC stage
**Branch**: `claude/rag-vs-graph-comparison-vAOGf`
**Parent paper**: *Experiential vs Synthetic Memory in Long-Running AI Agents* (Zenodo DOI 10.5281/zenodo.18798227)

## Motivation

The original experiment compared four memory **contents** (Experiential, Synthetic, Hybrid, None) under a single retrieval method (semantic-search RAG). The most surprising finding was that **synthetic memory underperformed the no-memory baseline** (2.65 < 3.30). This raises a confound:

> Was synthetic memory bad because of its **content** (documentation-style, lacking project specificity), or because of its **retrieval method** (flat semantic chunking that strips structure)?

Disentangling these requires a second axis: **retrieval method**. We propose adding the **LLM-Wiki** method (Karpathy gist; cf. [news.hada.io topic 28208](https://news.hada.io/topic?id=28208)) as a contrast to RAG, holding content constant.

## Hypothesis

**H1**: A wiki-structured representation of the same synthetic corpus will recover much of the gap, performing at or above the no-memory baseline. If true, retrieval method explains a large fraction of the original B<D result, not content quality.

**H2** (weaker): Wiki structure also benefits experiential memory but with smaller marginal gains, because the experiential corpus already contains implicit cross-reference structure from real collaboration.

**H3** (cost): Per-query token usage rises (the agent reads whole pages instead of chunks), but per-corpus setup cost falls to zero (no embeddings). Net cost is workload-dependent.

## Design

### Conditions

Existing four conditions retained; two new conditions added:

| Cond | Memory content | Retrieval | Status |
|------|---------------|-----------|--------|
| A | Experiential 157 | RAG | original |
| B | Synthetic 20 | RAG | original |
| C | Hybrid (A+B) | RAG | original |
| D | None | — | original |
| **E** | **Synthetic 20 (wiki-converted)** | **LLM-Wiki** | **new** |
| **F** | **Experiential 157 (wiki-converted)** | **LLM-Wiki** | **new** |

Optional follow-on: G = Hybrid wiki.

### Independent Variable

**Retrieval method only**, between B↔E and A↔F. Memory *content* is held constant: each wiki page records its source file in front-matter (`source: synthetic-memory/<file>.md`) and a lint pass verifies content fidelity.

### Controls

- **LLM**: same model as original (Claude Opus 4 / current `claude-opus-4-7`) across all conditions in any given comparison run.
- **Tasks**: `taskset_KO.md` (Korean original) unchanged. Cross-language replication uses `taskset.md`.
- **Soul Spec**: `soul-spec-anonymized/` unchanged.
- **Session isolation**: each task run in a fresh session. No cross-task contamination.
- **Tool surface for E/F**: `Read`, `Glob`, `Grep`, plus reading `wiki/CLAUDE.md` on session start. No `memory_search` / vector-search tool.
- **Tool surface for A/B/C**: as in original (RAG `memory_search` → `memory_get`).
- **Blind evaluation**: shuffled W/X/Y/Z labels (extend to 6 labels for new conditions).

### Metrics

Primary (matching original rubric):
- 4-category scores (Information Retrieval / Coding / Architecture / Context-Dependent), 1–5 Likert
- Overall mean

Secondary (new, captured per condition):
- **Tokens read per task** (proxy for cost)
- **Wall-clock latency per task**
- **Pages visited per task** (E/F only) — proxy for traversal depth
- **Citation accuracy** (E/F only) — does the agent cite the page it actually read?

### Wiki Construction

Implementation follows `wiki/CLAUDE.md`:

```
wiki/
├── CLAUDE.md       # operating rules (schema)
├── index.md        # catalog
├── log.md          # timeline of actions
└── pages/          # one markdown file per topic
```

For Condition E (synthetic-wiki):
1. Convert each of the 20 `synthetic-memory/*.md` files into one or more wiki pages.
2. Add front-matter with `source:` pointing back to the original file (for fidelity audit).
3. Add inline cross-references (`[other-page](other-page.md)`) and a `## Related` section.
4. Build `index.md` clustered by topic.

For Condition F (experiential-wiki, private data): same procedure applied to the ~157 experiential files. Performed by a researcher with access to the private corpus; not committed publicly.

### Conversion Fidelity (critical for fairness)

The wiki must contain **the same factual content** as the source files. Cross-references and structure are *additive overlay*, not editorial rewriting. A lint pass before evaluation:

- For each page with `source:` front-matter, verify all factual claims in the source appear in the page.
- Flag any addition not derivable from the source.
- Flag any deletion of source content.

If fidelity is not preserved, the comparison is contaminated.

### Cost Comparison (planned)

Record per condition:
- One-time setup cost (embedding compute for A/B/C; wiki authoring LLM tokens for E/F)
- Per-query cost (vector DB hits + embeddings for A/B/C; file reads for E/F)
- Maintenance cost when sources change (re-embed vs re-ingest)

## Current Status (PoC)

Implemented in this branch:

- [x] `wiki/CLAUDE.md` — schema and operating rules
- [x] `wiki/index.md` — initial catalog (Web/App Stack cluster only)
- [x] `wiki/log.md` — bootstrap log entry
- [x] 3 PoC pages in `wiki/pages/`: `nextjs-supabase`, `supabase-auth-rls`, `fullstack-architecture` (form a cross-referenced triangle for schema validation)
- [ ] Convert remaining 17 `synthetic-memory/` files
- [ ] Spawn prompt for Condition E (extend `spawn-prompts.md`)
- [ ] Evaluation script (Condition E run + scoring)
- [ ] Fidelity lint pass
- [ ] Repeat for Condition F (private)

## Open Questions

1. **Page granularity**: when a source file covers two topics, split into two pages or keep one? Current PoC keeps one page per source for simplicity. Splitting may improve retrieval precision but complicates fidelity audit.
2. **Index granularity**: single flat `index.md` vs. per-cluster sub-indexes? PoC uses single flat with H2 clusters.
3. **Wiki authoring agent vs. human**: should the wiki itself be authored by an LLM (matching the LLM-Wiki pattern's compounding-knowledge ideal) or hand-curated? PoC is hand-curated for fairness control. A future arm could test LLM-authored wikis.
4. **Token budget for E/F**: should we cap reads per task to make cost comparison fair? If yes, what cap?

## Reproducibility

The synthetic corpus and wiki are public (CC-BY-4.0). Anyone can reproduce Condition E by:

1. Cloning this repo on `claude/rag-vs-graph-comparison-vAOGf`.
2. Running an agent with `Read`/`Glob`/`Grep` tools rooted in `wiki/`.
3. Using prompts from `spawn-prompts.md` (Condition E section, TBA).
4. Scoring with `evaluation/rubric.md`.

Condition F (experiential-wiki) requires the private experiential corpus, available on request per the parent paper's data policy.
