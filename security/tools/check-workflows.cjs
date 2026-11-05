'use strict';
// 워크플로우 정적 점검 (n8n 없이). 팀 규격(AGENTS.md)과 B 안전장치가 JSON에 실제로 들어 있는지 본다.
// 사용: node security/tools/check-workflows.cjs <workflow.json> [...]
// 실행 결과를 대신하지 않는다. 연결이 끊긴 노드, 없는 웹훅 호출, 규칙 위반을 미리 찾는 용도다.

const fs = require('node:fs');
const path = require('node:path');

const files = process.argv.slice(2);
if (!files.length) { console.error('usage: node check-workflows.cjs <wf.json> ...'); process.exit(2); }

const wfs = files.map(f => ({ file: path.basename(f), wf: JSON.parse(fs.readFileSync(f, 'utf8')) }));
const webhookPaths = new Set();
for (const { wf } of wfs) for (const n of wf.nodes) if (n.type === 'n8n-nodes-base.webhook') webhookPaths.add(n.parameters.path);

const rows = [];
const add = (file, check, ok, detail = '') => rows.push({ file, check, ok, detail });
const SECRET = /(sk-[A-Za-z0-9]{16,}|gh[po]_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,})/;

for (const { file, wf } of wfs) {
  const names = new Set(wf.nodes.map(n => n.name));
  // 1. 연결 대상이 모두 있는 노드인가
  const broken = [];
  for (const [from, outs] of Object.entries(wf.connections || {})) {
    if (!names.has(from)) broken.push(`출발 ${from}`);
    for (const kind of Object.values(outs)) for (const branch of kind) for (const c of branch || []) if (!names.has(c.node)) broken.push(`${from}→${c.node}`);
  }
  add(file, '연결 대상 존재', !broken.length, broken.join(', '));

  // 2. 트리거에서 닿지 않는 노드 (AI 하위 노드는 ai_* 연결로 붙으므로 함께 본다)
  const adj = {};
  for (const [from, outs] of Object.entries(wf.connections || {})) for (const kind of Object.values(outs)) for (const b of kind) for (const c of b || []) {
    (adj[from] = adj[from] || []).push(c.node); (adj[c.node] = adj[c.node] || []).push(from);
  }
  const triggers = wf.nodes.filter(n => /webhook$|errorTrigger$|manualTrigger$/.test(n.type)).map(n => n.name);
  const seen = new Set(triggers); const q = [...triggers];
  while (q.length) { const x = q.shift(); for (const y of adj[x] || []) if (!seen.has(y)) { seen.add(y); q.push(y); } }
  const orphan = wf.nodes.filter(n => !seen.has(n.name) && !/stickyNote$/.test(n.type)).map(n => n.name);
  add(file, '고립 노드 없음', !orphan.length, orphan.join(', '));

  // 3. Code 노드 문법
  const bad = [];
  for (const n of wf.nodes) if (n.parameters && n.parameters.jsCode) {
    try { new Function('$input', '$json', '$', '$node', '$execution', `return (async () => {${n.parameters.jsCode}\n})`); } catch (e) { bad.push(`${n.name}: ${e.message}`); }
  }
  add(file, 'Code 노드 문법', !bad.length, bad.join(' | '));

  // 4. 웹훅 경로 ticketmoa- · Header Auth
  for (const n of wf.nodes.filter(n => n.type === 'n8n-nodes-base.webhook')) {
    add(file, `웹훅 ${n.parameters.path}`, /^ticketmoa-/.test(n.parameters.path) && (n.parameters.authentication === 'headerAuth' || !!(n.credentials || {}).httpHeaderAuth),
      `auth=${n.parameters.authentication || '-'}`);
  }

  // 5. OpenAI Credential 규칙
  const ai = wf.nodes.filter(n => (n.credentials || {}).openAiApi);
  if (ai.length) {
    const wrong = ai.filter(n => n.credentials.openAiApi.id !== 'openAiCourse0001').map(n => `${n.name}(${n.credentials.openAiApi.id})`);
    add(file, 'OpenAI Credential = OpenAI (.env)', !wrong.length, wrong.join(', '));
  }

  // 6. 하위 웹훅 호출: 대상 웹훅이 있고 timeout이 있는가
  for (const n of wf.nodes.filter(n => n.type === 'n8n-nodes-base.httpRequest')) {
    const url = String(n.parameters.url || '');
    const m = url.match(/\/webhook\/([a-z0-9-]+)/);
    const to = ((n.parameters.options || {}).timeout);
    if (m) add(file, `호출 ${n.name} → ${m[1]}`, webhookPaths.has(m[1]) && to !== undefined, `${webhookPaths.has(m[1]) ? '' : '대상 없음 '}timeout=${to}`);
    else if (to === undefined) add(file, `호출 ${n.name} timeout`, false, url);
  }

  // 7. 키·토큰 문자열
  const raw = JSON.stringify(wf);
  add(file, '키·토큰 없음', !SECRET.test(raw), (raw.match(SECRET) || [''])[0].slice(0, 12));
}

// 8. B 안전장치가 들어 있는가
const by = Object.fromEntries(wfs.map(x => [x.file, x.wf]));
const node = (f, n) => by[f] && by[f].nodes.find(x => x.name === n);
const code = (f, n) => ((node(f, n) || {}).parameters || {}).jsCode || '';
if (by['ticketmoa-agents.json']) {
  const cond = JSON.stringify((node('ticketmoa-agents.json', 'LLM 필요?') || {}).parameters || {});
  add('ticketmoa-agents.json', 'F-003 attempt < 3 조건', /attempt\)\s*<\s*3/.test(cond));
  add('ticketmoa-agents.json', 'F-003 rule_attempt_limit', code('ticketmoa-agents.json', '규칙 분류 결과').includes('rule_attempt_limit'));
  add('ticketmoa-agents.json', '질문을 <question>으로 감쌈', code('ticketmoa-agents.json', '규칙 신호 추출').includes("'<question>'"));
}
if (by['ticketmoa-refund.json']) {
  const f = 'ticketmoa-refund.json';
  add(f, '견적에 owner·expires_at', /owner: s\.user/.test(code(f, '환불 금액 계산')) && /expires_at/.test(code(f, '환불 금액 계산')));
  add(f, 'ignored_context', code(f, '요청 단계 판정').includes('ignored_context'));
  add(f, '확정 묶음 검사 (owner·booking·만료)', /p\.owner === s\.user/.test(code(f, '확인 자격 판정')) && /p\.booking_id === s\.booking_id/.test(code(f, '확인 자격 판정')) && /expires_at/.test(code(f, '확인 자격 판정')));
  add(f, '확정 때 재계산', code(f, '확인 재계산').includes('calcRefund('));
  add(f, '30만원 기준', /REFUND_APPROVAL_LIMIT = 300000/.test(code(f, '환불 금액 계산') + code(f, '확인 재계산')));
  const cancel = by[f].nodes.filter(n => /cancel|취소 실행|refund-execute/i.test(String((n.parameters || {}).url || '')));
  add(f, '실제 취소 호출 없음', !cancel.length, cancel.map(n => n.name).join(', '));
}

const pad = (s, n) => (s + ' '.repeat(n)).slice(0, n);
let fail = 0;
for (const r of rows) { if (!r.ok) fail++; console.log(`${r.ok ? 'PASS' : 'FAIL'}  ${pad(r.file, 26)} ${r.check}${r.detail ? '  · ' + r.detail : ''}`); }
console.log(`\n${rows.length - fail}/${rows.length} 통과`);
if (process.env.CHECK_JSON) fs.writeFileSync(process.env.CHECK_JSON, JSON.stringify(rows, null, 2));
process.exit(fail ? 1 : 0);
