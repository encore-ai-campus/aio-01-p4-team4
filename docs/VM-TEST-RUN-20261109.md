# 팀 VM 회귀 시험 기록 · 2026-11-09 (V행)

- 시각: 2026-11-09 11:45:32 ~ 11:49:06 KST
- 위치: 팀 VM `aio-t4`, 웹 터미널 `https://aio-t4.isitsoft.kr/ssh/` → `~/aio-01-p4-team4`
- 실행: 심환석 (Claude Code가 웹 터미널에 명령 입력)
- 소스: 서버의 워크플로우 10개와 케이스 3개가 `origin/main` `ad9073a`(11/09 11:03)와 SHA-256이 모두 같다 (1단계)
- 이번 회차에서 하지 않은 것: n8n 재시작, 워크플로우 배포(`push`), 재색인. 이미 떠 있던 n8n과 색인에 그대로 시험했다.

## 결과 요약

| 시험 | 명령 | 결과 | 보고서 (VM) |
| --- | --- | --- | --- |
| 공통 시나리오 (14유형 17케이스 × 3회) | `flow.py test r1109-common.json --repeat 3` | 14유형 모두 실행, 세부 판정 **50/51**. 실패 1건: WF-01 3회차 | `r1109-common-20261109-024734.json` |
| 팀 시나리오 (13케이스 × 1회) | `flow.py test r1109-team.json` | **13/13** | `r1109-team-20261109-024827.json` |
| 보안 시나리오 (8케이스 × 1회) | `flow.py test r1109-security-permissions.json` | **8/8** | `r1109-security-permissions-20261109-024839.json` |
| 정상 문의 `bench -n 5` | `flow.py bench ticketmoa-support requests/wf01.json -n 5` | p50 **5.21초**, p95 **5.58초**, 실패 **0/5** | `bench-ticketmoa-support-20261109-024906.json` |

- **장애 시나리오:** WF-04·WF-10·WF-11은 9/9 통과했다. 시험이 끝난 뒤 고장 스위치는 전부 `ok`, OpenAI 키도 원래 값으로 돌아왔다.
- **실패 1건:** WF-01 3회차가 `담당자 이관`(`verification_failed`)으로 끝났다. 답변 검증 단계가 `llm_unavailable`을 냈기 때문이다(아래 "실패 분석").
- **보고서 위치:** 4개 보고서는 VM `~/aio-tools/Last3Mon/78/runs/`에만 있고 저장소에는 넣지 못했다(VM에서 파일을 꺼낼 경로가 없음). 이 문서의 표는 실행 직후 VM에서 보고서를 읽어 옮긴 값이다.

---

## 0. 접속

**명령어**

```text
브라우저에서 https://aio-t4.isitsoft.kr/ssh/ 접속 → 서버 계정으로 로그인 (계정·비밀번호는 기록하지 않음)
cd ~/aio-01-p4-team4
```

**결과**

```text
toor@aio-t4:~/aio-01-p4-team4$
```

시험은 아래 스크립트 하나(`/tmp/reg1109/run.sh`)로 돌렸다. 저장소 폴더는 고치지 않았고, 스크립트·복사본 케이스·로그는 모두 `/tmp/reg1109/`에 있다. 스크립트 전문은 문서 끝 부록 A에 있다.

```bash
bash /tmp/reg1109/run.sh 2>&1 | tee /tmp/reg1109/run.log
```

## 1. 배포 소스 확인

**명령어**

```bash
sha256sum workflows/*.json cases/*.json | cut -c1-12,65-
```

**결과** (서버 값. 로컬 `git show origin/main:<파일> | shasum -a 256`과 13개 모두 일치)

| SHA-256 앞 12자리 | 파일 | `origin/main` `ad9073a` |
| --- | --- | --- |
| `bccce0c40e22` | `workflows/ticketmoa-agents.json` | 일치 |
| `a0ee51a88df5` | `workflows/ticketmoa-errors.json` | 일치 |
| `c61e824ad277` | `workflows/ticketmoa-handoff.json` | 일치 |
| `18ed0b8d067e` | `workflows/ticketmoa-index.json` | 일치 |
| `9ed4648e888c` | `workflows/ticketmoa-ops.json` | 일치 |
| `8037a6556e8e` | `workflows/ticketmoa-payment.json` | 일치 |
| `79fa901fac15` | `workflows/ticketmoa-refund.json` | 일치 |
| `e8950bcf62c8` | `workflows/ticketmoa-search.json` | 일치 |
| `1c7f5660cbf7` | `workflows/ticketmoa-support.json` | 일치 |
| `035c2e916e0e` | `workflows/ticketmoa-tech.json` | 일치 |
| `870a23008d76` | `cases/common.json` | 일치 |
| `bd4b5e7041e0` | `cases/security-permissions.json` | 일치 |
| `c3f012793817` | `cases/team.json` | 일치 |

이 표가 보여 주는 것은 서버 폴더의 파일이 main과 같다는 것까지다. n8n에 활성화된 워크플로우가 이 파일과 같은지는 이번에 비교하지 않았다.

## 2. 시험 전 상태

**명령어** (데이터 API 조회, 스크립트의 `st` 함수)

```bash
python3 -c "
import json,urllib.request as u
g=lambda p: json.load(u.urlopen('http://localhost:8800'+p,timeout=10))
c=g('/tickets-created');d=g('/dlq');a=g('/alerts');f=g('/admin/fault')
print('tickets',c.get('count'),'dlq',d.get('size'),'alerts',a.get('count'),'fault',json.dumps(f))"
```

**결과**

```text
tickets 10 dlq 35 alerts 104 fault {"faq": "ok", "tickets": "ok", "prompts": "ok", "usage": "ok", "dlq": "ok", "slow_seconds": 8.0}
```

## 3. 케이스 복사 (공용 데이터 보호)

`cases/common.json`과 `cases/team.json`은 시작할 때 `/tickets-reset`으로 공용 티켓을 모두 지운다. 다른 팀원과 웹앱이 쓰는 티켓을 지우지 않으려고 `/tmp`에 복사본을 만들었다. 복사본에서는 그 단계만 빼고, 다른 시험과 겹치지 않게 `request_id` 앞에 `r1109-`를 붙였다. 기대 결과(`expect`)와 케이스별 장애 스위치(`before`·`after`)는 바꾸지 않았다. 11/07 T행과 같은 방식이다.

**명령어**

```bash
python3 - <<'PY'
import json
def fx(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='request_id' and isinstance(v,str): o[k]='r1109-'+v
            else: fx(v)
    elif isinstance(o,list):
        for v in o: fx(v)
for n in ('common','team','security-permissions'):
    d=json.load(open(f'cases/{n}.json'))
    d.pop('before',None)
    fx(d['cases'])
    json.dump(d,open(f'/tmp/reg1109/r1109-{n}.json','w'),ensure_ascii=False,indent=1)
print('copied 3 case files: suite before removed, request_id prefixed r1109-')
PY
```

**결과**

```text
copied 3 case files: suite before removed, request_id prefixed r1109-
```

## 4. 예열

**명령어**

```bash
uv run --env-file .env tools/demo.py --warm
```

**결과** (11:45:33 KST)

```text
예열 1: HTTP 200, 8.0초, 자동 답변
예열 2: HTTP 200, 6.4초, 자동 답변
```

예열 호출 2건은 시험 집계에 넣지 않는다. 첫 예열 호출이 8.0초로, 쉬고 난 뒤 첫 호출이 느린 현상이 이번에도 나왔다.

## 5. 공통 시나리오 (3회 반복)

**명령어** (11:45:47 KST 시작)

```bash
export FLOW_PY=~/aio-tools/Last3Mon/78/tools/flow.py
uv run --env-file .env tools/flow.py test /tmp/reg1109/r1109-common.json --webhook ticketmoa-support --repeat 3
```

**결과:** `Passed 50/51`, 보고서 `runs/r1109-common-20261109-024734.json`

| 시나리오 | 판정 1 / 2 / 3회 | 시간(초) | route · reason | 티켓 | 근거 문서 · 가림 | LLM |
| --- | --- | --- | --- | --- | --- | --- |
| WF-01 정상 문의 | ✔ / ✔ / **✘** | 5.5 / 5.4 / 6.3 | 1·2회 자동 답변. **3회 담당자 이관 `verification_failed`** | 3회 `T-2011` | 1·2회 `mobile-ticket-troubleshooting`, 3회 없음 | 3 |
| WF-02 정보 부족 | ✔ ✔ ✔ | 1.7 / 1.7 / 1.5 | 보완 질문 `low_confidence_or_missing` | 없음 | - | 1 |
| WF-02b 보완 질문 한도 | ✔ ✔ ✔ | 0.5 / 0.6 / 0.6 | 담당자 이관 `clarify_limit_reached` | `T-2012` (2·3회 duplicate) | - | 0 |
| WF-03 지식에 없음 | ✔ ✔ ✔ | 1.9 / 2.0 / 2.3 | 담당자 이관 `unregistered_intent` | `T-2013` (2·3회 duplicate) | sources 없음 | 1 |
| WF-04 티켓 API 장애 | ✔ ✔ ✔ | 3.5 / 3.6 / 3.5 | 담당자 이관 `unregistered_intent` | `ticket: null` | - | 1 |
| WF-05 권한 없는 문서 | ✔ ✔ ✔ | 2.0 / 1.8 / 1.8 | 담당자 이관 `staff_only_request` | `T-2014` (2·3회 duplicate) | 직원 문서 없음 | 1 |
| WF-06 남의 건 | ✔ ✔ ✔ | 0.5 / 0.5 / 0.5 | 권한 없음 `not_owner` | 없음 | - | 0 |
| WF-07 개인정보 | ✔ ✔ ✔ | 0.5 / 0.5 / 0.5 | 자동 답변 | 없음 | 연락처 가림 `masked: 2` | 0 |
| WF-08 주입 | ✔ ✔ ✔ | 0.1 / 0.2 / 0.1 | 차단 `injection_pattern` (`blocked_by: rule`) | 없음 | - | 0 |
| WF-09 중복 요청 (1회째) | ✔ ✔ ✔ | 2.0 / 2.3 / 2.1 | 담당자 이관 `payment_error_handoff` | `T-2015` (2·3회 duplicate) | - | 1 |
| WF-09 중복 요청 (2회째, 같은 request_id) | ✔ ✔ ✔ | 2.0 / 2.0 / 2.1 | 담당자 이관 `payment_error_handoff` | `T-2015` duplicate | - | 1 |
| WF-10 LLM 멈춤 | ✔ ✔ ✔ | 1.3 / 0.9 / 0.9 | 담당자 이관 `agents_failed` | `T-2016` (2·3회 duplicate) | - | 0 |
| WF-11 느린 외부 API (8초 지연) | ✔ ✔ ✔ | 5.6 / 5.6 / 5.6 | 담당자 이관 `payment_failed` | `ticket: null` | - | 0 |
| WF-12 복합·긴급 | ✔ ✔ ✔ | 4.0 / 3.9 / 4.0 | 담당자 이관 `urgent_entry` | `T-2018` high (2·3회 duplicate) | `onsite-entry-fallback`, `masked: 2` | 3 |
| WF-13 잘못된 입력 · 빈 질문 | ✔ ✔ ✔ | 0.1 / 0.1 / 0.1 | HTTP 400 `empty_question` | - | - | - |
| WF-13 잘못된 입력 · 없는 사용자 | ✔ ✔ ✔ | 0.1 / 0.1 / 0.1 | HTTP 400 `unknown_user` | - | - | - |
| WF-13 잘못된 입력 · 501자 | ✔ ✔ ✔ | 0.1 / 0.1 / 0.2 | HTTP 400 `question_too_long` | - | - | - |

장애 단계 출력 (같은 실행):

```text
✔ before: HTTP 200 · 0.0s          ← WF-04 앞, 티켓 API 고장 스위치 켬
✔ after: HTTP 200 · 0.0s           ← WF-04 뒤, 되돌림
✔ OpenAI credential: real key from .env restored
✔ after: LLM up                    ← WF-10 뒤, LLM 되돌림
✔ before: HTTP 200 · 0.0s          ← WF-11 앞, 느린 API(8초) 켬
✔ after: HTTP 200 · 0.0s           ← WF-11 뒤, 되돌림
```

- 3회 모두 같은 `request_id`를 쓰므로, 티켓이 생기는 시나리오는 2·3회차에 새 티켓을 만들지 않고 1회차 티켓을 `duplicate: true`로 돌려받았다. 중복 방지(티켓 `key` = `request_id`)가 동작했다는 뜻이다.
- `T-2017`은 응답에 나오지 않았다. WF-11(`ticket: null`) 뒤에 데이터 API가 저장한 지연 티켓으로 추정하며, 확인하지는 않았다.

## 6. 팀 시나리오

**명령어** (11:47:34 KST)

```bash
uv run --env-file .env tools/flow.py test /tmp/reg1109/r1109-team.json --webhook ticketmoa-support
```

**결과:** `Passed 13/13`, 보고서 `runs/r1109-team-20261109-024827.json`

| 시나리오 | 판정 | 시간(초) | route · reason | 티켓 | 근거 문서 | LLM |
| --- | --- | --- | --- | --- | --- | --- |
| TM-01 앱 로그인 | ✔ | 4.9 | 자동 답변 | 없음 | `app-login-troubleshooting` | 3 |
| TM-02 환불 1차 (금액 안내) | ✔ | 2.4 | 자동 답변 `refund_quote_pending_confirm` | 없음 | `refund-policy` | 1 |
| TM-03 환불 2차 (확인 후 티켓) | ✔ | 0.7 | 담당자 이관 `refund_confirmed` | `T-2019` | `refund-policy` | 0 |
| TM-04 지나치게 막지 않음 | ✔ | 2.0 | 담당자 이관 `customer_asked_human` | `T-2020` | - | 1 |
| TM-05 이중결제 + 부정 감정 | ✔ | 2.1 | 담당자 이관 `strong_negative_sentiment` | `T-2021` | `payment-error-guide` | 1 |
| TM-06 경계 · 당일 취소 | ✔ | 2.2 | 담당자 이관 `show_day_cancel` | `T-2022` | `refund-policy` | 1 |
| TM-13 환불 30만원 초과 | ✔ | 2.5 | 담당자 이관 `over_limit` | `T-2023` | `refund-policy` | 1 |
| TM-07 매크로 제한 문의 | ✔ | 4.7 | 자동 답변 | 없음 | `fair-booking-policy` | 3 |
| TM-08 암표 신고 | ✔ | 1.9 | 담당자 이관 `registry_handoff` | `T-2024` | - | 1 |
| TM-09 반복 요청 6번째 (가산) | ✔ | 0.2 | 차단 `too_many_requests` (`blocked_by: rate_limit`) | 없음 | - | 0 |
| TM-10 해외 IP (가산) | ✔ | 0.2 | 차단 `country_not_allowed` (`geo`) | 없음 | - | 0 |
| TM-11 블랙리스트 IP (가산) | ✔ | 0.2 | 차단 `macro_detected` (`ip_blocklist`) | 없음 | - | 0 |
| TM-12 국내 IP 정상 처리 (가산) | ✔ | 5.1 | 자동 답변 | 없음 | `mobile-ticket-troubleshooting` | 3 |

TM-09 앞의 사전 호출 5건(`before: HTTP 200` 4.7 / 3.8 / 5.2 / 4.1 / 5.5초)은 차단 한도를 채우기 위한 요청이며 집계에 넣지 않는다. 티켓 `T-2025`~`T-2027`이 이 사전 호출에서 생긴 것인지는 확인하지 않았다(추정).

## 7. 보안 시나리오

**명령어** (11:48:27 KST)

```bash
uv run --env-file .env tools/flow.py test /tmp/reg1109/r1109-security-permissions.json --webhook ticketmoa-support
```

**결과:** `Passed 8/8`, 보고서 `runs/r1109-security-permissions-20261109-024839.json`

| 시나리오 | 판정 | 시간(초) | route · reason | 티켓 | 가림 · 근거 |
| --- | --- | --- | --- | --- | --- |
| SEC-01 직원 이름으로 직원 문서 요청 | ✔ | 2.0 | 담당자 이관 `staff_only_request` | `T-2028` | 직원 문서 없음 |
| SEC-02 `access_level: staff` 값 무시 | ✔ | 2.0 | 담당자 이관 `staff_only_request` | `T-2029` | 직원 문서 없음 |
| SEC-03 직원 이름으로 타인 문의 조회 | ✔ | 0.7 | 권한 없음 `not_owner` | 없음 | - |
| SEC-04 staff 값으로 타인 환불 정보 조회 | ✔ | 2.2 | 보완 질문 `low_confidence_or_missing` | 없음 | - |
| SEC-05 본인 문의, 연락처 가림 | ✔ | 0.5 | 자동 답변 | 없음 | `masked: 2` |
| SEC-06 본인 문의 상태 조회 | ✔ | 0.5 | 자동 답변 | 없음 | `masked: 2` |
| SEC-07 긴급 복합 문의 | ✔ | 4.0 | 담당자 이관 `urgent_entry` | `T-2030` high | `onsite-entry-fallback`, `masked: 2` |
| SEC-08 고객 이름으로 타인 문의·연락처 조회 | ✔ | 0.5 | 권한 없음 `not_owner` | 없음 | - |

## 8. 정상 문의 응답 시간

**명령어** (11:48:39 KST)

```bash
uv run --env-file .env tools/flow.py bench ticketmoa-support requests/wf01.json -n 5
```

**결과**, 보고서 `runs/bench-ticketmoa-support-20261109-024906.json`

```text
POST http://localhost:5678/webhook/ticketmoa-support × 5
✔ #1 · HTTP 200 · 5.37s · route 자동 답변
✔ #2 · HTTP 200 · 4.80s · route 자동 답변
✔ #3 · HTTP 200 · 5.58s · route 자동 답변
✔ #4 · HTTP 200 · 5.21s · route 자동 답변
✔ #5 · HTTP 200 · 5.13s · route 자동 답변
p50 5.21s · p95 5.58s · max 5.58s · failures 0/5
```

## 9. 시험 후 상태

**명령어:** 2단계와 같은 조회

**결과** (11:49:06 KST)

```text
tickets 30 dlq 37 alerts 108 fault {"faq": "ok", "tickets": "ok", "prompts": "ok", "usage": "ok", "dlq": "ok", "slow_seconds": 8.0}
```

| 항목 | 시험 전 | 시험 후 | 차이 |
| --- | --- | --- | --- |
| 티켓 | 10 | 30 | +20 (`T-2011`~`T-2030`) |
| DLQ | 35 | 37 | +2 |
| 알림 | 104 | 108 | +4 |
| 고장 스위치 | 전부 `ok` | 전부 `ok` | 되돌림 확인 |

DLQ와 알림이 각각 어느 시나리오에서 늘었는지는 하나하나 대조하지 않았다.

## 실패 분석 · WF-01 3회차

**명령어** (보고서에서 WF-01 응답만 출력)

```bash
python3 -c "
import json;d=json.load(open('/home/toor/aio-tools/Last3Mon/78/runs/r1109-common-20261109-024734.json'))
for r in d['results']:
    b=r.get('response') or {}
    if 'wf01' in str(b.get('request_id')): print(round(r.get('seconds',0),2),b.get('route'),b.get('reason'),json.dumps(b.get('timings')),json.dumps(b.get('agents'))[:300])
"
```

**결과**

| 회차 | 호출자 시간 | route · reason | n8n 내부 시간 (`timings`, ms) | agents |
| --- | --- | --- | --- | --- |
| 1 | 5.5초 | 자동 답변 | total 5,371 · agents 1,394 · search 347 · tech 3,549 | LLM 3회, `tech_issue`, 확신도 0.95 |
| 2 | 5.4초 | 자동 답변 | total 5,204 · agents 1,239 · search 328 · tech 3,558 | LLM 3회 |
| 3 | 6.3초 | **담당자 이관 `verification_failed`** | total 6,162 · agents 1,396 · search 402 · tech 4,072 · handoff 201 | LLM 3회, `verification_issues: ["llm_unavailable"]`, 티켓 `T-2011` |

- **증상:** 3회차는 분류와 검색은 정상이었고, 답변 검증에서 `llm_unavailable`이 나왔다. 그래서 설계대로 자동 답변을 내보내지 않고 담당자 이관으로 바꿨다(fail-closed).
- **원인 (추정):** tech 시간이 4,072ms로 1·2회차보다 약 0.5초 길었다. 검증 모델 호출이 시간 제한(검증 2초) 안에 끝나지 않은 것으로 보이지만, n8n 실행 화면에서 확인하지는 않았다. 11/07 결과서의 미결 문제 "모델 응답 변동"과 같은 종류다.
- **판정:** 기대 결과(`자동 답변`, 근거 문서 포함)와 달라 **실패**로 센다. 재시험해 통과한 결과로 바꿔 적지 않는다.
- **안전성:** 근거 없는 자동 답변은 나가지 않았다. 이관 티켓이 만들어졌고 HTTP 200으로 응답했다.

## 이 회차의 조건과 한계

- **1회차 결과:** 예열 뒤 한 회차다. 공통은 3회 반복이지만 회차 전체를 다시 돌리지 않았다.
- **재시작·배포·재색인 없음:** 이미 떠 있던 n8n과 색인에 시험했다. 색인이 마지막으로 만들어진 시각은 확인하지 않았다. 다만 WF-01·TM-01·TM-07·TM-12·WF-12의 근거 문서가 정상으로 나와 공개 색인은 동작 중이었다.
- **공용 서버:** 같은 시간에 다른 팀원이 n8n을 썼을 수 있다. 11:19 KST에 팀원 한 명이 원본 `cases/team.json`을 실행했는데(`team-20261109-021946.json`), 이때 `/tickets-reset`으로 티켓이 비워졌을 것으로 추정한다. 그래서 이번 회차의 티켓 번호가 `T-2011`부터 시작했다.
- **장애 스위치·키 변경:** 시험 도중 WF-04·10·11이 고장 스위치와 OpenAI 키를 잠깐 바꿨고, 끝난 뒤 되돌아간 것을 9단계에서 확인했다.
- **시간 구분:** "시간(초)"는 `flow.py`가 잰 호출자 전체 응답 시간이다. n8n 내부 시간은 응답의 `timings`이고, 실패 분석 표에만 적었다.

## 부록 A. 실행 스크립트 (`/tmp/reg1109/run.sh`)

```bash
#!/bin/bash
cd ~/aio-01-p4-team4
set -a; . ./.env; set +a
export FLOW_PY=~/aio-tools/Last3Mon/78/tools/flow.py
R=/tmp/reg1109
k(){ TZ=Asia/Seoul date '+%F %T KST'; }
st(){ python3 -c "
import json,urllib.request as u
g=lambda p: json.load(u.urlopen('http://localhost:8800'+p,timeout=10))
c=g('/tickets-created');d=g('/dlq');a=g('/alerts');f=g('/admin/fault')
print('tickets',c.get('count'),'dlq',d.get('size'),'alerts',a.get('count'),'fault',json.dumps(f))"; }
echo "== start $(k)"
echo "== source sha256"; sha256sum workflows/*.json cases/*.json | cut -c1-12,65-
echo "== state before"; st
python3 - <<'PY'
(3단계의 케이스 복사 코드)
PY
echo "== warm $(k)"; uv run --env-file .env tools/demo.py --warm
echo "== common x3 $(k)"; uv run --env-file .env tools/flow.py test $R/r1109-common.json --webhook ticketmoa-support --repeat 3
echo "== team $(k)"; uv run --env-file .env tools/flow.py test $R/r1109-team.json --webhook ticketmoa-support
echo "== security $(k)"; uv run --env-file .env tools/flow.py test $R/r1109-security-permissions.json --webhook ticketmoa-support
echo "== bench $(k)"; uv run --env-file .env tools/flow.py bench ticketmoa-support requests/wf01.json -n 5
echo "== state after $(k)"; st
ls -t ~/aio-tools/Last3Mon/78/runs | head -4
echo "== end $(k)"
```

`.env`는 팀 키와 OpenAI 키를 셸 환경으로 읽기만 한다. 이 문서와 로그에는 키 값이 없다. 실행 로그 전체는 VM `/tmp/reg1109/run.log`에 있다(재부팅하면 지워진다).
