#!/usr/bin/env python3
"""Fidelity lint for the LLM-Wiki representation of synthetic-memory/.

For each `wiki/pages/*.md` page that declares a `source:` field in its
YAML front-matter, this script verifies that the page is a faithful
*overlay* over the source file rather than an editorial rewrite. The
experimental fairness of Condition B (RAG over source) vs Condition E
(LLM-Wiki over wiki page) depends on this property.

What it strips before comparing (these are wiki-only additions, expected):
  - YAML front-matter at the top
  - The final `## Related` section
  - Inline cross-reference links: `[text](other-page.md)` becomes `text`,
    so a paragraph reading "see also [supabase-auth-rls](supabase-auth-rls.md)
    for ..." compares as "see also supabase-auth-rls for ..." against the
    source
  - Trailing/leading whitespace on each line

What it then checks (per page):
  - missing_in_wiki: lines present in source but absent from wiki body.
    Any non-empty entry here is a fidelity violation.
  - added_in_wiki: lines present in wiki body but absent from source.
    These are expected for inline cross-reference *prose* (e.g., the
    "see also ..." sentence above) but should still be reviewed.

Exit codes:
  0 — all pages with a `source:` field are faithful (no missing lines).
  1 — at least one page has missing source content.
  2 — a page declares a `source:` that does not exist on disk, or a
       structural problem (e.g., no front-matter).

Usage:
  python scripts/lint_fidelity.py                    # lint all pages
  python scripts/lint_fidelity.py --verbose          # show added lines too
  python scripts/lint_fidelity.py --page foo.md      # lint a single page
  python scripts/lint_fidelity.py --json > report.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_PAGES = REPO_ROOT / "wiki" / "pages"

FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
RELATED_SECTION_RE = re.compile(r"\n## Related\n.*\Z", re.DOTALL)
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SOURCE_FIELD_RE = re.compile(r"^source:\s*(.+?)\s*$", re.MULTILINE)


@dataclass
class PageReport:
    page: str
    source: str | None = None
    status: str = "ok"  # ok | missing | added-only | error
    missing_in_wiki: list[str] = field(default_factory=list)
    added_in_wiki: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "page": self.page,
            "source": self.source,
            "status": self.status,
            "missing_in_wiki_count": len(self.missing_in_wiki),
            "added_in_wiki_count": len(self.added_in_wiki),
            "missing_in_wiki": self.missing_in_wiki,
            "added_in_wiki": self.added_in_wiki,
            "error": self.error,
        }


def parse_front_matter(text: str) -> tuple[str | None, str]:
    """Return (front_matter_yaml_or_None, body_without_front_matter)."""
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return None, text
    return match.group(1), text[match.end():]


def extract_source_path(front_matter: str) -> str | None:
    match = SOURCE_FIELD_RE.search(front_matter)
    if not match:
        return None
    return match.group(1).strip().strip('"').strip("'")


def strip_related_section(body: str) -> str:
    return RELATED_SECTION_RE.sub("", body)


def strip_inline_links(text: str) -> str:
    """Replace `[text](url)` with `text`, preserving prose."""
    return INLINE_LINK_RE.sub(r"\1", text)


def normalize_lines(text: str) -> list[str]:
    """Split into stripped non-empty lines."""
    return [line.strip() for line in text.splitlines() if line.strip()]


def lint_page(page_path: Path) -> PageReport:
    page_rel = str(page_path.relative_to(REPO_ROOT))
    text = page_path.read_text(encoding="utf-8")

    fm, body = parse_front_matter(text)
    if fm is None:
        return PageReport(page=page_rel, status="error", error="no front-matter")

    source_rel = extract_source_path(fm)
    if source_rel is None:
        # Pages without `source:` are intentionally orphaned (not derived
        # from a single source file). Skip silently.
        return PageReport(page=page_rel, source=None, status="ok")

    source_path = REPO_ROOT / source_rel
    if not source_path.exists():
        return PageReport(
            page=page_rel,
            source=source_rel,
            status="error",
            error=f"source file not found: {source_path}",
        )

    source_text = source_path.read_text(encoding="utf-8")

    # Normalize both sides identically: strip Related, strip inline
    # cross-ref links (keeping the prose), normalize whitespace.
    wiki_body = strip_related_section(body)
    wiki_body = strip_inline_links(wiki_body)
    wiki_lines_set = set(normalize_lines(wiki_body))
    wiki_text_blob = "\n".join(normalize_lines(wiki_body))

    source_norm = strip_inline_links(source_text)
    source_lines = normalize_lines(source_norm)

    # Containment check: each source line must appear as a substring of
    # the normalized wiki text. This accepts the common pattern of
    # extending a source sentence with a trailing cross-reference clause
    # (e.g., source "X." → wiki "X. See [foo](foo.md) for ...").
    # Strict line-equality was rejected because such extensions still
    # preserve the source content — the experimental fairness concern is
    # content loss, not stylistic reflow.
    missing = [line for line in source_lines if line not in wiki_text_blob]
    # `added` is reported with caveat: cross-ref prose lives here too.
    added = sorted(wiki_lines_set - set(source_lines))

    if missing:
        status = "missing"
    elif added:
        status = "added-only"
    else:
        status = "ok"

    return PageReport(
        page=page_rel,
        source=source_rel,
        status=status,
        missing_in_wiki=missing,
        added_in_wiki=added,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--page", help="Lint a single page (filename only, e.g., 'foo.md')")
    ap.add_argument("--verbose", action="store_true", help="Show added lines too")
    ap.add_argument("--json", action="store_true", help="Emit JSON report to stdout")
    args = ap.parse_args()

    if args.page:
        candidates = [WIKI_PAGES / args.page]
    else:
        candidates = sorted(WIKI_PAGES.glob("*.md"))

    reports = [lint_page(p) for p in candidates if p.exists()]

    if args.json:
        print(json.dumps([r.to_dict() for r in reports], indent=2, ensure_ascii=False))
    else:
        ok = sum(1 for r in reports if r.status == "ok")
        added_only = sum(1 for r in reports if r.status == "added-only")
        missing = sum(1 for r in reports if r.status == "missing")
        errors = sum(1 for r in reports if r.status == "error")

        for r in reports:
            if r.status == "ok":
                continue
            print(f"\n=== {r.page}")
            if r.source:
                print(f"    source: {r.source}")
            print(f"    status: {r.status}")
            if r.error:
                print(f"    error: {r.error}")
            if r.missing_in_wiki:
                print(f"    MISSING in wiki ({len(r.missing_in_wiki)} lines):")
                for line in r.missing_in_wiki[:20]:
                    print(f"      - {line}")
                if len(r.missing_in_wiki) > 20:
                    print(f"      ... and {len(r.missing_in_wiki) - 20} more")
            if args.verbose and r.added_in_wiki:
                print(f"    ADDED in wiki ({len(r.added_in_wiki)} lines):")
                for line in r.added_in_wiki[:20]:
                    print(f"      + {line}")
                if len(r.added_in_wiki) > 20:
                    print(f"      ... and {len(r.added_in_wiki) - 20} more")

        print(f"\nSummary: ok={ok}  added-only={added_only}  missing={missing}  errors={errors}  total={len(reports)}")

    if any(r.status == "missing" for r in reports):
        return 1
    if any(r.status == "error" for r in reports):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
