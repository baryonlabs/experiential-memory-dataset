# 본 fork 연구의 관련 연구 (Public Reading List)

> **Sanitized public version.** 본 fork 연구의 학술 토대를 정리한 공개 자료.
> 적용 도메인의 구체적 사례·협력자·내부 일정은 *parent paper(Lee 2026)의 데이터 정책*에 따라 비공개. 협력자 요청 시 NDA 하에 공유. 자세한 안내는 문서 하단 참조.
>
> 본 fork 연구자: **홍승우 (Hong Seung-woo)**
> 작업 브랜치: [`claude/rag-vs-graph-comparison-vAOGf`](https://github.com/baryonlabs/experiential-memory-dataset/tree/claude/rag-vs-graph-comparison-vAOGf)
> 패러다임 정의: [`three-paradigms-KO.md`](three-paradigms-KO.md)
> 실험 설계: [`rag-vs-wiki-design.md`](rag-vs-wiki-design.md)

---

## 서론

본 fork는 원 실험 *Experiential vs Synthetic Memory in Long-Running AI Agents* (Lee 2026)에서 retrieval method가 단일(RAG)로 고정된 한계를 보완한다. 그 근거를 정리하기 위해 5개 핵심 선행 연구를 선정했다.

**선정 기준**:
1. RAG와 그래프/위키 방식의 직접 비교 실험을 포함
2. 실제 프로덕션 배포 경험 또는 그에 준하는 정량 증거
3. "언제 그래프가 도움이 되지 않는가"라는 비판적 균형 관점
4. 구조화된 B2B 워크로드(견적·티켓·이력 검색 등)에 적용 가능

**권장 읽기 순서**: Paper 2 (GraphRAG 원리) → Paper 1 (체계적 비교) → Paper 3 (Karpathy 위키 패턴) → Paper 4 (LinkedIn 프로덕션 사례) → Paper 5 (한계). 집중 4-6시간 예상. Paper 3은 짧지만 아이디어 밀도가 높아 천천히 읽기를 권장.

---

## 1. Han et al. 2025 — RAG vs GraphRAG 체계적 평가

- **출처**: arXiv:[2502.11371](https://arxiv.org/abs/2502.11371)
- **발표**: 2025년 2월

### 요약

GraphRAG 변형들이 서로 다른 데이터셋·메트릭으로 평가돼 직접 비교가 어려운 문제를 지적하고, **전처리·검색·생성 설정을 표준화한 통합 평가 프로토콜**을 제안. QA와 query-focused summarization 두 태스크에서 RAG와 GraphRAG가 서로 다른 강점을 보이며, 두 방식을 *선택적으로 결합*하는 전략이 일관된 향상을 가져옴을 보고.

### 본 fork에서의 의미

평가 프로토콜의 *템플릿*. 본 fork도 변수(retrieval method)만 분리해 측정해야 하므로, Han et al.의 "전처리·설정 고정" 원칙을 그대로 차용. 단, 본 fork의 차별점은 **콘텐츠 자체를 동일 코퍼스로 고정**(parent paper의 synthetic 20개 / experiential 157개)한 점 — Han et al.은 다른 코퍼스에서 비교하므로 콘텐츠 변이가 섞임.

---

## 2. Edge et al. 2024 — Microsoft GraphRAG (canonical 원논문)

- **출처**: arXiv:[2404.16130](https://arxiv.org/abs/2404.16130)
- **구현**: [microsoft/graphrag](https://github.com/microsoft/graphrag) (오픈소스)

### 요약

기존 RAG가 "이 코퍼스의 주요 테마는?" 같은 **전역 sensemaking 질문**에 취약함을 지적. 2단계 파이프라인 제안: (1) LLM으로 코퍼스에서 entity-relation 지식 그래프 추출, (2) 밀접하게 연결된 entity 클러스터(community)에 대한 summary를 사전 생성. 쿼리 시 community summary들이 부분 응답을 만들고 통합. 100만 토큰 규모 코퍼스에서 포괄성·다양성 모두 RAG 대비 유의미한 향상.

### 본 fork에서의 의미

GraphRAG의 *정의 기준*. [`three-paradigms-KO.md`](three-paradigms-KO.md)의 GraphRAG 정의가 이 논문 기반. 본 fork는 GraphRAG 자체를 1차 비교 대상으로 두지 *않고* (LLM-Wiki를 우선), 후속 옵션(Conditions G/H)으로 보존. 이유: (a) GraphRAG는 entity 추출 비용이 높고 한국어에서 별도 검증이 필요, (b) 가장 가벼운 구조적 대안(LLM-Wiki)이 RAG를 이기지 못하면 GraphRAG의 무거운 설계는 정당화 안 됨.

---

## 3. Karpathy 2026 — LLM-Wiki 패턴

- **출처**: [GitHub Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- **형식**: 패턴 제안 문서 (논문 아님, 2026년 4월)

### 요약

대부분의 RAG 시스템이 쿼리 시점에 청크를 검색하므로 *지식이 누적되지 않는다*는 한계를 지적. 대안으로 **3-layer 아키텍처**: (a) 원본 소스(불변), (b) LLM이 작성·유지하는 마크다운 위키, (c) 위키 운영 규칙(`CLAUDE.md`/`AGENTS.md`). 새 소스 인제스트 시 LLM이 단순 인덱싱이 아니라 *기존 위키를 업데이트*(엔티티 페이지 수정, 모순 표시, 교차 참조 강화). 임베딩 0, 청킹 0. `index.md` 기반 텍스트 탐색이 소~중규모에서 충분.

### 본 fork에서의 의미

본 fork **Conditions E/F의 직접적 framing**. PoC가 이 패턴을 그대로 구현(`wiki/CLAUDE.md`, `wiki/index.md`, `wiki/log.md`, `wiki/pages/`). Karpathy의 "지식 베이스 유지의 진짜 장벽은 *귀찮은 관리 작업*이고, LLM은 지루해하지 않는다"는 관찰이 본 fork 설계 철학의 핵심. 한계: 수백 페이지 이상 규모에서 `index.md` 단일 카탈로그가 비대해지면 별도 검색 보조가 필요해질 수 있음 (본 fork의 synthetic 20개·experiential 157개 규모에선 무관).

---

## 4. Xu et al. 2024 — LinkedIn KG-RAG 프로덕션 사례

- **출처**: arXiv:[2404.17723](https://arxiv.org/abs/2404.17723), SIGIR 2024 (DOI:10.1145/3626772.3661370)

### 요약

LinkedIn 기술 지원 고객 서비스 시스템에 **RAG + 지식 그래프 결합** 방식 배포. 이슈 티켓을 평문으로 처리하는 기존 RAG가 *이슈 내 구조*(증상-원인-해결책)와 *이슈 간 관계*(유사 문제, 동일 근원)를 잃는 문제를 KG 기반 sub-graph 검색으로 해결. **MRR +77.6%, BLEU +0.32, 이슈당 중간 해결 시간 −28.6%** (실배포 6개월 측정). 5개 논문 중 *유일한* 대규모 실배포 정량 증거.

### 본 fork에서의 의미

"구조화된 검색 향상이 실제 프로덕션 워크로드로 이전되는가"에 대한 가장 강력한 긍정 증거. 본 fork가 가정하는 적용 도메인(B2B quoting/pricing 등 *구조화된 이력 기반 워크플로우*)은 LinkedIn 사례와 위상적으로 유사 — 과거 이슈 ↔ 과거 견적, 이슈 해결 ↔ 신규 견적 생성. 평가 메트릭 체계(MRR, Recall@K, NDCG@K + BLEU, ROUGE)를 본 fork 평가에도 차용 검토. 단, LinkedIn은 KG(GraphRAG 계열)이고 본 fork 1차 비교는 LLM-Wiki — *이 차이가 본 fork의 학술적 기여 포인트*.

---

## 5. Xiang et al. 2025 — When NOT to use GraphRAG (균형추)

- **출처**: arXiv:[2506.05690](https://arxiv.org/abs/2506.05690)
- **벤치마크**: [GraphRAG-Bench](https://github.com/GraphRAG-Bench/GraphRAG-Benchmark) (오픈소스)

### 요약

"GraphRAG가 항상 우월"하다는 낙관론에 대한 체계적 반론. 4-task 벤치마크 제안: (1) 사실 검색, (2) 복잡 추론, (3) 맥락적 요약, (4) 창의적 생성. **GraphRAG는 단순 사실 검색에서 일반 RAG보다 자주 손해**. 계층적 지식 구조가 명확하고 심층 추론이 필요한 태스크에서만 일관된 이점. 그래프 구축 비용 대비 효용은 태스크 유형에 강하게 의존.

### 본 fork에서의 의미

본 fork의 **카테고리별 예측표**(`docs/rag-vs-wiki-design.md`의 Per-Category Predictions)의 직접 근거. parent paper의 4 카테고리(Information Retrieval / Coding / Architecture / Context-Dependent)를 Xiang et al.의 4-task 분류에 매핑하면 — IR은 작은 향상, Architecture/Context-Dependent는 큰 향상 — 라는 falsifiable 예측이 도출됨. **이 예측이 어긋나면 본 fork 가설 자체를 기각**. paper 작성 시 균형 관점의 핵심 인용.

---

## 결론 및 다음 단계

5개 논문 종합:

> **GraphRAG/LLM-Wiki는 전역 추론·계층적 지식·맥락 종합이 필요한 태스크에서 강하다. 단순 사실 검색에서는 일반 RAG가 충분하거나 유리하다. LLM-Wiki(Karpathy 패턴)는 임베딩 인프라 없이 지식을 누적하는 가장 가벼운 구조적 대안이다.**

본 fork의 가설(`docs/rag-vs-wiki-design.md` H1–H4)은 위 합의 위에 서 있다. 즉, 본 연구의 결과가 어느 방향으로 나오든 — 가설 지지든 기각이든 — 5개 논문이 형성한 *공통의 이해 지도* 위에 위치를 가질 수 있다.

### 본 fork의 12주 트랙 (학술 프로그램 일정과 정렬)

- **1단계 (1–4주차, 환경/학습)**: Paper 2, 3, 5 필독 → 이론적 토대. PoC 위키 구조 검증.
- **2단계 (5–10주차, 실험)**: Paper 1, 4의 평가 프로토콜·메트릭 차용. Conditions E/F 평가 실행.
- **3단계 (11–12주차, 작성)**: Paper 5의 균형 관점 인용. 본 fork만의 발견 정리.

### 협력 / 적용의 다음 단계

본 fork의 적용 도메인(B2B quoting/pricing 등 구조화된 이력 워크플로우)에서의 PoC는:

1. 적용 도메인의 실제 데이터 샘플 확보 (private — NDA 협의 후)
2. Karpathy 위키 패턴으로 가장 빠른 도메인-특화 PoC 구현 (임베딩 인프라 없이 즉시 시작 가능)
3. Paper 4(LinkedIn)의 평가 메트릭 체계로 측정

이 순서는 학술 트랙(public)과 적용 트랙(private)을 분리한 채 자연스럽게 병행시킬 수 있다.

### 한국어 적용

5개 논문 모두 영어 코퍼스 중심. 한국어 corpus에서의 GraphRAG entity 추출 성능, LLM-Wiki cross-reference 품질은 별도 검증 필요. 본 fork의 parent paper가 *한국어 원본 실험*이라는 점이 이 검증의 자연스러운 출발점 — Conditions E/F의 wiki 변환 자체가 한국어 LLM-Wiki의 첫 사례 검증이 됨.

---

## Private 자료 안내

본 문서는 학술 자산으로서 공개되며, 다음 정보는 *parent paper의 데이터 정책*에 따라 비공개로 유지됨:

- 본 fork의 적용 도메인의 *구체적 인스턴스*(특정 제품/회사/제3자 식별 정보)
- 협력 조직의 내부 일정·의사결정 컨텍스트
- 사업 파트너십의 세부 조항

협력 연구자는 다음 절차로 요청 가능 (parent paper의 절차 준용):

📧 **contact@clawsouls.ai**

요청 시 포함할 정보: 소속 및 연구 목적, 데이터 보관·보호 방안, 예상 출판/사용처. 2주 내 검토 후 NDA 하에 anonymized 버전 제공.
