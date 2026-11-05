'use strict';
// promptfoo 확장 훅: 환불 공격 세트 시작 전에 대기 상태(/cache)를 비운다.
// PF_RESET_URL이 없고 대상이 mock이면 mock의 /mock-reset을 부른다. 실제 대상이면 PF_RESET_URL을 꼭 준다.

async function resetBeforeAll(hookName, context) {
  if (hookName !== 'beforeAll') return context;
  const target = process.env.PF_TARGET_URL || 'http://127.0.0.1:8899/webhook/ticketmoa-support';
  const url = process.env.PF_RESET_URL || (target.includes('127.0.0.1:8899') ? 'http://127.0.0.1:8899/mock-reset' : '');
  if (!url) {
    console.warn('[hooks] PF_RESET_URL 없음: 이전 실행의 대기 상태가 남아 있으면 결과가 달라질 수 있습니다.');
    return context;
  }
  const res = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  if (!res.ok) throw new Error(`reset 실패: ${res.status} ${url}`);
  return context;
}

module.exports = { resetBeforeAll };
