# /// script
# requires-python = ">=3.10"
# dependencies = ["tiktoken>=0.8,<1"]
# ///
"""Compare the repository's ## section chunks with 500-token/80-overlap chunks.

Default mode is a local, no-API dry run. Paid embedding calls require both
--execute and --approve-openai-cost, a USD budget, and an interactive typed
confirmation. Outputs default to the OS temp directory, never the repository.

Examples:
  uv run tools/compare_chunking.py
  uv run --env-file .env tools/compare_chunking.py --execute \
    --approve-openai-cost --max-cost-usd 0.05
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import re
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MODEL = "text-embedding-3-large"
ENCODING_NAME = "cl100k_base"
PRICE_PER_MILLION_USD = 0.13  # OpenAI public list price recorded in the project on 2026-11-05.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
VECTOR_STORE_TOP_K = 100
FINAL_TOP_K = 3
EXPECTED_DOC_COUNT = 8
CONTACT_PATTERN = re.compile(
    r"(?:\b\d{2,3}[-. ]\d{3,4}[-. ]\d{4}\b|"
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})",
    re.IGNORECASE,
)
ACCESS_PATTERN = re.compile(r"^>\s*access_level:\s*(all|staff)\b", re.IGNORECASE | re.MULTILINE)
SECTION_PATTERN = re.compile(r"^##\s+(.+)\s*$", re.MULTILINE)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git_value(*args: str) -> str | None:
    import subprocess

    try:
        p = subprocess.run(
            ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        return p.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def js_string_length(text: str) -> int:
    """Match JavaScript String.length (UTF-16 code units), used by index Code."""
    return len(text.encode("utf-16-le")) // 2


def parse_doc(path: Path) -> dict[str, Any]:
    # Keep the file's original newline form, as JSON callers pass the decoded text through.
    with path.open("r", encoding="utf-8", newline="") as f:
        text = f.read()
    errors: list[str] = []
    access_match = ACCESS_PATTERN.search(text)
    section_matches = list(SECTION_PATTERN.finditer(text))
    if not access_match:
        errors.append("access_level이 없거나 all/staff 값이 아님")
    if len(section_matches) < 3:
        errors.append(f"## 절이 3개 미만 ({len(section_matches)})")
    pieces: list[dict[str, Any]] = []
    for i, match in enumerate(section_matches):
        body_start = match.end()
        body_end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(text)
        body = text[body_start:body_end].strip()
        if not body:
            errors.append(f"빈 ## 절: {match.group(1).strip()}")
        pieces.append({
            "section": match.group(1).strip(),
            "body": body,
            "heading_start": match.start(),
            "source_start": body_start,
            "source_end": body_end,
        })
    if CONTACT_PATTERN.search(text):
        errors.append("연락처 형식 문자열이 포함됨")
    return {
        "doc": path.stem,
        "filename": path.name,
        "text": text,
        "access_level": access_match.group(1).lower() if access_match else None,
        "pieces": pieces,
        "errors": errors,
        "sha256": sha256_bytes(path.read_bytes()),
    }


def load_documents(folder: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    files = sorted(folder.glob("*.md"), key=lambda p: p.name.casefold())
    if len(files) != EXPECTED_DOC_COUNT:
        raise ValueError(f"{folder}에서 Markdown 문서 {EXPECTED_DOC_COUNT}개를 기대했지만 {len(files)}개를 찾았습니다.")
    docs = [parse_doc(p) for p in files]
    issues = [{"doc": d["doc"], "errors": d["errors"]} for d in docs if d["errors"]]
    if issues:
        raise ValueError("색인 워크플로우와 같은 품질 검사에서 제외될 문서가 있습니다: " + json.dumps(issues, ensure_ascii=False))
    return docs, issues


def make_section_chunks(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reproduce the index workflow's ## extraction and document/section prefixes."""
    chunks = []
    for doc in docs:
        for piece in doc["pieces"]:
            body = piece["body"]
            content = f"# {doc['doc']}\n## {piece['section']}\n{body}"
            chunks.append({
                "method": "A_section",
                "doc": doc["doc"],
                "access_level": doc["access_level"],
                "section": piece["section"],
                "source_sections": [piece["section"]],
                "section_key": piece["section"],
                "text": content,
                "source_char_start": piece["heading_start"],
                "source_char_end": piece["source_end"],
            })
    return chunks


def tokenizer_offset_map(encoding: Any, text: str, token_ids: list[int]) -> list[int]:
    decoded, offsets = encoding.decode_with_offsets(token_ids)
    if decoded != text:
        raise ValueError("토크나이저의 원문 오프셋 복원이 정확하지 않아 절 범위를 안전하게 추적할 수 없습니다.")
    return offsets


def token_section_chunks(docs: list[dict[str, Any]], encoding: Any) -> list[dict[str, Any]]:
    """Split one heading-preserving document stream and retain body source ranges.

    Chunks use token windows with an 80-token source overlap. Window edges are
    moved to valid Unicode character boundaries, and a window is shortened if
    re-tokenizing that exact source slice would exceed 500 tokens. Original
    attribution is based on character-range overlap with section body text,
    not on generated chunk headings.
    """
    chunks: list[dict[str, Any]] = []
    for doc in docs:
        parts = [f"# {doc['doc']}\n"]
        section_spans: list[tuple[str, int, int]] = []
        cursor = len(parts[0])
        for piece in doc["pieces"]:
            heading = f"## {piece['section']}\n"
            parts.append(heading)
            cursor += len(heading)
            body_start = cursor
            parts.append(piece["body"])
            cursor += len(piece["body"])
            section_spans.append((piece["section"], body_start, cursor))
            parts.append("\n\n")
            cursor += 2
        source = "".join(parts)
        ids = encoding.encode(source, disallowed_special=())
        offsets = tokenizer_offset_map(encoding, source, ids)
        boundaries = [(i, offset) for i, offset in enumerate(offsets) if offset >= 0]
        boundaries.append((len(ids), len(source)))
        # Keep only increasing character boundaries. Negative offsets denote a token
        # that starts within a multi-byte character and cannot safely delimit text.
        safe_boundaries: list[tuple[int, int]] = []
        for token_index, char_index in boundaries:
            if not safe_boundaries or (token_index > safe_boundaries[-1][0] and char_index > safe_boundaries[-1][1]):
                safe_boundaries.append((token_index, char_index))
        if not safe_boundaries or safe_boundaries[0] != (0, 0):
            safe_boundaries.insert(0, (0, 0))
        cursor_token = 0
        previous_end_token: int | None = None
        while cursor_token < len(ids):
            start_token, start_offset = next((b for b in safe_boundaries if b[0] >= cursor_token), safe_boundaries[-1])
            candidates = [b for b in safe_boundaries if start_token < b[0] <= min(start_token + CHUNK_SIZE, len(ids))]
            if not candidates:
                raise ValueError(f"{doc['doc']}: 토큰 청크 경계를 만들 수 없습니다.")
            end_token, end_offset = candidates[-1]
            chunk_text = source[start_offset:end_offset]
            while len(encoding.encode(chunk_text, disallowed_special=())) > CHUNK_SIZE:
                candidates = [b for b in safe_boundaries if start_token < b[0] < end_token]
                if not candidates:
                    raise ValueError(f"{doc['doc']}: 문자 경계 조정 후에도 500 토큰 이내 청크를 만들 수 없습니다.")
                end_token, end_offset = candidates[-1]
                chunk_text = source[start_offset:end_offset]
            actual_chunk_tokens = len(encoding.encode(chunk_text, disallowed_special=()))
            source_sections = [
                name for name, body_start, body_end in section_spans
                if start_offset < body_end and end_offset > body_start
            ]
            if not source_sections:
                # Chunks containing only a document/section heading cannot be answer hits.
                source_sections = [
                    name for name, body_start, body_end in section_spans
                    if start_offset <= body_start < end_offset
                ]
            if not chunk_text.strip():
                continue
            section_key = " || ".join(source_sections)
            chunks.append({
                "method": "B_500_80",
                "doc": doc["doc"],
                "access_level": doc["access_level"],
                "section": section_key,
                "source_sections": source_sections,
                "section_key": section_key,
                "text": chunk_text,
                "source_token_start": start_token,
                "source_token_end": end_token,
                "source_char_start": start_offset,
                "source_char_end": end_offset,
                "token_count": actual_chunk_tokens,
                "overlap_tokens_with_previous": max(0, previous_end_token - start_token) if previous_end_token is not None else 0,
            })
            previous_end_token = end_token
            if end_token >= len(ids):
                break
            cursor_token = max(start_token + 1, end_token - CHUNK_OVERLAP)
    return chunks


def load_questions(path: Path, docs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"평가 질문이 없습니다: {path}")
    known = {d["doc"]: {p["section"] for p in d["pieces"]} for d in docs}
    seen: set[str] = set()
    for row in rows:
        qid = row.get("id", "").strip()
        if not qid or qid in seen:
            raise ValueError(f"질문 ID가 비었거나 중복입니다: {qid!r}")
        seen.add(qid)
        row["id"] = qid
        row["role"] = row.get("role", "all").strip().lower()
        row["question"] = row.get("question", "").strip()
        row["test_type"] = row.get("test_type", "").strip()
        row["expected_doc"] = row.get("expected_doc", "").strip()
        row["expected_sections"] = [s.strip() for s in row.get("expected_section", "").split(" || ") if s.strip()]
        if row["role"] not in {"all", "staff"}:
            raise ValueError(f"{qid}: 알 수 없는 role {row['role']!r}")
        if not row["question"]:
            raise ValueError(f"{qid}: 질문이 비었습니다.")
        if row["test_type"] == "positive":
            if row["expected_doc"] not in known:
                raise ValueError(f"{qid}: expected_doc가 knowledge 문서에 없습니다: {row['expected_doc']!r}")
            missing = [s for s in row["expected_sections"] if s not in known[row["expected_doc"]]]
            if not row["expected_sections"] or missing:
                raise ValueError(f"{qid}: expected_section이 문서 절과 일치하지 않습니다: {missing or row['expected_sections']}")
        elif row["test_type"] not in {"deny_staff", "no_ground", "no_external_leak"}:
            raise ValueError(f"{qid}: 알 수 없는 test_type {row['test_type']!r}")
    return rows, sha256_bytes(path.read_bytes())


def build_snapshot(docs: list[dict[str, Any]]) -> str:
    h = hashlib.sha256()
    for d in docs:
        h.update(d["filename"].encode("utf-8"))
        h.update(b"\0")
        h.update(d["text"].encode("utf-8"))
        h.update(b"\0")
    return h.hexdigest()


def output_dir(path: Path | None, run_id: str) -> Path:
    target = path or (Path(tempfile.gettempdir()) / "ticketmoa-rag-comparison" / run_id)
    target.mkdir(parents=True, exist_ok=False)
    return target


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict))
                else "미측정" if v is None
                else v
                for k, v in row.items()
            })


def chunk_rows(chunks_by_method: dict[str, list[dict[str, Any]]], encoding: Any) -> list[dict[str, Any]]:
    rows = []
    for method, chunks in chunks_by_method.items():
        for index, c in enumerate(chunks, 1):
            rows.append({
                "method": method,
                "chunk_id": f"{c['doc']}:{index}",
                "doc": c["doc"],
                "access_level": c["access_level"],
                "section_key": c["section_key"],
                "source_sections": c["source_sections"],
                "length_chars_js": js_string_length(c["text"]),
                "length_tokens_cl100k": c.get("token_count", len(encoding.encode(c["text"], disallowed_special=()))),
                "overlap_tokens_with_previous": c.get("overlap_tokens_with_previous", ""),
                "source_token_start": c.get("source_token_start", ""),
                "source_token_end": c.get("source_token_end", ""),
                "source_char_start": c.get("source_char_start", ""),
                "source_char_end": c.get("source_char_end", ""),
                "preview": c["text"].replace("\r", " ").replace("\n", " ")[:160],
                "text_sha256": sha256_bytes(c["text"].encode("utf-8")),
            })
    return rows


def stats(values: list[int | float]) -> dict[str, int | float | None]:
    if not values:
        return {"min": None, "median": None, "max": None}
    return {"min": min(values), "median": statistics.median(values), "max": max(values)}


def plan_metadata(
    docs: list[dict[str, Any]], questions: list[dict[str, Any]], question_hash: str,
    chunks_by_method: dict[str, list[dict[str, Any]]], encoding: Any, run_id: str,
    price: float,
) -> dict[str, Any]:
    chunk_token_counts = {
        name: sum(len(encoding.encode(c["text"], disallowed_special=())) for c in chunks)
        for name, chunks in chunks_by_method.items()
    }
    question_tokens = sum(len(encoding.encode(q["question"], disallowed_special=())) for q in questions)
    total_tokens = sum(chunk_token_counts.values()) + question_tokens
    return {
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "mode": "dry-run",
        "git_commit": git_value("rev-parse", "HEAD"),
        "git_branch": git_value("branch", "--show-current"),
        "git_worktree_status_at_run": git_value("status", "--porcelain"),
        "documents": [{"filename": d["filename"], "doc": d["doc"], "access_level": d["access_level"], "sha256": d["sha256"]} for d in docs],
        "document_snapshot_sha256": build_snapshot(docs),
        "question_csv": str(ROOT / "docs" / "RAG-EVALUATION-QUESTIONS.csv"),
        "question_count": len(questions),
        "question_csv_sha256": question_hash,
        "question_git_blob": git_value("rev-parse", "HEAD:docs/RAG-EVALUATION-QUESTIONS.csv"),
        "grading_rules_file": str(ROOT / "docs" / "RAG-EVALUATION-QUESTIONS.md"),
        "grading_rules_sha256": sha256_bytes((ROOT / "docs" / "RAG-EVALUATION-QUESTIONS.md").read_bytes()),
        "grading_rules_git_blob": git_value("rev-parse", "HEAD:docs/RAG-EVALUATION-QUESTIONS.md"),
        "question_type_counts": {t: sum(q["test_type"] == t for q in questions) for t in sorted({q["test_type"] for q in questions})},
        "model": MODEL,
        "tokenizer": ENCODING_NAME,
        "chunk_size_tokens": CHUNK_SIZE,
        "chunk_overlap_tokens": CHUNK_OVERLAP,
        "expected_chunk_tokens_a": chunk_token_counts["A_section"],
        "expected_chunk_tokens_b": chunk_token_counts["B_500_80"],
        "query_tokens_once_shared_by_both_methods": question_tokens,
        "expected_total_input_tokens": total_tokens,
        "price_usd_per_million_input_tokens": price,
        "estimated_embedding_cost_usd": total_tokens * price / 1_000_000,
        "runtime": {"python": sys.version.split()[0], "platform": platform.platform()},
        "vector_search_emulation": {
            "score": "cosine_similarity, rounded to 3 decimals before final rank",
            "sort": "descending score; stable insertion order for ties",
            "per_store_top_k": VECTOR_STORE_TOP_K,
            "dedupe": "doc + section metadata key",
            "final_top_k": FINAL_TOP_K,
            "all_role": "ticketmoa_kb_v1_all only",
            "staff_role": "ticketmoa_kb_v1_all plus ticketmoa_kb_v1_staff",
        },
        "limitations": [
            "검색은 저장소의 ticketmoa-search.json 정리 순서를 로컬 벡터로 재현하며 n8n 실행 결과가 아니다.",
            "no_ground/no_external_leak은 검색만 수행하므로 답변 생성·환각·외부 URL 응답을 판정하지 않는다.",
            "B 방식은 절 본문 원문 오프셋과 교차한 절 목록으로 정답을 판정한다.",
            "현재 저장소에 강사 지정 30/30 규칙 근거가 없어 CSV와 docs/RAG-EVALUATION-QUESTIONS.md에 기록된 기준만 적용한다.",
        ],
    }


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def js_round_3(score: float) -> float:
    return math.floor(score * 1000 + 0.5) / 1000


def retrieve(
    query_vector: list[float], chunks: list[dict[str, Any]], role: str,
) -> tuple[list[dict[str, Any]], float, bool]:
    started = time.perf_counter()
    allowed = [c for c in chunks if role == "staff" or c["access_level"] == "all"]
    public = [c for c in allowed if c["access_level"] == "all"]
    staff = [c for c in allowed if c["access_level"] == "staff"] if role == "staff" else []

    def top(store: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked = []
        for c in store:
            raw_score = cosine(query_vector, c["vector"])
            ranked.append({**c, "score": js_round_3(raw_score)})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:VECTOR_STORE_TOP_K]

    ranked = top(public) + top(staff)
    ranked.sort(key=lambda x: x["score"], reverse=True)
    deduped = []
    seen = set()
    for hit in ranked:
        key = (hit["doc"], hit["section_key"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(hit)
    hits = deduped[:FINAL_TOP_K]
    leaked = any(h["access_level"] == "staff" for h in hits) if role == "all" else False
    elapsed_ms = (time.perf_counter() - started) * 1000
    return hits, elapsed_ms, leaked


def embedding_batches(texts: list[str], encoding: Any, max_items: int = 64) -> list[list[str]]:
    batches: list[list[str]] = []
    current: list[str] = []
    token_count = 0
    for text in texts:
        n = len(encoding.encode(text, disallowed_special=()))
        if n > 8192:
            raise ValueError(f"단일 임베딩 입력이 8192 토큰을 넘습니다: {n}")
        if current and (len(current) >= max_items or token_count + n > 100_000):
            batches.append(current)
            current, token_count = [], 0
        current.append(text)
        token_count += n
    if current:
        batches.append(current)
    return batches


def call_embeddings(texts: list[str], api_key: str, encoding: Any) -> tuple[list[list[float]], int, float]:
    vectors: list[list[float]] = []
    reported_tokens = 0
    elapsed_ms = 0.0
    for batch in embedding_batches(texts, encoding):
        payload = json.dumps({"model": MODEL, "input": batch}, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            "https://api.openai.com/v1/embeddings", data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
            method="POST",
        )
        started = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"OpenAI embeddings API HTTP {e.code}; 자동 재시도는 하지 않았습니다.") from None
        except (urllib.error.URLError, TimeoutError) as e:
            raise RuntimeError(f"OpenAI embeddings API 연결/시간 초과; 자동 재시도는 하지 않았습니다: {e}") from None
        elapsed_ms += (time.perf_counter() - started) * 1000
        data = sorted(body.get("data", []), key=lambda item: item.get("index", 0))
        if len(data) != len(batch):
            raise RuntimeError(f"임베딩 응답 수가 요청 수와 다릅니다: {len(data)} / {len(batch)}")
        vectors.extend(item["embedding"] for item in data)
        reported_tokens += int((body.get("usage") or {}).get("total_tokens", 0))
    return vectors, reported_tokens, elapsed_ms


def write_results(
    outdir: Path, docs: list[dict[str, Any]], questions: list[dict[str, Any]],
    chunks_by_method: dict[str, list[dict[str, Any]]], query_vectors: list[list[float]],
    embeddings_usage: dict[str, Any], metadata: dict[str, Any], encoding: Any,
) -> None:
    # Keep the persisted field name aligned with main()'s usage payload. Missing
    # timing is unknown, not zero; JSON stores null and CSV/Markdown say 미측정.
    raw_query_embedding_ms = embeddings_usage.get("query_embedding_batch_ms")
    query_embedding_ms = (
        round(float(raw_query_embedding_ms), 3)
        if isinstance(raw_query_embedding_ms, (int, float)) and not isinstance(raw_query_embedding_ms, bool)
        else None
    )
    question_rows = []
    summary_rows = []
    for method, chunks in chunks_by_method.items():
        method_questions = []
        for q, vector in zip(questions, query_vectors):
            hits, search_ms, staff_leak = retrieve(vector, chunks, q["role"])
            acceptable_hit = False
            if q["test_type"] == "positive":
                acceptable_hit = any(
                    h["doc"] == q["expected_doc"] and
                    any(section in h["source_sections"] for section in q["expected_sections"])
                    for h in hits
                )
            internal_docs = {d["doc"] for d in docs}
            external_doc_leak = any(h["doc"] not in internal_docs for h in hits)
            if q["test_type"] == "positive":
                grading = "scored_positive"
                passed: bool | str = acceptable_hit
            elif q["test_type"] == "deny_staff":
                grading = "scored_access_control"
                passed = not staff_leak
            elif q["test_type"] == "no_external_leak":
                grading = "retrieval_only_answer_not_assessed"
                passed = "not_assessed"
            else:
                grading = "retrieval_only_answer_not_assessed"
                passed = "not_assessed"
            row = {
                "method": method,
                "id": q["id"],
                "role": q["role"],
                "question": q["question"],
                "test_type": q["test_type"],
                "expected_doc": q["expected_doc"],
                "expected_sections": q["expected_sections"],
                "top3": [
                    {"doc": h["doc"], "section": h["section"], "source_sections": h["source_sections"], "score": h["score"]}
                    for h in hits
                ],
                "hit_at_3": acceptable_hit if q["test_type"] == "positive" else "",
                "passed": passed,
                "grading_scope": grading,
                "retrieval_ms": round(search_ms, 3),
                "staff_doc_leak": staff_leak,
                "external_doc_leak": external_doc_leak,
                "retrieved_any": bool(hits),
                "top1_score": hits[0]["score"] if hits else 0,
            }
            method_questions.append(row)
            question_rows.append(row)
        positives = [r for r in method_questions if r["test_type"] == "positive"]
        access_rows = [r for r in method_questions if r["test_type"] == "deny_staff"]
        retrieval_times = [r["retrieval_ms"] for r in method_questions]
        token_counts = [len(encoding.encode(c["text"], disallowed_special=())) for c in chunks]
        char_counts = [js_string_length(c["text"]) for c in chunks]
        summary_rows.append({
            "method": method,
            "chunk_count": len(chunks),
            "chunk_chars_min": stats(char_counts)["min"],
            "chunk_chars_median": stats(char_counts)["median"],
            "chunk_chars_max": stats(char_counts)["max"],
            "chunk_tokens_min": stats(token_counts)["min"],
            "chunk_tokens_median": stats(token_counts)["median"],
            "chunk_tokens_max": stats(token_counts)["max"],
            "positive_hit_count": sum(bool(r["hit_at_3"]) for r in positives),
            "positive_question_count": len(positives),
            "hit_at_3": f"{sum(bool(r['hit_at_3']) for r in positives)}/{len(positives)}" if positives else "n/a",
            "hit_at_3_rate": round(sum(bool(r["hit_at_3"]) for r in positives) / len(positives), 6) if positives else "",
            "deny_staff_passed": sum(r["passed"] is True for r in access_rows),
            "deny_staff_count": len(access_rows),
            "staff_leak_count": sum(r["staff_doc_leak"] for r in method_questions),
            "external_doc_leak_count": sum(r["external_doc_leak"] for r in method_questions),
            "retrieval_ms_p50": round(statistics.median(retrieval_times), 3) if retrieval_times else "",
            "retrieval_ms_p95": round(sorted(retrieval_times)[math.ceil(0.95 * len(retrieval_times)) - 1], 3) if retrieval_times else "",
            "query_embedding_batch_ms_shared": query_embedding_ms,
        })
    chunks_csv = chunk_rows(chunks_by_method, encoding)
    write_csv(outdir / "summary.csv", summary_rows, list(summary_rows[0].keys()))
    write_csv(outdir / "questions.csv", question_rows, list(question_rows[0].keys()))
    write_csv(outdir / "chunks.csv", chunks_csv, list(chunks_csv[0].keys()))
    metadata.update({"mode": "executed", "embedding_usage": embeddings_usage, "summary": summary_rows})
    (outdir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# RAG 청킹 비교 결과", "",
        f"- 실행 ID: `{metadata['run_id']}`", f"- 실행 시각(UTC): `{metadata['created_at_utc']}`",
        f"- Git 커밋: `{metadata.get('git_commit')}`", f"- 문서 스냅샷 SHA-256: `{metadata['document_snapshot_sha256']}`",
        f"- 질문 CSV SHA-256: `{metadata['question_csv_sha256']}`", f"- 모델: `{MODEL}` / tokenizer `{ENCODING_NAME}`", "",
        "| 방식 | 청크 수 | 문자 길이 min/median/max | 토큰 길이 min/median/max | hit@3 | 검색 ms p50/p95 | 질문 임베딩 ms | 직원 누출 |",
        "|---|---:|---|---|---|---|---:|---:|",
    ]
    for s in summary_rows:
        query_ms = s["query_embedding_batch_ms_shared"]
        query_ms_text = f"{query_ms:.3f}" if query_ms is not None else "미측정"
        lines.append(f"| {s['method']} | {s['chunk_count']} | {s['chunk_chars_min']} / {s['chunk_chars_median']} / {s['chunk_chars_max']} | {s['chunk_tokens_min']} / {s['chunk_tokens_median']} / {s['chunk_tokens_max']} | {s['hit_at_3']} | {s['retrieval_ms_p50']} / {s['retrieval_ms_p95']} | {query_ms_text} | {s['staff_leak_count']} |")
    lines += ["", "검색 시간은 OpenAI query embedding API 시간을 제외한 로컬 cosine 검색·정렬 시간이다. 질문 임베딩 배치 시간은 실제 측정값만 기록하며, 값이 없으면 미측정으로 둔다. metadata.json에는 누락값을 null로 기록한다.", "no_ground/no_external_leak 문항은 답변 생성을 하지 않으므로 안전 응답·외부 URL 생성 여부를 채점하지 않았다."]
    (outdir / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="A ## chunking vs B 500-token/80-overlap RAG retrieval comparison")
    parser.add_argument("--knowledge", type=Path, default=ROOT / "knowledge")
    parser.add_argument("--questions", type=Path, default=ROOT / "docs" / "RAG-EVALUATION-QUESTIONS.csv")
    parser.add_argument("--out", type=Path, help="출력 폴더 (기본: OS 임시 폴더 아래 고유 실행 ID)")
    parser.add_argument("--price-usd-per-million", type=float, default=PRICE_PER_MILLION_USD)
    parser.add_argument("--dry-run", action="store_true", help="청킹·비용 계획만 생성합니다 (기본값).")
    parser.add_argument("--execute", action="store_true", help="임베딩 API를 실제 호출합니다. 기본은 dry-run입니다.")
    parser.add_argument("--approve-openai-cost", action="store_true", help="호출 비용 발생을 명시적으로 승인합니다.")
    parser.add_argument("--max-cost-usd", type=float, help="승인 가능한 예상 입력 비용 상한 (USD)")
    args = parser.parse_args()
    if args.execute and args.dry_run:
        parser.error("--execute와 --dry-run은 함께 사용할 수 없습니다.")
    if args.price_usd_per_million <= 0:
        parser.error("--price-usd-per-million은 양수여야 합니다.")
    if args.execute and (not args.approve_openai_cost or args.max_cost_usd is None):
        parser.error("유료 API 실행에는 --execute --approve-openai-cost --max-cost-usd 값이 모두 필요합니다.")
    if not args.execute and (args.approve_openai_cost or args.max_cost_usd is not None):
        parser.error("비용 승인 옵션은 --execute와 함께 사용할 수 있습니다.")
    if args.max_cost_usd is not None and args.max_cost_usd < 0:
        parser.error("--max-cost-usd는 0 이상이어야 합니다.")
    try:
        import tiktoken
    except ImportError:
        print("tiktoken이 필요합니다. `uv run tools/compare_chunking.py`로 실행하면 스크립트 메타데이터의 의존성을 준비합니다.", file=sys.stderr)
        return 2

    run_id = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    outdir = None
    try:
        docs, _ = load_documents(args.knowledge)
        questions, questions_hash = load_questions(args.questions, docs)
        encoding = tiktoken.get_encoding(ENCODING_NAME)
        a_chunks = make_section_chunks(docs)
        b_chunks = token_section_chunks(docs, encoding)
        methods = {"A_section": a_chunks, "B_500_80": b_chunks}
        meta = plan_metadata(docs, questions, questions_hash, methods, encoding, run_id, args.price_usd_per_million)
        outdir = output_dir(args.out, run_id)
        planned_chunk_rows = chunk_rows(methods, encoding)
        write_csv(outdir / "chunks.csv", planned_chunk_rows, list(planned_chunk_rows[0].keys()))
        (outdir / "plan.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Git: {meta.get('git_branch')} @ {meta.get('git_commit')}")
        print(f"문서: {len(docs)}개 / snapshot sha256={meta['document_snapshot_sha256']}")
        print(f"질문: {len(questions)}개 / 유형={json.dumps(meta['question_type_counts'], ensure_ascii=False)} / CSV sha256={questions_hash}")
        print(f"모델: {MODEL} / tokenizer: {ENCODING_NAME} / 단가: ${args.price_usd_per_million:.6f} per 1M input tokens")
        print("\n| 방식 | 청크 수 | 청크 본문 입력 토큰 |")
        print("|---|---:|---:|")
        for name, chunks in methods.items():
            n_tokens = sum(len(encoding.encode(c["text"], disallowed_special=())) for c in chunks)
            lengths = [js_string_length(c["text"]) for c in chunks]
            print(f"| {name} | {len(chunks)} | {n_tokens} |")
            print(f"  청크 문자 길이 min/median/max: {stats(lengths)}")
        print(f"질문 임베딩 입력 토큰(양 방식 공통 1회): {meta['query_tokens_once_shared_by_both_methods']}")
        print(f"총 예상 입력 토큰 (A+B+질문 1회): {meta['expected_total_input_tokens']}")
        print(f"예상 비용 (기록된 표준 요금 기준): ${meta['estimated_embedding_cost_usd']:.8f} USD")
        print("검색 구성: all은 고객용 저장소만, staff는 고객용+직원용 저장소; cosine score 반올림 후 내림차순·doc/section 중복 제거·top3")
        print(f"계획/청크 CSV 저장: {outdir}")
        if not args.execute:
            print("DRY-RUN: OpenAI API 호출 없음. 청크·계획 파일만 기록했습니다.")
            return 0
        estimate = float(meta["estimated_embedding_cost_usd"])
        if estimate > args.max_cost_usd:
            print(f"예상 비용 ${estimate:.8f}가 승인 상한 ${args.max_cost_usd:.8f}보다 큽니다. API를 호출하지 않았습니다.", file=sys.stderr)
            return 2
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            print("OPENAI_API_KEY 환경 변수가 없습니다. API를 호출하지 않았습니다.", file=sys.stderr)
            return 2
        if not sys.stdin.isatty():
            print("별도 대화형 비용 확인을 위해 터미널에서 실행해야 합니다. API를 호출하지 않았습니다.", file=sys.stderr)
            return 2
        expected_confirmation = f"APPROVE ${args.max_cost_usd:.6f}"
        typed = input(f"예상 표준 비용 ${estimate:.8f}, 승인 상한 ${args.max_cost_usd:.6f}. API 비용 발생에 동의하면 `{expected_confirmation}` 입력: ")
        if typed.strip() != expected_confirmation:
            print("비용 승인이 일치하지 않아 API를 호출하지 않았습니다.")
            return 2

        all_chunk_texts = [c["text"] for cs in methods.values() for c in cs]
        all_vectors, actual_tokens, chunk_embedding_ms = call_embeddings(all_chunk_texts, api_key, encoding)
        offset = 0
        for cs in methods.values():
            for c in cs:
                c["vector"] = all_vectors[offset]
                offset += 1
        query_vectors, query_tokens, query_embedding_ms = call_embeddings([q["question"] for q in questions], api_key, encoding)
        actual_tokens += query_tokens
        usage = {
            "actual_api_input_tokens_reported": actual_tokens,
            "estimated_api_input_tokens": meta["expected_total_input_tokens"],
            "estimated_cost_usd": estimate,
            "actual_cost_usd_at_configured_rate": actual_tokens * args.price_usd_per_million / 1_000_000,
            "chunk_embedding_api_ms": round(chunk_embedding_ms, 3),
            "query_embedding_batch_ms": round(query_embedding_ms, 3),
            "automatic_retries": 0,
        }
        write_results(outdir, docs, questions, methods, query_vectors, usage, meta, encoding)
        print(f"실험 완료. 실제 입력 토큰={actual_tokens}, 보고 단가 기준 비용=${usage['actual_cost_usd_at_configured_rate']:.8f}")
        print(f"결과 CSV/표: {outdir}")
        return 0
    except Exception as exc:
        print(f"오류: {exc}", file=sys.stderr)
        if outdir:
            print(f"이미 생성된 계획 파일은 유지했습니다: {outdir}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
