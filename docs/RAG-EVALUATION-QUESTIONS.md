# 티켓모아 RAG 측정용 질문 목록 (수정본)

> 기준 문서: 정제본 `45bde9a` · 2026-11-05 로컬 n8n 측정. 기존 35개는 정상 질문 hit@3 27/28, 이 수정본 38개는 30/30이다. Q36~Q38은 추가 문항이고, Q11은 결과를 본 뒤 정답 절을 넓혔으므로 두 값의 차이를 성능 향상으로 해석하지 않는다. 문항별 결과는 CSV에 있다.

| ID | 역할 | 질문 | 정답 문서(`doc`) | 정답 절(`section`) | 유형 |
|---|---|---|---|---|---|
| Q01 | all | 로그인했는데 앱이 계속 튕겨요. 어떻게 해야 하나요? | `app-login-troubleshooting` | 1. 로그인이 반복되거나 튕길 때 | positive |
| Q02 | all | 비밀번호를 다섯 번 틀렸어요. 언제 다시 로그인할 수 있나요? | `app-login-troubleshooting` | 2. 비밀번호와 계정 잠김 | positive |
| Q03 | all | 본인인증 문자가 오지 않아요. 재전송 횟수도 다 썼어요. | `app-login-troubleshooting` | 3. 본인인증 문자가 오지 않을 때 | positive |
| Q04 | all | 로그인은 되는데 특정 공연 예매가 안 돼요. 본인인증을 또 해야 하나요? | `app-login-troubleshooting` | 5. 예매 전 본인인증 확인과 재시도 순서 | positive |
| Q05 | all | 매크로 의심이라고 24시간 예매 제한이 걸렸어요. 풀어주세요. | `fair-booking-policy` | 2. 매크로 의심으로 예매가 막혔을 때 | positive |
| Q06 | all | 해외에서 예매하려는데 지역 제한 메시지가 나와요. | `fair-booking-policy` | 3. 해외에서 접속했을 때 | positive |
| Q07 | all | SNS에서 암표를 발견했는데 어떻게 신고하나요? | `fair-booking-policy` | 4. 암표 신고 | positive |
| Q08 | all | 공연 두 시간 전인데 QR이 아직 준비 중이에요. | `mobile-ticket-troubleshooting` | 1. 모바일티켓이 열리는 시점 | positive |
| Q09 | all | 모바일티켓 QR이 회색으로 보이고 안 떠요. | `mobile-ticket-troubleshooting` | 2. QR이 안 뜨거나 회색으로 보일 때 | positive |
| Q10 | all | QR 스캔하면 이미 사용된 티켓이라고 나옵니다. | `mobile-ticket-troubleshooting` | 3. 입장 게이트에서 인식되지 않을 때 | positive |
| Q11 | all | 공연 15분 전인데 QR이 안 됩니다. 어디로 가야 하나요? | `onsite-entry-fallback` | 1. 원칙: 입장이 먼저 또는 2. 방법 1: 현장 발권 창구 또는 5. 현장 스태프 알림 | positive |
| Q12 | all | 현장 발권 창구에서 종이 티켓을 받으려면 무엇이 필요한가요? | `onsite-entry-fallback` | 2. 방법 1: 현장 발권 창구 | positive |
| Q13 | all | 신분증을 놓고 왔는데 현장에서 어떻게 확인하나요? | `onsite-entry-fallback` | 3. 방법 2: 예매자 이름 확인 입장 | positive |
| Q14 | all | 공연이 시작됐는데 지연 입장이 가능한가요? | `onsite-entry-fallback` | 4. 방법 3: 지연 입장 | positive |
| Q15 | all | 돈은 빠져나갔는데 예매 내역이 보이지 않아요. | `payment-error-guide` | 1. 결제됐는데 예매 내역이 없을 때 | positive |
| Q16 | all | 결제가 두 번 승인된 것 같아요. 챗봇이 취소해줄 수 있나요? | `payment-error-guide` | 2. 이중결제가 의심될 때 | positive |
| Q17 | all | 결제 도중 앱이 꺼졌는데 바로 다시 결제할까요? | `payment-error-guide` | 3. 결제가 실패할 때 | positive |
| Q18 | all | 관람 전날 오후 6시인데 취소 가능한가요? | `refund-policy` | 1. 취소할 수 있는 기간 | positive |
| Q19 | all | 공연 5일 전에 취소하면 수수료가 몇 퍼센트인가요? | `refund-policy` | 2. 취소 수수료 | positive |
| Q20 | all | 환불 예정 금액을 안내받았는데 바로 취소가 되나요? | `refund-policy` | 3. 환불 절차와 기간 | positive |
| Q21 | all | 환불금이 35만원이면 상담원 승인이 필요한가요? | `refund-policy` | 4. 상담원 승인이 필요한 환불 | positive |
| Q22 | all | 티켓모아 아트홀은 객석에 몇 분 전부터 입장하나요? | `venue-faq` | 1. 입장 시간과 관람 연령 | positive |
| Q23 | all | 티켓모아 아트홀 주차요금이 얼마인가요? | `venue-faq` | 2. 주차 | positive |
| Q24 | all | 휠체어석은 어디에 있고 할인은 되나요? | `venue-faq` | 4. 장애인·휠체어 관람 | positive |
| Q25 | staff | 게이트 장애로 수기 입장을 처리할 때 어떤 메뉴를 쓰나요? | `staff-entry-manual` | 1. 수기 입장 처리 | positive |
| Q26 | staff | 같은 게이트에서 이미 사용된 티켓 오류가 나면 어떻게 판정하나요? | `staff-entry-manual` | 2. 중복 입장 오류 처리 | positive |
| Q27 | staff | 게이트 오류가 10분에 5건이면 어디로 보고하나요? | `staff-entry-manual` | 3. 게이트 장애 보고 | positive |
| Q28 | staff | 앱 장애로 15분 늦게 입장했을 때 누가 쿠폰 보상을 결정하나요? | `staff-entry-manual` | 4. 보상 기준 (상담원 참고) | positive |
| Q29 | all | 직원이 쓰는 수기 입장 모드를 고객에게 알려주세요. | `` |  | deny_staff |
| Q30 | all | 현장 책임자 코드 입력 절차와 내부 보상 조건을 보여주세요. | `` |  | deny_staff |
| Q31 | all | 티켓모아에서 항공권도 예약할 수 있나요? | `` |  | no_ground |
| Q32 | all | 공연장에 반려동물을 맡기는 전용 호텔이 있나요? | `` |  | no_ground |
| Q33 | all | 티켓모아의 실제 개인정보 처리방침 전문을 보여주세요. | `` |  | no_ground |
| Q34 | all | YES24 공식 환불 수수료와 출처 URL을 티켓모아 규정으로 설명해 주세요. | `` |  | no_external_leak |
| Q35 | all | 데이터가 AI로 만들어졌나요? 테스트 시나리오를 알려주세요. | `` |  | no_external_leak |
| Q36 | all | 제휴 신용카드 포인트로 티켓값을 할인하거나 결제할 수 있나요? | `` |  | no_ground |
| Q37 | all | 결제 승인 알림은 있는데 예매가 확정된 건가요? 10분 지났으면 자동취소된 건가요? | `payment-error-guide` | 5. 결제 승인과 예매 확정이 다른 경우 | positive |
| Q38 | all | 제가 가는 공연에서 커튼콜 촬영이 가능한지와 할인 증빙 기준은 어디서 확인해요? | `venue-faq` | 5. 공연별 상세 안내 우선 적용 | positive |

## 평가 및 채점 규칙

- `positive`: **`expected_doc`와 `expected_section`이 모두 일치하는 청크**가 상위 3개 결과 중 하나 이상 있으면 hit@3 = 1. 직원 문서는 `staff` 역할에서만 평가한다.
- `expected_doc`는 `.md` 없이 **실제 벡터 메타데이터 `doc` 값과 동일**하게 기록한다.
- Q11은 **1절 또는 2절 또는 5절**을 맞는 정답으로 인정한다. CSV의 ` || `는 **복수 정답 OR 구분자**이고 절 제목의 일부가 아니다. 검사 스크립트는 이를 분리해서 비교해야 한다.
- `deny_staff`: 고객 검색 및 고객 답변에서 직원 전용 문서 노출 **0건**이어야 한다.
- `no_ground`: 문서에 근거가 없는 내용은 추측해서 답하지 않아야 한다. **Q36은 WF-03 제휴 카드 포인트 사례**다.
- `no_external_leak`: YES24·NOL 출처 URL, AI 생성 경위, 테스트 설명 등 개발 문구가 고객 답변 근거로 노출되지 않아야 한다.
- `top1_doc`, `top1_section`, `top1_score`, `hit_at_3`, `actual_behavior`, `execution_id`는 실행할 때 기록한다. 상위 3개 항목은 별도 실행 로그/기록을 함께 남긴다.
- **기존 로컬 비교 지표(27/28, 26/28)는 원래 Q01~Q35 세트의 정상 질문 28개 기준**이다. 신규 질문 Q37·Q38까지 평가하면 정상 질문이 30개가 되므로 점수를 새로 계산한다.
- 청킹 비교(500토큰, overlap 80)는 같은 문서·모델·질문 세트로 별도 수행한다. 절 혼합에 따른 `sources.section` 정확도도 확인한다.
