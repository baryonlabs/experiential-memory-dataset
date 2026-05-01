# RAG vs GraphRAG vs LLM-Wiki — 세 패러다임 비교

> **본 fork 연구의 정의 문서.**
> 원 실험: *Experiential vs Synthetic Memory in Long-Running AI Agents* (Lee 2026, [Zenodo 10.5281/zenodo.18798227](https://zenodo.org/records/18798227))
> 본 확장 연구: 홍승우 (Hong Seung-woo). 원 실험이 *content* 차원만 변화시킨 채 *retrieval method*는 RAG로 고정한 한계를 지적하며, 동일 코퍼스 위에서 retrieval 패러다임을 변수로 추가한다.
> 작업 브랜치: [`claude/rag-vs-graph-comparison-vAOGf`](https://github.com/baryonlabs/experiential-memory-dataset/tree/claude/rag-vs-graph-comparison-vAOGf)
> 설계 문서: [`docs/rag-vs-wiki-design.md`](rag-vs-wiki-design.md)

---

## 1. 왜 세 패러다임을 모두 비교하는가

원 실험의 가장 의외였던 결과 — **Synthetic(2.65) < Baseline(3.30)** — 는 두 가지 해석 사이에서 결정되지 않은 채 남아 있다:

- (a) 콘텐츠가 노이즈였다
- (b) flat RAG가 콘텐츠의 구조를 깎아냈다

(b)를 검증하려면 *retrieval 방식*을 변수로 둬야 하고, 그 순간 "RAG의 대안"이라는 설계 공간 전체가 시야에 들어온다. 그 공간에는 최소 세 점이 존재한다 — 본 문서는 그 세 점의 정확한 정의와 차이를 정리한다.

---

## 2. 개별 정의

### 2.1 RAG (Retrieval-Augmented Generation, flat)

**핵심 메커니즘**: 코퍼스를 청크 단위로 분할 → 각 청크를 임베딩 모델로 벡터화 → vector DB에 저장 → 쿼리도 임베딩해 k-NN 유사도 검색 → 상위 k개 청크를 LLM 프롬프트에 주입.

**대표 출처**: Lewis et al. 2020 (원 RAG 논문). 이후 LangChain·LlamaIndex 등 대부분의 프레임워크가 채택한 표준 패러다임.

**원 실험에서**: Conditions A (Experiential), B (Synthetic), C (Hybrid)가 모두 이 방식.

### 2.2 GraphRAG (Edge et al. 2024)

**핵심 메커니즘**: LLM으로 코퍼스에서 **엔티티-관계 지식 그래프**를 추출 → 밀접하게 연결된 엔티티 클러스터(community)에 대해 **community summary**를 사전 생성 → 쿼리 시 각 community summary가 부분 응답을 만들고, 이를 통합해 최종 답변 산출.

**대표 출처**: Edge et al. 2024, *From Local to Global: A Graph RAG Approach to Query-Focused Summarization* (arXiv:[2404.16130](https://arxiv.org/abs/2404.16130)). Microsoft Research의 오픈소스 구현체 [microsoft/graphrag](https://github.com/microsoft/graphrag).

**프로덕션 사례**: LinkedIn 고객 서비스 KG-RAG (Xu et al. 2024, arXiv:[2404.17723](https://arxiv.org/abs/2404.17723)) — MRR +77.6%, 해결 시간 −28.6%.

**한계**: Xiang et al. 2025 ([2506.05690](https://arxiv.org/abs/2506.05690))는 단순 사실 검색에서 GraphRAG가 일반 RAG에 자주 *진다*는 점을 체계적으로 보고.

### 2.3 LLM-Wiki (Karpathy 2026)

**핵심 메커니즘**: 원본 소스 → LLM이 **마크다운 위키**(`wiki/pages/*.md`)를 작성·유지 → `index.md`가 카탈로그 → 페이지간 cross-reference로 그래프 구조 형성 → 쿼리 시 LLM이 `Read`/`Glob`/`Grep` 으로 인덱스부터 탐색 → 관련 페이지를 따라가며 답변.

**핵심 차별점**:
- 임베딩 0, 벡터 DB 0, 그래프 DB 0
- 새 소스 인제스트 시 LLM이 *기존 위키를 업데이트* (지식이 누적·복리 성장)
- 인프라는 마크다운 파일 + git만

**대표 출처**: [Karpathy gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) (2026년 4월).

**본 fork 연구에서**: Conditions E (synthetic-wiki), F (experiential-wiki).

---

## 3. 비교표

### 3.1 구조와 메커니즘

| 축 | RAG | GraphRAG | LLM-Wiki |
|---|---|---|---|
| 인덱스 자료구조 | 임베딩된 청크 (vector DB) | Entity-relation KG + community summary | 마크다운 파일 + `index.md` + 페이지간 링크 |
| 검색 메커니즘 | k-NN 벡터 유사도 | 그래프 traversal + community summary 조회 | `Read` / `Glob` / `Grep` + `## Related` 링크 따라가기 |
| 결정론 | 비결정론적 (top-k 컷오프) | 부분 결정론적 (community 선택은 결정적) | 결정론적 (LLM 추론 자체 외) |
| 디버깅 가능성 | 낮음 (왜 이 청크가 검색됐는지 불투명) | 중간 (그래프 path는 추적 가능, summary 생성은 불투명) | 높음 (LLM이 따라간 링크 = 그대로 trace) |

### 3.2 비용 구조

| 축 | RAG | GraphRAG | LLM-Wiki |
|---|---|---|---|
| 사전 빌드 비용 | 임베딩 compute + vector DB 구축 | LLM 기반 entity 추출 + community 클러스터링 (가장 비쌈) | LLM 큐레이션 시간 (인프라 구축비 0) |
| 쿼리당 비용 | 쿼리 임베딩 + vector search | community summary 조회 + LLM 통합 | 파일 read N회 (가장 쌈) |
| 갱신 비용 | 신규 청크 임베딩만 | entity 추출 + 그래프 부분 재구성 | LLM이 N개 페이지 동시 업데이트 |
| 임베딩 모델 의존 | 강함 (모델 변경 시 전수 재임베딩) | 부분적 | 없음 |
| 인프라 요구 | vector DB + 임베딩 모델 hosting | graph DB 또는 인메모리 그래프 + LLM | 파일시스템 + git만 |
| Cold-start | 전수 임베딩 완료 후 사용 가능 | entity 추출 완료 후 사용 가능 (가장 김) | 첫 페이지부터 사용 가능 |

### 3.3 워크로드 적합성 (Xiang et al. 2025의 4-task 분류 기반)

| 워크로드 유형 | RAG | GraphRAG | LLM-Wiki |
|---|---|---|---|
| 단순 사실 검색 | **유리** | 오히려 손해 | 동등 |
| 복잡한 추론 (multi-hop) | 약함 | **유리** | 중간 |
| 맥락적 요약 / 전역 sensemaking | 가장 약함 | **가장 유리** | 강함 (cross-ref 따라가면) |
| 창의적 생성 | 의존도 낮음 | 의존도 낮음 | 의존도 낮음 |

### 3.4 본 실험과의 매핑

| Condition | 메모리 콘텐츠 | retrieval 패러다임 | 상태 |
|---|---|---|---|
| A | Experiential 157 | RAG | 원 실험 |
| B | Synthetic 20 | RAG | 원 실험 |
| C | Hybrid (A+B) | RAG | 원 실험 |
| D | None | — | 원 실험 |
| **E** | **Synthetic 20 (wiki 변환)** | **LLM-Wiki** | **본 fork PoC (3/20 완료)** |
| **F** | **Experiential 157 (wiki 변환)** | **LLM-Wiki** | **본 fork (private 작업 예정)** |
| G (선택) | Synthetic 20 (KG 변환) | GraphRAG | 후속 옵션 |
| H (선택) | Experiential 157 (KG 변환) | GraphRAG | 후속 옵션 |

**1차 비교(필수)**: B vs E — 동일 콘텐츠, RAG ↔ LLM-Wiki. 가설 (b) 검증.
**2차 비교(권장)**: A vs F — 동일 콘텐츠, RAG ↔ LLM-Wiki. experiential 코퍼스에서도 효과 있는지.
**3차 비교(선택)**: B vs G, A vs H — 설계 공간의 세 점 모두 측정. 비용은 가장 높지만 학술적 가치 큼.

---

## 4. 본 fork 연구의 좌표

홍승우의 본 fork 연구는 **설계 공간에서 명시적으로 LLM-Wiki 점만 추가**한다. GraphRAG는 후속 옵션으로 두는 이유는:

1. **연구 가설의 초점**: 원 실험 결과(B<D)의 retrieval-method 가설을 가장 직접적으로 검증하려면, 가장 *가벼운* 구조적 대안(LLM-Wiki)이 RAG를 이기는지부터 본다. 이기지 못하면 GraphRAG의 무거운 설계가 정당화되지 않는다.
2. **사용자(연구자)의 관심사 정합**: 임베딩 매몰비용·복잡성에서 벗어나려는 동기 → LLM-Wiki가 직접적 해답. GraphRAG는 그래프 DB라는 또 다른 인프라 부담을 수반.
3. **재현 비용**: 본 repo는 공개 데이터셋. LLM-Wiki는 마크다운 파일만 있으면 누구나 재현 가능. GraphRAG는 microsoft/graphrag 셋업 + 한국어 entity 추출 검증이 추가로 필요.

GraphRAG 조건(G/H)은 LLM-Wiki 결과가 유의미하게 나온 *이후*, 자동 최적화 단계([karpathy/autoresearch](https://github.com/karpathy/autoresearch) 적용)와 함께 검토하는 것이 자연스럽다.

---

## 5. 검증 가능한 가설 (재진술)

세 패러다임 비교 프레이밍 위에서 본 연구의 가설은 다음과 같이 정리된다:

- **H1 (강)**: B에서 E로 retrieval만 바꾸면 점수가 baseline 위로 상승한다 → 원 B<D 결과의 *주요인은 retrieval 방식*.
- **H2 (약)**: A에서 F로 retrieval만 바꿔도 향상은 작다 → experiential 코퍼스는 이미 implicit cross-ref 구조를 갖고 있음.
- **H3 (카테고리)**: 향상 폭은 Architecture / Context-Dependent에서 가장 크고, Information Retrieval에서 가장 작다 (Xiang et al. 2025의 task-dependence 발견과 일관).
- **H4 (비용)**: LLM-Wiki는 사전 빌드 비용 0, 쿼리당 비용 ↑. 워크로드별 손익분기점은 코퍼스 크기와 쿼리 빈도에 의존.

각 가설은 falsifiable하다 — 예측 방향과 어긋나는 결과가 나오면 명시적으로 기각.

---

## 6. 참고 문헌

상세 인용은 [`docs/rag-vs-wiki-design.md`](rag-vs-wiki-design.md#references) 참고. 본 비교의 직접적 근거:

1. **[Edge et al. 2024]** — GraphRAG canonical 논문 (arXiv:2404.16130)
2. **[Xu et al. 2024]** — LinkedIn KG-RAG 프로덕션 사례 (arXiv:2404.17723)
3. **[Han et al. 2025]** — RAG vs GraphRAG 체계적 평가 (arXiv:2502.11371)
4. **[Xiang et al. 2025]** — task-dependence, "When NOT to use GraphRAG" (arXiv:2506.05690)
5. **[Karpathy 2026]** — LLM-Wiki gist
