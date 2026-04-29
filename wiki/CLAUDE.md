# Wiki Operating Rules

This file is the schema for an LLM-maintained wiki, following the LLM-Wiki pattern (Karpathy gist; cf. `docs/rag-vs-wiki-design.md`). It instructs an LLM agent (e.g., Claude Code) on how to ingest sources, answer queries, and maintain the wiki.

## Layout

```
wiki/
├── CLAUDE.md       # this file (schema/rules)
├── index.md        # catalog of all pages
├── log.md          # append-only timeline of ingest/query/lint actions
└── pages/          # one markdown file per topic
```

## Page Format

Every page in `pages/` MUST begin with YAML front-matter:

```yaml
---
summary: One-line description (≤120 chars)
tags: [tag1, tag2]
related: [page-id-1, page-id-2]
source: synthetic-memory/<filename>.md   # for converted seed pages
---
```

Body sections (in order):

1. `# Title` — H1, matches page ID (kebab-case filename without `.md`)
2. Substantive content (sections by H2)
3. Inline cross-references using markdown links: `[supabase-auth-rls](supabase-auth-rls.md)`
4. `## Related` — final section listing cross-referenced pages with one-line "why related"

## index.md Format

Append-only catalog. One row per page. Columns: page link, summary, tags. Group by tag cluster when natural. Do not reorder existing rows; append new ones in the correct cluster.

## log.md Format

Append-only timeline. One entry per action:

```
## 2026-04-29T12:34:56Z — ingest
- source: synthetic-memory/nextjs-supabase.md
- new pages: [nextjs-supabase]
- updated pages: [supabase-auth-rls, fullstack-architecture]
- notes: cross-referenced PKCE flow from supabase-auth-rls
```

Action types: `ingest`, `query`, `lint`, `manual-edit`.

## Workflows

### Ingest (new source → wiki)

Trigger: a new file is added to `raw-sources/` (or pointed to by the user).

1. **Read** the new source in full.
2. **Search** `index.md` (and `Grep` page bodies) for related existing pages — list 3–10 candidates.
3. **Decide** page boundaries:
   - One coherent topic → one new page in `pages/`.
   - Multiple topics → multiple pages.
   - Topic already covered → update existing page instead of creating a duplicate.
4. **Write** the new page(s) following the page format above.
5. **Update** related pages: add inline links and `## Related` entries pointing to the new page.
6. **Update** `index.md` with one row per new page.
7. **Append** to `log.md` an `ingest` entry naming new and updated pages.

### Query (user question → answer)

1. **Read** `index.md` first.
2. Identify candidate pages by tag/summary; `Grep` page bodies if `index.md` is insufficient.
3. **Read** the candidate pages in full (do not partially scan).
4. Follow `## Related` links transitively up to depth 2 if relevant.
5. Compose the answer with explicit `[page#section]` citations.
6. **Append** a `query` entry to `log.md` (question, pages read, citations).

### Lint (periodic maintenance)

Run when explicitly invoked. Checks:

- **Orphan pages**: not linked from `index.md` or any other page → flag for review.
- **Broken links**: `[…](missing.md)` → fix or remove.
- **Stale claims**: front-matter `source` exists but page contents diverge from source → flag.
- **Duplicate pages**: high topical overlap → propose merge.
- **Missing back-links**: page A links to B but B does not list A in `## Related` → add reciprocal link.

Output a lint report to `log.md` under a `lint` entry; do not auto-fix without confirmation.

## Hard Rules

- **No embeddings**, no vector search, no external retrieval. Use only `Read`, `Glob`, `Grep`, `Edit`, `Write`.
- **Preserve original content** during ingest. Do not summarize away factual details from source files; the wiki must remain a faithful index over the source material.
- **No silent rewrites** of historical pages: substantive changes append to `log.md`.
- **Cite when answering**: every factual claim in a query response should reference a page.
- **Append, don't reorder** in `index.md` and `log.md`.

## Out of Scope (intentionally)

- Authoring UI (Obsidian, etc.) — the wiki is plain markdown; any editor works.
- Auto-ingest watchers — ingestion is explicitly invoked.
- Graph visualization — readable through `index.md` + `## Related` sections.
