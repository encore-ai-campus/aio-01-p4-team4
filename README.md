# 티켓모아 · 고객 기술지원 멀티에이전트 (n8n)

가상의 티켓 예매 플랫폼 티켓모아의 고객 기술 문의를 자동 분류하고, 지식 문서(RAG)와 예매 조회로 답하며, 필요한 건은 상담원에게 이관하는 n8n 워크플로우.

- 팀: 티켓모아 · 최두나(리드·통합) · 최강현(오케스트레이션) · 정예진(RAG) · 심환석(연동·안정성) · 김인혜(시험·품질)
- 기간: 2026-11-05 ~ 2026-11-09 (제출 11/09 13:50)
- 스택: n8n 2.42.6, OpenAI gpt-4.1-mini, text-embedding-3-large, In-Memory Vector Store, 연습용 데이터 API
- 입구: `POST /webhook/ticketmoa-support` (Header `X-Team-Key`)

## 디렉터리

```
ticketmoa-repo/
├── README.md              # 이 파일 (실행 방법·웹훅 경로·시연 순서)
├── AGENTS.md              # 코딩 에이전트 규칙 (모두 먼저 읽기)
├── CLAUDE.md              # @AGENTS.md
├── docs/
│   ├── TOPIC.md           # 주제 제안서
│   ├── PLAN.md            # 기획서 (images/architecture.png)
│   ├── IMPLEMENTATION-PLAN.md  # 구현 순서·역할·하위 웹훅 계약
│   ├── PROMPTS.md         # 역할별 바이브코딩 프롬프트
│   ├── TODO.md
│   ├── TEAM-CHARTER.md    # (80일차에 작성)
│   ├── WORKFLOW-DESIGN.md # (구현 완료 후 작성) 산출물 1
│   ├── RAG-ARCHITECTURE.md# (구현 완료 후 작성) 산출물 2
│   ├── EXECUTION-RESULT.md# (구현 완료 후 작성) 산출물 3
│   ├── daily/             # 데일리 기록 80·81·82
│   └── images/
├── workflows/             # n8n JSON, 한 사람 = 한 파일, 키 없음
│   ├── ticketmoa-support.json   최두나
│   ├── ticketmoa-agents.json    최강현
│   ├── ticketmoa-refund.json    최강현
│   ├── ticketmoa-index.json     정예진
│   ├── ticketmoa-search.json    정예진
│   ├── ticketmoa-tech.json      정예진
│   ├── ticketmoa-payment.json   심환석
│   ├── ticketmoa-handoff.json   심환석
│   └── ticketmoa-errors.json    심환석
├── lib/
│   ├── common.js          # 공통 함수 원본 (Code 노드에 복사해서 씀)
│   ├── README.md          # 함수 목록·누가 어디서 쓰나
│   └── test/common.test.js
├── config/registry.json   # 업무 레지스트리 (Supervisor 프롬프트 재료)
├── config/ip-policy.json  # 가상 IP 국가·블랙리스트 (가산, TM-10~12)
├── knowledge/             # 지식 문서 8개 (staff-entry-manual만 관리자 전용)
├── data/                  # users.json 5명, records.json 5건 (가짜 데이터)
├── cases/                 # common.json(공통 14유형), team.json(팀 12개, TM-09~12는 가산)
├── requests/              # 시연·bench용 요청 파일
└── runs/                  # flow.py test·bench 보고서 (결과서 증거)
```

## 처음 받은 사람

```bash
git clone <저장소 주소> && cd ticketmoa-repo
node --test lib/test/*.test.js          # 공통 함수 테스트 (14개 통과해야 함)
```

n8n에서 손으로 할 것: Credential 3개(`OpenAI`, `ticketmoa-data-api`(X-Api-Key), `ticketmoa-team-key`(X-Team-Key)) 만들기, 워크플로우 활성화, `ticketmoa-index` 한 번 실행.

## 시험

```bash
uv run tools/flow.py push workflows/*.json
uv run tools/flow.py test cases/common.json --webhook ticketmoa-support -v
uv run tools/flow.py test cases/team.json -v
```

## 시연 순서 (발표)

1. WF-01 QR 문의 → 분류·검색·검증·근거  2. WF-02 보완 질문  3. WF-12 공연 10분 전 QR → 대체 입장 먼저 + 현장 알림
4. TM-02·03 환불 2단계  5. WF-04 티켓 API 장애 → DLQ·알림  6. `/logs`와 티켓 목록  7. 결과 표·실패 사례
