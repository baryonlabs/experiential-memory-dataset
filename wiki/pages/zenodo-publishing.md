---
summary: Zenodo academic preprint publishing — web interface and REST API, DOI assignment, versioning, GitHub release auto-archive, communities, licensing, sandbox testing
tags: [zenodo, doi, publishing, preprint, academic, archival]
related: [git-workflow, github-actions]
source: synthetic-memory/zenodo-publishing.md
---

# Academic Preprint Publishing on Zenodo

## Overview

Zenodo is a general-purpose open repository hosted by CERN. It provides DOIs for research outputs including papers, datasets, software, and preprints. Free to use, supports files up to 50 GB.

## Creating a Deposit

### Via Web Interface

1. Go to zenodo.org → Upload → New Upload.
2. Upload files (PDF, datasets, code archives).
3. Fill in metadata: title, authors, description, keywords.
4. Choose access right: Open Access, Embargoed, Restricted, or Closed.
5. Select upload type: Publication → Preprint (for academic papers).
6. Publish. A DOI is minted immediately.

### Via REST API

```bash
# Create empty deposit
curl -X POST 'https://zenodo.org/api/deposit/depositions' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{}'

# Upload file
curl -X PUT 'https://zenodo.org/api/deposit/depositions/DEPOSIT_ID/files/paper.pdf' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  --data-binary @paper.pdf

# Add metadata
curl -X PUT 'https://zenodo.org/api/deposit/depositions/DEPOSIT_ID' \
  -H 'Authorization: Bearer ACCESS_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "metadata": {
      "title": "My Research Paper",
      "upload_type": "publication",
      "publication_type": "preprint",
      "description": "Abstract here...",
      "creators": [{"name": "Lee, Tom", "affiliation": "Example University"}],
      "keywords": ["AI", "agents"],
      "license": "cc-by-4.0"
    }
  }'

# Publish
curl -X POST 'https://zenodo.org/api/deposit/depositions/DEPOSIT_ID/actions/publish' \
  -H 'Authorization: Bearer ACCESS_TOKEN'
```

## DOI Assignment

- Each deposit gets a unique DOI: `10.5281/zenodo.XXXXXXX`.
- A **concept DOI** links all versions together.
- DOIs are registered with DataCite and are permanent.

## Versioning

1. On the deposit page, click "New version".
2. Upload updated files and metadata.
3. Publish. New DOI is minted; concept DOI still resolves to the latest.

Pairs with [git-workflow](git-workflow.md) tag/release discipline — every Zenodo version typically maps to a tagged release in the source repo.

## GitHub Integration

Zenodo can auto-archive GitHub releases:

1. Link your GitHub account in Zenodo settings.
2. Enable the repository toggle.
3. Create a GitHub release → Zenodo auto-creates a deposit with the release assets.
4. A DOI badge is generated for your README.

The release-trigger pattern is the same one used for npm provenance and CI deploys — see [github-actions](github-actions.md#triggers).

## Communities

Submit deposits to Zenodo communities for visibility. Community curators review and accept/reject submissions.

## Licensing

Common choices:

- **CC-BY-4.0**: Attribution required. Standard for papers.
- **CC0**: Public domain. Good for datasets.
- **MIT/Apache-2.0**: For software.

## Metadata Schema

Required fields: `title`, `upload_type`, `description`, `creators` (array of `{name, affiliation}`).

Optional but recommended: `keywords`, `license`, `related_identifiers` (link to arXiv, GitHub, etc.), `grants` (funding info).

## Sandbox

Use `sandbox.zenodo.org` for testing. Separate account and API tokens. DOIs minted in sandbox are not real.

## Related

- [git-workflow](git-workflow.md) — tagged releases as the canonical unit that maps to Zenodo versions; rebase/squash discipline keeps version history clean.
- [github-actions](github-actions.md) — `release` trigger fires both Zenodo auto-archive (via GitHub integration) and any CI publish flows simultaneously.
