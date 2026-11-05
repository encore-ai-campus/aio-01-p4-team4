# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""knowledge/*.md를 ticketmoa-index로 보내 다시 색인하고, 검색이 되는지 확인한다.

In-Memory 색인은 n8n이 다시 켜지면 사라질 수 있으므로 flow.py push 뒤에 다시 돌린다.
OpenAI 임베딩을 호출하므로 필요할 때만 실행한다.

  uv run --env-file .env tools/reindex.py

팀 키는 환경 변수 TM_TEAM_KEY로 준다. n8n 주소는 N8N_URL로 바꿀 수 있다 (기본 http://localhost:5678).
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
N8N_URL = os.environ.get("N8N_URL", "http://localhost:5678").rstrip("/")
KEY = os.environ.get("TM_TEAM_KEY") or os.environ.get("FLOW_WEBHOOK_KEY", "")


def post(path: str, body: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        f"{N8N_URL}/webhook/{path}",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Team-Key": KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        sys.exit(f"{path}: HTTP {error.code}. 팀 키, 워크플로우 게시 상태를 확인한다.")
    except urllib.error.URLError as error:
        sys.exit(f"{path}: 연결 실패 ({error.reason}). n8n이 켜져 있는지 확인한다.")
    except TimeoutError:
        sys.exit(f"{path}: {timeout}초 안에 응답이 없다.")
    except json.JSONDecodeError:
        sys.exit(f"{path}: 응답이 JSON이 아니다.")


def main() -> int:
    if not KEY:
        sys.exit("TM_TEAM_KEY가 없다. uv run --env-file .env tools/reindex.py 로 실행한다.")

    files = sorted((ROOT / "knowledge").glob("*.md"))
    if not files:
        sys.exit("knowledge/*.md가 없다.")
    documents = [{"doc": path.stem, "text": path.read_text(encoding="utf-8")} for path in files]

    result = post("ticketmoa-index", {"documents": documents}, timeout=180)
    length = result.get("chunk_length", {})
    print(f"문서 {result.get('valid_document_count')}/{len(documents)} "
          f"(일반 {result.get('public_document_count')}, 스태프 {result.get('staff_document_count')})")
    print(f"청크 {result.get('chunk_count')}개, 길이 최소 {length.get('min')} · "
          f"중앙값 {length.get('median')} · 최대 {length.get('max')} (문자 수)")
    print(f"색인 결과: {result.get('outcome')}")

    issues = result.get("issues") or []
    for issue in issues:
        print(f"문제: {issue.get('doc')} {issue.get('stage')} {issue.get('errors')}")
    if issues or result.get("outcome") != "store_output_received":
        return 1

    # 색인 응답의 청크 수는 저장 전 값이라, 일반·스태프 색인을 실제로 검색해 확인한다.
    search = post("ticketmoa-search", {"query": "QR 입장", "access_level": "staff", "top_k": 3}, timeout=30)
    print(f"검색 확인: 일반 색인 {search.get('indexed')}, 스태프 색인 {search.get('staff_indexed')}, "
          f"결과 {len(search.get('hits') or [])}건")
    if search.get("error") or not search.get("indexed") or not search.get("staff_indexed"):
        print(f"검색 확인 실패: {search.get('error')}")
        return 1
    print("색인 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
