#!/usr/bin/env python3
"""
Validate sync between ProductionQ templates and strict MUST matrix doc.

Scope:
- Compare Q01~Q15 only.
- Compare queryKind / canonical_episode / sensitive_policy / strict_must keys
  (predicateCodeAnyOf, excludePredicateCodeAnyOf, qAnyOf)
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_PATH = REPO_ROOT / "front/common/productionQ/templates.ts"
MATRIX_PATH = REPO_ROOT / "fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md"
QUESTION_IDS = {f"Q{i:02d}" for i in range(1, 16)}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    for idx in range(open_index, len(text)):
        ch = text[idx]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return idx
    raise ValueError("Unmatched brace while parsing templates.ts")


def extract_template_blocks(ts_text: str) -> list[str]:
    arr_start = ts_text.find("export const productionQTemplates")
    if arr_start < 0:
        raise ValueError("productionQTemplates declaration not found")
    arr_open = ts_text.find("[", arr_start)
    arr_close = ts_text.rfind("];")
    if arr_open < 0 or arr_close < 0:
        raise ValueError("productionQTemplates array boundaries not found")

    blocks: list[str] = []
    idx = arr_open + 1
    while idx < arr_close:
        brace_open = ts_text.find("{", idx, arr_close)
        if brace_open < 0:
            break
        brace_close = find_matching_brace(ts_text, brace_open)
        blocks.append(ts_text[brace_open : brace_close + 1])
        idx = brace_close + 1
    return blocks


def extract_field(block: str, key: str) -> str | None:
    m = re.search(rf"\b{re.escape(key)}\s*:\s*'([^']*)'", block)
    return m.group(1) if m else None


def extract_strict_must_block(template_block: str) -> str | None:
    marker = "strict_must:"
    pos = template_block.find(marker)
    if pos < 0:
        return None
    open_brace = template_block.find("{", pos)
    if open_brace < 0:
        return None
    close_brace = find_matching_brace(template_block, open_brace)
    return template_block[open_brace : close_brace + 1]


def parse_ts_array_values(block: str, key: str) -> list[str]:
    m = re.search(rf"\b{re.escape(key)}\s*:\s*\[([^\]]*)\]", block, flags=re.DOTALL)
    if not m:
        return []
    return [s.strip() for s in re.findall(r"'([^']+)'", m.group(1))]


def norm_list(values: list[str]) -> list[str]:
    return sorted({v.strip() for v in values if v.strip()})


def parse_templates(ts_text: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for block in extract_template_blocks(ts_text):
        qid = extract_field(block, "question_id")
        if not qid or qid not in QUESTION_IDS:
            continue
        strict = extract_strict_must_block(block) or ""
        rows[qid] = {
            "queryKind": extract_field(block, "queryKind"),
            "canonical_episode": extract_field(block, "canonical_episode"),
            "sensitive_policy": extract_field(block, "sensitive_policy"),
            "strict": {
                "predicateCodeAnyOf": norm_list(parse_ts_array_values(strict, "predicateCodeAnyOf")),
                "excludePredicateCodeAnyOf": norm_list(parse_ts_array_values(strict, "excludePredicateCodeAnyOf")),
                "qAnyOf": norm_list(parse_ts_array_values(strict, "qAnyOf")),
            },
        }
    return rows


def split_md_table_line(line: str) -> list[str]:
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return parts


def strip_ticks(v: str) -> str:
    return v.strip().strip("`").strip()


def parse_cell_list(cell: str, key: str) -> list[str]:
    m = re.search(rf"{re.escape(key)}\s*=\s*\[([^\]]*)\]", cell)
    if not m:
        return []
    inner = m.group(1)
    return [x.strip().strip("`") for x in inner.split(",") if x.strip()]


def parse_matrix(md_text: str) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line.startswith("| `Q"):
            continue
        cols = split_md_table_line(line)
        if len(cols) < 8:
            continue
        qid = strip_ticks(cols[0])
        if qid not in QUESTION_IDS:
            continue
        strict_cell = cols[4]
        rows[qid] = {
            "queryKind": strip_ticks(cols[2]),
            "canonical_episode": strip_ticks(cols[3]),
            "sensitive_policy": strip_ticks(cols[6]),
            "strict": {
                "predicateCodeAnyOf": norm_list(parse_cell_list(strict_cell, "predicateCodeAnyOf")),
                "excludePredicateCodeAnyOf": norm_list(parse_cell_list(strict_cell, "excludePredicateCodeAnyOf")),
                "qAnyOf": norm_list(parse_cell_list(strict_cell, "qAnyOf")),
            },
        }
    return rows


def compare(rows_ts: dict[str, dict], rows_md: dict[str, dict]) -> list[str]:
    diffs: list[str] = []
    for qid in sorted(QUESTION_IDS):
        t = rows_ts.get(qid)
        m = rows_md.get(qid)
        if not t:
            diffs.append(f"{qid}: missing in templates.ts")
            continue
        if not m:
            diffs.append(f"{qid}: missing in matrix.md")
            continue

        for key in ("queryKind", "canonical_episode", "sensitive_policy"):
            if (t.get(key) or "") != (m.get(key) or ""):
                diffs.append(f"{qid}: {key} mismatch (template='{t.get(key)}', matrix='{m.get(key)}')")

        for key in ("predicateCodeAnyOf", "excludePredicateCodeAnyOf", "qAnyOf"):
            tv = t["strict"].get(key, [])
            mv = m["strict"].get(key, [])
            if tv != mv:
                diffs.append(f"{qid}: strict_must.{key} mismatch (template={tv}, matrix={mv})")
    return diffs


def main() -> int:
    ts_rows = parse_templates(read_text(TEMPLATES_PATH))
    md_rows = parse_matrix(read_text(MATRIX_PATH))
    diffs = compare(ts_rows, md_rows)
    if diffs:
        print("FAIL: templates.ts and 04 matrix are out of sync.")
        for d in diffs:
            print(f"- {d}")
        return 1

    print("PASS: templates.ts and 04 matrix sync gate")
    print(f"- compared question ids: {len(QUESTION_IDS)} (Q01~Q15)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
