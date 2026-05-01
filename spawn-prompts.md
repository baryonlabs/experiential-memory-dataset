# Experiment Spawn Prompts

The exact prompts used to run each experimental condition. Each condition was executed in an isolated session with Claude Opus 4 (claude-opus-4-6).

## Task File

All conditions reference the same task file containing 15 questions (CT-1~5, AD-1~5, CD-1~5). See `taskset.md` for the full question set. IR-1~5 were administered in a separate round.

## Condition A — Experiential Memory

```
You are an AI development assistant. Before answering the questions below,
read ALL memory files from <MEMORY_DIR> (there are ~157 files) and also
read <MEMORY_DIR>/MEMORY.md. These contain your working memory from past
sessions. Study them carefully, then answer all 15 questions in <TASK_FILE>
thoroughly. Read that file first to see the questions. Use the memory context
to inform your answers. Do NOT read any files from <SYNTHETIC_DIR>.
```

- **Label**: `experiment-condition-A`
- **Memory source**: ~157 experiential memory files accumulated over 2 weeks of human-agent collaboration
- **Token usage**: 77.6k tokens, runtime 2m34s

## Condition B — Synthetic Memory

```
You are an AI development assistant. Before answering the questions below,
read ALL files from <SYNTHETIC_DIR> (there are ~20 documentation files).
These contain reference documentation about the project's tech stack.
Study them carefully, then answer all 15 questions in <TASK_FILE> thoroughly.
Read that file first to see the questions. Use only the synthetic memory
context to inform your answers. Do NOT read files from <MEMORY_DIR>.
```

- **Label**: `experiment-condition-B`
- **Memory source**: 20 synthetic documentation files (topic-matched, token-matched to A within 10%)
- **Token usage**: 51k tokens, runtime 1m45s

## Condition C — Hybrid (Experiential + Synthetic)

```
You are an AI development assistant. Before answering the questions below,
read ALL files from BOTH directories: (1) <MEMORY_DIR> (~157 files) AND
(2) <SYNTHETIC_DIR> (~20 files). Also read <MEMORY_DIR>/MEMORY.md.
These contain your working memory and reference docs. Study them carefully,
then answer all 15 questions in <TASK_FILE> thoroughly. Read that file first
to see the questions.
```

- **Label**: `experiment-condition-C`
- **Memory source**: Both experiential (~157 files) and synthetic (~20 files)
- **Token usage**: 200k tokens, runtime 2m51s

## Condition D — Baseline (No Memory)

```
You are an AI development assistant working on a project called ClawSouls —
an AI agent persona marketplace. Answer all 15 questions in <TASK_FILE>
thoroughly based on your general knowledge. Read that file first.
Do NOT read any files from <MEMORY_DIR> or <SYNTHETIC_DIR>.
Use only your general knowledge and the question context.
```

- **Label**: `experiment-condition-D`
- **Memory source**: None (LLM general knowledge only)
- **Token usage**: 21.3k tokens, runtime 1m50s

## Condition E — Synthetic Wiki (LLM-Wiki retrieval)

```
You are an AI development assistant. Before answering the questions below,
first read <WIKI_DIR>/CLAUDE.md to learn the wiki's operating rules. Then
read <WIKI_DIR>/index.md to see the catalog. For each question, identify
relevant pages by tag/summary in index.md, read those pages in full from
<WIKI_DIR>/pages/, and follow `## Related` links transitively up to depth 2
when relevant. Cite the page (e.g., [page#section]) for each factual claim.
Do NOT read files from <MEMORY_DIR>, <SYNTHETIC_DIR>, or any other source.
Use only Read / Glob / Grep over <WIKI_DIR>. Then answer all 15 questions
in <TASK_FILE> thoroughly.
```

- **Label**: `experiment-condition-E`
- **Memory source**: Same 20 synthetic files as B, restructured as an LLM-Wiki at `wiki/` (front-matter + `index.md` + `## Related` cross-refs). Content fidelity verified by `scripts/lint_fidelity.py` before evaluation.
- **Tool surface**: `Read`, `Glob`, `Grep` only. No `memory_search`, no semantic/vector retrieval, no embeddings.
- **Hypothesis tested**: H1 — does retrieval method alone (B→E) recover the gap to baseline?
- **Token usage / runtime**: TBD (record on first eval run)

## Condition F — Experiential Wiki (LLM-Wiki retrieval, private)

```
You are an AI development assistant. Before answering the questions below,
first read <WIKI_DIR>/CLAUDE.md to learn the wiki's operating rules. Then
read <WIKI_DIR>/index.md to see the catalog. For each question, identify
relevant pages by tag/summary in index.md, read those pages in full from
<WIKI_DIR>/pages/, and follow `## Related` links transitively up to depth 2
when relevant. Cite the page (e.g., [page#section]) for each factual claim.
Do NOT read files from <MEMORY_DIR>, <SYNTHETIC_DIR>, or any other source.
Use only Read / Glob / Grep over <WIKI_DIR>. Then answer all 15 questions
in <TASK_FILE> thoroughly.
```

- **Label**: `experiment-condition-F`
- **Memory source**: Same ~157 experiential files as A, restructured as an LLM-Wiki. Private (contains sensitive info) — produced and evaluated by researchers with access to the original experiential corpus, not committed to the public repo.
- **Tool surface**: Same as E.
- **Hypothesis tested**: H2 — does retrieval method help when the corpus already has implicit cross-reference structure from real collaboration?
- **Token usage / runtime**: TBD

## Placeholders

| Placeholder | Description |
|-------------|-------------|
| `<MEMORY_DIR>` | Directory containing experiential memory files (~157 .md files) |
| `<SYNTHETIC_DIR>` | Directory containing synthetic memory files (~20 .md files) |
| `<WIKI_DIR>` | Directory containing the LLM-Wiki representation (`CLAUDE.md`, `index.md`, `log.md`, `pages/`). For Condition E this is the public `wiki/` directory; for Condition F it is the researcher's private experiential-wiki build. |
| `<TASK_FILE>` | File containing the 15 evaluation questions (see `taskset.md`) |

## Reproducing with OpenClaw

To reproduce using OpenClaw's `sessions_spawn`:

1. Place experiential memory files in your workspace `memory/` directory
2. Place synthetic memory files in a separate directory
3. Place the task file (from `taskset.md`) in a known path
4. Replace `<MEMORY_DIR>`, `<SYNTHETIC_DIR>`, and `<TASK_FILE>` with your actual paths
5. Ask your OpenClaw agent to spawn each condition:
   - "Run experiment condition A with experiential memory"
   - The agent will call `sessions_spawn` with the appropriate prompt

## Reproducing without OpenClaw

Using Claude API directly:

```python
import anthropic

client = anthropic.Anthropic()

# Load memory files as context
memory_context = load_all_files("experiential-memory/")  # ~157 files
task_text = open("taskset.md").read()

# Condition A: Experiential
response = client.messages.create(
    model="claude-opus-4-20250514",
    system="You are an AI development assistant.",
    messages=[{
        "role": "user",
        "content": f"Here are your memory files:\n\n{memory_context}\n\n"
                   f"Now answer all 15 questions thoroughly:\n\n{task_text}"
    }]
)
```

Repeat for each condition, varying only the memory context provided.
