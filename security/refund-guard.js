// 환불 2단계 안전장치 (ticketmoa-refund용) · 담당 B 최강현
//
// 규칙: lib/common.js와 같다. n8n Code 노드는 파일을 불러올 수 없으니 필요한 함수만 복사해 쓴다.
// 이 파일을 고치면 `node --test security/test/*.test.js`를 통과시키고 노드에 다시 복사한다.
// 함수끼리 서로 부르지 않는다 (상수만 같이 복사). 날짜·금액 계산은 lib/common.js의 calcRefund를 쓴다.
//
// 원칙 (security/refund-threat-model.md 2절 불변 조건)
//   1. 신원은 요청의 user, 금액·소유자는 서버가 조회한 예매 기록에서만 온다. context의 값은 믿지 않는다.
//   2. 확정은 context.confirm === true 하나뿐이다. 질문 글이나 LLM 출력은 확정을 만들지 못한다.
//   3. 확정은 서버에 저장된 1차 견적(pending)에 묶인다: 같은 사용자 · 같은 예매 · 만료 전 · 한 번만.
//   4. 확정 시점에 금액을 다시 계산하고, 견적과 다르면 티켓을 만들지 않고 다시 안내한다.
//   5. 판단할 수 없으면 티켓을 만들지 않는다 (기본 거부).

const REFUND_PENDING_TTL_MIN = 30;  // 1차 견적 유효 시간 (분)
const UNTRUSTED_CONTEXT_FIELDS = ['user', 'requester', 'role', 'access_level', 'approved', 'approval',
  'amount', 'refund', 'refund_amount', 'fee', 'ticket', 'status', 'owner', 'record_id'];

/** /cache 키. 사용자와 예매번호를 둘 다 넣어 남의 견적을 꺼내 쓸 수 없게 한다. */
function pendingKey(user, bookingId) {
  return `pending:${user}:${bookingId}`;
}

/** context에 들어온, 믿지 않고 무시한 칸 이름 (로그·security.reason용). */
function ignoredContextFields(context) {
  const c = context && typeof context === 'object' ? context : {};
  return UNTRUSTED_CONTEXT_FIELDS.filter(k => k in c);
}

/**
 * 예매 기록에서 calcRefund 입력을 만든다. 금액·매수·날짜는 기록에서만 읽는다.
 * booking_id T20261104-0412 → 예매일 2026-11-04, show "… 2026-11-21 19:30 R석 2매" → 공연 시각·2매
 * @returns {{bookingId:string, amount:number, qty:number, bookedAt:string, showAt:string}|null}
 */
function bookingFromRecord(record) {
  const r = record || {};
  const b = /^T(\d{4})(\d{2})(\d{2})-/.exec(r.booking_id || '');
  const s = /(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})/.exec(r.show || '');
  if (!b || !s || typeof r.amount !== 'number') return null;
  const q = /(\d+)\s*매/.exec(r.show || '');
  return {
    bookingId: r.booking_id,
    amount: r.amount,
    qty: q ? Number(q[1]) : 1,
    bookedAt: `${b[1]}-${b[2]}-${b[3]}T12:00:00+09:00`,
    showAt: `${s[1]}T${s[2]}:00+09:00`,
  };
}

/**
 * 1차 요청 판단.
 * @param {{user:string, recordId:string, record:object, calc:object, now?:string|Date}} p
 *   record: 서버가 조회한 기록 (남의 건이면 payment가 forbidden을 준다 → record null로 넘김)
 *   calc:   calcRefund(bookingFromRecord(record)) 결과
 * @returns {{decision:'forbidden'|'clarify'|'handoff'|'quote', reason:string, pending?:object}}
 */
function quoteDecision(p) {
  const x = p || {};
  if (!x.record) return { decision: 'forbidden', reason: 'not_owner_or_missing' };
  if (x.record.requester !== x.user) return { decision: 'forbidden', reason: 'not_owner' };
  const c = x.calc;
  if (!c) return { decision: 'clarify', reason: 'cannot_calculate' };
  if (!c.allowed) return { decision: 'handoff', reason: 'after_deadline_or_show_day' };
  if (c.needsApproval) return { decision: 'handoff', reason: 'over_approval_limit' };
  const now = x.now ? new Date(x.now) : new Date();
  return {
    decision: 'quote',
    reason: '',
    pending: {
      key: pendingKey(x.user, x.record.booking_id),
      owner: x.user,
      record_id: x.recordId,
      booking_id: x.record.booking_id,
      amount: x.record.amount,
      fee: c.fee,
      refund: c.refund,
      rule: c.rule,
      quoted_at: now.toISOString(),
      expires_at: new Date(now.getTime() + REFUND_PENDING_TTL_MIN * 60000).toISOString(),
      status: 'pending',
    },
  };
}

/**
 * 2차 요청 판단. pending은 서버 /cache에서 pendingKey(요청 user, context.booking_id)로 읽은 값이다.
 * record·calc는 pending.record_id로 다시 조회·계산한 값이다 (검사와 사용 시점을 맞춤).
 * @returns {{decision:'cancel'|'clarify'|'forbidden'|'handoff'|'requote'|'create_ticket', reason:string, ticket?:object}}
 *   create_ticket이면 호출한 쪽이 먼저 pending.status를 'used'로 저장한 뒤 티켓을 만든다.
 */
function confirmDecision(p) {
  const x = p || {};
  const ctx = x.context && typeof x.context === 'object' ? x.context : {};
  if (ctx.confirm === false) return { decision: 'cancel', reason: 'customer_declined' };
  if (ctx.confirm !== true) return { decision: 'clarify', reason: 'confirm_not_boolean_true' };
  if (!ctx.booking_id) return { decision: 'clarify', reason: 'missing_booking_id' };
  const pd = x.pending;
  if (!pd) return { decision: 'clarify', reason: 'no_pending_quote' };
  if (pd.owner !== x.user) return { decision: 'forbidden', reason: 'pending_owner_mismatch' };
  if (pd.booking_id !== ctx.booking_id) return { decision: 'forbidden', reason: 'booking_mismatch' };
  if (pd.status !== 'pending') return { decision: 'clarify', reason: 'pending_already_used' };
  const now = x.now ? new Date(x.now) : new Date();
  if (now > new Date(pd.expires_at)) return { decision: 'clarify', reason: 'pending_expired' };
  if (!x.record || x.record.requester !== x.user) return { decision: 'forbidden', reason: 'not_owner' };
  const c = x.calc;
  if (!c) return { decision: 'clarify', reason: 'cannot_calculate' };
  if (!c.allowed) return { decision: 'handoff', reason: 'after_deadline_or_show_day' };
  if (c.needsApproval) return { decision: 'handoff', reason: 'over_approval_limit' };
  if (c.refund !== pd.refund) return { decision: 'requote', reason: 'amount_changed_since_quote' };
  return {
    decision: 'create_ticket',
    reason: 'customer_confirmed',
    // 티켓 본문은 pending과 기록에서만 만든다. context·질문 글은 넣지 않는다.
    ticket: {
      category: 'refund',
      priority: 'normal',
      summary: `환불 요청 확정: ${pd.booking_id} 환불 예정 ${pd.refund}원 (수수료 ${pd.fee}원, 규칙 ${pd.rule})`,
      booking_id: pd.booking_id,
      record_id: pd.record_id,
      refund: pd.refund,
      idempotency_key: `refund:${pd.owner}:${pd.booking_id}:${pd.quoted_at}`,
    },
  };
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    REFUND_PENDING_TTL_MIN, UNTRUSTED_CONTEXT_FIELDS,
    pendingKey, ignoredContextFields, bookingFromRecord, quoteDecision, confirmDecision,
  };
}
