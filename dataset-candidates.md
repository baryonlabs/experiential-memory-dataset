# 데이터셋 후보 조사 — 퍼소나 붕괴 기반 오작동 조기 경보

> 관련 이슈: [#1 데이터셋 선정을 집중적으로 고민해보자.](https://github.com/baryonlabs/experiential-memory-dataset/issues/1)

## 1. 문제 정의

이슈 #1의 가설:

> 다양한 데이터셋 & 퍼소나로 실험했을 때 **퍼소나 붕괴(persona collapse)** 현상을 파악하면,
> **오작동(제약된 실행을 벗어나는 행동)** 에 대한 미리 알림(early warning)이 가능하지 않을까?

이 가설을 검증하려면 두 가지 신호를 한 실험 안에서 동시에 관찰할 수 있어야 한다.

1. **퍼소나 붕괴 신호** — 에이전트가 부여된 정체성/말투/원칙에서 점진적으로 이탈하는 정도
2. **제약 이탈 신호** — 에이전트가 명시된 안전·정책·범위 제약을 실제로 위반하는 사건

가설의 핵심은 **(1)이 (2)보다 먼저, 더 약한 형태로 관측된다**는 것이다. 즉 퍼소나 드리프트를
선행 지표(leading indicator)로 쓸 수 있는지가 검증 대상이다. 따라서 후보 데이터셋은
"드리프트 측정용"과 "위반 측정용"으로 나누되, **둘을 시간축으로 정렬할 수 있는지**를
가장 중요한 선정 기준으로 본다.

## 2. 선정 기준

| 기준 | 설명 | 가중치 |
|------|------|:---:|
| 멀티턴/장기 세션 | 드리프트는 누적 현상 — 단일 턴 데이터는 부적합 | 높음 |
| 퍼소나/역할 명세 존재 | 붕괴를 측정하려면 기준선(assigned persona)이 필요 | 높음 |
| 제약·정책 라벨 | 위반 이벤트가 라벨링되어 있어야 (1)↔(2) 정렬 가능 | 높음 |
| 턴 단위 타임스탬프/시퀀스 | 선행성 검증을 위해 시간 정렬 필수 | 높음 |
| 도메인 다양성 | "다양한 데이터셋"이라는 이슈 요구 충족 | 중간 |
| 라이선스 | 본 리포가 CC-BY-4.0 — 호환 라이선스 선호 | 중간 |

## 3. 후보 데이터셋

### A. 퍼소나 드리프트 / 역할 일관성 (드리프트 신호용)

| 데이터셋 | 규모/특징 | 적합성 | 비고 |
|----------|-----------|--------|------|
| **persona_drift** (likenneth, GitHub) | LLM 대화 내 퍼소나 드리프트 측정·제어 코드/데이터 | 높음 | 드리프트 정량화 메트릭 기제공, 본 실험에 바로 차용 가능 |
| **CHARCO** (Character-Coherent Dialogues) | 230K+ 멀티턴 대화, 퍼소나 프로파일·감정 라벨 | 높음 | 대규모 기준선 확보용. 위반 라벨은 없음 |
| **Identity Drift in LLM Agents** (arXiv 2412.00804) | LLM 에이전트 대화의 정체성 드리프트 분석 | 높음 | 8라운드 내 드리프트 관측 — 선행성 가설과 직접 연결 |
| **Echo / EchoMode** (drift detection benchmark) | 장기 컨텍스트 세션의 퍼소나 안정성 드리프트 곡선 | 중간 | 모델별 드리프트 곡선 — 메트릭 참고용 |

### B. 제약 위반 / 에이전트 안전 (위반 신호용)

| 데이터셋 | 규모/특징 | 적합성 | 비고 |
|----------|-----------|--------|------|
| **ODCV-Bench** (arXiv 2512.20798) | 40개 멀티스텝 시나리오, KPI 압력 하 결과지향 제약 위반 | 매우 높음 | "제약된 실행 이탈"의 정의에 가장 근접. Mandated vs Incentivized 변형 — 맹목적 복종 vs 창발적 오정렬 분리 |
| **SHADE-Arena / CUA-SHADE-Arena** | 양성 주작업 + 은닉 악의적 부작업 (17 / 15 쌍) | 높음 | 부작업 수행 = 명시적 위반 이벤트. 멀티스텝 trajectory 보유 |
| **AgentAuditor** | LLM 에이전트 안전·보안 인간수준 평가 | 중간 | 평가 프로토콜·라벨 스킴 참고 |
| **BeSafe-Bench** (arXiv 2603.25747) | 기능적 환경 내 상황형 에이전트의 행동 안전 위험 | 중간 | 도메인 다양성 보강용 |

### C. 장기 기억 / 멀티세션 (본 리포 실험과의 연속성)

| 데이터셋 | 규모/특징 | 적합성 | 비고 |
|----------|-----------|--------|------|
| **LongMemEval** (ICLR 2025) | 500문항, ~57M 토큰, 문항당 ~50세션 | 높음 | 본 리포의 경험적/합성 기억 실험과 가장 자연스럽게 연결 |
| **MemoryAgentBench** (ICLR 2026) | 증분 멀티턴, EventQA·FactConsolidation 신규 | 높음 | 기억 갱신·일관성 — 드리프트와 기억 손상의 교차 검증 |
| **SWE-ContextBench / EXPEREPAIR** | SWE 에이전트의 경험 재사용·이중기억 ablation | 중간 | 코딩 에이전트 도메인 — 본 taskset(Coding Tasks)과 정합 |

### D. 퍼소나 기반 공격 (붕괴 유발 조건 통제용)

| 데이터셋 | 규모/특징 | 적합성 | 비고 |
|----------|-----------|--------|------|
| **Persona Jailbreaking** (arXiv 2601.16466) | 퍼소나를 통한 LLM 탈옥 사례 | 중간 | 붕괴를 "유도"하는 통제 변인 — 자연 드리프트와 대비군으로 활용 |

## 4. 본 리포지토리 데이터셋과의 연결

현재 리포의 4개 조건(A 경험적 / B 합성 / C 하이브리드 / D 베이스라인) 실험은
이미 **고정 퍼소나(Soul Spec) + 멀티세션 기억 + 도메인 taskset** 구조를 갖추고 있다.
이슈 #1 가설 검증에 필요한 것은 다음 두 가지 확장이다.

1. **드리프트 계측 추가** — 각 응답에 대해 Soul Spec(`SOUL.md`, `IDENTITY.md`) 대비
   퍼소나 일관성 점수(prompt-to-line / line-to-line consistency)를 턴 단위로 기록.
   `persona_drift` 또는 Identity Drift 논문의 메트릭을 차용.
2. **위반 이벤트 라벨 추가** — taskset의 Category 4(Context-Dependent Decisions)는
   이미 rubric에서 *"1점: 위험한 판단(보안·법적 리스크 무시)"* 을 정의하고 있어
   사실상 제약 위반 라벨의 원형이다. ODCV-Bench의 KPI 압력 시나리오를 추가하면
   위반 신호를 의도적으로 강화한 대비군을 만들 수 있다.

이 두 신호를 같은 세션 타임라인에 정렬하면 이슈의 핵심 질문
("드리프트가 위반보다 먼저 오는가?")을 본 리포 자체 데이터로 검증할 수 있다.

## 5. 추천 조합

가설 검증을 위한 최소 구성(MVP):

- **드리프트 기준선**: `persona_drift` 메트릭 + 본 리포 Soul Spec
- **위반 시나리오**: ODCV-Bench (Incentivized 변형) — "제약 이탈"의 명확한 그라운드 트루스
- **장기 세션 백본**: LongMemEval — 50+ 세션에 걸친 누적 드리프트 관측
- **대비군**: Persona Jailbreaking — 유도된 붕괴 vs 자연 드리프트 구분

이 조합이면 "다양한 데이터셋 & 퍼소나"(이슈 요구)와 "붕괴→위반 선행성"(가설)을
한 실험 설계 안에서 모두 다룰 수 있다.

## 6. 미해결 질문 / 다음 단계

- [ ] 각 후보의 정확한 라이선스 확인 (CC-BY-4.0 재배포 호환 여부)
- [ ] ODCV-Bench와 LongMemEval의 세션 포맷을 공통 스키마로 정규화 가능한가?
- [ ] 퍼소나 드리프트 메트릭을 한국어 세션(본 실험의 원어)에 적용 시 신뢰도 검증 필요
- [ ] "선행성" 측정 방법론 — 드리프트 곡선의 변곡점 vs 위반 시점의 lead time 정의
- [ ] 본 리포의 조건 A(경험적 기억)가 드리프트를 줄이는지/늘리는지 사전 가설 수립

## 참고 자료

- [persona_drift — Measuring and Controlling Persona Drift in Language Model Dialogs (GitHub)](https://github.com/likenneth/persona_drift)
- [Examining Identity Drift in Conversations of LLM Agents (arXiv 2412.00804)](https://arxiv.org/abs/2412.00804)
- [Understanding Persona Drift in LLMs (Emergent Mind)](https://www.emergentmind.com/topics/persona-drift)
- [Enhancing Character-Coherent Role-Playing Dialogue (CHARCO, MDPI)](https://www.mdpi.com/2078-2489/16/9/738)
- [A Benchmark for Evaluating Outcome-Driven Constraint Violations in Autonomous AI Agents — ODCV-Bench (arXiv 2512.20798)](https://arxiv.org/abs/2512.20798)
- [AgentAuditor: Human-Level Safety and Security Evaluation for LLM Agents (OpenReview)](https://openreview.net/pdf/2ceecf4bf50bffa7cff2d145fadb18c23daf7206.pdf)
- [BeSafe-Bench: Behavioral Safety Risks of Situated Agents (arXiv 2603.25747)](https://arxiv.org/html/2603.25747)
- [LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory (GitHub, ICLR 2025)](https://github.com/xiaowu0162/longmemeval)
- [MemoryAgentBench: Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions (GitHub, ICLR 2026)](https://github.com/HUST-AI-HYZ/MemoryAgentBench)
- [Persona Jailbreaking in Large Language Models (arXiv 2601.16466)](https://www.arxiv.org/pdf/2601.16466)
- [Prioritizing Real-Time Failure Detection in AI Agents (Partnership on AI)](https://partnershiponai.org/wp-content/uploads/2025/09/agents-real-time-failure-detection.pdf)
