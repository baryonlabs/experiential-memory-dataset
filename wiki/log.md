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

## 2026-05-01T09:49:57Z — manual-edit (Condition E corpus complete)

- actor: claude-code (branch `claude/rag-vs-graph-comparison-vAOGf`)
- action: convert remaining 17 `synthetic-memory/` files to wiki pages
- new pages: [age-encryption, docusaurus-docs, domain-dns, git-workflow, github-actions, hugo-blog, mcp-server, npm-publishing, seo-marketing, soul-spec, stripe-integration, trademark-ip, typescript-cli, unity-cesium, unity-input-system, vercel-deployment, zenodo-publishing]
- updated pages: [] (existing 3 PoC pages unchanged)
- index.md: rebuilt as full 7-cluster catalog (Web/App Stack, Authoring/Publishing, DevOps/Release, Tooling/CLI, Domain/Infra, Game/3D, Project Identity)
- notes:
  - Each page records its `source:` in front-matter for the future fidelity lint pass.
  - Cross-references chosen on actual content overlap (not forced by tag) — e.g., `vercel-deployment` ↔ `domain-dns` because vercel-deployment.md has a Custom Domains section that cites the exact DNS recipe in domain-dns.md.
  - `soul-spec` intentionally has no `## Related` cross-refs (orphan-ish): it documents the meta-format used by `soul-spec-anonymized/`, not a tool the rest of the wiki integrates with. Lint should flag this for review but the orphan status is justified.
  - Total: 20 wiki pages corresponding 1:1 to the 20 `synthetic-memory/` source files. Condition E corpus is now complete pending fidelity lint.
