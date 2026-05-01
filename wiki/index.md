# Wiki Index

Catalog of all pages. See `CLAUDE.md` for conventions. Append new rows in the appropriate cluster; do not reorder existing rows.

## Web / App Stack

| Page | Summary | Tags |
|------|---------|------|
| [nextjs-supabase](pages/nextjs-supabase.md) | Next.js App Router + Supabase integration patterns (SSR, auth callback, server actions, realtime) | nextjs, supabase, ssr, auth, realtime |
| [supabase-auth-rls](pages/supabase-auth-rls.md) | Supabase Auth providers, PKCE flow, and PostgreSQL Row-Level Security (RLS) policies | supabase, auth, rls, postgresql, security |
| [fullstack-architecture](pages/fullstack-architecture.md) | Full-stack architecture decisions, recommended Next.js+Supabase+Vercel stack, API design and environment strategy | architecture, nextjs, supabase, vercel, monorepo, environments |
| [vercel-deployment](pages/vercel-deployment.md) | Vercel deployment patterns — vercel.json, env vars, deployment pipeline, ISR/caching, custom domains, monitoring, monorepo | vercel, deployment, nextjs, serverless, cdn, isr |
| [stripe-integration](pages/stripe-integration.md) | Stripe Checkout sessions, client redirect, signed webhooks, key event types, local testing with stripe-cli, idempotency | stripe, payments, webhooks, subscriptions, billing |

## Authoring / Publishing

| Page | Summary | Tags |
|------|---------|------|
| [hugo-blog](pages/hugo-blog.md) | Hugo static site generator — installation, theme submodules, hugo.toml, content with front matter, shortcodes, deployment, taxonomies, multilingual | hugo, static-site, blog, markdown, deployment |
| [docusaurus-docs](pages/docusaurus-docs.md) | Docusaurus documentation site — setup, configuration, sidebars, MDX, versioning, search, deployment, i18n | docs, docusaurus, mdx, static-site, deployment |
| [zenodo-publishing](pages/zenodo-publishing.md) | Zenodo academic preprint publishing — web/REST API, DOI, versioning, GitHub release auto-archive, communities, licensing, sandbox | zenodo, doi, publishing, preprint, academic, archival |
| [seo-marketing](pages/seo-marketing.md) | Technical SEO (meta, OG, JSON-LD, sitemap, robots), blog crossposting strategy with canonical URLs, social media, analytics | seo, marketing, og-tags, canonical, social, analytics |

## DevOps / Release

| Page | Summary | Tags |
|------|---------|------|
| [git-workflow](pages/git-workflow.md) | Git branching strategies, rebasing, history rewriting (filter-repo), cherry-pick, stash, Conventional Commits | git, version-control, rebase, history, conventional-commits |
| [github-actions](pages/github-actions.md) | GitHub Actions workflow file structure, triggers, job dependencies, matrix strategy, secrets, caching, artifacts, reusable workflows | ci, cd, github-actions, automation, devops |
| [npm-publishing](pages/npm-publishing.md) | npm package publishing workflow — package.json fields, SemVer, scoped packages, provenance, GitHub Actions automation | npm, publishing, semver, provenance, packaging |

## Tooling / CLI

| Page | Summary | Tags |
|------|---------|------|
| [typescript-cli](pages/typescript-cli.md) | TypeScript CLI development — package.json bin/files, ESM tsconfig, Commander/yargs/citty, tsup, prompts, terminal output, config, error handling, testing | cli, typescript, commander, tsup, esm |
| [mcp-server](pages/mcp-server.md) | Model Context Protocol (MCP) server development — architecture, TypeScript SDK, resources/tools/prompts, transport, Claude Desktop config | mcp, ai, server, sdk, typescript, claude |
| [age-encryption](pages/age-encryption.md) | age file encryption (Filippo Valsorda) — CLI, recipients, SSH keys, programmatic use, E2E sync patterns | encryption, cli, security, ssh, e2e |

## Domain / Infra

| Page | Summary | Tags |
|------|---------|------|
| [domain-dns](pages/domain-dns.md) | Domain registration, Cloudflare DNS records, SSL/TLS modes, common configuration recipes (Vercel, GitHub Pages, email) | dns, cloudflare, ssl, domains, infra |
| [trademark-ip](pages/trademark-ip.md) | Trademark filing process — Korea (KIPRIS/KIPO), United States (USPTO), Madrid Protocol; Nice Classification, intent-to-use vs use-based, maintenance | trademark, ip, legal, kipo, uspto, madrid |

## Game / 3D

| Page | Summary | Tags |
|------|---------|------|
| [unity-cesium](pages/unity-cesium.md) | Cesium for Unity — 3D Tiles streaming, Cesium3DTileset, CesiumGeoreference, CesiumGlobeAnchor, imagery overlays, ECEF coordinates, ion authentication | unity, cesium, 3d, geospatial, gamedev |
| [unity-input-system](pages/unity-input-system.md) | Unity new Input System — Input Actions asset, generated C# class, PlayerInput component, action types, composite bindings, runtime rebinding, touch/mobile | unity, input, gamedev, controls, rebinding |

## Project Identity

| Page | Summary | Tags |
|------|---------|------|
| [soul-spec](pages/soul-spec.md) | Soul Spec format — JSON+Markdown package for AI agent personas (soul.json, SOUL.md, IDENTITY.md, MEMORY.md, USER.md), packaging, composition, versioning | agent, persona, spec, soul, identity |
