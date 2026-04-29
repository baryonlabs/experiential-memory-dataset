# Wiki Log

Append-only timeline of ingest, query, lint, and manual-edit actions. See `CLAUDE.md` for entry format.

## 2026-04-29T20:19:37Z — manual-edit (PoC seed)

- actor: claude-code (branch `claude/rag-vs-graph-comparison-vAOGf`)
- action: bootstrap wiki with 3 seed pages converted from `synthetic-memory/`
- new pages: [nextjs-supabase, supabase-auth-rls, fullstack-architecture]
- updated pages: []
- index.md: created with first cluster ("Web / App Stack")
- notes:
  - This is a manual seed, not a full ingest — used to validate the schema in `CLAUDE.md` and the cross-reference pattern.
  - Each seed page records its source in front-matter (`source: synthetic-memory/<file>.md`) so a future lint pass can verify content fidelity.
  - Cross-references intentionally form a triangle (each page links to the other two) to exercise the back-link rule.
  - 17 remaining `synthetic-memory/` files are not yet ingested (see `docs/rag-vs-wiki-design.md` for plan).
