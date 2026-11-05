'use strict';
// 계약 모형 서버 (가짜 ticketmoa-support).
// 목적: promptfoo 설정(HTTP 호출, X-Team-Key, 응답 읽기, 판정식)이 우리 공통 계약에서 돌아가는지
//       n8n 없이 먼저 확인한다. 실제 워크플로우의 품질을 재는 것이 아니다.
// 실행: node security/promptfoo/mock-webhook.cjs   (127.0.0.1:8899, 키는 PF_TEAM_KEY, 기본 "mock-key")
// lib/common.js의 함수를 그대로 써서 400·차단·가림 판단은 본체와 같은 규칙을 쓴다.

const http = require('node:http');
const path = require('node:path');
const root = path.resolve(__dirname, '..', '..');
const C = require(path.join(root, 'lib', 'common.js'));
const users = require(path.join(root, 'data', 'users.json'));
const records = require(path.join(root, 'data', 'records.json'));

const G = require(path.join(root, 'security', 'refund-guard.js'));

const PORT = Number(process.env.PF_MOCK_PORT || 8899);
const KEY = process.env.PF_TEAM_KEY || 'mock-key';
// PF_MOCK_MODE=vulnerable: 환불 안전장치를 끈 대비용 모드 (context를 믿고, 견적 없이 확정, 재사용 허용).
const MODE = process.env.PF_MOCK_MODE || 'guarded';
const cache = new Map();   // 데이터 API /cache 대신
const rate = new Map();    // /cache/ratelimit:<user> 대신
const ipPolicy = require(path.join(root, 'config', 'ip-policy.json'));
let ticketSeq = 0;
const won = n => `${Number(n).toLocaleString('ko-KR')}원`;
const REFUND_SRC = [{ doc: 'refund-policy', section: '2', score: 0.8 }];

function findRecord(q, ctx) {
  const rid = (q.match(/C-\d{4}/) || [])[0];
  if (rid) return [rid, records[rid]];
  const bid = (q.match(/T\d{8}-\d{4}/) || [])[0] || ctx.booking_id;
  const hit = Object.entries(records).find(([, r]) => r.booking_id && r.booking_id === bid);
  return hit || [null, null];
}

function refund(body, user, base) {
  const q = String(body.question || '');
  const ctx = body.context && typeof body.context === 'object' ? body.context : {};
  const ignored = G.ignoredContextFields(ctx);
  const sec = { reason: ignored.length ? `ignored_context:${ignored.join(',')}` : '' };
  const reply = (route, answer, extra = {}) =>
    [200, C.buildResponse({ ...base, route, answer, sources: REFUND_SRC, security: sec, ...extra })];
  const handoff = (reason) => reply(C.ROUTES.HANDOFF, '상담원에게 환불 요청을 전달했습니다.',
    { ticket: `T-${9000 + ++ticketSeq}`, reason });

  if (MODE === 'vulnerable') {
    if (ctx.confirm) return handoff('trusted_context_confirm');             // 견적·소유자 확인 없음
    const [, r] = findRecord(q, ctx);
    const amount = ctx.amount || (r && r.amount) || 0;                       // context 금액을 믿음
    return reply(C.ROUTES.AUTO, `환불 예정 금액은 ${won(amount)}입니다. 확정하시겠어요?`, { ticket: null });
  }

  // 2차: 확정 요청
  if ('confirm' in ctx) {
    const pending = cache.get(G.pendingKey(user.name, ctx.booking_id)) || null;
    const record = pending ? records[pending.record_id] : null;
    const calc = record ? C.calcRefund(G.bookingFromRecord(record)) : null;
    const d = G.confirmDecision({ user: user.name, context: ctx, pending, record, calc });
    if (d.decision === 'create_ticket') {
      cache.set(pending.key, { ...pending, status: 'used' });            // 먼저 소비, 그다음 티켓
      return handoff('customer_confirmed');
    }
    if (d.decision === 'forbidden') return reply(C.ROUTES.FORBIDDEN, '본인 예매만 처리할 수 있습니다.', { ticket: null, reason: d.reason });
    if (d.decision === 'handoff') return handoff(d.reason);
    if (d.decision === 'cancel') return reply(C.ROUTES.AUTO, '취소를 진행하지 않았습니다.', { ticket: null, reason: d.reason });
    return reply(C.ROUTES.CLARIFY, '확정할 환불 안내 내역이 없습니다. 예매번호와 함께 환불 금액을 먼저 확인해 주세요.',
      { ticket: null, reason: d.reason });
  }

  // 1차: 견적
  if (/오늘/.test(q)) return handoff('show_day');                         // 당일 취소는 규정상 상담원
  const [recordId, record] = findRecord(q, ctx);
  if (!record) return reply(C.ROUTES.CLARIFY, '환불할 예매의 문의번호(C-)나 예매번호(T)를 알려 주세요.', { ticket: null });
  const b = G.bookingFromRecord(record);
  const d = G.quoteDecision({ user: user.name, recordId, record, calc: b ? C.calcRefund(b) : null });
  if (d.decision === 'forbidden') return reply(C.ROUTES.FORBIDDEN, '본인 예매만 처리할 수 있습니다.', { ticket: null, sources: [] });
  if (d.decision === 'handoff') return handoff(d.reason);
  if (d.decision !== 'quote') return reply(C.ROUTES.CLARIFY, '예매 정보를 확인할 수 없습니다.', { ticket: null });
  cache.set(d.pending.key, d.pending);
  return reply(C.ROUTES.AUTO,
    `${d.pending.booking_id} 예매 금액 ${won(d.pending.amount)}, 수수료 ${won(d.pending.fee)}, 환불 예정 ${won(d.pending.refund)}입니다. 확정하시겠어요?`,
    { ticket: null });
}

// PF_MOCK_BROKEN=1: 일부러 결함을 넣은 모드. 판정식이 실제로 결함을 잡는지(거짓 통과가 아닌지) 확인용.
function broken(body) {
  const base = { request_id: body.request_id, agents: { llm_calls: 1 }, timings: {} };
  const q = String(body.question || '');
  if (/스태프|수기/.test(q)) return [200, C.buildResponse({ ...base, route: C.ROUTES.AUTO, answer: '책임자 코드 1234 입력',
    sources: [{ doc: 'staff-entry-manual', section: '3', score: 0.9 }] })];
  if (/C-2001/.test(q)) return [200, { ...C.buildResponse({ ...base, route: C.ROUTES.AUTO }), answer: '처리 중, 010-0000-4821' }];
  if (/환불/.test(q)) return [200, C.buildResponse({ ...base, route: C.ROUTES.AUTO, answer: '환불이 완료되었습니다.', ticket: 'T-9' })];
  if (q.length > 500) return [500, { error: 'boom' }];
  return [200, C.buildResponse({ ...base, route: C.ROUTES.AUTO, answer: 'ok' })];
}

function handle(body) {
  if (process.env.PF_MOCK_BROKEN) return broken(body);
  const v = C.validateRequest(body, users);
  if (!v.ok) return [400, C.badRequest(v.codes)];
  const base = { request_id: body.request_id, agents: { llm_calls: 0 }, timings: {} };
  const blockedBy = (by, reason) => [200, C.buildResponse({ ...base, route: C.ROUTES.BLOCKED,
    answer: '요청이 제한되었습니다. 잠시 뒤 다시 시도해 주세요.', security: { blocked_by: by, reason } })];

  // PF_MOCK_ABUSE=1: 본체 앞단의 가산 규칙(IP 정책 TM-10~12, 사용자별 요청 제한 TM-09)을 켠다. LLM 전에 막는다.
  if (process.env.PF_MOCK_ABUSE && MODE !== 'vulnerable') {
    const ctx0 = body.context && typeof body.context === 'object' ? body.context : {};
    const ip = C.checkIpPolicy(ctx0.client_ip, ipPolicy);
    if (ip.blocked) return blockedBy(ip.blocked_by, ip.reason);
    const rl = C.checkRateLimit(rate.get(v.user.name) || []);
    rate.set(v.user.name, rl.recent);
    if (rl.blocked) return blockedBy('rate_limit', rl.reason);
  }

  const inj = MODE === 'vulnerable' ? { blocked: false } : C.detectInjection(body.question);
  if (inj.blocked) {
    return [200, C.buildResponse({ ...base, route: C.ROUTES.BLOCKED, answer: '처리할 수 없는 요청입니다.',
      security: { blocked_by: inj.blocked_by, reason: inj.reason } })];
  }

  const q = body.question;
  const ctx = body.context || {};
  base.agents.llm_calls = 1;
  if (ctx.pending_action === 'refund_request' || /환불|취소/.test(q)) return refund(body, v.user, base);

  const rid = (q.match(/C-\d{4}/) || [])[0];
  if (rid) {
    const rec = records[rid];
    if (!rec || rec.requester !== v.user.name) {
      return [200, C.buildResponse({ ...base, route: C.ROUTES.FORBIDDEN, answer: '본인 건만 조회할 수 있습니다.' })];
    }
    const m = C.maskDeep(rec);
    return [200, C.buildResponse({ ...base, route: C.ROUTES.AUTO,
      answer: `${rid} ${m.value.title}: ${m.value.status}. 연락처 ${m.value.contact.phone}`,
      security: { masked: m.masked } })];
  }

  // 문서 권한은 질문 글이 아니라 users.json의 access_level로만 정한다 (context는 믿지 않음).
  if (/스태프|수기|책임자\s*코드/.test(q) && v.user.access_level !== 'staff') {
    return [200, C.buildResponse({ ...base, route: C.ROUTES.HANDOFF, answer: '현장 담당자에게 전달했습니다.',
      sources: [], ticket: 'T-mock-1' })];
  }

  return [200, C.buildResponse({ ...base, route: C.ROUTES.AUTO, answer: '앱을 최신 버전으로 업데이트한 뒤 다시 열어 주세요.',
    sources: [{ doc: 'mobile-ticket-troubleshooting', section: '1', score: 0.82 }] })];
}

http.createServer((req, res) => {
  const send = (code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(obj)); };
  if (req.method === 'POST' && req.url === '/mock-reset') { cache.clear(); rate.clear(); ticketSeq = 0; return send(200, { ok: true }); }
  if (req.method !== 'POST' || req.url !== '/webhook/ticketmoa-support') return send(404, { error: 'not found' });
  if (req.headers['x-team-key'] !== KEY) return send(401, { error: 'unauthorized' });
  let raw = '';
  req.on('data', c => { raw += c; });
  req.on('end', () => {
    let body;
    try { body = JSON.parse(raw); } catch { return send(400, C.badRequest(['invalid_json'])); }
    if (process.env.PF_MOCK_LOG) console.log(JSON.stringify({ request_id: body.request_id, context: body.context, qlen: (body.question || '').length }));
    const [code, out] = handle(body);
    send(code, out);
  });
}).listen(PORT, '127.0.0.1', () => console.log(`mock ticketmoa-support on http://127.0.0.1:${PORT}`));
