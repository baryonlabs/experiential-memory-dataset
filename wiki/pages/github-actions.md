---
summary: GitHub Actions workflow file structure, triggers, job dependencies, matrix strategy, secrets, caching, artifacts, reusable workflows
tags: [ci, cd, github-actions, automation, devops]
related: [git-workflow, npm-publishing, vercel-deployment, docusaurus-docs, hugo-blog]
source: synthetic-memory/github-actions.md
---

# GitHub Actions CI/CD

## Workflow File Structure

Workflows live in `.github/workflows/*.yml`:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build
```

## Triggers

- **push/pull_request**: Branch/tag filters, path filters. Branch model details in [git-workflow](git-workflow.md).
- **schedule**: Cron syntax (`cron: '0 0 * * *'`).
- **workflow_dispatch**: Manual trigger with optional inputs.
- **release**: On GitHub release creation.
- **repository_dispatch**: External webhook trigger.

Path filtering:

```yaml
on:
  push:
    paths:
      - 'packages/web/**'
      - '!**.md'
```

## Job Dependencies

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps: [...]
```

## Matrix Strategy

```yaml
strategy:
  matrix:
    node-version: [18, 20, 22]
    os: [ubuntu-latest, macos-latest]
  fail-fast: false
```

## Secrets & Variables

- **Secrets**: Settings → Secrets and variables → Actions. Access via `${{ secrets.MY_SECRET }}`.
- **Variables**: Non-sensitive config. Access via `${{ vars.MY_VAR }}`.
- **Environment secrets**: Scoped to specific environments with protection rules.
- **GITHUB_TOKEN**: Auto-generated, scoped to the repository. Configure permissions in the workflow.

## Caching

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: ${{ runner.os }}-npm-
```

Or use the built-in cache in `actions/setup-node` (`cache: 'npm'`).

## Artifacts

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/

# In another job:
- uses: actions/download-artifact@v4
  with:
    name: build-output
```

## Reusable Workflows

```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true
```

Call with:

```yaml
jobs:
  deploy:
    uses: ./.github/workflows/reusable-deploy.yml
    with:
      environment: production
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## Common Patterns

- **Concurrency**: `concurrency: { group: ${{ github.ref }}, cancel-in-progress: true }` to avoid duplicate runs.
- **Conditional steps**: `if: github.event_name == 'push'`.
- **Composite actions**: Bundle multiple steps into a reusable action in `action.yml`.
- **Self-hosted runners**: Use `runs-on: self-hosted` for private infrastructure or GPU workloads.

## Common Use Cases

- Publish to npm with provenance — see [npm-publishing](npm-publishing.md#automation-with-github-actions).
- Auto-deploy to Vercel — see [vercel-deployment](vercel-deployment.md#deployment-pipeline).
- Build and deploy docs — see [docusaurus-docs](docusaurus-docs.md#deployment), [hugo-blog](hugo-blog.md#deployment).

## Related

- [git-workflow](git-workflow.md) — push/PR triggers map directly onto branching strategy; Conventional Commits drive semantic-release-style automation.
- [npm-publishing](npm-publishing.md) — release-triggered publish workflow with OIDC provenance.
- [vercel-deployment](vercel-deployment.md) — alternative to Actions-driven deploys; hybrid setups are common.
- [docusaurus-docs](docusaurus-docs.md), [hugo-blog](hugo-blog.md) — static-site CI deploy patterns.
