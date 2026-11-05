#!/usr/bin/env python3
"""support 워크플로우에 가산 차단(TM-09 반복 요청 · TM-10 해외 IP · TM-11 블랙리스트 IP)을 넣은 사본을 만든다.

  python3 tools/abuse_guard_apply.py workflows/ticketmoa-support.json -o <출력.json>
  python3 tools/abuse_guard_apply.py <입력> --in-place      # 리드가 자기 파일에 넣을 때

저장소의 support(리드 파일)는 기본으로 건드리지 않는다. 출력 파일만 쓴다.
Code 노드의 함수는 lib/common.js 원문을, IP 정책은 config/ip-policy.json을 그대로 복사한다.

넣는 위치: Blocked by rule? ─false→ Abuse rules → Get rate → Rate check → Abuse blocked?
            ─true→ Blocked answer (기존, 문구만 blocked_by별로) · ─false→ Save rate → Load registry (기존)
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = "http://data-api:8800/cache/"
NAMES = ["Abuse rules", "Get rate", "Rate check", "Abuse blocked?", "Save rate"]


def lib_block() -> str:
    """lib/common.js의 12·13절(RATE_LIMIT, rateLimitKey, checkRateLimit, checkIpPolicy) 원문."""
    src = (ROOT / "lib/common.js").read_text(encoding="utf-8")
    start = src.index("const RATE_LIMIT = ")
    end = src.index("if (typeof module !== 'undefined'")
    return src[start:end].rstrip() + "\n"


def code(body: str, with_policy: bool) -> str:
    head = "// ↓ lib/common.js에서 그대로 복사 (고치려면 lib/common.js를 고치고 tools/abuse_guard_apply.py를 다시 돌린다)\n"
    head += lib_block() + "// ↑ lib/common.js 복사 끝\n\n"
    if with_policy:
        policy = json.loads((ROOT / "config/ip-policy.json").read_text(encoding="utf-8"))
        head += "// config/ip-policy.json 복사본 (가상 IP 정책, RFC 5737 대역). 정책을 고치면 이 노드도 다시 만든다.\n"
        head += "const IP_POLICY = " + json.dumps(policy, ensure_ascii=False, indent=2) + ";\n\n"
    return head + body


ABUSE_RULES = """// 가산 TM-10·11: context.client_ip가 있으면 가상 IP 정책으로 검사 (없으면 통과). LLM 앞.
// TM-09용 반복 요청 키도 여기서 만든다 (사용자 + 질문 해시, 질문 원문은 남기지 않음).
const body = $('Question webhook').first().json.body || {};
const ctx = body.context && typeof body.context === 'object' ? body.context : {};
const ip = checkIpPolicy(String(ctx.client_ip || '').trim(), IP_POLICY);
return [{ json: {
  ip_blocked: ip.blocked,
  blocked_by: ip.blocked_by,
  reason: ip.reason,
  country: ip.country,
  rate_key: rateLimitKey(body.user, body.question),
  started_at: $json.started_at,
} }];
"""

RATE_CHECK = """// 가산 TM-09: 같은 사용자·같은 질문이 60초에 6번째면 차단. 같은 request_id는 한 번만 센다.
// /cache 조회가 실패하면(데이터 API 문제) 막지 않고 통과시킨다 (fail-open).
const a = $('Abuse rules').first().json;
const base = { rate_key: a.rate_key, started_at: a.started_at, country: a.country };
if (a.ip_blocked) return [{ json: { ...base, blocked: true, blocked_by: a.blocked_by, reason: a.reason, recent: [] } }];
const res = $input.first().json || {};
const status = typeof res.statusCode === 'number' ? res.statusCode : null;
if (status !== 200 && status !== 404) {
  return [{ json: { ...base, blocked: false, blocked_by: '', reason: '', recent: [], rate_check: 'cache_unavailable' } }];
}
const prev = status === 200 && res.body && Array.isArray(res.body.value) ? res.body.value : [];
const body = $('Question webhook').first().json.body || {};
const r = checkRateLimit(prev, new Date(), body.request_id);
return [{ json: { ...base, blocked: r.blocked, blocked_by: r.blocked ? 'rate_limit' : '', reason: r.reason,
  recent: r.recent, count: r.count } }];
"""

BLOCKED_OLD = "  answer: '보안 정책상 처리할 수 없는 요청입니다. 예매·티켓 관련 문의를 다시 남겨 주세요.',\n"
BLOCKED_NEW = """  answer: ({
    geo: '현재 지역에서는 예매할 수 없습니다. 일부 공연은 공연사 요청으로 국내 접속에서만 예매할 수 있습니다. 해외 체류 중이면 [마이페이지 > 해외 예매 인증]에서 본인인증을 마친 뒤 이용해 주세요 (공연마다 허용 여부가 다릅니다). VPN·프록시 접속은 부정 접속으로 판단될 수 있습니다.',
    ip_blocklist: '부정 접속이 의심되어 이 접속 환경에서는 문의를 처리할 수 없습니다. 본인이라면 고객센터에서 본인 확인 후 해제를 요청해 주세요.',
    rate_limit: '같은 요청이 짧은 시간에 반복되어 잠시 제한되었습니다. 1분 뒤 다시 시도해 주세요.',
  })[$json.blocked_by] || '보안 정책상 처리할 수 없는 요청입니다. 예매·티켓 관련 문의를 다시 남겨 주세요.',
"""


def cache_http(name: str, method: str, pos) -> dict:
    params = {
        "url": "={{ '" + CACHE + "' + encodeURIComponent($json.rate_key) }}",
        "options": {"timeout": 1000, "response": {"response": {"fullResponse": True, "neverError": True}}},
    }
    if method == "POST":
        params.update({"method": "POST", "sendBody": True, "specifyBody": "json",
                       "jsonBody": "={{ JSON.stringify({ value: $json.recent, ttl: 120 }) }}"})
    return {"parameters": params, "name": name, "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": pos, "onError": "continueErrorOutput"}


def patch(w: dict) -> dict:
    by = {n["name"]: n for n in w["nodes"]}
    for need in ("Blocked by rule?", "Blocked answer", "Load registry", "Injection rules"):
        if need not in by:
            sys.exit(f"support에 '{need}' 노드가 없다 (리드가 이름을 바꿨으면 apply.py를 맞춘다)")
    if any(n in by for n in NAMES):
        sys.exit("이미 차단 노드가 들어 있다")
    con = w["connections"]
    false_out = con["Blocked by rule?"]["main"][1]
    if [d["node"] for d in false_out] != ["Load registry"]:
        sys.exit(f"Blocked by rule? false 출력이 Load registry가 아니다: {false_out}")

    blocked = by["Blocked answer"]["parameters"]
    if BLOCKED_OLD not in blocked["jsCode"]:
        sys.exit("Blocked answer 문구가 예상과 다르다 (리드가 바꿨으면 apply.py를 맞춘다)")
    blocked["jsCode"] = blocked["jsCode"].replace(BLOCKED_OLD, BLOCKED_NEW)

    x, y = by["Blocked by rule?"]["position"]
    lx, _ = by["Load registry"]["position"]
    # 새 노드는 Blocked by rule? 아래 줄(y+220)에 놓는다. 기존 노드는 옮기지 않는다.
    row = y + 220
    step = max(160, (lx - x) // 2)
    nodes = [
        {"parameters": {"jsCode": code(ABUSE_RULES, True)}, "name": "Abuse rules",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [x, row]},
        cache_http("Get rate", "GET", [x + step, row]),
        {"parameters": {"jsCode": code(RATE_CHECK, False)}, "name": "Rate check",
         "type": "n8n-nodes-base.code", "typeVersion": 2, "position": [x + 2 * step, row]},
        {"parameters": {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose", "version": 2},
                                       "conditions": [{"id": "abuse1", "leftValue": "={{ $json.blocked }}", "rightValue": "",
                                                       "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                                       "combinator": "and"}, "options": {}},
         "name": "Abuse blocked?", "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": [x + 3 * step, row]},
        cache_http("Save rate", "POST", [x + 4 * step, row + 120]),
    ]
    for n in nodes:
        n["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"ticketmoa-support/abuse/{n['name']}"))
    w["nodes"].extend(nodes)

    def to(name):
        return [{"node": name, "type": "main", "index": 0}]

    con["Blocked by rule?"]["main"][1] = to("Abuse rules")
    con["Abuse rules"] = {"main": [to("Get rate")]}
    con["Get rate"] = {"main": [to("Rate check"), to("Rate check")]}        # 성공·오류 모두 Rate check (fail-open)
    con["Rate check"] = {"main": [to("Abuse blocked?")]}
    con["Abuse blocked?"] = {"main": [to("Blocked answer"), to("Save rate")]}
    con["Save rate"] = {"main": [to("Load registry"), to("Load registry")]}  # 저장 실패해도 계속
    return w


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("input")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-o", "--output")
    g.add_argument("--in-place", action="store_true")
    a = p.parse_args()
    w = patch(json.loads(Path(a.input).read_text(encoding="utf-8")))
    out = Path(a.input) if a.in_place else Path(a.output)
    out.write_text(json.dumps(w, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"차단 노드 {len(NAMES)}개를 넣었다 → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
