# Experiential vs Synthetic Memory in AI Agents — Dataset

Dataset for the paper: **"Experiential vs Synthetic Memory in Long-Running AI Agents: A Controlled Experiment in Software Development"**

📄 Paper: [Zenodo DOI 10.5281/zenodo.18798227](https://zenodo.org/records/18798227)

## Overview

This dataset accompanies a controlled experiment comparing four memory conditions for AI coding agents:

| Condition | Description | Data Available |
|-----------|-------------|----------------|
| A: Experiential | Real memory from 2-week collaboration (~157 files) | Statistics only (contains sensitive info) |
| B: Synthetic | Documentation-style knowledge (~20 files) | ✅ Full data |
| C: Hybrid | A + B combined | On request (contains sensitive info) |
| D: Baseline | No memory (LLM general knowledge only) | ✅ Full responses |

## Results Summary

| Category | A (Experiential) | B (Synthetic) | C (Hybrid) | D (Baseline) |
|----------|:---:|:---:|:---:|:---:|
| Information Retrieval (5) | 4.2 | 1.4 | **5.0** | 2.0 |
| Coding Tasks (5) | 4.2 | 3.2 | **5.0** | 4.0 |
| Architecture Decisions (5) | 4.8 | 3.4 | **5.0** | 4.0 |
| Context-Dependent (5) | **5.0** | 2.6 | 4.8 | 3.2 |
| **Overall (20)** | **4.55** | **2.65** | **4.95** | **3.30** |

**Key Finding**: Hybrid memory (experiential + synthetic) achieves near-perfect scores (4.95/5.0), outperforming either source alone. Surprisingly, synthetic memory alone performs *worse* than no memory at all (2.65 < 3.30).

---

## v2 연구 확장: RAG vs LLM-Wiki 비교 (진행 중)

> 이 섹션은 원 실험을 확장하는 후속 연구입니다. 본 fork 연구는 **홍승우 (Hong Seung-woo)** 가 원 실험에서 *retrieval method*가 단일(RAG)로 고정된 한계를 지적하며 진행하는 확장입니다.
> 작업 브랜치: [`claude/rag-vs-graph-comparison-vAOGf`](https://github.com/baryonlabs/experiential-memory-dataset/tree/claude/rag-vs-graph-comparison-vAOGf)
> 패러다임 비교 정의: [`docs/three-paradigms-KO.md`](docs/three-paradigms-KO.md)
> 설계 문서: [`docs/rag-vs-wiki-design.md`](docs/rag-vs-wiki-design.md)

### 동기

원 실험에서 가장 의외였던 결과는 **Synthetic(2.65) < Baseline(3.30)** — 메모리가 *없는 것보다 못함*. 이 결과는 두 가지 해석이 분리되지 않은 채 남아 있습니다:

- (a) **콘텐츠 문제** — synthetic 문서가 실제로 노이즈를 추가한다
- (b) **검색 방식 문제** — flat RAG의 의미 청킹이 문서 구조를 깎아낸다

검증하려면 *동일 코퍼스를 다른 검색 방식으로 접근*하는 조건이 필요합니다.

### 추가 조건 (E, F)

| Cond | 메모리 콘텐츠 | 검색 방식 | 상태 |
|------|---------------|-----------|------|
| E | Synthetic 20 (wiki 변환) | LLM-Wiki | PoC 완료 (3/20), 나머지 변환 대기 |
| F | Experiential 157 (wiki 변환) | LLM-Wiki | private 코퍼스 작업 예정 |

각 변환 페이지는 front-matter에 `source: synthetic-memory/<file>.md` 를 명시해 **콘텐츠 동일성**을 추적합니다 — 평가 전 fidelity lint로 검증해야 B vs E, A vs F 비교가 오염되지 않습니다.

### 사용 방법론 및 도구

- **LLM-Wiki 패턴** — 마크다운 디렉터리 + `index.md` + 페이지간 cross-reference + `log.md`. 임베딩·벡터 DB 불필요. 원전: [Karpathy gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).
- **Claude Code** — `Read` / `Glob` / `Grep` 기본 도구만으로 위키 탐색·인제스트. 별도 retrieval 인프라 비용 0.
- **운영 규칙**: [`wiki/CLAUDE.md`](wiki/CLAUDE.md) — ingest / query / lint 워크플로우 정의
- **공정성 통제**: 페이지 front-matter `source:` 필드 + fidelity lint로 위키가 원문의 *오버레이*임을 보장 (편집적 재작성 금지)

### 참고 문헌

5개 핵심 선행 연구의 deep summary와 본 fork와의 관계는 [`docs/related-work-public-KO.md`](docs/related-work-public-KO.md) 참조 (Han et al. 2025 / Edge et al. 2024 / Karpathy 2026 / Xu et al. 2024 / Xiang et al. 2025). 짧은 인용 형식은 [`docs/rag-vs-wiki-design.md`](docs/rag-vs-wiki-design.md#references) 참조.

### 실행 방법 (구독 경로 — API 키 불필요)

평가는 두 가지 백엔드를 지원하며, **기본은 Claude Code 구독**입니다 (Pro/Max). API 키 비용 없이 돌릴 수 있습니다.

```bash
# 0) 사전 체크: API 키가 환경에 있으면 구독 대신 API가 우선됨 → 풀어두기
unset ANTHROPIC_API_KEY
claude auth                       # 로그인 상태 확인 (필요시 로그인)

# 1) 파싱 검증 (비용 0)
python3 scripts/run_condition_e_via_claude_code.py --dry-run

# 2) 단일 task 파일럿 (1 task만 실행)
python3 scripts/run_condition_e_via_claude_code.py --task IR-1

# 3) 한 cycle 전체: lint → 20 task 실행 → judge 채점 → loss 출력
bash autoresearch/run_experiment.sh
# → mean_score=X.XX  loss=X.XXXX  (loss = 1 - (mean_score - 1) / 4)
```

API 백엔드(per-token 과금)를 쓰려면:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic
AR_BACKEND=api bash autoresearch/run_experiment.sh
```

### TODO (다음 단계)

- [x] PoC: 위키 스키마(`wiki/CLAUDE.md`) + 3개 페이지 변환 + cross-reference 삼각형
- [x] 5개 문헌 기반 설계 문서 (`docs/rag-vs-wiki-design.md`) — 가설, 조건 매트릭스, 카테고리별 예측, 참고문헌
- [x] 나머지 17개 `synthetic-memory/` 파일 위키 변환 → Condition E 코퍼스 완성 (20/20)
- [x] `spawn-prompts.md` 에 Condition E/F 프롬프트 추가
- [x] Fidelity lint 스크립트 (`scripts/lint_fidelity.py`) — 20/20 페이지 통과 (substring 의미)
- [x] 평가 자동화 스크립트 (`scripts/run_condition_e.py`) — Anthropic SDK tool-use, sandboxed Read/Glob/Grep
- [x] LLM-as-judge 채점 스크립트 (`scripts/score_responses.py`) — `evaluation/rubric.md` 기반 1–5 점수
- [x] [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) 통합 scaffolding (`autoresearch/program.md`, `autoresearch/run_experiment.sh`) — 변형 가능 타깃·loss·cycle 정의
- [ ] **첫 실측 실행**: 위 "실행 방법" 절차로 hand-curated wiki의 베이스라인 mean_score / loss 측정 (구독으로 0원 가능)
- [ ] **자동 최적화 루프 가동**: `karpathy/autoresearch` 본체에 본 scaffolding 연결, 밤새 자율 실험 (위키 구조 → loss 최적화)
- [ ] **Condition F (private)**: 협력 연구자 환경에서 experiential corpus 위에 동일 파이프라인 적용 (private)
  - **autoresearch란**: 단일 GPU 환경에서 AI 에이전트가 코드를 수정·재학습·검증하며 *밤새 자율적으로 실험*하도록 만든 프레임워크 (MIT). 한 번의 실험 사이클 약 5분, 시간당 ~12회 반복, 메트릭 기반으로 변경을 채택/폐기.
  - **본 연구에 적용 시**: 에이전트가 **위키 구조 자체**(페이지 granularity, 링크 밀도, `index.md` 포맷, ingest 프롬프트, `## Related` 깊이 등)를 변형하면서 taskset 점수를 메트릭으로 *자동 탐색*.
  - **연구 호의 2단계**: ① 사람이 손으로 만든 LLM-Wiki 베이스라인(현재 PoC) → ② autoresearch로 *최적 위키 구조* 자동 발견. 수동 설계의 한계를 넘어, 이 워크로드에서 가장 효과적인 메모리 구조가 무엇인지 *경험적으로* 결정하는 것이 최종 목표.

---

## Repository Structure

```
├── README.md                       # This file
├── taskset.md                      # 20 evaluation tasks (English)
├── taskset_KO.md                   # 20 evaluation tasks (Korean, original)
├── spawn-prompts.md                # Exact prompts used per condition (sanitized)
├── evaluation/
│   ├── rubric.md                   # Scoring rubric (1-5 Likert, English)
│   ├── rubric_KO.md                # Scoring rubric (Korean)
│   ├── scores.csv                  # Raw scores per condition per task
│   └── protocol.md                 # Blind evaluation protocol
├── synthetic-memory/               # Condition B: 20 synthetic memory files
│   ├── nextjs-supabase.md
│   ├── soul-spec.md
│   └── ... (18 more files)
├── responses/
│   ├── condition-B-responses.md    # Synthetic condition responses (English)
│   ├── condition-B-responses_KO.md # Synthetic condition responses (Korean)
│   ├── condition-D-responses.md    # Baseline condition responses (English)
│   └── condition-D-responses_KO.md # Baseline condition responses (Korean)
├── experiential-memory-stats.md    # Statistics about Condition A (no raw data)
├── soul-spec-anonymized/           # Anonymized Soul Spec used across conditions
│   ├── SOUL.md
│   ├── IDENTITY.md
│   ├── AGENTS.md
│   └── soul.json
│
│   # v2 extension (RAG vs LLM-Wiki) — branch claude/rag-vs-graph-comparison-vAOGf
├── docs/
│   ├── rag-vs-wiki-design.md       # Conditions E/F design, hypotheses, references
│   ├── three-paradigms-KO.md       # RAG vs GraphRAG vs LLM-Wiki definitions
│   └── related-work-public-KO.md   # 5-paper sanitized lit review
├── wiki/                           # Conditions E/F: LLM-Wiki representation
│   ├── CLAUDE.md                   # Wiki operating rules (ingest/query/lint)
│   ├── index.md                    # Catalog (20 pages, 7 clusters)
│   ├── log.md                      # Append-only action log
│   └── pages/                      # 20 wiki pages (1:1 with synthetic-memory/)
├── scripts/                        # Eval / lint / score automation
│   ├── lint_fidelity.py            # Wiki vs source fidelity check
│   ├── run_condition_e.py          # Condition E runner — Anthropic SDK (per-token billing)
│   ├── run_condition_e_via_claude_code.py  # Condition E runner — local `claude` CLI (subscription, no API key)
│   └── score_responses.py          # LLM-as-judge scorer (--backend claude-code|api)
├── autoresearch/                   # karpathy/autoresearch integration
│   ├── README.md                   # Targets, loss, cycle, guardrails
│   ├── program.md                  # Agent instructions
│   └── run_experiment.sh           # lint -> eval -> score -> emit loss
└── results/                        # Eval run outputs (git-ignored payloads, kept as needed)
```

## Requesting Private Data

Conditions A (Experiential) and C (Hybrid) contain personally sensitive information including API credentials, employment details, and business strategy. These are available to researchers upon request:

📧 **contact@clawsouls.ai**

We will provide anonymized versions within 2 weeks of request. Please include:
- Your affiliation and research purpose
- How the data will be stored and protected
- Expected publication/use of the data

## Language & Reproducibility Notice

> **Original experiment was conducted in Korean.** Both the agent's working memory and the evaluation tasks were in Korean, as this reflects the natural working language of the human-agent collaboration.
>
> English translations of the taskset, rubric, and responses are provided for international accessibility (see `*_KO.md` files for Korean originals). Memory files in `synthetic-memory/` and private experiential memory remain in Korean — this is an inherent part of the experimental conditions, not a limitation to be corrected.
>
> **Replication in English** may yield different absolute scores due to language-dependent LLM behavior, but is expected to preserve relative rankings across conditions. We welcome cross-language replication studies.

## Experiment Environment

- **LLM**: Claude Opus 4 (Anthropic, `claude-opus-4-6`)
- **Method**: Each condition was run in a separate, isolated session with memory folder swap as the only variable
- **Memory retrieval**: Semantic search (RAG) over the memory corpus — the agent queries relevant memory files per task, not the entire corpus at once
- **Evaluation**: Single human evaluator, blind (shuffled W/X/Y/Z labels)
- **Exact prompts**: See `spawn-prompts.md` for the sanitized prompts used per condition

## Reproducing the Experiment

### Method 1: Using an AI Agent Framework (Most Faithful)

This experiment was originally run using an agent framework that provides:
- Isolated session spawning (one session per condition)
- RAG-based memory retrieval (`memory_search` → `memory_get`)
- Tool access (file read, exec, web search)

To reproduce faithfully:

1. Set up any agent framework that supports isolated sessions and RAG (e.g., OpenClaw, LangChain, or custom)
2. Place experiential memory files in the agent's memory directory
3. Place synthetic memory files in a separate directory
4. Configure the same LLM (Claude Opus 4 or comparable)
5. Use the prompts from `spawn-prompts.md`, replacing `<MEMORY_DIR>`, `<SYNTHETIC_DIR>`, and `<TASK_FILE>` with your paths
6. Run each condition in isolation and record responses

**Note**: RAG introduces non-determinism — the exact memory snippets retrieved per query may vary. This is inherent to the experimental design and reflects real-world agent behavior.

### Method 2: Using Claude API (Simplified)

For a simplified reproduction without RAG (all memory in context):

```python
import anthropic
from pathlib import Path

client = anthropic.Anthropic()

def load_all_files(directory):
    """Load all .md files from a directory."""
    texts = []
    for f in sorted(Path(directory).glob("*.md")):
        texts.append(f"## {f.name}\n\n{f.read_text()}")
    return "\n\n---\n\n".join(texts)

soul_spec = open("soul-spec-anonymized/SOUL.md").read()
tasks = open("taskset.md").read()

# Condition B (Synthetic) — fully reproducible with public data
synthetic_memory = load_all_files("synthetic-memory/")

response = client.messages.create(
    model="claude-opus-4-20250514",
    system=f"{soul_spec}\n\n## Memory Files\n\n{synthetic_memory}",
    messages=[{"role": "user", "content": tasks}]
)
print(response.content[0].text)

# Condition D (Baseline) — no memory
response = client.messages.create(
    model="claude-opus-4-20250514",
    system=soul_spec,
    messages=[{"role": "user", "content": tasks}]
)
```

### Method 3: Using Claude.ai Web UI (Conditions B and D only)

1. Open [claude.ai](https://claude.ai) in incognito/private mode
2. Select Claude Opus with Extended Thinking
3. **Condition B**: Paste soul spec + all 20 synthetic memory files + tasks as first message
4. **Condition D**: Paste soul spec + tasks only (no memory)
5. Record responses and evaluate using `evaluation/rubric.md`

**Limitation**: Conditions A and C require ~157 experiential memory files (~300KB), which is impractical to paste manually. Use Method 1 or 2 for these conditions.

### Key Requirements for Valid Replication

- **Isolation**: Each condition must run in a completely separate session (no cross-contamination)
- **Same model**: Use the same model version across all four conditions
- **Blind evaluation**: Shuffle condition labels before scoring to prevent evaluator bias
- **Same tasks**: Use the exact tasks from `taskset.md` without modification
- **Language**: Use Korean tasks (`taskset_KO.md`) for faithful replication, or English (`taskset.md`) for cross-language replication

## Citation

```bibtex
@misc{lee2026experiential,
  title={Experiential vs Synthetic Memory in Long-Running AI Agents: 
         A Controlled Experiment in Software Development},
  author={Tom Lee},
  year={2026},
  publisher={Zenodo},
  doi={10.5281/zenodo.18798227}
}
```

## License

- **Dataset**: CC-BY-4.0
- **Synthetic memory files**: CC-BY-4.0
- **Paper**: CC-BY-4.0
