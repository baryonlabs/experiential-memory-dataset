---
summary: npm package publishing workflow — package.json fields, SemVer, publishing commands, scoped packages, provenance, GitHub Actions automation
tags: [npm, publishing, semver, provenance, packaging]
related: [typescript-cli, git-workflow, github-actions, trademark-ip]
source: synthetic-memory/npm-publishing.md
---

# npm Package Publishing Workflow

## Pre-publish Checklist

1. **package.json** fields: `name`, `version`, `description`, `main`/`exports`, `files`, `license`, `repository`.
2. **`files` field**: Whitelist only what's needed (e.g., `["dist"]`). Alternatively use `.npmignore`.
3. **`exports` field** (modern): Define entry points explicitly.
4. **README.md**: npm displays this as the package page.
5. **LICENSE**: Required for public packages.

Before settling on a package name, check trademark conflicts — see [trademark-ip](trademark-ip.md).

## Versioning (SemVer)

- **MAJOR** (1.x.x → 2.0.0): Breaking changes.
- **MINOR** (x.1.x → x.2.0): New features, backward-compatible.
- **PATCH** (x.x.1 → x.x.2): Bug fixes.

Bump version:

```bash
npm version patch   # 1.0.0 → 1.0.1
npm version minor   # 1.0.1 → 1.1.0
npm version major   # 1.1.0 → 2.0.0
```

This updates `package.json`, creates a git tag, and commits. Pairs naturally with [git-workflow](git-workflow.md#conventional-commits) Conventional Commits.

## Publishing

```bash
npm login           # authenticate (one-time)
npm publish         # publish to registry
npm publish --access public  # required for scoped packages (@scope/name)
```

### Dry Run

```bash
npm publish --dry-run   # shows what would be published
npm pack                # creates tarball locally for inspection
```

## Scoped Packages

Scoped packages (`@myorg/tool`) are private by default on npm. Use `--access public` for open source, or configure in `package.json`:

```json
{ "publishConfig": { "access": "public" } }
```

## Pre/Post Scripts

```json
{
  "scripts": {
    "prepublishOnly": "npm run build && npm test",
    "preversion": "npm test",
    "postversion": "git push && git push --tags"
  }
}
```

`prepublishOnly` runs before `npm publish`. Use it to ensure build output is fresh.

## npm Provenance

Enable supply-chain transparency:

```bash
npm publish --provenance
```

Requires publishing from a CI environment (GitHub Actions) with OIDC. Adds a verified build link to the package page.

## Automation with GitHub Actions

```yaml
on:
  release:
    types: [published]
jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # for provenance
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: https://registry.npmjs.org
      - run: npm ci && npm run build
      - run: npm publish --provenance
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Full Actions trigger reference: [github-actions](github-actions.md#triggers).

## Deprecation & Unpublish

```bash
npm deprecate my-pkg@1.0.0 "Use v2 instead"
npm unpublish my-pkg@1.0.0   # within 72 hours only
```

## Best Practices

- Always build before publishing (`prepublishOnly`).
- Use `np` (interactive publisher) for safer manual releases.
- Tag pre-releases: `npm publish --tag beta`.
- Check bundle size with `bundlephobia.com` or `size-limit`.
- Use `npm pack` + inspect tarball to verify contents before publishing.

For TypeScript-specific build/bin setup that this workflow consumes, see [typescript-cli](typescript-cli.md).

## Related

- [typescript-cli](typescript-cli.md) — `bin` field, dist setup, and shebang preservation that this publishing workflow assumes.
- [git-workflow](git-workflow.md) — `npm version` writes git tags; rebase/squash discipline keeps tags meaningful.
- [github-actions](github-actions.md) — release-trigger publish workflow with OIDC provenance.
- [trademark-ip](trademark-ip.md) — package-name conflicts and trademark availability before locking in a name.
