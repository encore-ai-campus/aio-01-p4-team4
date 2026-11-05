# 보안 검증 연결 가이드 (선택형)

`security/`의 검증 도구(promptfoo, PyRIT)는 **서비스의 상시 요청 흐름에 들어 있지 않다.** 기본은 꺼져 있고, 필요할 때만 아래 순서로 붙였다가 떼어 낸다. 워크플로우와 공통 계약은 바꾸지 않는다. 도구는 고객처럼 바깥에서 웹훅을 부를 뿐이다.

```
[상시 경로]  고객 → ticketmoa-support → agents / refund / tech … → 응답       (n8n, 항상 켜짐)
[선택 경로]  시험 도구 ─HTTP→ ticketmoa-support (같은 계약, 팀 키)              (필요할 때만)
                └→ 결과 파일 (runs/ 또는 security/promptfoo/results/)
```

## 언제 켜나

| 때 | 무엇을 | 도구 |
| --- | --- | --- |
| 워크플로우를 고친 뒤 (커밋 전) | 보안 회귀: 주입·권한·가림·환불 위조 | promptfoo |
| 기능 동결 전 1회, 발표 전 1회 | 다양한 변형·다회차 공격 탐색 | PyRIT (설계 예시) |
| 장애 시나리오 확인 | 요청 폭주·큰 입력 | promptfoo abuse 세트 |

## 연결 방법 3가지

| 방식 | 대상 | 언제 | 필요한 것 |
| --- | --- | --- | --- |
| A. 계약 모형 서버 | `security/promptfoo/mock-webhook.cjs` | n8n 없이 시험 설계만 확인 | Node 22+ |
| B. 로컬 n8n | 각자 PC의 n8n 웹훅 | 내 파일을 고친 직후 | n8n, 팀 키 Credential |
| C. 팀 서버 n8n | 서버의 n8n 웹훅 (SSH 터널 또는 서버 안에서 실행) | 병합 뒤 회귀, 결과서 숫자 | 리드 허락, 팀 키 |

서버 주소·포트·비밀번호는 이 문서에 쓰지 않는다. 리드에게 받는다.

## 순서: 연결 → 실행 → 저장 → 종료

1. **연결 설정** (셸 환경 변수로만. 파일에 쓰지 않는다)
   ```bash
   export PF_TARGET_URL=<웹훅 주소>/webhook/ticketmoa-support
   export PF_TEAM_KEY=<팀 키>            # n8n Credential ticketmoa-team-key와 같은 값
   export PF_RESET_URL=<캐시 비우기 주소> # 환불·대응 세트만
   ```
2. **실행**
   - promptfoo: `npx promptfoo@0.125.1 eval -c security/promptfoo/promptfooconfig.refund.yaml --no-cache --no-share --delay 13000`
   - PyRIT: `security/pyrit/README.md`의 실행 예시 (별도 Python 가상환경)
3. **저장**: 결과 JSON·HTML을 `runs/`(E와 합의) 또는 `security/promptfoo/results/`에 날짜를 붙여 둔다. 결과에 키·연락처 원문이 없는지 `tscan scan`으로 확인.
4. **종료**: 환경 변수를 지우고(`unset PF_TEAM_KEY`), 모형 서버·결과 뷰어를 끈다. 캐시를 비워 시험 흔적(견적, 요청 제한 기록)을 남기지 않는다.

## 지켜야 할 것

- **상시 경로에 넣지 않는다.** 시험 도구를 n8n 노드로 만들거나 본체가 부르게 하지 않는다.
- **같은 계약으로만 부른다.** 시험 전용 우회 경로·디버그 헤더를 만들지 않는다.
- **비용:** 실제 n8n은 LLM을 부른다. 강사 키를 함께 쓰므로 반복은 3회까지, PyRIT의 공격자 LLM 방식은 팀 합의 후에만.
- **요청 제한:** 같은 사용자로 여러 번 보내는 세트는 `--delay 13000` (60초 5건 제한).
- **공유:** 결과 외부 공유 끄기 (`--no-share`, `sharing: false`). 실제 고객 데이터로 시험하지 않는다 (가짜 users·records만).
