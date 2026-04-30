# RAG vs LLM-Wiki — Experimental Design Extension

**Status**: Proposal / PoC stage
**Branch**: `claude/rag-vs-graph-comparison-vAOGf`
**Parent paper**: *Experiential vs Synthetic Memory in Long-Running AI Agents* (Zenodo DOI 10.5281/zenodo.18798227)

## Motivation

The original experiment compared four memory **contents** (Experiential, Synthetic, Hybrid, None) under a single retrieval method (semantic-search RAG). The most surprising finding was that **synthetic memory underperformed the no-memory baseline** (2.65 < 3.30). This raises a confound:

> Was synthetic memory bad because of its **content** (documentation-style, lacking project specificity), or because of its **retrieval method** (flat semantic chunking that strips structure)?

Disentangling these requires a second axis: **retrieval method**. We propose adding the **LLM-Wiki** method ([Karpathy 2026][karpathy]; cf. [news.hada.io topic 28208](https://news.hada.io/topic?id=28208)) as a contrast to RAG, holding content constant.

## Related Work and Positioning

Three lines of work motivate this extension:

**1. Structured retrieval generally beats flat RAG on relational tasks.** Microsoft's GraphRAG ([Edge et al. 2024][graphrag]) builds an entity knowledge graph plus community summaries from a corpus, demonstrating substantial gains over conventional RAG on global sensemaking queries over million-token datasets. LinkedIn's deployed customer-service KG-RAG ([Xu et al. 2024][linkedin]) reports **+77.6% MRR**, **+0.32 BLEU**, and **−28.6% median issue resolution time** in production — the strongest empirical evidence to date that preserving inter-document structure pays off on real workloads.

**2. The advantage is task-dependent, not universal.** [Xiang et al. 2025][whennot] benchmark when graph augmentation actually helps and find GraphRAG **frequently underperforms vanilla RAG** on many real tasks: graph structure helps most for *hierarchical reasoning and contextual summarization*, least for *plain fact retrieval*. This maps directly onto our taskset's four categories (see *Per-Category Predictions* below).

**3. Systematic head-to-head benchmarks exist but use different corpora.** [Han et al. 2025][ragvsgraphrag] provide unified evaluation protocols comparing RAG and GraphRAG on QA and query-focused summarization, finding distinct strengths per paradigm and that hybrid selection strategies win consistently. Our experiment differs by holding *content* constant across conditions (same 20 synthetic / 157 experiential files used in both arms), isolating retrieval-method effect on a *single-agent software-development* workload — a context absent from the existing benchmarks.

### Where this experiment sits in the design space

| Point | Index | Retrieval | Build cost | Examples |
|-------|-------|-----------|------------|----------|
| Flat RAG | embedding chunks | vector similarity | embedding compute + DB | original Conditions A–C |
| GraphRAG | entity KG + community summaries | graph traversal + summary lookup | LLM-driven graph extraction | [Edge et al.][graphrag], [Xu et al.][linkedin] |
| **LLM-Wiki (this work)** | **markdown pages + `index.md` + `## Related`** | **`Read`/`Glob`/`Grep` + link traversal** | **LLM-curated cross-refs only** | [Karpathy gist][karpathy], Conditions E/F |

LLM-Wiki is the *lightest-weight* point in this design space: no entity extraction, no embeddings, no vector DB, no graph DB. Its cost-of-entry is hours of LLM authoring time, not engineering complexity. This makes it especially attractive for the user's stated pain points (embedding sunk cost, per-search cost, technical complexity).

A future arm could add **Condition G = Microsoft-GraphRAG-on-same-corpus** to span all three points; deferred for scope.

## Hypothesis

**H1**: A wiki-structured representation of the same synthetic corpus will recover much of the gap, performing at or above the no-memory baseline. If true, retrieval method explains a large fraction of the original B<D result, not content quality.

**H2** (weaker): Wiki structure also benefits experiential memory but with smaller marginal gains, because the experiential corpus already contains implicit cross-reference structure from real collaboration.

**H3** (cost): Per-query token usage rises (the agent reads whole pages instead of chunks), but per-corpus setup cost falls to zero (no embeddings). Net cost is workload-dependent.

### Per-Category Predictions

Following [Xiang et al. 2025][whennot] — graph structure helps most for hierarchical reasoning and contextual synthesis, least for plain fact retrieval — we predict the per-category effect of moving from RAG to Wiki on the synthetic corpus:

| Category | RAG (B, observed) | Wiki (E, predicted) | Rationale |
|----------|:---:|:---:|---|
| Information Retrieval | 1.4 | small gain (≈2.0–2.5) | Mostly fact lookup; structure helps disambiguation only |
| Coding Tasks | 3.2 | moderate gain (≈3.8–4.2) | Agent benefits from following related-page links to find idiomatic patterns |
| Architecture Decisions | 3.4 | **large gain (≈4.3–4.8)** | Hierarchical reasoning across stack layers — exactly where structure pays off |
| Context-Dependent | 2.6 | **large gain (≈4.0–4.5)** | Cross-reference traversal is the natural fit |

Falsification: if E ≈ B across all four categories, retrieval method does *not* explain the original B<D result, and the content-quality interpretation stands. If E exceeds B in IR but not in Architecture/Context-Dependent, our prediction is wrong in direction and the literature's task-dependence claim doesn't transfer to this workload.

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

## References

- <a id="ref-ragvsgraphrag"></a>**[Han et al. 2025]** Han, H., Ma, L., Wang, Y., Shomer, H., Lei, Y., Qi, Z., Guo, K., Hua, Z., Long, B., Liu, H., Aggarwal, C. C., & Tang, J. (2025). *RAG vs. GraphRAG: A Systematic Evaluation and Key Insights*. arXiv:2502.11371. <https://arxiv.org/abs/2502.11371>
  *Used here as the methodological model for unified evaluation protocols (preprocessing, retrieval, generation held constant). Our contribution differs by holding content constant and varying retrieval method on a software-development workload.*

- <a id="ref-graphrag"></a>**[Edge et al. 2024]** Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., Truitt, S., Metropolitansky, D., Ness, R. O., & Larson, J. (2024). *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*. arXiv:2404.16130. <https://arxiv.org/abs/2404.16130>
  *Canonical GraphRAG instantiation: entity KG + community summaries. Our LLM-Wiki sits at a different point in the design space (markdown + cross-refs, no entity extraction).*

- <a id="ref-karpathy"></a>**[Karpathy 2026]** Karpathy, A. *LLM-Wiki pattern* (gist). <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>
  *Direct framing for Conditions E/F. Defines the three-layer architecture (raw sources / wiki / schema) and the ingest–query–lint workflow that `wiki/CLAUDE.md` operationalizes.*

- <a id="ref-linkedin"></a>**[Xu et al. 2024]** Xu, Z., Cruz, M. J., Guevara, M., Wang, T., Deshpande, M., Wang, X., & Li, Z. (2024). *Retrieval-Augmented Generation with Knowledge Graphs for Customer Service Question Answering*. SIGIR 2024. arXiv:2404.17723. doi:10.1145/3626772.3661370. <https://arxiv.org/abs/2404.17723>
  *Strongest deployed empirical evidence for structured retrieval over flat RAG: +77.6% MRR, +0.32 BLEU, −28.6% median resolution time at LinkedIn. Cited as evidence that retrieval-method gains transfer to production workloads.*

- <a id="ref-whennot"></a>**[Xiang et al. 2025]** Xiang, Z., Wu, C., Zhang, Q., Chen, S., Hong, Z., Huang, X., & Su, J. (2025). *When to use Graphs in RAG: A Comprehensive Analysis for Graph Retrieval-Augmented Generation*. arXiv:2506.05690. <https://arxiv.org/abs/2506.05690>
  *Provides the task-dependence claim: graph helps for hierarchical reasoning and contextual summarization, not plain fact retrieval. Grounds the per-category predictions table.*

[ragvsgraphrag]: #ref-ragvsgraphrag
[graphrag]: #ref-graphrag
[karpathy]: #ref-karpathy
[linkedin]: #ref-linkedin
[whennot]: #ref-whennot
