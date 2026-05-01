---
summary: Soul Spec format — JSON+Markdown package for AI agent personas (soul.json, SOUL.md, IDENTITY.md, MEMORY.md, USER.md), packaging, composition, versioning
tags: [agent, persona, spec, soul, identity]
related: []
source: synthetic-memory/soul-spec.md
---

# Soul Spec Format: JSON + Markdown Persona Packages

## Overview

Soul Spec is a format for defining AI agent personas as portable, structured packages. A soul spec combines identity metadata (JSON) with rich narrative content (Markdown) into a single distributable unit.

## File Structure

A soul spec package consists of:

```
my-persona/
├── soul.json          # Structured metadata
├── SOUL.md            # Core identity narrative
├── IDENTITY.md        # Detailed personality & voice
├── MEMORY.md          # Long-term memory / knowledge base
├── USER.md            # User profile & preferences
└── assets/            # Optional: avatar, voice samples
    └── avatar.png
```

## soul.json Schema

```json
{
  "version": "1.0",
  "name": "Agent B",
  "description": "A coding agent with personality",
  "author": "ClawSouls",
  "license": "CC-BY-4.0",
  "tags": ["coding", "assistant", "personality"],
  "files": {
    "soul": "SOUL.md",
    "identity": "IDENTITY.md",
    "memory": "MEMORY.md",
    "user": "USER.md"
  },
  "config": {
    "model": "claude-sonnet-4-20250514",
    "temperature": 0.7,
    "systemPromptOrder": ["soul", "identity", "memory", "user"]
  }
}
```

## SOUL.md

The core identity file defines:

- **Name and role**: Who the agent is.
- **Personality traits**: Communication style, values, quirks.
- **Capabilities**: What the agent can and cannot do.
- **Boundaries**: Ethical guidelines, safety rules.

Written in second person ("You are...") or first person ("I am...") depending on framework conventions.

## IDENTITY.md

Extended personality definition:

- Voice and tone guidelines.
- Example interactions.
- Cultural context and language preferences.
- Behavioral rules (when to be formal vs casual).

## MEMORY.md

Curated long-term knowledge:

- Key facts the agent should always know.
- Project context and history summaries.
- Technical knowledge relevant to the agent's domain.
- Updated periodically, not on every interaction.

## USER.md

Profile of the primary user:

- Preferences and communication style.
- Technical skill level.
- Timezone, language preferences.
- Project context relevant to interactions.

## Packaging & Distribution

Soul specs can be distributed as:

- **Git repositories**: Version-controlled, forkable.
- **npm packages**: `npm install @clawsouls/brad-persona`.
- **ZIP archives**: For direct sharing.
- **Registry API**: Upload/download via a central registry.

## Composition

Multiple soul specs can be layered:

1. **Base persona** (foundation personality).
2. **Domain overlay** (adds expertise — e.g., "coding" or "writing").
3. **User customization** (personal preferences).

Files are merged in order; later files override earlier ones for conflicting directives.

## Versioning

Follow SemVer for persona packages:

- **MAJOR**: Fundamental personality change.
- **MINOR**: New capabilities or knowledge areas.
- **PATCH**: Wording tweaks, bug fixes in behavior.

## Related

This page describes the *meta-format* used by the parent experiment's `soul-spec-anonymized/` directory (`SOUL.md`, `IDENTITY.md`, `AGENTS.md`, `soul.json`). It stands alone in the wiki because no other page is a functional dependency of it; the format is the substrate the experiment runs on, not a tool the experiment integrates with.
