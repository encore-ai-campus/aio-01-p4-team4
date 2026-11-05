# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""발표 시연: cases/의 요청을 차례로 보내고 결과만 보기 좋게 보여 준다.

  uv run --env-file .env tools/demo.py --warm            # 시연 전 예열 (QR 문의 2번, LLM 사용)
  uv run --env-file .env tools/demo.py --pause           # 전체, 단계마다 Enter
  uv run --env-file .env tools/demo.py wf01 wf12         # 고른 단계만
  uv run --env-file .env tools/demo.py --list            # 단계 목록

팀 키는 환경 변수 TM_TEAM_KEY로 받고 화면에 쓰지 않는다. n8n 주소는 N8N_URL (기본 http://localhost:5678).
기대와 다르면 표시만 하고 다음 단계로 넘어간다. 같은 요청을 짧은 시간에 반복하면 TM-09 차단(60초에 6번째)에 걸린다.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678").rstrip("/")
KEY = os.environ.get("TM_TEAM_KEY") or os.environ.get("FLOW_WEBHOOK_KEY", "")

# (단계, 케이스 파일, 케이스 이름 앞부분, 기대, 설명)
STEPS = [
    ("wf13", "common", "WF-13 잘못된 입력 · 빈 질문", {"status": 400}, "잘못된 입력은 LLM 전에 400으로 거절"),
    ("wf08", "common", "WF-08", {"route": "차단"}, "주입 문구는 LLM 0회로 차단"),
    ("wf07", "common", "WF-07", {"route": "자동 답변"}, "본인 건 조회, 연락처는 가림"),
    ("wf06", "common", "WF-06", {"route": "권한 없음"}, "남의 건은 알려 주지 않음"),
    ("wf01", "common", "WF-01", {"route": "자동 답변"}, "분류 · 검색 · 작성 · 검증을 거친 근거 답변"),
    ("wf12", "common", "WF-12", {"route": "담당자 이관"}, "공연 직전: 대체 입장 근거, 긴급 티켓, 현장 알림"),
    ("tm10", "team", "TM-10", {"route": "차단"}, "가산: 해외 IP를 LLM 전에 차단"),
]


def load_case(file: str, prefix: str) -> dict:
    cases = json.loads((ROOT / "cases" / f"{file}.json").read_text(encoding="utf-8"))["cases"]
    for case in cases:
        if case["name"].startswith(prefix):
            return case
    sys.exit(f"cases/{file}.json에 '{prefix}' 케이스가 없다.")


def send(body: dict) -> tuple[int, dict, float]:
    request = urllib.request.Request(
        f"{N8N_URL}/webhook/ticketmoa-support",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Team-Key": KEY},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8")), time.time() - started
    except urllib.error.HTTPError as error:
        try:
            data = json.loads(error.read().decode("utf-8"))
        except ValueError:
            data = {}
        return error.code, data, time.time() - started
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        print(f"  연결 실패: {type(error).__name__}")
        return 0, {}, time.time() - started


def show(status: int, data: dict, seconds: float, want: dict) -> bool:
    ok = all((status if k == "status" else data.get(k)) == v for k, v in want.items())
    print(f"  결과    : {'OK' if ok else '기대와 다름'} (기대 {want})")
    print(f"  HTTP    : {status}, {seconds:.1f}초")
    if data.get("error"):
        print(f"  오류    : {data.get('error')} {data.get('codes')}")
    if data.get("route"):
        print(f"  route   : {data.get('route')}" + (f" ({data['reason']})" if data.get("reason") else ""))
    security = data.get("security") or {}
    if security.get("blocked_by"):
        print(f"  차단    : {security['blocked_by']}")
    if security.get("masked"):
        print(f"  가림    : 연락처 {security['masked']}개")
    agents = data.get("agents") or {}
    if "llm_calls" in agents:
        print(f"  LLM     : {agents['llm_calls']}회")
    docs = []
    for source in data.get("sources") or []:
        if source.get("doc") not in docs:
            docs.append(source.get("doc"))
    if docs:
        print(f"  근거    : {', '.join(docs)}")
    ticket = data.get("ticket")
    if isinstance(ticket, dict):
        print(f"  티켓    : {ticket.get('id')} (우선순위 {ticket.get('priority')})")
    answer = str(data.get("answer") or "").strip().replace("\n", " ")
    if answer:
        print(f"  답변    : {answer[:150]}{'…' if len(answer) > 150 else ''}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="발표 시연: cases/의 요청을 차례로 보낸다.")
    parser.add_argument("steps", nargs="*", help="단계 이름 (생략하면 전체)")
    parser.add_argument("--pause", action="store_true", help="단계마다 Enter를 기다린다")
    parser.add_argument("--warm", action="store_true", help="QR 문의를 2번 보내 예열하고 끝낸다")
    parser.add_argument("--list", action="store_true", help="단계 목록을 보여 준다")
    args = parser.parse_args()

    if args.list:
        for name, _, prefix, _, note in STEPS:
            print(f"{name}  {prefix}: {note}")
        return 0
    if not KEY:
        sys.exit("TM_TEAM_KEY가 없다. uv run --env-file .env tools/demo.py 로 실행한다.")

    stamp = str(int(time.time()))
    if args.warm:
        body = dict(load_case("common", "WF-01")["body"])
        for i in range(2):
            body["request_id"] = f"warm-{stamp}-{i}"
            status, data, seconds = send(body)
            print(f"예열 {i + 1}: HTTP {status}, {seconds:.1f}초, {data.get('route')}")
        return 0

    unknown = [s for s in args.steps if s not in {step[0] for step in STEPS}]
    if unknown:
        sys.exit(f"없는 단계: {unknown}. --list로 확인한다.")
    chosen = [step for step in STEPS if not args.steps or step[0] in args.steps]
    failed = 0
    for index, (name, file, prefix, want, note) in enumerate(chosen, 1):
        case = load_case(file, prefix)
        body = dict(case["body"])
        body["request_id"] = f"demo-{stamp}-{name}"
        print(f"\n[{index}/{len(chosen)}] {case['name']}: {note}")
        print(f"  사용자  : {body.get('user')}")
        question = str(body.get("question") or "(빈 질문)")
        print(f"  질문    : {question[:90]}")
        if args.pause:
            input("  Enter로 보내기 ")
        status, data, seconds = send(body)
        if not show(status, data, seconds, want):
            failed += 1
    print(f"\n완료: {len(chosen) - failed}/{len(chosen)} 기대대로")
    return 0


if __name__ == "__main__":
    sys.exit(main())
