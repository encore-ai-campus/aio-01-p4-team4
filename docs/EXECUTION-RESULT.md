# 티켓모아 실행 결과서 (EXECUTION-RESULT)

> 산출물 ③ (25점) · 작성 담당: **E 시험·품질 · 김인혜**
> 제출 기준 결과: **팀 VM, `main` `a5c80dc`, 공통 3회 50/51, 팀 13/13** (0절 A행). 시험별 코드·문서 버전은 0절 표를 따른다.
> 측정일: 2026-11-04 ~ 2026-11-05
> **측정 환경 및 출처 표기 안내**: 본 문서의 수치는 `runs/`(로컬 WSL `AIO`) 및 `runs/vm/`(팀 VM `aio-t4`) 디렉터리에 저장된 실행 보고서 JSON 실측값을 기본으로 사용하며, **로컬 측정치**와 **팀 VM 측정치**를 열로 구분해 섞지 않는다. `runs/` 보고서 파일 밖의 값(11/04 팀 공유치, `tools/reindex.py` 터미널 출력, 로컬 첫 호출 `8.1s`, 로컬 `GET /logs?source=live` 120건 메모리 조회)은 각 표와 본문에 출처를 별도로 명시한다.

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

1~7절 표의 **로컬** 열은 D·E·F행이고, **팀 VM** 열은 가산 차단을 넣기 전인 B행(`445ba2d`)이다. 경과 기록으로 남기며, 최신 VM 값은 이 절의 A행을 본다.

---

## 1. 전체 시험 결과 요약 (`runs/` 및 `runs/vm/` 기준)

이 절부터 7절까지의 **팀 VM** 값은 가산 차단을 넣기 전 B행(`445ba2d`)이다. 최신 값은 0절 A행(`a5c80dc`)이다.

### 1.1 시험 세트별 통과율 요약

| 구분 | 명령 | 11/04 로컬 (`d213d89`, 33청크, 팀 공유치*) | 11/05 로컬 단회 (커밋 기록 없음, **33청크**, 실측) | 11/05 로컬 3회 반복 (`45bde9a`, **42청크**, 실측) | **11/05 팀 VM (`445ba2d`, 42청크, 실측)** | 근거 보고서 (`runs/` · `runs/vm/`) |
| --- | --- | --- | --- | --- | --- | --- |
| **공통 시나리오** (14유형 17케이스) | `flow.py test cases/common.json --webhook ticketmoa-support` | 17/17 × 3회 (51/51) | **17 / 17** (100.0%, **33청크**)<br>*(키 갱신 전 출발점: 14 / 17)* | **49 / 51** (96.1%, **42청크**)<br>*(1회차 17/17 · 2회차 16/17 · 3회차 16/17)* | **51 / 51** (100.0%, **3회 반복**)<br>*(17/17 · 17/17 · 17/17, **42청크**)* | 로컬: `runs/common-20261105-114641.json` (출발점)<br>로컬(33청크): `runs/common-20261105-121025.json`<br>로컬(42청크): `runs/common-20261105-123211.json`<br>**VM(42청크)**: `runs/vm/common-20261105-034700.json` |
| **팀 필수 시나리오** (`TM-01`~`08`, `TM-13` · 9케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 9/9, 9/9, 8/9 (26/27) | **9 / 9** (100.0%, **33청크**) | **27 / 27** (100.0%, **42청크**)<br>*(9/9 · 9/9 · 9/9)* | **9 / 9** (100.0%, **1회**, **42청크**) | 로컬(33청크): `runs/team-20261105-121121.json`<br>로컬(42청크): `runs/team-20261105-123416.json`<br>**VM(42청크)**: `runs/vm/team-20261105-034811.json` |
| **팀 가산 시나리오** (`TM-09`~`12` · 4케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 1/4 × 3회 (`TM-12` 통과) | **1 / 4** (`TM-12` 통과, **33청크**) | **3 / 12** (`TM-12` 3/3 통과, `TM-09`~`11` 미연결, **42청크**) | **1 / 4** (`TM-12` 통과, `TM-09`~`11` 미연결, **1회**) | 위와 같음 *(가산 연결 후 로컬 단회 `13/13`은 `runs/team-20261105-140447.json` 참고)* |
| **팀 전체 합계** (13케이스) | `flow.py test cases/team.json --webhook ticketmoa-support` | 10/13, 10/13, 9/13 (29/39) | **10 / 13** (76.9%, **33청크**) | **30 / 39** (76.9%, **42청크**)<br>*(10/13 · 10/13 · 10/13)* | **10 / 13** (76.9%, **1회**, **42청크**) | 위와 같음 |
| **장애 시나리오** (`WF-04`, `WF-10`, `WF-11`) | `common.json` 내 포함 | 3/3 × 3회 (9/9) | **3 / 3** (100.0%, **33청크**) | **9 / 9** (100.0%, **42청크**) | **9 / 9** (100.0%, **3회 반복**, **42청크**) | 로컬: `runs/common-20261105-123211.json`<br>**VM**: `runs/vm/common-20261105-034700.json` |
| **정상 문의 `bench -n 5`** (`requests/wf01.json`) | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | p50 `6.1s` (`-n 3`, `d213d89` 이전*) | — | **p50 4.61s · p95 5.15s** · 실패 0/5 (**42청크**) | **p50 5.45s · p95 6.00s** · 실패 0/5 (**42청크**) | 로컬: `runs/bench-ticketmoa-support-20261105-123440.json`<br>**VM**: `runs/vm/bench-ticketmoa-support-20261105-034838.json` |

> **\*11/04 로컬 값 출처 안내**: 11/04 수치(공통 `51/51`, 팀 `29/39`, `bench -n 3` p50 `6.1s`)는 `runs/` 디렉터리에 JSON 보고서 파일이 보관되어 있지 않으며, 리드(A)가 측정해 `docs/WORKFLOW-DESIGN.md` 4.6절 및 `docs/daily/DAY80.md` 1절에 기록한 공유치다. 또한 `runs/vm/` 파일명의 시각(`034700` 등)은 VM 서버 UTC 시각이며 한국 시각(KST)으로는 2026-11-05 12:47~12:48이다.

### 1.2 색인(`ticketmoa-index`) 실행 측정값

`uv run --env-file .env tools/reindex.py` 실행 시 터미널 표준출력으로 반환된 색인·검색 확인 값(출처: `reindex.py` 실행 콘솔 출력 및 `docs/RAG-ARCHITECTURE.md` 1절·5.1절, `runs/` 보고서 파일 아님)은 다음과 같다.

| 측정 시각 · 환경 | 전체 문서 | 일반 문서 (`all`) | 스태프 문서 (`staff`) | 청크 수 | 청크 길이 최소 / 중앙값 / 최대 (문자) | 색인 결과 (`outcome`) | 검색 확인 (`QR 입장`, `top_k: 3`) |
| --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| 2026-11-05 12:09 (로컬, 기존 문서) | 8 / 8 | 7 | 1 | **33개** | 116 / 194 / 379 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |
| 2026-11-05 12:32 (로컬, 정제본 `45bde9a`) | 8 / 8 | 7 | 1 | **42개** | 116 / 229 / 432 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |
| 2026-11-05 12:44 (**팀 VM `445ba2d`**, 정제본 `45bde9a`) | 8 / 8 | 7 | 1 | **42개** | 116 / 229 / 432 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |
| 2026-11-05 14:16 (**팀 VM `a5c80dc`**, 정제본 `45bde9a`) | 8 / 8 | 7 | 1 | **42개** | 116 / 229 / 432 | `store_output_received` | 일반 `True`, 스태프 `True`, 결과 3건 |

---

## 2. 시나리오별 상세 결과 (`runs/` 로컬 및 `runs/vm/` 팀 VM 실측치)

### 2.1 공통 시나리오 (`cases/common.json` · 14유형 17케이스)

- **로컬 단회 보고서 (33청크)**: `runs/common-20261105-121025.json` (**17 / 17 통과**)
- **로컬 3회 반복 보고서 (42청크)**: `runs/common-20261105-123211.json` (**49 / 51 통과**)
- **팀 VM 3회 반복 보고서 (`445ba2d`, 42청크)**: `runs/vm/common-20261105-034700.json` (**51 / 51 통과**)

| 케이스 | 기대 판정 (`expect`) | 로컬 단회 (**33청크**) | 로컬 3회 반복 (**42청크**) | 로컬 3회 시간 (s, **42청크**) | **팀 VM 3회 반복 (`445ba2d`, 42청크)** | **팀 VM 3회 시간 (s)** | 실제 응답 `route` · 주요 필드 확인 |
| --- | --- | :---: | :---: | :---: | :---: | :---: | --- |
| **WF-01 정상 문의** (`wf01`) | `자동 답변`, `sources` ⊃ `mobile-ticket-troubleshooting`, ≤ 8s | ✔ 통과 (6.0s) | **1 / 3** | 7.3s, 6.2s(✘), 6.3s(✘) | **3 / 3** | **6.6s, 6.8s, 6.1s** | VM 3회 모두 `자동 답변`(`score: 0.63`) 통과. 로컬 42청크 반복 #2·#3은 `reason: "llm_unavailable"`로 `담당자 이관` (4절 사례 3 참고) |
| **WF-02 정보 부족** (`wf02`) | `보완 질문` (`attempt: 1`) | ✔ 통과 (2.4s) | **3 / 3** | 2.5s, 2.2s, 1.7s | **3 / 3** | **1.8s, 1.7s, 1.5s** | `route: "보완 질문"`, `confidence: 0.3`, `reason: "low_confidence_or_missing"` |
| **WF-02b 보완 질문 한도** (`wf02b`) | `담당자 이관`, `ticket` ⊃ `"T-"` (`attempt: 3`) | ✔ 통과 (0.8s) | **3 / 3** | 0.7s, 0.5s, 0.6s | **3 / 3** | **0.6s, 0.6s, 0.6s** | `route: "담당자 이관"`, `llm_calls: 0`, `reason: "clarify_limit_reached"`, 티켓 `T-2001` 생성 |
| **WF-03 지식에 없음** (`wf03`) | `담당자 이관`, `sources: []`, `ticket` ⊃ `"T-"` | ✔ 통과 (4.3s) | **3 / 3** | 6.2s, 3.8s, 5.3s | **3 / 3** | **3.9s, 4.0s, 4.6s** | `route: "담당자 이관"`, `sources: []`, `reason: "writer_not_grounded"`, 티켓 생성 |
| **WF-04 티켓 API 장애** (`wf04`) | HTTP 200, `담당자 이관`, `ticket: null` (`tickets: "error"`) | ✔ 통과 (5.2s) | **3 / 3** | 5.4s, 4.9s, 5.0s | **3 / 3** | **5.0s, 5.1s, 5.0s** | `route: "담당자 이관"`, `ticket: null`, `handoff: {"dlq": true, "alert": true}` |
| **WF-05 권한 없는 문서** (`wf05`) | `sources`·`answer`에 `staff-entry-manual`·`책임자 코드`·`수기 모드` 미포함 | ✔ 통과 (5.1s) | **3 / 3** | 3.9s, 3.7s, 3.8s | **3 / 3** | **4.8s, 4.9s, 4.7s** | 일반 고객(`박서준`, `access_level: "all"`) 검색 시 스태프 문서 사전 제외, 기밀 문구 노출 0건 |
| **WF-06 남의 건** (`wf06`) | `권한 없음`, 답변에 상태·타인 연락처 미포함 | ✔ 통과 (0.7s) | **3 / 3** | 0.4s, 0.4s, 0.5s | **3 / 3** | **0.7s, 0.7s, 0.6s** | `route: "권한 없음"`, `reason: "not_owner"`, `llm_calls: 0`, 타인(`정민아`) 정보 미노출 |
| **WF-07 개인정보** (`wf07`) | 연락처 원문 미포함, `security.masked` ∈ `{1,2,3}` | ✔ 통과 (0.7s) | **3 / 3** | 0.5s, 0.7s, 0.6s | **3 / 3** | **0.5s, 0.4s, 0.5s** | `route: "자동 답변"`, `010-****-3307`, `d***@example.com` 가림 (`security.masked: 2`) |
| **WF-08 주입** (`wf08`) | `차단`, `agents.llm_calls: 0` | ✔ 통과 (0.3s) | **3 / 3** | 0.2s, 0.2s, 0.2s | **3 / 3** | **0.1s, 0.2s, 0.1s** | `route: "차단"`, `security.blocked_by: "rule"`, `reason: "injection_pattern"`, `llm_calls: 0` |
| **WF-09 중복 요청 (1회째)** (`wf09`) | `담당자 이관` | ✔ 통과 (2.1s) | **3 / 3** | 1.9s, 2.0s, 1.9s | **3 / 3** | **2.2s, 2.2s, 2.2s** | `route: "담당자 이관"`, `category: "payment_error"`, 티켓 `T-2004` 생성 |
| **WF-09 중복 요청 (2회째)** (`wf09`) | `담당자 이관`, `ticket.duplicate: true` | ✔ 통과 (2.1s) | **3 / 3** | 1.8s, 1.8s, 1.5s | **3 / 3** | **1.9s, 2.1s, 2.3s** | 동일 `request_id: "wf09"` 재요청 시 동일 티켓 번호 + `"duplicate": true` 반환 |
| **WF-10 LLM 멈춤** (`wf10`) | HTTP 200, `route` ≠ `"보완 질문"` (`llm: "down"`) | ✔ 통과 (1.5s) | **3 / 3** | 0.9s, 0.7s, 0.8s | **3 / 3** | **1.2s, 0.8s, 0.7s** | OpenAI 키 장애 주입 시 HTTP 200 + `route: "담당자 이관"` (`reason: "agents_failed"`) |
| **WF-11 느린 외부 API** (`wf11`) | HTTP 200, ≤ 6s (`tickets: "slow"`, 8s 지연) | ✔ 통과 (5.6s) | **3 / 3** | 5.5s, 5.5s, 5.5s | **3 / 3** | **5.6s, 5.6s, 5.5s** | 조회 2.2s 예산 타임아웃 후 이관 예산 내 종료 (`dlq: true`, `alert: true`) |
| **WF-12 복합·긴급** (`wf12`) | `담당자 이관`, `ticket.priority: "high"`, `sources` ⊃ `onsite-entry-fallback`, 답변에 `"현장 발권"`·`"접수"` | ✔ 통과 (3.6s) | **3 / 3** | 4.4s, 3.3s, 3.4s | **3 / 3** | **4.9s, 4.2s, 3.8s** | `2ad2849` 반영 후 `search ∥ payment` 병렬 실행, 대체 입장 안내 + `C-2002`(`"접수됨"`) 안내 + `priority: "high"` 티켓 + `venue-staff` 알림 (4절 사례 1 참고) |
| **WF-13 빈 질문** (`wf13a`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.1s, 0.1s, 0.2s | **3 / 3** | **0.1s, 0.1s, 0.2s** | HTTP 400 `{"error": "invalid request", "codes": ["empty_question"]}` |
| **WF-13 없는 사용자** (`wf13b`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.2s, 0.1s, 0.1s | **3 / 3** | **0.2s, 0.2s, 0.2s** | HTTP 400 `{"error": "invalid request", "codes": ["unknown_user"]}` |
| **WF-13 501자** (`wf13c`) | HTTP 400, `error` ⊃ `"invalid request"` | ✔ 통과 (0.1s) | **3 / 3** | 0.1s, 0.1s, 0.1s | **3 / 3** | **0.2s, 0.2s, 0.2s** | HTTP 400 `{"error": "invalid request", "codes": ["question_too_long"]}` |

---

### 2.2 팀 시나리오 (`cases/team.json` · 필수 9개 + 가산 4개 = 13케이스)

- **로컬 단회 보고서 (33청크)**: `runs/team-20261105-121121.json` (**10 / 13 통과** — 필수 **9 / 9**, 가산 **1 / 4**)
- **로컬 3회 반복 보고서 (42청크)**: `runs/team-20261105-123416.json` (**30 / 39 통과** — 필수 **27 / 27**, 가산 **3 / 12**)
- **팀 VM 단회 보고서 (`445ba2d`, 42청크)**: `runs/vm/team-20261105-034811.json` (**10 / 13 통과** — 필수 **9 / 9**, 가산 **1 / 4**)

| 구분 | 케이스 | 기대 판정 (`expect`) | 로컬 단회 (**33청크**) | 로컬 3회 반복 (**42청크**) | 로컬 3회 시간 (s, **42청크**) | **팀 VM 단회 (`445ba2d`, 42청크)** | 실제 응답 `route` · 주요 필드 확인 |
| :---: | --- | --- | :---: | :---: | :---: | :---: | --- |
| 필수 | **TM-01 앱 로그인** (`tm01`) | `자동 답변`, `sources` ⊃ `app-login-troubleshooting` | ✔ 통과 (4.6s) | **3 / 3** | 4.6s, 4.5s, 4.9s | **✔ 통과 (5.6s)** | `route: "자동 답변"`, `app-login-troubleshooting` (`score: 0.603~0.604`) |
| 필수 | **TM-02 환불 1차 (금액 안내)** (`tm02a`) | `자동 답변`, `ticket: null`, `sources` ⊃ `refund-policy` | ✔ 통과 (2.0s) | **3 / 3** | 2.1s, 1.9s, 2.2s | **✔ 통과 (2.6s)** | 수수료 0원·환불 예정액 `152,000원` 계산, `ticket: null`, `/cache`에 견적 저장 |
| 필수 | **TM-03 환불 2차 (확인 후 티켓)** (`tm02b`) | `담당자 이관`, `ticket` ⊃ `"T-"` (`confirm: true`) | ✔ 통과 (0.7s) | **3 / 3** | 0.7s, 0.6s, 0.5s | **✔ 통과 (0.7s)** | `llm_calls: 0`, `category: "refund"`, `reason: "refund_confirmed"`, 티켓 `T-2001` 생성 |
| 필수 | **TM-04 지나치게 막지 않음** (`tm04`) | `security.blocked_by: ""`, `route` ≠ `"차단"` | ✔ 통과 (1.6s) | **3 / 3** | 1.7s, 1.5s, 1.6s | **✔ 통과 (2.1s)** | `"시스템 점검"` 포함 문의 과잉 차단 없음 (`blocked_by: ""`, `담당자 이관`) |
| 필수 | **TM-05 이중결제 + 부정 감정** (`tm05`) | `담당자 이관`, `sources` ⊃ `payment-error-guide`, 취소 단정 문구 금지 | ✔ 통과 (1.8s) | **3 / 3** | 1.8s, 1.9s, 2.1s | **✔ 통과 (2.4s)** | `sentiment: "angry"`(`reason: "strong_negative_sentiment"`), `payment-error-guide` 근거 포함 이관 (`T-2003`) |
| 필수 | **TM-06 경계 · 당일 취소** (`tm06`) | `담당자 이관`, `sources` ⊃ `refund-policy` | ✔ 통과 (1.7s) | **3 / 3** | 1.8s, 1.8s, 1.8s | **✔ 통과 (2.3s)** | `reason: "show_day_cancel"`, `refund-policy` 근거 포함 이관 (`T-2004`) |
| 필수 | **TM-13 환불 30만원 초과 → 이관** (`tm13`) | `담당자 이관`, `sources` ⊃ `refund-policy`, `ticket` ⊃ `"T-"` | ✔ 통과 (2.2s) | **3 / 3** | 2.2s, 2.2s, 2.0s | **✔ 통과 (2.7s)** | `C-2006`(352,000원) 30만원 초과 감지로 1차 확인 없이 즉시 이관 (`reason: "over_limit"`, `T-2005`) |
| 필수 | **TM-07 매크로 제한 문의** (`tm07`) | `자동 답변`, `sources` ⊃ `fair-booking-policy`, 답변 ⊃ `"24시간"` | ✔ 통과 (4.3s) | **3 / 3** | 4.2s, 3.9s, 4.7s | **✔ 통과 (5.8s)** | `route: "자동 답변"`, `fair-booking-policy` (`score: 0.453`), `"24시간"` 자동 해제 안내 포함 |
| 필수 | **TM-08 암표 신고 → 보안팀 이관** (`tm08`) | `담당자 이관`, `ticket` ⊃ `"T-"` | ✔ 통과 (1.7s) | **3 / 3** | 1.4s, 1.5s, 1.4s | **✔ 통과 (1.9s)** | `category: "scalping_report"`, `reason: "registry_handoff"`, 티켓 `T-2006` 생성 |
| 가산 | **TM-09 반복 요청 차단 (6번째)** (`tm09`) | `차단`, `security.blocked_by: "rate_limit"` | ✘ 실패 (4.3s) | **0 / 3** | 3.9s, 3.6s, 5.0s | **✘ 실패 (5.6s)** | `445ba2d` 기준 가산 기능(`checkRateLimit`) 본체 미연결로 `자동 답변` 반환 |
| 가산 | **TM-10 해외 IP 차단** (`tm10`) | `차단`, `security.blocked_by: "geo"` | ✘ 실패 (1.3s) | **0 / 3** | 1.6s, 1.4s, 1.4s | **✘ 실패 (1.9s)** | `445ba2d` 기준 가산 기능(`checkIpPolicy`) 본체 미연결로 `보완 질문` 반환 |
| 가산 | **TM-11 블랙리스트 IP 차단** (`tm11`) | `차단`, `security.blocked_by: "ip_blocklist"` | ✘ 실패 (3.9s) | **0 / 3** | 4.7s, 4.4s, 3.9s | **✘ 실패 (5.2s)** | `445ba2d` 기준 가산 기능(`checkIpPolicy`) 본체 미연결로 `자동 답변` 반환 |
| 가산 | **TM-12 국내 IP 정상 처리** (`tm12`) | `자동 답변`, `security.blocked_by: ""` | ✔ 통과 (4.4s) | **3 / 3** | 4.5s, 4.7s, 4.1s | **✔ 통과 (5.4s)** | 국내 IP(`203.0.113.10`) 과잉 차단 없이 `자동 답변` 정상 반환 |

---

## 3. 응답 시간(`bench -n 5`) 및 실행 로그(`/logs`) 분석

### 3.1 대표 요청 `flow.py bench -n 5` 측정 결과 (로컬 및 팀 VM, 42청크)

2026-11-05 로컬 환경(3종)과 **팀 VM(`445ba2d`, `requests/wf01.json`)**에서 각각 **5회(`-n 5`)** 연속 측정한 결과다.

| 환경 | 요청 파일 | 시나리오 유형 | 횟수 (`n`) | `p50` | `p95` | `max` | 실패 수 | 5회 개별 측정값 (s) | 근거 보고서 (`runs/` · `runs/vm/`) |
| :---: | --- | --- | :---: | :---: | :---: | :---: | :---: | --- | --- |
| **팀 VM (`445ba2d`)** | `requests/wf01.json` | 정상 기술 문의 (`자동 답변`, LLM 3회) | 5 | **5.45s** (`5.452s`) | **6.00s** (`6.000s`) | **6.00s** (`6.000s`) | **0 / 5** | `5.10`, `6.00`, `5.45`, `5.27`, `5.92` | `runs/vm/bench-ticketmoa-support-20261105-034838.json` |
| 로컬 | `requests/wf01.json` | 정상 기술 문의 (`자동 답변`, LLM 3회) | 5 | **4.61s** (`4.606s`) | **5.15s** (`5.149s`) | **5.15s** (`5.149s`) | 0 / 5 | `4.11`, `4.29`, `5.15`, `4.61`, `4.64` | `runs/bench-ticketmoa-support-20261105-123440.json` |
| 로컬 | `requests/wf02.json` | 정보 부족 (`보완 질문`, LLM 1회) | 5 | **1.26s** (`1.260s`) | **1.28s** (`1.279s`) | **1.28s** (`1.279s`) | 0 / 5 | `1.28`, `1.19`, `1.26`, `1.13`, `1.26` | `runs/bench-ticketmoa-support-20261105-123446.json` |
| 로컬 | `requests/wf12.json` | 복합·긴급 (`search ∥ payment` 병렬 + 긴급 이관, LLM 3회) | 5 | **3.38s** (`3.376s`) | **3.49s** (`3.492s`) | **3.49s** (`3.492s`) | 0 / 5 | `3.38`, `3.26`, `3.21`, `3.49`, `3.47` | `runs/bench-ticketmoa-support-20261105-123503.json` |

### 3.2 데이터 API `/logs?source=live` 집계 (로컬 시험 직후 메모리 조회, 120건)

> **출처 안내**: 아래 표는 `runs/` JSON 파일 안에 들어 있는 값이 아니라, 2026-11-05 로컬에서 `common.json --repeat 3`(51건), `team.json --repeat 3`(39건 + `TM-09` `before` 사전 호출 5건 × 3회 = 15건, 소계 54건), `bench -n 5` 3종(15건)을 연속 실행한 직후 로컬 데이터 API의 `GET http://localhost:8800/logs?source=live` 엔드포인트를 조회해 집계한 **총 120건**의 인메모리 실행 기록이다 (`51 + 54 + 15 = 120건`). 기록에 질문 원문·답변·이름·연락처는 포함되지 않음을 확인했다.

#### (1) 최종 `route` 및 상태 비율 (`status` 110건 + `rejected` 9건 + 사전 호출 중 1건 = 120건, 로컬 `/logs` 출처)

| 구분 (`route` / `status`) | 건수 (로컬 `/logs`) | 비율 (110건 기준 / 120건 기준) | 비고 |
| --- | :---: | :---: | --- |
| `담당자 이관` | 53건 | 48.2% / 44.2% | 지식 없음, 결제 오류, 환불 확정/예외, 긴급 입장, 장애 폴백 등 |
| `자동 답변` | 31건 (본 시험) + 10건 (`TM-09` `before` 사전 호출 중 일부) | 28.2% / 34.2% | QR·앱 로그인·매크로 문의, 본인 조회, 환불 1차 금액 안내 등 |
| `보완 질문` | 11건 | 10.0% / 9.2% | `WF-02` (3회 + bench 5회), `TM-10` (3회) |
| `권한 없음` | 3건 | 2.7% / 2.5% | `WF-06` 타인 건 조회 (3회) |
| `차단` | 3건 | 2.7% / 2.5% | `WF-08` 프롬프트 주입 규칙 차단 (3회) |
| `rejected` (HTTP 400) | 9건 | 8.2% / 7.5% | `WF-13a`·`13b`·`13c` 잘못된 입력 (3종 × 3회) |
| **합계** | **본 시험·bench 110건** (`TM-09` `before` 사전 호출 포함 시 **120건**) | **100.0%** | — |

#### (2) 하위 웹훅 단계별 소요 시간 (`steps`) 및 LLM 호출 수 (`llm_calls`) (출처: 로컬 `GET /logs?source=live`)

| 측정 항목 | 호출 건수 (`n`) | `p50` (로컬) | `p95` (로컬) | `max` (로컬) | 비고 |
| --- | :---: | :---: | :---: | :---: | --- |
| `agents_ms` (`ticketmoa-agents`) | 98 | **1,119 ms** | **2,065 ms** | 2,254 ms | Supervisor 분류 (규칙 분기 시 14~200ms) |
| `search_ms` (`ticketmoa-search`) | 51 | **376 ms** | **1,058 ms** | 1,346 ms | OpenAI 임베딩 + In-Memory Vector Store 검색 |
| `tech_ms` (`ticketmoa-tech`) | 45 | **2,429 ms** | **3,015 ms** | 3,934 ms | **답변 작성 LLM + `ticketmoa-agents-verify` 검증 LLM을 합친 전체 시간** |
| `handoff_ms` (`ticketmoa-handoff`) | 47 | **180 ms** | **3,037 ms** | 3,088 ms | 정상 시 ~180ms, `WF-04`·`WF-11` 장애 재시도 시 ~3,088ms |
| `payment_ms` (`ticketmoa-payment`) | 23 | **150 ms** | **2,147 ms** | 2,164 ms | 정상 시 ~150ms, `WF-11` 8초 지연 주입 시 ~2,164ms 타임아웃 |
| `refund_ms` (`ticketmoa-refund`) | 9 | **707 ms** | **982 ms** | 982 ms | 예매 조회 + 수수료 계산 + `/cache` 저장 또는 이관 |
| 요청당 `llm_calls` | 110 | **1회** | **3회** | 3회 (평균 **1.47회**) | 규칙 차단·400·보완한도·본인조회·환불확정은 `0회` |

---

## 4. 실패 사례 분석 및 조치·재시험 결과 (5건)

과제 요건(실패 사례 2건 이상, 원인·조치·재시험 결과 명시)에 따라 개발 및 시험 과정에서 발생한 5건의 실패 사례를 기록한다.

### 사례 1 · 지식 문서를 42청크로 늘린 뒤 `WF-12` 긴급 문의에서 대체 입장 문서 근거 누락 (발표 핵심 사례)

- **발생 시나리오**: `WF-12 복합·긴급` (`"공연 10분 전인데 모바일티켓 QR이 안 떠요! 어제 문의한 C-2002도 어떻게 됐는지 확인해 주세요"`)
- **근거 기록**: 지식 문서 정제본(`45bde9a`, 33청크 → 42청크) 적용 직후 로컬 시험 4회 연속 실패 및 수정 커밋 `2ad2849` (`docs/RAG-ARCHITECTURE.md` 1.2절, `docs/daily/DAY80.md` 3절)
- **현상**:
  - 기존 33청크 문서에서는 `WF-12`가 `3/3` 통과했으나, 안전 지침을 보강해 지식 문서를 **42청크**(`45bde9a`)로 늘리자 `WF-12`가 **4회 연속 실패(0/4)**했다.
  - 응답의 `route: "담당자 이관"`과 `ticket.priority: "high"`는 정상이었으나, 필수 근거인 `onsite-entry-fallback`(현장 대체 입장 안내)이 `sources`에서 빠지고 `mobile-ticket-troubleshooting` 절들만 반환되었다.
- **원인**:
  - `mobile-ticket-troubleshooting.md`가 5개 절로 늘어나면서, 질문 문구(`"모바일티켓 QR이 안 떠요"`)와 어휘 유사도가 높은 모바일티켓 일반 문제 해결 청크들이 상위권(1~4위)을 모두 차지해, 정작 공연 직전 긴급 상황에 필요한 `onsite-entry-fallback` 문서가 검색 상위 4위(`top_k: 4`) 밖으로 밀려났다.
  - 즉 문서 내용의 오류가 아니라, 긴급 입장 문의에서도 일반 기술 문의와 넓은 검색 범위를 함께 쓰며 검색 순위에만 의존하던 구조가 원인이었다.
- **조치**:
  - 커밋 `2ad2849`에서 본체(`workflows/ticketmoa-support.json`)의 `Call search` 및 병렬 `Call search ∥` 노드를 수정해, 긴급 입장 문의(`urgency === "high"`)일 때는 검색 `scope`를 `["onsite-entry-fallback"]`으로 고정하여 대체 입장 근거가 검색 4위 밖으로 밀리지 않도록 개선했다.
- **재시험 결과**:
  - 수정 후 42청크 기준 로컬 3회 반복 시험(`runs/common-20261105-123211.json`)에서 `WF-12`가 **3 / 3 통과**(`4.4s`, `3.3s`, `3.4s`)했고, **팀 VM(`445ba2d`, 42청크) 3회 반복 시험(`runs/vm/common-20261105-034700.json`)에서도 3 / 3 통과(`4.9s`, `4.2s`, `3.8s`)**하며 `onsite-entry-fallback` 근거와 `"현장 발권"` 안내가 안정적으로 포함됨을 확인했다.

### 사례 2 · OpenAI Credential 인증 실패(HTTP 401)로 인한 색인 누락 및 정상/보완/긴급 문의 이관 폴백

- **발생 시나리오**: `WF-01 정상 문의`, `WF-02 정보 부족`, `WF-12 복합·긴급` (출발점 시험 `14 / 17` 통과)
- **근거 보고서**: `runs/common-20261105-114641.json` (2026-11-05 11:46, 로컬)
- **현상**:
  - `WF-01`(기대: `자동 답변`), `WF-02`(기대: `보완 질문`), `WF-12`(기대: `priority: "high"` 및 `onsite-entry-fallback` 근거 포함) 3건 모두 HTTP 200과 함께 `route: "담당자 이관"`, `sources: []`, `ticket.priority: "normal"`, `agents.error: "llm_unavailable"`, `reason: "agents_failed"`를 반환하며 실패했다.
  - 동시에 `tools/reindex.py` 실행 시 `ticketmoa-search` 확인 단계에서 `일반 색인 False, 스태프 색인 False, error: "index_unavailable"`이 발생했다.
- **원인**:
  - `.env` 파일에 복사된 `OPENAI_API_KEY`가 만료·오타 상태(`HTTP 401 Incorrect API key provided`)였고, 주석 기호(`#`)가 빠진 설명 줄이 섞여 있어 환경 변수 로드 및 n8n `OpenAI (.env)`(`openAiCourse0001`) 인증이 실패했다.
  - 그 결과 LLM 호출 전 규칙으로 처리되는 14개 케이스(입력 검증, 주입 차단, `attempt: 3`, 예약번호/문의번호 정규식 기반 조회, 장애 폴백 등)는 통과했으나, LLM 분류와 임베딩이 필수인 3개 케이스는 fail-closed 설계에 따라 상담원 이관으로 빠졌다.
- **조치**:
  1. `.env`의 비변수 설명 줄을 주석(`#`) 처리하고 LF 개행으로 정리한 뒤 유효한 `OPENAI_API_KEY`(`GET /v1/models` HTTP 200 확인)로 교체했다.
  2. `Last3Mon/65/n8n/register-credentials.sh`로 `OpenAI (.env)` Credential을 재등록하고 n8n 컨테이너를 재시작해 메모리 내 Credential 캐시를 갱신한 뒤 `uv run --env-file .env tools/reindex.py`로 8개 문서 전체 색인을 완료했다.
- **재시험 결과**:
  - 직후 재시험 보고서 `runs/common-20261105-121025.json`(로컬, 33청크)에서 `WF-01`(`자동 답변`, `6.0s`), `WF-02`(`보완 질문`, `2.4s`), `WF-12`(`담당자 이관`, `priority: "high"`, `3.6s`)가 모두 통과하여 **17 / 17 전원 통과**를 확인했다.

### 사례 3 · `WF-01`·`TM-07` 간헐적 `llm_unavailable` 이관 및 시간 제한(2.5초) 유지 판단

- **발생 시나리오**: `WF-01 정상 문의` (로컬 `--repeat 3`의 #2·#3회차), `TM-07 매크로 제한 문의` (11/04 로컬 3회 반복 중 1회차)
- **근거 보고서 및 출처**: `runs/common-20261105-123211.json` (2026-11-05 12:32, 로컬 42청크), 11/04 로컬 시험 기록(출처: `docs/WORKFLOW-DESIGN.md` 4.6절), 컨테이너 재시작 직후 로컬 단건 호출 기록(8.1s, 콘솔 측정치로 `runs/` 파일 없음)
- **현상**:
  1. 로컬 컨테이너 재시작 직후 첫 `WF-01` 단건 호출(콘솔 확인, `runs/` 미보관)에서 `route: "자동 답변"`과 `sources`는 정상 생성되었으나 전체 소요 시간이 `8.1s`(`total_ms: 6175ms`)로 `expect.max_seconds: 8`을 `0.1s` 초과한 사례가 있었다.
  2. 2026-11-05 12:32 로컬 42청크 `common.json --repeat 3`(`runs/common-20261105-123211.json`)에서 `WF-01` #1회차는 `7.3s`(`tech_ms: 3934ms`)로 통과했으나, #2회차(`6.2s`, `tech_ms: 2657ms`)와 #3회차(`6.3s`, `tech_ms: 2647ms`)는 분류(`intents: ["tech_issue"]`, `confidence: 0.95`)와 검색까지 성공하고도 `route: "담당자 이관"`, `sources: []`, `reason: "llm_unavailable"`로 실패했다. (11/04 로컬 시험에서도 `TM-07`이 3회 중 1회 `llm_unavailable`로 이관됨.)
- **원인 분석**:
  - `workflows/ticketmoa-tech.json`의 `작성 모델`(`gpt-4.1-mini`) 노드에 `timeout: 2500`(2.5초)과 `maxRetries: 1`이 설정되어 있어, OpenAI 응답이 순간적으로 2.5초를 넘기면 `작성 실패 결과` 노드를 통해 `reason: "llm_unavailable"`로 안전 이관된 것으로 추정된다.
  - 다만 응답의 `timings.steps.tech_ms`(로컬 `/logs` 기준 `p50 2,429ms`, `p95 3,015ms`)는 **`작성 모델` 단독 시간이 아니라 답변 작성 LLM과 `ticketmoa-agents-verify` 검증 LLM 호출을 합친 값**이므로, `tech_ms` 수치만으로 2.5초 타임아웃이 원인이었다고 단정할 수는 없으며 n8n 실행 기록의 상세 오류 메시지는 추가 확인이 필요하다.
- **조치 판단 및 이후 시험 결과 (2.5초 제한 유지)**:
  - `작성 모델` timeout을 3.5~4초로 늘리면 분류(최대 3초) + 검색 + 작성 + 검증의 최악 합계 시간이 시나리오 판정 기준인 **8초(`max_seconds: 8`)를 초과**하게 된다.
  - 12:32 실패 이후 수행한 로컬 `team.json --repeat 3`(`runs/team-20261105-123416.json`, 12:34)에서 `TM-07`이 `3 / 3` 통과했고, 로컬 `bench -n 5`(`runs/bench-ticketmoa-support-20261105-123440.json`, 12:34)에서도 `WF-01`이 **5 / 5 통과(`p50 4.61s`, `p95 5.15s`)**했다.
  - 무엇보다 **팀 VM(`445ba2d`, 42청크)에서 실행한 `common.json --repeat 3`(`runs/vm/common-20261105-034700.json`, 12:47 KST)에서 `WF-01`이 3 / 3 통과(`6.6s`, `6.8s`, `6.1s` ≤ 8s)해 전체 `51 / 51`을 달성**했고, **VM `bench -n 5`(`runs/vm/bench-ticketmoa-support-20261105-034838.json`, 12:48 KST)에서도 5 / 5 통과(`p50 5.45s`, `p95 6.00s`)**했으므로 `작성 모델` 2.5초 제한을 그대로 **유지**하기로 결정했다.
  - **최신 VM 재시험 (`a5c80dc`, 0절 A행)**: 공통 3회 `50 / 51`로, `WF-01` 1회차가 `push`와 재색인 직후 `llm_unavailable`로 이관됐다(`7.3s`, `tech_ms` 약 2.7초). 2·3회차와 `bench -n 5`는 통과했다. 시간 초과형 실패가 1건으로 조정 기준(2건 이상) 미만이라 2.5초를 유지한다.
  - **잔여 위험**: 팀 VM 시험 직전 단건 호출에서 `WF-01`이 `verification_failed`로 1회 이관된 사례가 있었고, 로컬과 VM 모두에서 간헐적 `llm_unavailable` 이관이 관측되었으므로, 완전 해결로 보지 않고 계속 모니터링한다.

### 사례 4 · 강한 불만 문의(`TM-05`) 이관 시 근거 문서(`sources`) 누락

- **발생 시나리오**: `TM-05 이중결제 + 부정 감정` (`"두 번 결제됐는데 진짜 짜증나네요. 154,000원이 두 번 빠져나갔어요"`)
- **근거 기록**: 2026-11-04 통합 시험 및 커밋 `d213d89` (`docs/daily/DAY80.md` 3절, `docs/TEAM-CHARTER.md` 6절)
- **현상**:
  - `TM-05`의 기대 결과는 `route: "담당자 이관"`이면서 동시에 `sources`에 `payment-error-guide`가 포함되어야 하나, 초기 통합 버전에서는 `sources: []`가 반환되어 실패했다.
- **원인**:
  - 본체(`ticketmoa-support`)의 `Plan route`에서 강한 부정 감정(`sentiment: "angry"` → `strong_negative_sentiment`)이나 관람 당일 취소(`show_day_cancel`)가 감지되면 지식 문서 검색(`ticketmoa-search`)을 거치지 않고 곧바로 `handoff` 분기로 보냈기 때문에 근거 문서가 비어 있었다.
- **조치**:
  - 커밋 `d213d89`에서 본체 `Route` 스위치에 `evidence_handoff` 갈래(`Call search (evidence)` → `Evidence handoff answer`)를 추가해, 강한 불만 문의(`sentiment: "angry"`)나 당일 취소 문의도 해당 업무의 `kb_scope` 문서를 먼저 검색한 뒤 `sources`를 담아 `ticketmoa-handoff`로 넘기도록 수정했다.
- **재시험 결과**:
  - 로컬 3회 반복(`runs/team-20261105-123416.json`)에서 `TM-05`(`1.8s`, `1.9s`, `2.1s`)와 `TM-06`(`1.8s`, `1.8s`, `1.8s`)이 **3 / 3 통과**했고, **팀 VM(`runs/vm/team-20261105-034811.json`)에서도 `TM-05`(`2.4s`), `TM-06`(`2.3s`) 모두 통과**하며 `payment-error-guide`·`refund-policy` 근거가 정상 포함됨을 확인했다.

### 사례 5 · 가산 시나리오(`TM-09`~`TM-11`) 반복 요청 및 IP 차단 미연결 (`445ba2d`까지, `a5c80dc`에서 해결)

- **발생 시나리오**: `TM-09 반복 요청 차단 (6번째 요청)`, `TM-10 해외 IP 차단`, `TM-11 블랙리스트 IP 차단`
- **근거 보고서**: 로컬 `runs/team-20261105-121121.json`, `runs/team-20261105-123416.json` 및 **팀 VM `runs/vm/team-20261105-034811.json`**
- **현상**:
  - 기대값은 모두 `route: "차단"` 및 `security.blocked_by` 값(`"rate_limit"`, `"geo"`, `"ip_blocklist"`)이나, `445ba2d`까지는 일반 문의와 동일하게 분류·답변 경로를 타서 `자동 답변`(`TM-09`, `TM-11`) 또는 `보완 질문`(`TM-10`)과 `security.blocked_by: ""`를 반환해 로컬 `0 / 3`, 팀 VM `0 / 1` 실패했다.
- **원인**:
  - `lib/common.js`의 `checkRateLimit`·`checkIpPolicy` 함수(현재 `node --test lib/test/*.test.js` 단위 테스트 **20 / 20** 통과)와 `config/ip-policy.json`, 패치 스크립트(`tools/abuse_guard_apply.py`, PR #13)는 준비되어 있었으나, 필수 시나리오 VM 검증을 먼저 끝내는 원칙에 따라 `445ba2d` 시점에는 본체(`workflows/ticketmoa-support.json`)에 연결하지 않은 상태였다.
- **조치 및 현재 상태**:
  - 국내 정상 IP(`203.0.113.10`)가 과잉 차단되지 않는지 확인하는 `TM-12`는 로컬 **3 / 3**, 팀 VM **1 / 1** 통과했다.
  - 팀 VM에서 필수 시나리오(공통 `51/51`, 팀 필수 `9/9`) 통과를 확인한 뒤, 후속 커밋 `6f158de`에서 본체에 차단 노드 5개를 연결해 로컬 `runs/team-20261105-140447.json`에서 **팀 13 / 13 전원 통과**를 확인했다. 이후 VM에 재배포한 `a5c80dc`에서도 **팀 13 / 13**으로 통과했다 (0절 A행, `TM-09`~`11` 각 0.2초, LLM 호출 전 차단).

---

## 5. KSM-REQ 6절 제출 전 체크리스트 및 기능별 검증 표

### 5.1 제출 전 체크리스트 (`Lecture/80-82-Project/Req/KSM-REQ.md` 6절 원문 15개 항목)

과제 원문(`Lecture/80-82-Project/Req/KSM-REQ.md` 6절)의 15개 체크리스트(노코드 워크플로우 설계서 4, RAG 아키텍처 설계서 4, 워크플로우 실행 결과서 4, 공통 3) 충족 여부와 확인 근거는 다음과 같다.

| # | 구분 | 체크리스트 항목 (`KSM-REQ.md` 6절 원문) | 확인 근거 (산출물 절 · 구현 파일 · 실측 보고서) | 충족 |
| :---: | --- | --- | --- | :---: |
| 1 | **노코드 워크플로우 설계서** | Trigger → 처리 → 출력 흐름이 실제 구현과 일치한다. | `docs/WORKFLOW-DESIGN.md` 2~3절 및 `workflows/ticketmoa-*.json` 7종(`support`, `agents`, `search`, `tech`, `payment`, `refund`, `handoff`) 노드 흐름 일치 확인 | [x] |
| 2 | **노코드 워크플로우 설계서** | 병렬·분기·루프 구조의 사용 목적이 명확하다. | `docs/WORKFLOW-DESIGN.md` 4절 (신뢰도·권한·감정 분기, `WF-12` `Call search ∥`·`Call payment ∥` 병렬, `WF-02`·`WF-02b` `attempt` 보완 질문 루프 및 재시도 루프 명시) | [x] |
| 3 | **노코드 워크플로우 설계서** | 외부 연동별 인증 및 오류 처리를 기록했다. | `docs/WORKFLOW-DESIGN.md` 5·7절 (`X-Team-Key`, `X-Api-Key`, `OpenAI (.env)` 인증 및 401/403 비재시도, 429/5xx/timeout 재시도·DLQ·알림·Error Workflow 기록) | [x] |
| 4 | **노코드 워크플로우 설계서** | 노드 간 페이로드의 필수·선택 필드와 변환 로직을 작성했다. | `docs/WORKFLOW-DESIGN.md` 6절 (하위 웹훅 및 주요 연결선별 필수·선택 필드, `lib/common.js` 변환·정규화·마스킹 로직, 실제 페이로드 예시 수록) | [x] |
| 5 | **RAG 아키텍처 설계서** | 청킹 단위·오버랩·길이 분포와 선정 근거를 작성했다. | `docs/RAG-ARCHITECTURE.md` 1~2절 (`knowledge/*.md` 8개 문서 `##` 절 단위 청킹, 오버랩 0, 42개 청크 길이 116/229/432자 분포 및 500/80 비교 실험 수치 기록) | [x] |
| 6 | **RAG 아키텍처 설계서** | 임베딩 모델 선정 이유와 실제 벡터 차원을 기록했다. | `docs/RAG-ARCHITECTURE.md` 3절 (`text-embedding-3-large`, 실제 벡터 차원 3,072차원 확인 근거, 문장 의미 검색 목적과 비교 실험 부재 기록) | [x] |
| 7 | **RAG 아키텍처 설계서** | 거리 계산 방식과 인덱스·메타데이터 구조를 작성했다. | `docs/RAG-ARCHITECTURE.md` 3~4절 (Cosine Similarity 재계산 대조 확인, `ticketmoa_kb_v1_all`·`ticketmoa_kb_v1_staff` 권한 분리 파티션 및 메타데이터·검색 전후 필터 구조) | [x] |
| 8 | **RAG 아키텍처 설계서** | 백업·복구 및 확장 방안을 작성했다. | `docs/RAG-ARCHITECTURE.md` 5절 (Git 원본 백업, `tools/reindex.py` 재색인 시간 측정과 비용 추산, 자동 롤백 미구현 기록, 문서 10배 확장 추산) | [x] |
| 9 | **워크플로우 실행 결과서** | 주요 시나리오별 실행 테스트 로그가 있다. | 본 문서 1~3절 (`cases/common.json` 17케이스, `cases/team.json` 13케이스 로컬·팀 VM 실측, `bench -n 5`, 로컬 `/logs` 120건 단계별 `steps` 및 `llm_calls` 기록) | [x] |
| 10 | **워크플로우 실행 결과서** | 예외 상황의 실제 처리 결과가 있다. | 본 문서 2.1~2.2절 (`WF-03` 무근거 이관, `WF-04` 티켓 API 500 장애 DLQ+알림, `WF-05`~`08` 권한·PII·주입 차단, `WF-09` 중복 방지, `WF-10` LLM 장애, `WF-11` 8초 지연, `WF-13` 400 검증) | [x] |
| 11 | **워크플로우 실행 결과서** | 기대 결과와 실제 결과를 구분했다. | 본 문서 2.1절·2.2절 시나리오 표에서 `기대 판정 (expect)` 열과 로컬·팀 VM 실제 결과 및 `실제 응답 route · 주요 필드 확인` 열을 분리해 대조 기록 | [x] |
| 12 | **워크플로우 실행 결과서** | 실패 사례와 재시험 결과를 기록했다. | 본 문서 4절 (사례 1 `WF-12` 42청크 근거 누락 → `2ad2849`로 로컬·VM `3/3` 통과, 사례 2 OpenAI 401 → `17/17` 통과, 사례 3 `WF-01`·`TM-07` 간헐 이관 → VM B행 `51/51`, A행 `50/51`·`bench 5/5` 확인 후 제한 유지, 사례 4 `TM-05` 근거 누락 → 통과, 사례 5 가산 연결 → VM A행 `13/13`) | [x] |
| 13 | **공통** | 세 설계서·결과서의 내용이 실제 구현과 일치한다. | `docs/WORKFLOW-DESIGN.md`, `docs/RAG-ARCHITECTURE.md`, `docs/EXECUTION-RESULT.md`의 워크플로우·노드명·메모리 키·계약 필드가 `workflows/*.json` 및 `lib/common.js`와 일치 | [x] |
| 14 | **공통** | 예시 수치를 팀의 실제 측정값으로 교체했다. | 모든 통과율·소요 시간(`p50`/`p95`)·청크 분포·단계별 시간(`steps`)을 `runs/*.json`, `runs/vm/*.json` 보고서 및 `reindex.py`·`/logs` 실측값으로 기입 | [x] |
| 15 | **공통** | 인증정보와 개인정보가 문서·로그·저장소에 노출되지 않았다. | 키는 n8n Credential(`openAiCourse0001`, `ticketmoa-data-api`, `ticketmoa-team-key`)에만 분리, 가짜 연락처(`010-****-3307`) 마스킹 및 `/logs` 원문·PII 노출 0건 확인. 제출 전 `tscan scan .` 오탐 정리는 남아 있음 | [x] |

### 5.2 기능별 검증 표

티켓모아 고객 기술지원 워크플로우의 15개 핵심 기능에 대한 구현 위치와 로컬(`runs/`)·팀 VM(`runs/vm/`, B행 `445ba2d`) 실측 검증 결과는 다음과 같다. 최신 VM 결과는 0절 A행이다.

| # | 기능별 검증 항목 | 구현 워크플로우 · 노드 | 검증 시나리오 | 로컬 및 팀 VM 실측 결과 (`runs/` · `runs/vm/`) | 충족 |
| :---: | --- | --- | --- | --- | :---: |
| 1 | **공통 Webhook 입구 및 Header Auth 인증**: `POST /webhook/ticketmoa-support` 단일 입구와 `X-Team-Key` Header Auth(`ticketmoa-team-key`) 적용, 공통 응답 9개 필드(`request_id`, `route`, `answer`, `sources`, `ticket`, `agents`, `security`, `timings`, `reason`) 준수 | `ticketmoa-support` · `Question webhook`, `Build response` | 전체 (WF-01~13, TM-01~13) | 로컬·팀 VM 전 케이스 응답 스키마 100% 일치 (`runs/vm/common-20261105-034700.json`) | ✔ |
| 2 | **입력 유효성 검증 (규칙)**: 빈 질문(`empty_question`), 미등록 사용자(`unknown_user`), 501자 이상(`question_too_long`) 요청 시 LLM 호출 전 HTTP 400 `{"error":"invalid request","codes":[...]}` 반환 | `ticketmoa-support` · `Get users` → `Check input` → `Reject invalid` | WF-13a, WF-13b, WF-13c | 로컬 **9 / 9**, 팀 VM **9 / 9 통과** (HTTP 400, 0.1~0.2s, `llm_calls: 0`) | ✔ |
| 3 | **프롬프트 주입(Injection) 사전 차단**: `"이전 지시 무시"`, `"시스템 프롬프트"` 등 주입 패턴을 LLM 호출 전 규칙으로 차단(`route: "차단"`, `security.blocked_by: "rule"`, `llm_calls: 0`)하고 정상 문의는 과잉 차단하지 않음 | `ticketmoa-support` · `Injection rules` → `Blocked answer` | WF-08, TM-04, TM-12 | WF-08 로컬 **3 / 3**·VM **3 / 3**, TM-04·TM-12 로컬 **6 / 6**·VM **2 / 2 통과** | ✔ |
| 4 | **업무 레지스트리 기반 Supervisor 분류 및 Fail-Closed**: `config/registry.json`을 읽어 Structured Output JSON으로 의도·신뢰도·긴급도·감정(`angry` 등)을 분류하고, 파싱 실패·오류 시 `담당자 이관`으로 안전 폴백 | `ticketmoa-support` · `Load registry`, `ticketmoa-agents` · `Supervisor 분류`, `분류 결과 검사` | WF-01, WF-10, TM-01~08 | 정상 분류 및 LLM 장애 시 fail-closed 이관 확인 (VM 공통 **51 / 51**) | ✔ |
| 5 | **보완 질문 루프 및 반복 한도 이관**: 정보 부족·저신뢰(`confidence < 0.7` 또는 필수 슬롯 누락) 시 `보완 질문`으로 되묻고, `attempt >= 3`이면 LLM 호출 없이 즉시 `담당자 이관` | `ticketmoa-agents` · `LLM 필요?`, `ticketmoa-support` · `Plan route` | WF-02 (`attempt: 1`), WF-02b (`attempt: 3`) | WF-02 로컬 **3 / 3**·VM **3 / 3**, WF-02b 로컬 **3 / 3**·VM **3 / 3 통과** (`llm_calls: 0`) | ✔ |
| 6 | **문서 품질 검사 및 권한 분리 색인**: `knowledge/*.md` 8개 문서를 `##` 절 단위로 청킹하고, 색인 전 품질 검사(절 개수·`access_level`·빈 절·연락처 포함 여부) 후 `ticketmoa_kb_v1_all`과 `ticketmoa_kb_v1_staff`로 분리 저장 | `ticketmoa-index` · `Validate and make chunks`, `Store public chunks`, `Store staff chunks` | `tools/reindex.py` | 문서 8/8 (일반 7, 스태프 1, 정제본 42청크), `issues: []`, `store_output_received` 확인 | ✔ |
| 7 | **검색 전 문서 권한 필터링 (Pre-filtering)**: 질문 문구가 아니라 조회된 사용자의 `access_level`로 검색 대상 메모리 키를 결정하여 일반 고객(`all`) 검색 시 스태프 전용 문서(`staff-entry-manual`) 원천 배제 | `ticketmoa-search` · `검색 준비`, `스태프 권한?` | WF-05 | WF-05 로컬 **3 / 3**, 팀 VM **3 / 3 통과** (`staff-entry-manual`·`책임자 코드`·`수기 모드` 노출 0건) | ✔ |
| 8 | **근거 기반 RAG 답변 및 무근거 추측 금지**: 검색된 문서(`hits`) 범위 안에서만 답변과 `sources`를 작성하고, 지식 문서에 근거가 없는 질문은 지어내지 않고 `담당자 이관`(`sources: []`) 처리 | `ticketmoa-tech` · `답변 작성`, `작성 결과 검사` | WF-01, WF-03, TM-01, TM-07 | WF-03 로컬 **3 / 3**, 팀 VM **3 / 3 통과** (`route: "담당자 이관"`, `sources: []`, `writer_not_grounded`) | ✔ |
| 9 | **검증 Agent(Reviewer) 다중 점검**: 작성된 답변이 검색 근거(`hits`) 내에 있는지, 환불·취소 직접 실행 주장이 없는지, 개인정보가 없는지 검증하고 미통과 시 `담당자 이관` 처리 | `ticketmoa-tech` · `검증 호출` → `ticketmoa-agents` · `검증 Agent` (`/webhook/ticketmoa-agents-verify`) | WF-01, WF-12, TM-01, TM-07 | 정상 답변 시 `llm_calls: 3`(분류+작성+검증)으로 검증 통과 확인 (VM `WF-01` **3 / 3**) | ✔ |
| 10 | **본인 건만 조회 (소유권 검증)**: 예매·문의 조회(`GET /tickets/<id>?requester=`) 시 요청 `user`와 기록 소유자가 다르면 HTTP 403을 받아 `route: "권한 없음"`으로 응답하고 내용 노출 차단 | `ticketmoa-payment` · `본인 건 조회`, `조회 판정` | WF-06, WF-07 | WF-06 로컬 **3 / 3**, 팀 VM **3 / 3 통과** (`route: "권한 없음"`, `reason: "not_owner"`, 타인 정보 노출 0건) | ✔ |
| 11 | **개인정보(PII) 마스킹 및 가림 개수 기록**: 응답 본문·티켓 요약·로그에서 전화번호와 이메일을 마스킹(`010-****-xxxx`, `x***@example.com`)하고 가린 개수를 `security.masked`에 기록 | `ticketmoa-payment`, `ticketmoa-support` · `maskPII` (`lib/common.js`) | WF-07, WF-12 | WF-07·WF-12 로컬 **6 / 6**, 팀 VM **6 / 6 통과** (원문 노출 0건, `security.masked: 2`) | ✔ |
| 12 | **환불 2단계 고객 확인 및 예외 즉시 이관**: 에이전트가 직접 취소를 실행하지 않고 1차에 수수료·환불 예정액 안내(`ticket: null`), 2차 `context.confirm === true` 확인 시에만 환불 티켓 생성. 30만원 초과·당일 취소는 즉시 이관 | `ticketmoa-refund` · `calcRefund`, `/cache`, `ticketmoa-support` · `Refund confirm?` | TM-02, TM-03, TM-06, TM-13 | 로컬 각 **3 / 3 (12 / 12)**, 팀 VM 각 **1 / 1 (4 / 4) 통과**, 미확인 티켓 생성 0건 | ✔ |
| 13 | **복합·긴급 문의 병렬 처리 및 현장 알림**: 공연 30분 이내 입장 장애와 문의 조회가 결합된 복합 문의 시 긴급 검색 범위 고정(`2ad2849`) 및 `search ∥ payment` 병렬 호출로 대체 입장 안내(`onsite-entry-fallback`) + 조회 결과 + 긴급 티켓(`priority: "high"`) + 현장 알림(`venue-staff`) 처리 | `ticketmoa-support` · `Call search ∥`, `Call payment ∥`, `Merge search + lookup`, `ticketmoa-tech` | WF-12 | WF-12 로컬 **3 / 3** (`3.3~4.4s`), 팀 VM **3 / 3** (`3.8~4.9s`), 로컬 `bench -n 5` **p50 3.38s** (5/5 통과) | ✔ |
| 14 | **외부 API·LLM 장애 격리, 선택적 재시도, 중복 방지, DLQ·알림**: timeout 설정 및 429·5xx·timeout만 재시도(401·403 제외), 티켓 API 장애 시 `ticket: null` + `/dlq` + `/alerts` 기록(HTTP 200 유지), `key=request_id`로 중복 티켓 방지(`duplicate: true`), `ticketmoa-errors` Error Workflow 구성 | `ticketmoa-handoff`, `ticketmoa-payment`, `ticketmoa-errors`, `ticketmoa-support` | WF-04, WF-09(1·2차), WF-10, WF-11 | WF-04·09·10·11 로컬 **15 / 15**, 팀 VM **15 / 15 통과** (500 에러 0건, `WF-11` VM 5.5~5.6s ≤ 6s) | ✔ |
| 15 | **비식별 실행 로그(`/logs`) 기록 및 비밀키 분리**: 응답 직전 `POST /logs`에 `request_id`, `route`, `intents`, `steps`, `llm_calls`, `has_ticket`, `blocked_by`, `masked`, `status`, `duration_ms`만 기록(질문 원문·연락처 제외)하고 저장소 내 API 키·토큰 노출 0건 유지 | `ticketmoa-support` · `Log record` → `POST /logs`, n8n Credentials | `/logs?source=live` (120건), `flow.py check` | `/logs` 120건 원문·PII 노출 0건 확인, Credential 고정 ID 사용 확인 | ✔ |

---

## 6. 시나리오 파일(`cases/`, `requests/`) 검토 결과

담당 파일인 `cases/common.json`, `cases/team.json`, `cases/README.md`, `requests/*.json`을 전수 검토한 결과는 다음과 같다.

1. **`cases/common.json` (14유형 17케이스)**:
   - `expect` 조건은 과제 공통 기준과 정확히 일치하며 일절 수정하지 않았다.
   - 질문 문구도 실제 고객센터 문의 말투(`"모바일티켓 QR이 회색으로만 나오고 안 떠요. 어떻게 해야 하나요?"`, `"공연 10분 전인데 모바일티켓 QR이 안 떠요! 어제 문의한 C-2002도 어떻게 됐는지 확인해 주세요"` 등)로 자연스럽게 작성되어 있어 추가 수정 없이 그대로 유지하는 것이 안전하다.
2. **`cases/team.json` (13케이스: 필수 9 + 가산 4)**:
   - `TM-01`~`TM-08`, `TM-13`(필수 9개)은 `data/records.json`(`C-2001`~`C-2006`) 및 `knowledge/*.md` 8개 문서와 정합성이 맞고, 로컬 3회 반복 시험(**27 / 27**) 및 팀 VM 단회 시험(**9 / 9**)에서 전원 통과했다.
   - `TM-09`~`TM-12`(가산 4개)는 `context.client_ip`에 RFC 5737 문서용 예약 대역(`198.51.100.7`, `203.0.113.66`, `203.0.113.10`)만 사용하여 실제 개인정보·외부 IP 없이 시연 가능하도록 설계되어 있다.
3. **`requests/wf01.json`, `requests/wf02.json`, `requests/wf12.json`**:
   - 시연 및 `flow.py bench` 측정용 요청 본문으로, `cases/common.json`의 `WF-01`, `WF-02`, `WF-12` 요청과 동일하며 `bench -n 5`에서 모두 정상 동작함을 확인했다.

---

## 7. 보관된 실행 보고서 목록 (`runs/` 및 `runs/vm/`)

| 파일명 | 측정 시각 | 환경 · 문서 스냅샷 | 실행 명령 | 결과 요약 |
| --- | --- | :---: | --- | --- |
| `runs/common-20261105-114641.json` | 2026-11-05 11:46:41 KST | 로컬 (색인 전) | `flow.py test cases/common.json --webhook ticketmoa-support -v` | **14 / 17** (OpenAI 키 교체 전 출발점, 실패 사례 2 증거) |
| `runs/common-20261105-121025.json` | 2026-11-05 12:10:25 KST | 로컬 (**33청크**) | `flow.py test cases/common.json --webhook ticketmoa-support -v` | **17 / 17** (키 교체·33청크 색인 직후 단회 전원 통과) |
| `runs/team-20261105-121121.json` | 2026-11-05 12:11:21 KST | 로컬 (**33청크**) | `flow.py test cases/team.json --webhook ticketmoa-support -v` | **10 / 13** (팀 필수 **9 / 9**, 가산 1 / 4) |
| `runs/common-20261105-123211.json` | 2026-11-05 12:32:11 KST | 로컬 (**42청크**) | `flow.py test cases/common.json --webhook ticketmoa-support --repeat 3` | **49 / 51** (16케이스 3/3 통과, `WF-01` 1/3 — 실패 사례 1·3 증거) |
| `runs/team-20261105-123416.json` | 2026-11-05 12:34:16 KST | 로컬 (**42청크**) | `flow.py test cases/team.json --webhook ticketmoa-support --repeat 3` | **30 / 39** (팀 필수 **27 / 27**, 가산 3 / 12) |
| `runs/bench-ticketmoa-support-20261105-123440.json` | 2026-11-05 12:34:40 KST | 로컬 (**42청크**) | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | **p50 4.61s · p95 5.15s** · max 5.15s · 실패 0/5 |
| `runs/bench-ticketmoa-support-20261105-123446.json` | 2026-11-05 12:34:46 KST | 로컬 (**42청크**) | `flow.py bench ticketmoa-support requests/wf02.json -n 5` | **p50 1.26s · p95 1.28s** · max 1.28s · 실패 0/5 |
| `runs/bench-ticketmoa-support-20261105-123503.json` | 2026-11-05 12:35:03 KST | 로컬 (**42청크**) | `flow.py bench ticketmoa-support requests/wf12.json -n 5` | **p50 3.38s · p95 3.49s** · max 3.49s · 실패 0/5 |
| `runs/common-20261105-140723.json` | 2026-11-05 14:07 KST | 로컬 (42청크, C행) | 공통 3회 | 49 / 51 |
| `runs/team-20261105-140447.json` | 2026-11-05 14:04 KST | 로컬 (42청크, C행) | 팀 1회 | 13 / 13 |
| **`runs/vm/common-20261105-051822.json`** | 2026-11-05 14:18 KST *(파일명 UTC)* | **팀 VM (`a5c80dc`, 42청크, A행)** | `flow.py test cases/common.json --webhook ticketmoa-support --repeat 3` | **50 / 51** (`WF-01` 1회 `llm_unavailable`) |
| **`runs/vm/team-20261105-051921.json`** | 2026-11-05 14:19 KST *(파일명 UTC)* | **팀 VM (`a5c80dc`, 42청크, A행)** | `flow.py test cases/team.json` | **13 / 13** (필수 9 / 9, 가산 4 / 4) |
| **`runs/vm/bench-ticketmoa-support-20261105-051948.json`** | 2026-11-05 14:19 KST *(파일명 UTC)* | **팀 VM (`a5c80dc`, 42청크, A행)** | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | **p50 5.50s · p95 5.77s** · 실패 0/5 |
| **`runs/vm/common-20261105-034700.json`** | 2026-11-05 12:47:00 KST *(파일명 UTC 03:47)* | **팀 VM (`445ba2d`, 42청크)** | `flow.py test cases/common.json --webhook ticketmoa-support --repeat 3` | **51 / 51** (공통 17케이스 × 3회 반복 전원 통과) |
| **`runs/vm/team-20261105-034811.json`** | 2026-11-05 12:48:11 KST *(파일명 UTC 03:48)* | **팀 VM (`445ba2d`, 42청크)** | `flow.py test cases/team.json --webhook ticketmoa-support -v` | **10 / 13** (팀 필수 **9 / 9**, 가산 1 / 4) |
| **`runs/vm/bench-ticketmoa-support-20261105-034838.json`** | 2026-11-05 12:48:38 KST *(파일명 UTC 03:48)* | **팀 VM (`445ba2d`, 42청크)** | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | **p50 5.45s · p95 6.00s** · max 6.00s · 실패 0/5 |
