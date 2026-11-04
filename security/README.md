# security/ · B 오케스트레이션 보안 (최강현)

두 층으로 나뉜다.

| 층 | 무엇 | 상시 동작? |
| --- | --- | --- |
| **안전장치** (워크플로우 안) | 환불 견적 묶음, context 무시, 확정 조건, attempt 3회 LLM 생략, Credential 규칙. 원본 함수 `refund-guard.js` | 예. n8n 노드에 들어가 항상 동작 |
| **보안 검증 계층** (워크플로우 밖) | promptfoo 회귀 시험(구현), PyRIT 탐색(설계 예시) | **아니오.** 필요할 때 `CONNECT.md` 순서로 연결해 실행하고 끈다 |

공통 계약, 다른 사람 워크플로우, `lib/common.js`, `cases/`는 건드리지 않는다.

## 파일

| 파일 | 내용 |
| --- | --- |
| [refund-threat-model.md](refund-threat-model.md) | 위협 모델: 불변 조건 5개, 위협 T01~T10, 잔여 위험 |
| [refund-ontology.json](refund-ontology.json) | 보안 온톨로지(OAG): 고객·예매·견적·티켓 객체와 행동의 전제 조건 |
| [refund-guard.js](refund-guard.js) · [test/](test/refund-guard.test.js) | 안전장치 순수 함수 원본 (Code 노드에 복사) · 단위 시험 13개 |
| [CONNECT.md](CONNECT.md) | 검증 도구 연결 가이드: 연결 → 실행 → 저장 → 종료 |
| [promptfoo/](promptfoo/README.md) | 보안 회귀 시험 3세트 (공통 10 · 환불 10 · 대응 17), 계약 모형 서버, findings |
| [pyrit/](pyrit/README.md) | PyRIT 탐색 설계 예시: jailbreak · prompt injection · data leakage · unsafe output · tool misuse · multi-turn |
| [presentation/](presentation/) | 공격 대응 방침 예시 PDF |

## 워크플로우에 들어간 것

- `workflows/ticketmoa-refund.json`: 견적에 `owner`·`expires_at`, `ignored_context`, 확정 시 같은 사용자·예매·만료 전 검사
- `workflows/ticketmoa-agents.json`: Credential `OpenAI (.env)`, `LLM 필요?`에 attempt < 3 (F-003)
- 출발점은 `hwanseok-mvp` 판. 노드 구성은 그대로, Code 노드·조건·Credential만 바꿈

## 시험

```powershell
node --test security/test/*.test.js lib/test/*.test.js
node security/promptfoo/mock-webhook.cjs        # 다른 터미널
npx promptfoo@0.125.1 eval -c security/promptfoo/promptfooconfig.refund.yaml --no-cache --no-share
```
