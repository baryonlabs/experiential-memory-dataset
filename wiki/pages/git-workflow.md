---
summary: Git branching strategies, rebasing, history rewriting (filter-repo), cherry-pick, stash, and Conventional Commits
tags: [git, version-control, rebase, history, conventional-commits]
related: [github-actions, npm-publishing, age-encryption]
source: synthetic-memory/git-workflow.md
---

# Git Branching, Rebasing, and History Rewriting

## Branching Strategy

### GitHub Flow (Simple)

- `main` is always deployable.
- Create feature branches from `main`: `git checkout -b feat/my-feature`.
- Open PR, get review, merge. Delete branch after merge.

### Git Flow (Complex)

- `main` — production releases.
- `develop` — integration branch.
- `feature/*` — branch from develop.
- `release/*` — prepare releases.
- `hotfix/*` — urgent production fixes.

## Rebasing

### Interactive Rebase

```bash
git rebase -i HEAD~5    # edit last 5 commits
```

Commands: `pick`, `reword` (edit message), `edit` (amend), `squash` (combine with previous), `fixup` (squash, discard message), `drop` (remove).

### Rebase onto main

```bash
git checkout feature
git rebase main
# Resolve conflicts if any
git push --force-with-lease
```

`--force-with-lease` is safer than `--force` — it fails if someone else pushed.

## Squash Merging

```bash
# Via GitHub PR: "Squash and merge" button
# Via CLI:
git checkout main
git merge --squash feature
git commit -m "feat: implement feature X"
```

Produces a clean single commit on main.

## History Rewriting

### Amend Last Commit

```bash
git commit --amend -m "new message"
git commit --amend --no-edit  # add staged changes to last commit
```

### filter-branch (Legacy)

```bash
git filter-branch --tree-filter 'rm -f secrets.txt' HEAD
```

**Deprecated** in favor of `git filter-repo`.

### git filter-repo (Recommended)

```bash
pip install git-filter-repo

# Remove a file from all history
git filter-repo --path secrets.txt --invert-paths

# Rewrite author info
git filter-repo --mailmap mailmap.txt

# Move subdirectory to root
git filter-repo --subdirectory-filter subdir/
```

`filter-repo` is much faster and safer than `filter-branch`. If the goal is to *avoid* committing secrets in the first place, encrypt them at rest with [age-encryption](age-encryption.md) before commit.

## Cherry-Pick

```bash
git cherry-pick abc1234         # apply a single commit
git cherry-pick abc1234..def5678  # apply a range
git cherry-pick --no-commit abc1234  # apply without committing
```

## Stashing

```bash
git stash                   # save working changes
git stash pop               # restore and remove stash
git stash list              # list stashes
git stash apply stash@{2}   # apply specific stash
git stash drop stash@{0}    # delete a stash
```

## Useful Commands

```bash
git log --oneline --graph --all  # visual log
git reflog                       # recovery: find lost commits
git bisect start                 # binary search for bad commit
git blame file.txt               # line-by-line attribution
git clean -fd                    # remove untracked files
git diff --staged                # diff staged changes
```

## Conventional Commits

Format: `type(scope): description`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`.

Examples:

```
feat(auth): add Google OAuth login
fix(api): handle null response from endpoint
docs: update README installation section
chore: bump dependencies
```

Conventional commit messages plug naturally into automated release flows ([npm-publishing](npm-publishing.md#versioning-semver), [github-actions](github-actions.md#triggers)).

## Related

- [github-actions](github-actions.md) — push/PR triggers for CI; branch filters and path filters drive when workflows fire.
- [npm-publishing](npm-publishing.md) — `npm version` writes a git tag; rebase/squash discipline keeps tags meaningful.
- [age-encryption](age-encryption.md) — encrypting secrets *before* commit avoids the need for `filter-repo` history rewrites later.
