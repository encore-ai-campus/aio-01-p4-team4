# 티켓모아 실행 결과서 (EXECUTION-RESULT)

> 산출물 ③ (25점) · 작성 담당: **E 시험·품질 · 김인혜**
> 제출 기준 결과: **팀 VM, `main` `a5c80dc`, 공통 3회 50/51, 팀 13/13** (0절 A행)
> 측정일: 2026-11-04 ~ 2026-11-05
> **측정 환경 표기 안내**: 0절은 팀 VM 결과와 시험 기준표다. 1~6절은 **로컬(WSL · n8n 2.42.6 · 연습용 데이터 API) 측정치**이며 표마다 로컬로 표시했다. 환경과 코드 버전은 0절 표로 구분한다.

---

## 0. 시험 기준표 (버전 · 환경 · 결과)

**제출 기준 값은 A행이다.** 나머지 행은 경과 기록이고 서로 합치거나 비교하지 않는다. 문서 42청크는 `45bde9a`의 지식 문서, 33청크는 그 이전 문서다. 시각은 KST다. `runs/vm/` 보고서의 파일 이름 시각은 UTC다.

| | 환경 | 시각 | 코드 | 문서 | 가산 차단 | 공통 | 팀 (필수) | `bench -n 5` (WF-01 질문) | 보고서 |
| --- | --- | --- | --- | :---: | :---: | :---: | :---: | :---: | --- |
| **A** | **팀 VM** | **11/05 14:16~14:20** | **`main` `a5c80dc`** | **42** | **있음** | **50/51** (3회) | **13/13** (9/9, 1회) | **p50 5.50초, p95 5.77초** | `runs/vm/common-20261105-051822.json`, `team-20261105-051921.json`, `bench-ticketmoa-support-20261105-051948.json` |
| B | 팀 VM | 11/05 12:44~12:48 | `main` `445ba2d` | 42 | 없음 | 51/51 (3회) | 10/13 (9/9, 1회) | p50 5.45초, p95 6.00초 | `runs/vm/common-20261105-034700.json`, `team-20261105-034811.json`, `bench-ticketmoa-support-20261105-034838.json` |
| C | 로컬 (리드) | 11/05 14:04~14:07 | 브랜치 `support-guards` (`6f158de`와 같은 워크플로우) | 42 | 있음 | 49/51 (3회) | 13/13 (9/9, 1회) | 미측정 | `runs/common-20261105-140723.json`, `runs/team-20261105-140447.json` |
| D | 로컬 (E) | 11/05 12:32~12:35 | 커밋 기록 없음 (`2ad2849` 수정 포함으로 보임) | 42 | 없음 | 49/51 (3회) | 30/39 (27/27, 3회) | p50 4.61초, p95 5.15초 | 1~3절, 7절 |
| E | 로컬 (E) | 11/05 12:09~12:11 | 커밋 기록 없음 (`2ad2849` 수정 포함으로 보임) | 33 | 없음 | 17/17 (1회) | 10/13 (9/9, 1회) | 미측정 | 1~3절, 7절 |
| F | 로컬 (E) | 11/05 11:46 | 키 교체 전 출발점 | 미기록 | 없음 | 14/17 (1회) | 미측정 | 미측정 | `runs/common-20261105-114641.json` |

- C와 D는 숫자(49/51)가 같지만 다른 시험이다. 실패도 모두 WF-01이지만 회차가 다르다.
- 11/04 로컬 값(`d213d89`, 공통 17/17 3회)의 보고서는 저장소에 없다. 강사 안내대로 위 표와 섞지 않는다.

### 0.1 A행 공통 시나리오 (팀 VM, `a5c80dc`, 3회)

회차별 통과: 16/17, 17/17, 17/17.

| 케이스 | 통과 | 시간(초) | 실제 route · reason |
| --- | :---: | :---: | --- |
| WF-01 정상 문의 | 2/3 | 7.3 / 5.6 / 6.2 | 담당자 이관 `llm_unavailable`; 자동 답변 |
| WF-02 정보 부족 | 3/3 | 1.7 / 2.2 / 1.9 | 보완 질문 `low_confidence_or_missing` |
| WF-02b 보완 질문 한도 | 3/3 | 0.6 / 0.8 / 0.6 | 담당자 이관 `clarify_limit_reached` |
| WF-03 지식에 없음 | 3/3 | 3.9 / 3.8 / 4.4 | 담당자 이관 `writer_not_grounded` |
| WF-04 티켓 API 장애 | 3/3 | 5.0 / 4.4 / 4.8 | 담당자 이관 `writer_not_grounded`; 담당자 이관 `writer_not_in_context` |
| WF-05 권한 없는 문서 | 3/3 | 5.0 / 4.4 / 4.2 | 담당자 이관 `writer_not_in_context`; 담당자 이관 `writer_staff_only_terms` |
| WF-06 남의 건 | 3/3 | 0.5 / 0.5 / 0.5 | 권한 없음 `not_owner` |
| WF-07 개인정보 | 3/3 | 0.5 / 0.5 / 0.5 | 자동 답변 |
| WF-08 주입 | 3/3 | 0.1 / 0.2 / 0.1 | 차단 `injection_pattern` |
| WF-09 중복 요청 (1회째) | 3/3 | 2.0 / 2.0 / 2.6 | 담당자 이관 `payment_error_handoff` |
| WF-09 중복 요청 (2회째, 같은 request_id) | 3/3 | 2.4 / 2.0 / 2.1 | 담당자 이관 `payment_error_handoff` |
| WF-10 LLM 멈춤 | 3/3 | 1.1 / 1.0 / 0.8 | 담당자 이관 `agents_failed` |
| WF-11 느린 외부 API | 3/3 | 5.7 / 5.8 / 5.6 | 담당자 이관 `payment_failed` |
| WF-12 복합·긴급 | 3/3 | 3.9 / 3.7 / 4.6 | 담당자 이관 `urgent_entry` |
| WF-13 잘못된 입력 · 빈 질문 | 3/3 | 0.1 / 0.1 / 0.2 | HTTP 400 |
| WF-13 잘못된 입력 · 없는 사용자 | 3/3 | 0.1 / 0.1 / 0.1 | HTTP 400 |
| WF-13 잘못된 입력 · 501자 | 3/3 | 0.2 / 0.1 / 0.2 | HTTP 400 |

**실패 1건:** WF-01 1회차가 `llm_unavailable`로 이관됐다(7.3초, 분류 3.5초, `tech` 2.7초). `push`와 재색인 직후 첫 시험의 1회차다. 2·3회차와 `bench` 5회는 자동 답변으로 통과했다. 작성 모델 제한 2.5초에 걸린 것으로 보지만, n8n 실행 기록의 오류 메시지는 아직 확인하지 않았다.

### 0.2 A행 팀 시나리오 (팀 VM, `a5c80dc`, 1회)

| 케이스 | 통과 | 시간(초) | 실제 route · reason |
| --- | :---: | :---: | --- |
| TM-01 우리 유형의 정상 · 앱 로그인 | 1/1 | 6.0 | 자동 답변 |
| TM-02 환불 2단계 · 1차 (금액 안내) | 1/1 | 2.7 | 자동 답변 `refund_quote_pending_confirm` |
| TM-03 환불 2단계 · 2차 (확인 후 티켓) | 1/1 | 0.8 | 담당자 이관 `refund_confirmed` |
| TM-04 지나치게 막지 않음 | 1/1 | 2.0 | 담당자 이관 `customer_asked_human` |
| TM-05 이중결제 + 부정 감정 | 1/1 | 2.0 | 담당자 이관 `strong_negative_sentiment` |
| TM-06 경계 · 당일 취소 | 1/1 | 2.4 | 담당자 이관 `show_day_cancel` |
| TM-13 환불 30만원 초과 → 이관 | 1/1 | 2.7 | 담당자 이관 `over_limit` |
| TM-07 매크로 제한 문의 | 1/1 | 4.9 | 자동 답변 |
| TM-08 암표 신고 → 보안팀 이관 | 1/1 | 1.8 | 담당자 이관 `registry_handoff` |
| TM-09 반복 요청 차단 (6번째 요청) | 1/1 | 0.2 | 차단 `too_many_requests` |
| TM-10 해외 IP 차단 | 1/1 | 0.2 | 차단 `country_not_allowed` |
| TM-11 블랙리스트 IP 차단 | 1/1 | 0.2 | 차단 `macro_detected` |
| TM-12 국내 IP는 정상 처리 (과잉 차단 없음) | 1/1 | 5.6 | 자동 답변 |

`1~7절`의 표는 D·E·F행의 로컬 결과다. VM 값으로 바꾸지 않고 경과 기록으로 남긴다.

---

## 1. 전체 시험 결과 요약 (로컬 측정, `runs/` 기준)

### 1.1 시험 세트별 통과율 요약

| 구분 | 명령 | 11/04 로컬 (`d213d89`, 공유치) | 11/05 로컬 단회 (실측) | 11/05 로컬 3회 반복 (`--repeat 3`, 실측) | 근거 보고서 (`runs/`) |
| --- | --- | --- | --- | --- | --- |
| **공통 시나리오** (14유형 17케이스) | `flow.py test cases/common.json --webhook ticketmoa-support` | 17/17 × 3회 (51/51) | **17 / 17** (100.0%)<br>*(키 갱신 전 출발점: 14 / 17)* | **49 / 51** (96.1%)<br>*(1회차 17/17 · 2회차 16/17 · 3회차 16/17)* | `runs/common-20261105-114641.json` (출발점, 로컬)<br>`runs/common-20261105-121025.json` (단회, 로컬)<br>`runs/common-20261105-123211.json` (3회 반복, 로컬) |
| **팀 필수 시나리오** (`TM-01`~`08`, `TM-13` · 9케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 9/9, 9/9, 8/9 (26/27) | **9 / 9** (100.0%) | **27 / 27** (100.0%)<br>*(9/9 · 9/9 · 9/9)* | `runs/team-20261105-121121.json` (단회, 로컬)<br>`runs/team-20261105-123416.json` (3회 반복, 로컬) |
| **팀 가산 시나리오** (`TM-09`~`12` · 4케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 1/4 × 3회 (`TM-12` 통과) | **1 / 4** (`TM-12` 통과) | **3 / 12** (`TM-12` 3/3 통과, `TM-09`~`11` 미연결) | `runs/team-20261105-121121.json` (단회, 로컬)<br>`runs/team-20261105-123416.json` (3회 반복, 로컬) |
| **팀 전체 합계** (13케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 10/13, 10/13, 9/13 (29/39) | **10 / 13** (76.9%) | **30 / 39** (76.9%)<br>*(10/13 · 10/13 · 10/13)* | 위와 같음 |
| **장애 시나리오** (`WF-04`, `WF-10`, `WF-11`) | `common.json` 내 포함 | 3/3 × 3회 (9/9) | **3 / 3** (100.0%) | **9 / 9** (100.0%) | `runs/common-20261105-123211.json` (로컬) |

### 1.2 색인(`ticketmoa-index`) 실행 측정값 (로컬 측정)

`uv run --env-file .env tools/reindex.py` 실행 시 반환된 색인·검색 확인 실측값은 다음과 같다.

| 측정 시각 (로컬) | 전체 문서 | 일반 문서 (`all`) | 스태프 문서 (`staff`) | 청크 수 | 청크 길이 최소 / 중앙값 / 최대 (문자) | 색인 결과 (`outcome`) | 검색 확인 (`QR 입장`, `top_k: 3`) |
| --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| 2026-11-05 12:09 (로컬) | 8 / 8 | 7 | 1 | 33개 | 116 / 194 / 379 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |
| 2026-11-05 12:32 (로컬, 최신 `knowledge/` 반영) | 8 / 8 | 7 | 1 | 42개 | 116 / 229 / 432 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |

---

## 2. 시나리오별 상세 결과 (`runs/` 실측치, 로컬)

### 2.1 공통 시나리오 (`cases/common.json` · 14유형 17케이스)

- **단회 통합 보고서**: `runs/common-20261105-121025.json` (**17 / 17 통과**, 로컬)
- **3회 반복 보고서**: `runs/common-20261105-123211.json` (**49 / 51 통과**, 로컬)

| 케이스 | 기대 판정 (`expect`) | 단회 결과 (로컬) | 3회 반복 통과율 (로컬) | 3회 반복 소요 시간 (s, 로컬) | 실제 응답 `route` · 주요 필드 확인 (로컬) |
| --- | --- | :---: | :---: | :---: | --- |
| **WF-01 정상 문의** (`wf01`) | `자동 답변`, `sources` ⊃ `mobile-ticket-troubleshooting`, ≤ 8s | ✔ 통과 (6.0s) | **1 / 3** | 7.3s, 6.2s(✘), 6.3s(✘) | 단회 및 반복 #1은 `자동 답변`(`score: 0.63`) 통과. 반복 #2·#3은 `tech_ms` 2,657ms·2,647ms로 `작성 모델` 2.5초 timeout에 걸려 `담당자 이관`(`llm_unavailable`) 처리 (4절 실패 사례 2 참고) |
| **WF-02 정보 부족** (`wf02`) | `보완 질문` (`attempt: 1`) | ✔ 통과 (2.4s) | **3 / 3** | 2.5s, 2.2s, 1.7s | `route: "보완 질문"`, `confidence: 0.3`, `reason: "low_confidence_or_missing"` |
| **WF-02b 보완 질문 한도** (`wf02b`) | `담당자 이관`, `ticket` ⊃ `"T-"` (`attempt: 3`) | ✔ 통과 (0.8s) | **3 / 3** | 0.7s, 0.5s, 0.6s | `route: "담당자 이관"`, `llm_calls: 0`, `reason: "clarify_limit_reached"`, 티켓 `T-2001` 생성 |
| **WF-03 지식에 없음** (`wf03`) | `담당자 이관`, `sources: []`, `ticket` ⊃ `"T-"` | ✔ 통과 (4.3s) | **3 / 3** | 6.2s, 3.8s, 5.3s | `route: "담당자 이관"`, `sources: []`, `reason: "writer_not_grounded"`, 티켓 생성 |
| **WF-04 티켓 API 장애** (`wf04`) | HTTP 200, `담당자 이관`, `ticket: null` (`tickets: "error"`) | ✔ 통과 (5.2s) | **3 / 3** | 5.4s, 4.9s, 5.0s | `route: "담당자 이관"`, `ticket: null`, `handoff: {"dlq": true, "alert": true}` |
| **WF-05 권한 없는 문서** (`wf05`) | `sources`·`answer`에 `staff-entry-manual`·`책임자 코드`·`수기 모드` 미포함 | ✔ 통과 (5.1s) | **3 / 3** | 3.9s, 3.7s, 3.8s | 일반 고객(`박서준`, `access_level: "all"`) 검색 시 스태프 문서 사전 제외, 기밀 문구 노출 0건 |
| **WF-06 남의 건** (`wf06`) | `권한 없음`, 답변에 상태·타인 연락처 미포함 | ✔ 통과 (0.7s) | **3 / 3** | 0.4s, 0.4s, 0.5s | `route: "권한 없음"`, `reason: "not_owner"`, `llm_calls: 0`, 타인(`정민아`) 정보 미노출 |
| **WF-07 개인정보** (`wf07`) | 연락처 원문 미포함, `security.masked` ∈ `{1,2,3}` | ✔ 통과 (0.7s) | **3 / 3** | 0.5s, 0.7s, 0.6s | `route: "자동 답변"`, `010-****-3307`, `d***@example.com` 가림 (`security.masked: 2`) |
| **WF-08 주입** (`wf08`) | `차단`, `agents.llm_calls: 0` | ✔ 통과 (0.3s) | **3 / 3** | 0.2s, 0.2s, 0.2s | `route: "차단"`, `security.blocked_by: "rule"`, `reason: "injection_pattern"`, `llm_calls: 0` |
| **WF-09 중복 요청 (1회째)** (`wf09`) | `담당자 이관` | ✔ 통과 (2.1s) | **3 / 3** | 1.9s, 2.0s, 1.9s | `route: "담당자 이관"`, `category: "payment_error"`, 티켓 `T-2004` 생성 |
| **WF-09 중복 요청 (2회째)** (`wf09`) | `담당자 이관`, `ticket.duplicate: true` | ✔ 통과 (2.1s) | **3 / 3** | 1.8s, 1.8s, 1.5s | 동일 `request_id: "wf09"` 재요청 시 동일 티켓 번호 + `"duplicate": true` 반환 |
| **WF-10 LLM 멈춤** (`wf10`) | HTTP 200, `route` ≠ `"보완 질문"` (`llm: "down"`) | ✔ 통과 (1.5s) | **3 / 3** | 0.9s, 0.7s, 0.8s | OpenAI 키 장애 주입 시 HTTP 200 + `route: "담당자 이관"` (`reason: "agents_failed"`) |
| **WF-11 느린 외부 API** (`wf11`) | HTTP 200, ≤ 6s (`tickets: "slow"`, 8s 지연) | ✔ 통과 (5.6s) | **3 / 3** | 5.5s, 5.5s, 5.5s | 조회 2.2s 예산 타임아웃 후 이관 예산 내 종료 (`total_ms`: 5,424ms, `dlq: true`, `alert: true`) |
| **WF-12 복합·긴급** (`wf12`) | `담당자 이관`, `ticket.priority: "high"`, `sources` ⊃ `onsite-entry-fallback`, 답변에 `"현장 발권"`·`"접수"` | ✔ 통과 (3.6s) | **3 / 3** | 4.4s, 3.3s, 3.4s | `search ∥ payment` 병렬 실행, 대체 입장 안내 + `C-2002`(`"접수됨"`) 안내 + `priority: "high"` 티켓 + `venue-staff` 알림 |
| **WF-13 빈 질문** (`wf13a`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.1s, 0.1s, 0.2s | HTTP 400 `{"error": "invalid request", "codes": ["empty_question"]}` |
| **WF-13 없는 사용자** (`wf13b`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.2s, 0.1s, 0.1s | HTTP 400 `{"error": "invalid request", "codes": ["unknown_user"]}` |
| **WF-13 501자** (`wf13c`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.1s, 0.1s, 0.1s | HTTP 400 `{"error": "invalid request", "codes": ["question_too_long"]}` |

---

### 2.2 팀 시나리오 (`cases/team.json` · 필수 9개 + 가산 4개 = 13케이스)

- **단회 보고서**: `runs/team-20261105-121121.json` (**10 / 13 통과** — 필수 **9 / 9**, 가산 **1 / 4**, 로컬)
- **3회 반복 보고서**: `runs/team-20261105-123416.json` (**30 / 39 통과** — 필수 **27 / 27**, 가산 **3 / 12**, 로컬)

| 구분 | 케이스 | 기대 판정 (`expect`) | 단회 결과 (로컬) | 3회 반복 통과율 (로컬) | 3회 반복 소요 시간 (s, 로컬) | 실제 응답 `route` · 주요 필드 확인 (로컬) |
| :---: | --- | --- | :---: | :---: | :---: | --- |
| 필수 | **TM-01 앱 로그인** (`tm01`) | `자동 답변`, `sources` ⊃ `app-login-troubleshooting` | ✔ 통과 (4.6s) | **3 / 3** | 4.6s, 4.5s, 4.9s | `route: "자동 답변"`, `app-login-troubleshooting` (`score: 0.604`) |
| 필수 | **TM-02 환불 1차 (금액 안내)** (`tm02a`) | `자동 답변`, `ticket: null`, `sources` ⊃ `refund-policy` | ✔ 통과 (2.0s) | **3 / 3** | 2.1s, 1.9s, 2.2s | 수수료 0원·환불 예정액 `152,000원` 계산, `ticket: null`, `/cache`에 견적 저장 |
| 필수 | **TM-03 환불 2차 (확인 후 티켓)** (`tm02b`) | `담당자 이관`, `ticket` ⊃ `"T-"` (`confirm: true`) | ✔ 통과 (0.7s) | **3 / 3** | 0.7s, 0.6s, 0.5s | `llm_calls: 0`, `category: "refund"`, `reason: "refund_confirmed"`, 티켓 `T-2001` 생성 |
| 필수 | **TM-04 지나치게 막지 않음** (`tm04`) | `security.blocked_by: ""`, `route` ≠ `"차단"` | ✔ 통과 (1.6s) | **3 / 3** | 1.7s, 1.5s, 1.6s | `"시스템 점검"` 포함 문의 과잉 차단 없음 (`blocked_by: ""`, `담당자 이관`) |
| 필수 | **TM-05 이중결제 + 부정 감정** (`tm05`) | `담당자 이관`, `sources` ⊃ `payment-error-guide`, 취소 단정 문구 금지 | ✔ 통과 (1.8s) | **3 / 3** | 1.8s, 1.9s, 2.1s | `reason: "strong_negative_sentiment"`, `payment-error-guide` 근거 포함 이관 (`T-2003`) |
| 필수 | **TM-06 경계 · 당일 취소** (`tm06`) | `담당자 이관`, `sources` ⊃ `refund-policy` | ✔ 통과 (1.7s) | **3 / 3** | 1.8s, 1.8s, 1.8s | `reason: "show_day_cancel"`, `refund-policy` 근거 포함 이관 (`T-2004`) |
| 필수 | **TM-13 환불 30만원 초과 → 이관** (`tm13`) | `담당자 이관`, `sources` ⊃ `refund-policy`, `ticket` ⊃ `"T-"` | ✔ 통과 (2.2s) | **3 / 3** | 2.2s, 2.2s, 2.0s | `C-2006`(352,000원) 30만원 초과 감지로 1차 확인 없이 즉시 이관 (`reason: "over_limit"`, `T-2005`) |
| 필수 | **TM-07 매크로 제한 문의** (`tm07`) | `자동 답변`, `sources` ⊃ `fair-booking-policy`, 답변 ⊃ `"24시간"` | ✔ 통과 (4.3s) | **3 / 3** | 4.2s, 3.9s, 4.7s | `route: "자동 답변"`, `fair-booking-policy` (`score: 0.453`), `"24시간"` 자동 해제 안내 포함 |
| 필수 | **TM-08 암표 신고 → 보안팀 이관** (`tm08`) | `담당자 이관`, `ticket` ⊃ `"T-"` | ✔ 통과 (1.7s) | **3 / 3** | 1.4s, 1.5s, 1.4s | `category: "scalping_report"`, `reason: "registry_handoff"`, 티켓 `T-2006` 생성 |
| 가산 | **TM-09 반복 요청 차단 (6번째)** (`tm09`) | `차단`, `security.blocked_by: "rate_limit"` | ✘ 실패 (4.3s) | **0 / 3** | 3.9s, 3.6s, 5.0s | 가산 기능(`checkRateLimit`) 본체 미연결로 `자동 답변` 반환 |
| 가산 | **TM-10 해외 IP 차단** (`tm10`) | `차단`, `security.blocked_by: "geo"` | ✘ 실패 (1.3s) | **0 / 3** | 1.6s, 1.4s, 1.4s | 가산 기능(`checkIpPolicy`) 본체 미연결로 `보완 질문` 반환 |
| 가산 | **TM-11 블랙리스트 IP 차단** (`tm11`) | `차단`, `security.blocked_by: "ip_blocklist"` | ✘ 실패 (3.9s) | **0 / 3** | 4.7s, 4.4s, 3.9s | 가산 기능(`checkIpPolicy`) 본체 미연결로 `자동 답변` 반환 |
| 가산 | **TM-12 국내 IP 정상 처리** (`tm12`) | `자동 답변`, `security.blocked_by: ""` | ✔ 통과 (4.4s) | **3 / 3** | 4.5s, 4.7s, 4.1s | 국내 IP(`203.0.113.10`) 과잉 차단 없이 `자동 답변` 정상 반환 |

---

## 3. 응답 시간(`bench -n 5`) 및 실행 로그(`/logs`) 분석 (로컬 측정)

### 3.1 대표 요청 3종 `flow.py bench -n 5` 측정 결과 (로컬)

11/04 측정(`-n 3`, `WF-01` p50 6.1초)을 보완하여, 2026-11-05 로컬 환경에서 대표 요청 3종(`requests/wf01.json`, `requests/wf02.json`, `requests/wf12.json`)을 각각 **5회(`-n 5`)** 연속 측정한 결과다.

| 요청 파일 | 시나리오 유형 | 횟수 (`n`) | `p50` (로컬) | `p95` (로컬) | `max` (로컬) | 실패 수 | 5회 개별 측정값 (s, 로컬) | 근거 보고서 (`runs/`) |
| --- | --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| `requests/wf01.json` | 정상 기술 문의 (`자동 답변`, LLM 3회) | 5 | **4.61s** (`4.606s`) | **5.15s** (`5.149s`) | **5.15s** (`5.149s`) | 0 / 5 | `4.11`, `4.29`, `5.15`, `4.61`, `4.64` | `runs/bench-ticketmoa-support-20261105-123440.json` |
| `requests/wf02.json` | 정보 부족 (`보완 질문`, LLM 1회) | 5 | **1.26s** (`1.260s`) | **1.28s** (`1.279s`) | **1.28s** (`1.279s`) | 0 / 5 | `1.28`, `1.19`, `1.26`, `1.13`, `1.26` | `runs/bench-ticketmoa-support-20261105-123446.json` |
| `requests/wf12.json` | 복합·긴급 (`search ∥ payment` 병렬 + 긴급 이관, LLM 3회) | 5 | **3.38s** (`3.376s`) | **3.49s** (`3.492s`) | **3.49s** (`3.492s`) | 0 / 5 | `3.38`, `3.26`, `3.21`, `3.49`, `3.47` | `runs/bench-ticketmoa-support-20261105-123503.json` |

### 3.2 데이터 API `/logs?source=live` 집계 (로컬 110건 기준)

`common.json --repeat 3`(51건), `team.json --repeat 3`(39건 + `TM-09` 사전 호출 15건), `bench -n 5`(15건) 실행 동안 `POST /logs`에 기록된 **총 110건**(로컬)의 분포는 다음과 같다. 기록에 질문 원문·답변·이름·연락처는 포함되지 않음을 확인했다.

#### (1) 최종 `route` 및 상태 비율 (총 110건, 로컬)

| 구분 (`route` / `status`) | 건수 (로컬) | 비율 (%) | 비고 |
| --- | :---: | :---: | --- |
| `담당자 이관` | 53건 | 48.2% | 지식 없음, 결제 오류, 환불 확정/예외, 긴급 입장, 장애 폴백 등 |
| `자동 답변` | 31건 | 28.2% | QR·앱 로그인·매크로 문의, 본인 조회, 환불 1차 금액 안내 등 |
| `보완 질문` | 11건 | 10.0% | `WF-02` (3회 + bench 5회), `TM-10` (3회) |
| `권한 없음` | 3건 | 2.7% | `WF-06` 타인 건 조회 (3회) |
| `차단` | 3건 | 2.7% | `WF-08` 프롬프트 주입 규칙 차단 (3회) |
| `rejected` (HTTP 400) | 9건 | 8.2% | `WF-13a`·`13b`·`13c` 잘못된 입력 (3종 × 3회) |
| **합계** | **110건** | **100.0%** | — |

#### (2) 하위 웹훅 단계별 소요 시간 (`steps`, 로컬) 및 LLM 호출 수 (`llm_calls`)

| 측정 항목 | 호출 건수 (`n`) | `p50` (로컬) | `p95` (로컬) | `max` (로컬) | 비고 |
| --- | :---: | :---: | :---: | :---: | --- |
| `agents_ms` (`ticketmoa-agents`) | 98 | **1,119 ms** | **2,065 ms** | 2,254 ms | Supervisor 분류 (규칙 분기 시 14~200ms) |
| `search_ms` (`ticketmoa-search`) | 51 | **376 ms** | **1,058 ms** | 1,346 ms | OpenAI 임베딩 + In-Memory Vector Store 검색 |
| `tech_ms` (`ticketmoa-tech`) | 45 | **2,429 ms** | **3,015 ms** | 3,934 ms | 답변 작성 LLM + `ticketmoa-agents-verify` 검증 LLM 포함 |
| `handoff_ms` (`ticketmoa-handoff`) | 47 | **180 ms** | **3,037 ms** | 3,088 ms | 정상 시 ~180ms, `WF-04`·`WF-11` 장애 재시도 시 ~3,088ms |
| `payment_ms` (`ticketmoa-payment`) | 23 | **150 ms** | **2,147 ms** | 2,164 ms | 정상 시 ~150ms, `WF-11` 8초 지연 주입 시 ~2,164ms 타임아웃 |
| `refund_ms` (`ticketmoa-refund`) | 9 | **707 ms** | **982 ms** | 982 ms | 예매 조회 + 수수료 계산 + `/cache` 저장 또는 이관 |
| 요청당 `llm_calls` | 110 | **1회** | **3회** | 3회 (평균 **1.47회**) | 규칙 차단·400·보완한도·본인조회·환불확정은 `0회` |

---

## 4. 실패 사례 분석 및 조치·재시험 결과 (4건)

과제 요건(실패 사례 2건 이상, 원인·조치·재시험 결과 명시)에 따라 개발 및 시험 과정에서 발생한 4건의 실패 사례를 `runs/` 보고서 근거와 함께 기록한다.

### 사례 1 · OpenAI Credential 인증 실패(HTTP 401)로 인한 색인 누락 및 정상/보완/긴급 문의 이관 폴백

- **발생 시나리오**: `WF-01 정상 문의`, `WF-02 정보 부족`, `WF-12 복합·긴급` (출발점 시험 `14 / 17` 통과)
- **근거 보고서**: `runs/common-20261105-114641.json` (2026-11-05 11:46, 로컬)
- **증상**:
  - `WF-01`(기대: `자동 답변`), `WF-02`(기대: `보완 질문`), `WF-12`(기대: `priority: "high"` 및 `onsite-entry-fallback` 근거 포함) 3건 모두 HTTP 200과 함께 `route: "담당자 이관"`, `sources: []`, `ticket.priority: "normal"`, `agents.error: "llm_unavailable"`, `reason: "agents_failed"`를 반환하며 실패했다.
  - 동시에 `tools/reindex.py` 실행 시 `ticketmoa-search` 확인 단계에서 `일반 색인 False, 스태프 색인 False, error: "index_unavailable"`이 발생했다.
- **원인**:
  - `.env` 파일에 복사된 `OPENAI_API_KEY`가 만료·오타 상태(`HTTP 401 Incorrect API key provided`)였고, 주석 기호(`#`)가 빠진 설명 줄이 섞여 있어 환경 변수 로드 및 n8n `OpenAI (.env)`(`openAiCourse0001`) 인증이 실패했다.
  - 그 결과 LLM 호출 전 규칙으로 처리되는 14개 케이스(입력 검증, 주입 차단, `attempt: 3`, 예약번호/문의번호 정규식 기반 조회, 장애 폴백 등)는 통과했으나, LLM 분류와 임베딩이 필수인 3개 케이스는 fail-closed 설계에 따라 상담원 이관으로 빠졌다.
- **조치**:
  1. `.env`의 비변수 설명 줄을 주석(`#`) 처리하고 LF 개행으로 정리한 뒤 유효한 `OPENAI_API_KEY`(`GET /v1/models` HTTP 200 확인)로 교체했다.
  2. `Last3Mon/65/n8n/register-credentials.sh`로 `OpenAI (.env)` Credential을 재등록하고 n8n 컨테이너를 재시작해 메모리 내 Credential 캐시를 갱신한 뒤 `uv run --env-file .env tools/reindex.py`로 8개 문서 전체 색인을 완료했다.
- **재시험 결과**:
  - 재시험 보고서 `runs/common-20261105-121025.json`(로컬)에서 `WF-01`(`자동 답변`, `6.0s`), `WF-02`(`보완 질문`, `2.4s`), `WF-12`(`담당자 이관`, `priority: "high"`, `3.6s`)가 모두 통과하여 **17 / 17 전원 통과**를 확인했다.

### 사례 2 · `ticketmoa-tech` 답변 작성 모델의 짧은 타임아웃(2.5초) 및 콜드스타트로 인한 정상 문의 간헐적 실패

- **발생 시나리오**: `WF-01 정상 문의` (컨테이너 재시작 직후 단회 시험 및 `--repeat 3`의 #2·#3회차), `TM-07 매크로 제한 문의` (11/04 3회 반복 중 1회차)
- **근거 보고서**: `runs/common-20261105-123211.json` (2026-11-05 12:32, 로컬), 11/04 로컬 시험 기록(`docs/WORKFLOW-DESIGN.md` 4.6절)
- **증상**:
  1. 컨테이너 재시작 직후 첫 `WF-01` 호출 시 `route: "자동 답변"`과 `sources`는 정상 생성되었으나 전체 소요 시간이 `8.1s`(`total_ms: 6175ms`)로 측정되어 `expect.max_seconds: 8` 기준을 `0.1s` 초과했다.
  2. `common.json --repeat 3` 실행(`runs/common-20261105-123211.json`)에서 `WF-01` #1회차는 `7.3s`(`tech_ms: 3934ms`)로 통과했으나, #2회차(`6.2s`, `tech_ms: 2657ms`)와 #3회차(`6.3s`, `tech_ms: 2647ms`)는 분류(`intents: ["tech_issue"]`, `confidence: 0.95`)와 검색까지 성공하고도 `route: "담당자 이관"`, `sources: []`, `reason: "llm_unavailable"`로 실패했다.
  3. 11/04 로컬 시험에서도 `TM-07`이 3회 중 1회 동일하게 `reason: "llm_unavailable"`로 이관되었다.
- **원인**:
  - `workflows/ticketmoa-tech.json`의 `작성 모델`(`gpt-4.1-mini`) 노드에 `timeout: 2500`(2.5초)과 `maxRetries: 1`이 설정되어 있다.
  - OpenAI API 응답 시간이 2.5초를 소폭 초과하면(`tech_ms` 약 2.65초) 답변 생성 노드가 즉시 타임아웃 오류를 내고 `작성 실패 결과` 노드로 넘어가 `"reason": "llm_unavailable"`과 함께 `담당자 이관`으로 폴백된다. `/logs` 집계에서도 `tech_ms`의 `p50`이 `2,429ms`, `p95`가 `3,015ms`로 측정되어 2.5초 제한이 정상 응답의 중앙값 바로 위에 걸려 있음이 실측으로 입증되었다.
- **조치 및 재시험 결과**:
  - 웜업 상태에서 실행한 `runs/common-20261105-121025.json`에서는 `WF-01`이 `6.0s`(`total_ms: 5802ms`)로 통과했고, `runs/team-20261105-123416.json`에서는 `TM-07`이 3회 모두(`4.2s`, `3.9s`, `4.7s`) `자동 답변`으로 통과했다.
  - 또한 `bench -n 5` 측정(`runs/bench-ticketmoa-support-20261105-123440.json`)에서도 `WF-01`이 5회 연속 `자동 답변`으로 성공하며 **`p50 4.61s`, `p95 5.15s`, `failures 0/5`**를 기록했다.
  - **후속 권고 (C 담당 정예진 전달 사항)**: `ticketmoa-tech.json`의 `작성 모델` timeout을 `2500ms`에서 `3500~4000ms`(또는 `maxRetries: 0` + 단일 timeout `3800ms`)로 조정하면 본체 8초 제한 안에서 간헐적 `llm_unavailable` 이관을 근본적으로 방지할 수 있다.

### 사례 3 · 강한 불만 문의(`TM-05`) 이관 시 근거 문서(`sources`) 누락

- **발생 시나리오**: `TM-05 이중결제 + 부정 감정` (`"두 번 결제됐는데 진짜 짜증나네요. 154,000원이 두 번 빠져나갔어요"`)
- **근거 기록**: 2026-11-04 통합 시험 및 커밋 `d213d89` (`docs/daily/DAY80.md` 3절, `docs/TEAM-CHARTER.md` 6절)
- **증상**:
  - `TM-05`의 기대 결과는 `route: "담당자 이관"`이면서 동시에 `sources`에 `payment-error-guide`가 포함되어야 하나, 초기 통합 버전에서는 `sources: []`가 반환되어 실패했다.
- **원인**:
  - 본체(`ticketmoa-support`)의 `Plan route`에서 강한 부정 감정(`sentiment: "negative"` / `strong_negative_sentiment`)이나 관람 당일 취소(`show_day_cancel`)가 감지되면 지식 문서 검색(`ticketmoa-search`)을 거치지 않고 곧바로 `handoff` 분기로 보냈기 때문에 근거 문서가 비어 있었다.
- **조치**:
  - 커밋 `d213d89`에서 본체 `Route` 스위치에 `evidence_handoff` 갈래(`Call search (evidence)` → `Evidence handoff answer`)를 추가해, 강한 불만 문의나 당일 취소 문의도 해당 업무의 `kb_scope` 문서를 먼저 검색한 뒤 `sources`를 담아 `ticketmoa-handoff`로 넘기도록 수정했다.
- **재시험 결과**:
  - `runs/team-20261105-121121.json` 및 `runs/team-20261105-123416.json`(로컬 3회 반복)에서 `TM-05`(`1.8s`, `1.9s`, `2.1s`)와 `TM-06`(`1.8s`, `1.8s`, `1.8s`) 모두 **3 / 3 통과**했으며, `TM-05` 응답의 `sources`에 `payment-error-guide`(`score: 0.483`)가 정상 포함됨을 확인했다.

### 사례 4 · 가산 시나리오(`TM-09`~`TM-11`) 반복 요청 및 IP 차단 미연결

- **발생 시나리오**: `TM-09 반복 요청 차단 (6번째 요청)`, `TM-10 해외 IP 차단`, `TM-11 블랙리스트 IP 차단`
- **근거 보고서**: `runs/team-20261105-121121.json`, `runs/team-20261105-123416.json` (로컬)
- **증상**:
  - 기대값은 모두 `route: "차단"` 및 `security.blocked_by` 값(`"rate_limit"`, `"geo"`, `"ip_blocklist"`)이나, 실제 응답은 일반 문의와 동일하게 분류·답변 경로를 타서 `자동 답변`(`TM-09`, `TM-11`) 또는 `보완 질문`(`TM-10`)과 `security.blocked_by: ""`를 반환해 `0 / 3` 실패했다.
- **원인**:
  - `lib/common.js`의 `checkRateLimit`·`checkIpPolicy` 함수(단위 테스트 16/16 통과)와 `config/ip-policy.json`은 작성되어 있으나, 필수 시나리오 우선 원칙(`TODO.md` 3절·7절)에 따라 아직 본체(`workflows/ticketmoa-support.json`)의 입력 검사 뒤 노드로 연결하지 않은 상태다.
- **현재 상태 및 계획** (아래는 로컬 D행 시점 기록이다. 이후 `support`에 연결해 팀 VM A행에서 TM-09~11이 통과했다):
  - 국내 정상 IP(`203.0.113.10`)가 과잉 차단되지 않는지 확인하는 `TM-12`는 **3 / 3 통과**(`4.5s`, `4.7s`, `4.1s`)했다.
  - 팀 VM에서 필수 시나리오(공통 17개 + 팀 필수 9개) 통과를 확정한 뒤, `docs/PROMPTS.md` D 4단계 메모에 따라 본체 `Check input` 뒤·LLM 호출 전에 규칙 노드를 연결할지 리드(A)가 결정한다.

---

## 5. KSM-REQ 6절 체크리스트 (15개 항목 검증)

과제 요구사항 명세(KSM-REQ 6절)의 15개 필수 점검 항목에 대한 구현 위치와 `runs/` 실측 검증 결과는 다음과 같다.

| # | KSM-REQ 6절 체크리스트 항목 | 구현 워크플로우 · 노드 | 검증 시나리오 | 로컬 실측 결과 (`runs/`) | 충족 |
| :---: | --- | --- | --- | --- | :---: |
| 1 | **공통 Webhook 입구 및 Header Auth 인증**: `POST /webhook/ticketmoa-support` 단일 입구와 `X-Team-Key` Header Auth(`ticketmoa-team-key`) 적용, 공통 응답 9개 필드(`request_id`, `route`, `answer`, `sources`, `ticket`, `agents`, `security`, `timings`, `reason`) 준수 | `ticketmoa-support` · `Question webhook`, `Build response` | 전체 (WF-01~13, TM-01~13) | 전 케이스 응답 스키마 100% 일치 (`common-20261105-121025.json`) | ✔ |
| 2 | **입력 유효성 검증 (규칙)**: 빈 질문(`empty_question`), 미등록 사용자(`unknown_user`), 501자 이상(`question_too_long`) 요청 시 LLM 호출 전 HTTP 400 `{"error":"invalid request","codes":[...]}` 반환 | `ticketmoa-support` · `Get users` → `Check input` → `Reject invalid` | WF-13a, WF-13b, WF-13c | 3종 × 3회 = **9 / 9 통과** (HTTP 400, 0.1~0.2s, `llm_calls: 0`) | ✔ |
| 3 | **프롬프트 주입(Injection) 사전 차단**: `"이전 지시 무시"`, `"시스템 프롬프트"` 등 주입 패턴을 LLM 호출 전 규칙으로 차단(`route: "차단"`, `security.blocked_by: "rule"`, `llm_calls: 0`)하고 정상 문의는 과잉 차단하지 않음 | `ticketmoa-support` · `Injection rules` → `Blocked answer` | WF-08, TM-04, TM-12 | WF-08 **3 / 3 통과** (`0.2s`, `llm_calls: 0`), TM-04·TM-12 **6 / 6 통과** | ✔ |
| 4 | **업무 레지스트리 기반 Supervisor 분류 및 Fail-Closed**: `config/registry.json`을 읽어 Structured Output JSON으로 의도·신뢰도·긴급도·감정을 분류하고, 파싱 실패·오류 시 `담당자 이관`으로 안전 폴백 | `ticketmoa-support` · `Load registry`, `ticketmoa-agents` · `Supervisor 분류`, `분류 결과 검사` | WF-01, WF-10, TM-01~08 | 정상 분류 및 LLM 장애 시 fail-closed 이관 확인 | ✔ |
| 5 | **보완 질문 루프 및 반복 한도 이관**: 정보 부족·저신뢰(`confidence < 0.7` 또는 필수 슬롯 누락) 시 `보완 질문`으로 되묻고, `attempt >= 3`이면 LLM 호출 없이 즉시 `담당자 이관` | `ticketmoa-agents` · `LLM 필요?`, `ticketmoa-support` · `Plan route` | WF-02 (`attempt: 1`), WF-02b (`attempt: 3`) | WF-02 **3 / 3 통과** (`보완 질문`), WF-02b **3 / 3 통과** (`llm_calls: 0`, 티켓 생성) | ✔ |
| 6 | **문서 품질 검사 및 권한 분리 색인**: `knowledge/*.md` 8개 문서를 `##` 절 단위로 청킹하고,色인 전 품질 검사(절 개수·`access_level`·빈 절·연락처 포함 여부) 후 `ticketmoa_kb_v1_all`과 `ticketmoa_kb_v1_staff`로 분리 저장 | `ticketmoa-index` · `Validate and make chunks`, `Store public chunks`, `Store staff chunks` | `tools/reindex.py` | 문서 8/8 (일반 7, 스태프 1), `issues: []`, `store_output_received` 확인 | ✔ |
| 7 | **검색 전 문서 권한 필터링 (Pre-filtering)**: 질문 문구가 아니라 조회된 사용자의 `access_level`로 검색 대상 메모리 키를 결정하여 일반 고객(`all`) 검색 시 스태프 전용 문서(`staff-entry-manual`) 원천 배제 | `ticketmoa-search` · `검색 준비`, `스태프 권한?` | WF-05 | WF-05 **3 / 3 통과** (`staff-entry-manual` 및 `책임자 코드`·`수기 모드` 노출 0건) | ✔ |
| 8 | **근거 기반 RAG 답변 및 무근거 추측 금지**: 검색된 문서(`hits`) 범위 안에서만 답변과 `sources`를 작성하고, 지식 문서에 근거가 없는 질문은 지어내지 않고 `담당자 이관`(`sources: []`) 처리 | `ticketmoa-tech` · `답변 작성`, `작성 결과 검사` | WF-01, WF-03, TM-01, TM-07 | WF-03 **3 / 3 통과** (`route: "담당자 이관"`, `sources: []`, `writer_not_grounded`) | ✔ |
| 9 | **검증 Agent(Reviewer) 다중 점검**: 작성된 답변이 검색 근거(`hits`) 내에 있는지, 환불·취소 직접 실행 주장이 없는지, 개인정보가 없는지 검증하고 미통과 시 `담당자 이관` 처리 | `ticketmoa-tech` · `검증 호출` → `ticketmoa-agents` · `검증 Agent` (`/webhook/ticketmoa-agents-verify`) | WF-01, WF-12, TM-01, TM-07 | 정상 답변 시 `llm_calls: 3`(분류+작성+검증)으로 검증 통과 확인 | ✔ |
| 10 | **본인 건만 조회 (소유권 검증)**: 예매·문의 조회(`GET /tickets/<id>?requester=`) 시 요청 `user`와 기록 소유자가 다르면 HTTP 403을 받아 `route: "권한 없음"`으로 응답하고 내용 노출 차단 | `ticketmoa-payment` · `본인 건 조회`, `조회 판정` | WF-06, WF-07 | WF-06 **3 / 3 통과** (`route: "권한 없음"`, `reason: "not_owner"`, 타인 정보 노출 0건) | ✔ |
| 11 | **개인정보(PII) 마스킹 및 가림 개수 기록**: 응답 본문·티켓 요약·로그에서 전화번호와 이메일을 마스킹(`010-****-xxxx`, `x***@example.com`)하고 가린 개수를 `security.masked`에 기록 | `ticketmoa-payment`, `ticketmoa-support` · `maskPII` (`lib/common.js`) | WF-07, WF-12 | WF-07 **3 / 3 통과**, WF-12 **3 / 3 통과** (원문 노출 0건, `security.masked: 2`) | ✔ |
| 12 | **환불 2단계 고객 확인 및 예외 즉시 이관**: 에이전트가 직접 취소를 실행하지 않고 1차에 수수료·환불 예정액 안내(`ticket: null`), 2차 `context.confirm === true` 확인 시에만 환불 티켓 생성. 30만원 초과·당일 취소는 즉시 이관 | `ticketmoa-refund` · `calcRefund`, `/cache`, `ticketmoa-support` · `Refund confirm?` | TM-02, TM-03, TM-06, TM-13 | TM-02·03·06·13 각 **3 / 3 (총 12 / 12) 통과**, 미확인 티켓 생성 0건 | ✔ |
| 13 | **복합·긴급 문의 병렬 처리 및 현장 알림**: 공연 30분 이내 입장 장애와 문의 조회가 결합된 복합 문의 시 `search ∥ payment` 병렬 호출로 대체 입장 안내(`onsite-entry-fallback`) + 조회 결과 + 긴급 티켓(`priority: "high"`) + 현장 알림(`venue-staff`) 처리 | `ticketmoa-support` · `Call search ∥`, `Call payment ∥`, `Merge search + lookup`, `ticketmoa-tech` | WF-12 | WF-12 **3 / 3 통과** (`3.3~4.4s`), `bench -n 5` **p50 3.38s** (5/5 통과) | ✔ |
| 14 | **외부 API·LLM 장애 격리, 선택적 재시도, 중복 방지, DLQ·알림**: timeout 설정 및 429·5xx·timeout만 재시도(401·403 제외), 티켓 API 장애 시 `ticket: null` + `/dlq` + `/alerts` 기록(HTTP 200 유지), `key=request_id`로 중복 티켓 방지(`duplicate: true`), `ticketmoa-errors` Error Workflow 구성 | `ticketmoa-handoff`, `ticketmoa-payment`, `ticketmoa-errors`, `ticketmoa-support` | WF-04, WF-09(1·2차), WF-10, WF-11 | WF-04·09·10·11 총 **15 / 15 통과** (500 에러 0건, `WF-11` 5.5s ≤ 6s) | ✔ |
| 15 | **비식별 실행 로그(`/logs`) 기록 및 비밀키 분리**: 응답 직전 `POST /logs`에 `request_id`, `route`, `intents`, `steps`, `llm_calls`, `has_ticket`, `blocked_by`, `masked`, `status`, `duration_ms`만 기록(질문 원문·연락처 제외)하고 저장소 내 API 키·토큰 노출 0건 유지 | `ticketmoa-support` · `Log record` → `POST /logs`, n8n Credentials | `/logs?source=live` (110건), `flow.py check` | `/logs` 110건 원문·PII 노출 0건 확인, Credential 고정 ID 사용 확인 | ✔ |

---

## 6. 시나리오 파일(`cases/`, `requests/`) 검토 결과

담당 파일인 `cases/common.json`, `cases/team.json`, `cases/README.md`, `requests/*.json`을 전수 검토한 결과는 다음과 같다.

1. **`cases/common.json` (14유형 17케이스)**:
   - `expect` 조건은 과제 공통 기준과 정확히 일치하며 일절 수정하지 않았다.
   - 질문 문구도 실제 고객센터 문의 말투(`"모바일티켓 QR이 회색으로만 나오고 안 떠요. 어떻게 해야 하나요?"`, `"공연 10분 전인데 모바일티켓 QR이 안 떠요! 어제 문의한 C-2002도 어떻게 됐는지 확인해 주세요"` 등)로 자연스럽게 작성되어 있어 추가 수정 없이 그대로 유지하는 것이 안전하다.
2. **`cases/team.json` (13케이스: 필수 9 + 가산 4)**:
   - `TM-01`~`TM-08`, `TM-13`(필수 9개)은 `data/records.json`(`C-2001`~`C-2006`) 및 `knowledge/*.md` 8개 문서와 정합성이 맞고, 3회 반복 시험에서 **27 / 27 전원 통과**했다.
   - `TM-09`~`TM-12`(가산 4개)는 `context.client_ip`에 RFC 5737 문서용 예약 대역(`198.51.100.7`, `203.0.113.66`, `203.0.113.10`)만 사용하여 실제 개인정보·외부 IP 없이 시연 가능하도록 설계되어 있다.
3. **`requests/wf01.json`, `requests/wf02.json`, `requests/wf12.json`**:
   - 시연 및 `flow.py bench` 측정용 요청 본문으로, `cases/common.json`의 `WF-01`, `WF-02`, `WF-12` 요청과 동일하며 `bench -n 5`에서 모두 정상 동작함을 확인했다.

---

## 7. 보관된 실행 보고서 목록 (`runs/`)

| 파일명 | 측정 시각 (KST) | 환경 | 실행 명령 | 결과 요약 |
| --- | --- | :---: | --- | --- |
| `runs/vm/common-20261105-051822.json` | 2026-11-05 14:18 | **VM** | `flow.py test cases/common.json --webhook ticketmoa-support --repeat 3` | **50 / 51** (A행) |
| `runs/vm/team-20261105-051921.json` | 2026-11-05 14:19 | **VM** | `flow.py test cases/team.json` | **13 / 13** (A행) |
| `runs/vm/bench-ticketmoa-support-20261105-051948.json` | 2026-11-05 14:19 | **VM** | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | **p50 5.50s · p95 5.77s** · 실패 0/5 (A행) |
| `runs/vm/common-20261105-034700.json` | 2026-11-05 12:47 | VM | 공통 3회 | 51 / 51 (B행) |
| `runs/vm/team-20261105-034811.json` | 2026-11-05 12:48 | VM | 팀 1회 | 10 / 13 (B행) |
| `runs/vm/bench-ticketmoa-support-20261105-034838.json` | 2026-11-05 12:48 | VM | `bench -n 5` | p50 5.45s · p95 6.00s (B행) |
| `runs/common-20261105-140723.json` | 2026-11-05 14:07 | 로컬 | 공통 3회 | 49 / 51 (C행) |
| `runs/team-20261105-140447.json` | 2026-11-05 14:04 | 로컬 | 팀 1회 | 13 / 13 (C행) |
| `runs/common-20261105-114641.json` | 2026-11-05 11:46:41 | 로컬 | `flow.py test cases/common.json --webhook ticketmoa-support -v` | **14 / 17** (OpenAI 키 교체 전 출발점, 실패 사례 1 증거) |
| `runs/common-20261105-121025.json` | 2026-11-05 12:10:25 | 로컬 | `flow.py test cases/common.json --webhook ticketmoa-support -v` | **17 / 17** (공통 시나리오 전원 통과) |
| `runs/common-20261105-123211.json` | 2026-11-05 12:32:11 | 로컬 | `flow.py test cases/common.json --webhook ticketmoa-support --repeat 3` | **49 / 51** (16케이스 3/3, `WF-01` 1/3 — 실패 사례 2 증거) |
| `runs/team-20261105-121121.json` | 2026-11-05 12:11:21 | 로컬 | `flow.py test cases/team.json --webhook ticketmoa-support -v` | **10 / 13** (팀 필수 **9 / 9**, 가산 1 / 4) |
| `runs/team-20261105-123416.json` | 2026-11-05 12:34:16 | 로컬 | `flow.py test cases/team.json --webhook ticketmoa-support --repeat 3` | **30 / 39** (팀 필수 **27 / 27**, 가산 3 / 12) |
| `runs/bench-ticketmoa-support-20261105-123440.json` | 2026-11-05 12:34:40 | 로컬 | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | **p50 4.61s · p95 5.15s** · max 5.15s · 실패 0/5 |
| `runs/bench-ticketmoa-support-20261105-123446.json` | 2026-11-05 12:34:46 | 로컬 | `flow.py bench ticketmoa-support requests/wf02.json -n 5` | **p50 1.26s · p95 1.28s** · max 1.28s · 실패 0/5 |
| `runs/bench-ticketmoa-support-20261105-123503.json` | 2026-11-05 12:35:03 | 로컬 | `flow.py bench ticketmoa-support requests/wf12.json -n 5` | **p50 3.38s · p95 3.49s** · max 3.49s · 실패 0/5 |
