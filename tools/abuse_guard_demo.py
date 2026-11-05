#!/usr/bin/env python3
"""가산 차단 시연 (TM-09 반복 요청 · TM-10 해외 IP · TM-11 블랙리스트 IP · TM-12 국내 IP 정상). Windows·macOS·Linux.

  python3 tools/abuse_guard_demo.py            # 전부 차례로
  python3 tools/abuse_guard_demo.py tm09       # 하나만 (tm09 | tm10 | tm11 | tm12)
  python3 tools/abuse_guard_demo.py --pause    # 단계마다 Enter (발표용)

팀 키는 .env의 TM_TEAM_KEY, 주소는 N8N_URL(기본 http://localhost:5678)·DATA_API_URL(기본 http://localhost:8800).
IP는 실제 접속 주소가 아니라 요청의 context.client_ip(가상 IP, RFC 5737 문서용 대역)로 준다.
시작할 때 /cache-clear로 반복 요청 기록을 비운다.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
N8N = os.environ.get("N8N_URL", "http://localhost:5678").rstrip("/")
DATA = os.environ.get("DATA_API_URL", "http://localhost:8800").rstrip("/")


def team_key() -> str:
    if os.environ.get("TM_TEAM_KEY"):
        return os.environ["TM_TEAM_KEY"]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("TM_TEAM_KEY="):
                return line.split("=", 1)[1].strip()
    sys.exit("TM_TEAM_KEY가 없다 (.env 또는 환경 변수)")


KEY = team_key()
PAUSE = "--pause" in sys.argv


def post(url: str, body: dict, key: bool = True):
    req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **({"X-Team-Key": KEY} if key else {})})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read() or b"{}"), time.time() - start
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"{}"), time.time() - start


def ask(label: str, user: str, question: str, ip: str | None = None, rid: str | None = None) -> dict:
    body = {"request_id": rid or f"demo-{int(time.time() * 1000)}", "user": user, "channel": "web", "question": question}
    if ip:
        body["context"] = {"client_ip": ip}
    status, res, sec = post(f"{N8N}/webhook/ticketmoa-support", body)
    sec_info = res.get("security") or {}
    llm = (res.get("agents") or {}).get("llm_calls")
    mark = "⛔" if res.get("route") == "차단" else "✅"
    print(f"  {mark} {label:14} HTTP {status} · {sec:4.1f}s · route={res.get('route')} · "
          f"blocked_by={sec_info.get('blocked_by') or '-'} · llm_calls={llm}")
    print(f"     {str(res.get('answer', ''))[:110]}")
    return res


def step(title: str) -> None:
    print(f"\n== {title}")
    if PAUSE:
        input("   (Enter) ")


def tm09() -> None:
    step("TM-09 반복 요청: 같은 사용자가 같은 질문을 1분 안에 6번 (5번까지 통과, 6번째 차단)")
    for i in range(1, 7):
        ask(f"{i}번째 요청", "박서준", "예매 오픈 언제예요?", rid=f"demo-tm09-{int(time.time())}-{i}")


def tm10() -> None:
    step("TM-10 해외 IP: 198.51.100.7 (가상 정책상 US) → LLM 앞에서 차단, 해외 예매 인증 안내")
    ask("해외 IP", "이도윤", "별의 정원 예매하려는데 안 돼요", ip="198.51.100.7")


def tm11() -> None:
    step("TM-11 블랙리스트 IP: 203.0.113.66 (매크로 탐지로 등록) → 차단")
    ask("블랙리스트 IP", "김하늘", "QR이 안 떠요", ip="203.0.113.66")


def tm12() -> None:
    step("TM-12 국내 IP: 203.0.113.10 (KR) → 막지 않고 평소처럼 답변")
    ask("국내 IP", "김하늘", "모바일티켓 QR이 회색으로만 나오고 안 떠요", ip="203.0.113.10")


def main() -> int:
    picks = [a for a in sys.argv[1:] if not a.startswith("--")] or ["tm09", "tm10", "tm11", "tm12"]
    status, res, _ = post(f"{DATA}/cache-clear", {}, key=False)
    print(f"반복 요청 기록 비움 (/cache-clear {status}, {res.get('cleared')}건)")
    for name in picks:
        {"tm09": tm09, "tm10": tm10, "tm11": tm11, "tm12": tm12}[name]()
    post(f"{DATA}/cache-clear", {}, key=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
