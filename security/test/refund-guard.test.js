// node --test security/test/*.test.js
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const G = require('../refund-guard.js');
const C = require(path.join(__dirname, '..', '..', 'lib', 'common.js'));
const records = require(path.join(__dirname, '..', '..', 'data', 'records.json'));

const NOW = '2026-11-05T10:00:00+09:00';
const rec = records['C-2005']; // 이도윤, T20261104-0412, 152,000원 2매, 2026-11-21
const calcAt = (r, now) => C.calcRefund({ ...G.bookingFromRecord(r), now });
const quote = () => G.quoteDecision({ user: '이도윤', recordId: 'C-2005', record: rec, calc: calcAt(rec, NOW), now: NOW });
const confirm = (over = {}) => {
  const q = quote();
  return G.confirmDecision({
    user: '이도윤',
    context: { pending_action: 'refund_request', booking_id: 'T20261104-0412', confirm: true },
    pending: q.pending, record: rec, calc: calcAt(rec, NOW), now: NOW, ...over,
  });
};

test('기록에서만 금액·매수·날짜를 읽는다', () => {
  const b = G.bookingFromRecord(rec);
  assert.equal(b.amount, 152000);
  assert.equal(b.qty, 2);
  assert.equal(b.showAt, '2026-11-21T19:30:00+09:00');
  assert.equal(G.bookingFromRecord({ booking_id: 'x' }), null);
});

test('정상 1차: 견적과 pending (사용자·예매에 묶임)', () => {
  const q = quote();
  assert.equal(q.decision, 'quote');
  assert.equal(q.pending.key, 'pending:이도윤:T20261104-0412');
  assert.equal(q.pending.status, 'pending');
  assert.equal(q.pending.refund, 152000);
});

test('남의 기록으로 견적 금지 (confused deputy)', () => {
  const q = G.quoteDecision({ user: '박서준', recordId: 'C-2005', record: rec, calc: calcAt(rec, NOW), now: NOW });
  assert.equal(q.decision, 'forbidden');
});

test('30만원 초과는 견적 대신 바로 이관 (TM-13)', () => {
  const r = records['C-2006'];
  const q = G.quoteDecision({ user: '정민아', recordId: 'C-2006', record: r, calc: calcAt(r, NOW), now: NOW });
  assert.equal(q.decision, 'handoff');
  assert.equal(q.reason, 'over_approval_limit');
});

test('정상 2차: 티켓 본문은 pending에서만, 멱등 키 포함', () => {
  const d = confirm();
  assert.equal(d.decision, 'create_ticket');
  assert.equal(d.ticket.refund, 152000);
  assert.match(d.ticket.idempotency_key, /^refund:이도윤:T20261104-0412:/);
});

test('confirm은 boolean true만 (문자열 "true", 질문 글은 확정 아님)', () => {
  assert.equal(confirm({ context: { booking_id: 'T20261104-0412', confirm: 'true' } }).decision, 'clarify');
  assert.equal(confirm({ context: { booking_id: 'T20261104-0412' } }).decision, 'clarify');
  assert.equal(confirm({ context: { booking_id: 'T20261104-0412', confirm: false } }).decision, 'cancel');
});

test('견적 없이 확정 위조 → 티켓 없음', () => {
  assert.equal(confirm({ pending: null }).reason, 'no_pending_quote');
});

test('다른 사용자가 남의 pending으로 확정 (세션 가로채기) → forbidden', () => {
  const q = quote();
  const d = G.confirmDecision({ user: '박서준', context: { booking_id: 'T20261104-0412', confirm: true, user: '이도윤' },
    pending: q.pending, record: rec, calc: calcAt(rec, NOW), now: NOW });
  assert.equal(d.decision, 'forbidden');
});

test('다른 예매로 바꿔치기 → forbidden', () => {
  assert.equal(confirm({ context: { booking_id: 'T20261020-0155', confirm: true } }).reason, 'booking_mismatch');
});

test('재사용 (replay) → 티켓 없음', () => {
  const q = quote();
  const used = { ...q.pending, status: 'used' };
  assert.equal(confirm({ pending: used }).reason, 'pending_already_used');
});

test('만료된 견적 → 티켓 없음', () => {
  assert.equal(confirm({ now: '2026-11-05T10:31:00+09:00' }).reason, 'pending_expired');
});

test('견적 뒤 금액이 바뀌면 다시 안내 (TOCTOU)', () => {
  const later = calcAt(rec, '2026-11-13T10:00:00+09:00'); // 관람 8일 전 → 수수료 10%
  assert.equal(confirm({ calc: later, now: NOW }).decision, 'requote');
});

test('context의 금액·권한 칸은 무시 목록에 남는다', () => {
  assert.deepEqual(G.ignoredContextFields({ confirm: true, amount: 1, role: 'admin', booking_id: 'x' }), ['role', 'amount']);
});
