#!/usr/bin/env python3
"""
Phase1 runtime validation for reveal target_key policy.

Covers:
- BP3-4: missing target_key row policy (drama10 reject / others warn)
- BP4-4: Q01_EXP_01 codebook-based reproduction check
- BP6-2: unresolved(backfill-impossible) rows report
- BP6-4: expansion question coverage (B-lane target_key) >= 80%
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

MYSQL_CONTAINER = "nospoiler-mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "nospoiler_event"

ROOT = Path(__file__).resolve().parents[2]
QUESTION_MAP_PATH = ROOT / "fivecircles/architecture/specs/extension100/question-map.q01-expansion.phase1.json"
TAXONOMY_PATH = ROOT / "fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json"
ANSWERSET_PATH = ROOT / "fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json"
PHASE1_TS_PATH = ROOT / "front/common/productionQ/inheritancePhase1.ts"


def mysql(query: str) -> list[list[str]]:
    cmd = [
        "docker",
        "exec",
        "-i",
        MYSQL_CONTAINER,
        "mysql",
        "--default-character-set=utf8mb4",
        f"-u{MYSQL_USER}",
        f"-p{MYSQL_PASSWORD}",
        "-N",
        "-B",
        MYSQL_DATABASE,
        "-e",
        query,
    ]
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "mysql query failed")
    rows: list[list[str]] = []
    for line in proc.stdout.splitlines():
        if line:
            rows.append(line.split("\t"))
    return rows


def sql_in_strings(values: list[str]) -> str:
    escaped = [v.replace("\\", "\\\\").replace("'", "\\'") for v in values]
    return ", ".join(f"'{v}'" for v in escaped)


def sql_in_ints(values: list[int]) -> str:
    return ", ".join(str(v) for v in values)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_attribute_bindings(ts_text: str) -> dict[str, list[int]]:
    m = re.search(
        r"const attributeTargetBindings:\s*Record<string,\s*number\[]>\s*=\s*\{(.*?)\};",
        ts_text,
        re.S,
    )
    if not m:
        return {}
    block = m.group(1)
    result: dict[str, list[int]] = {}
    for key, raw_ids in re.findall(r"\b(A_[A-Z0-9_]+)\s*:\s*\[([^\]]*)\]", block):
        ids: list[int] = []
        for token in raw_ids.split(","):
            token = token.strip()
            if token.isdigit():
                ids.append(int(token))
        result[key] = ids
    return result


def build_children_map(edges: list[list[str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for edge in edges:
        if len(edge) != 2:
            continue
        parent, child = edge
        out.setdefault(parent, []).append(child)
    return out


def expand_keys(seeds: list[str], children_map: dict[str, list[str]]) -> list[str]:
    visited: set[str] = set()
    queue: list[str] = list(seeds)
    guard = 0
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        guard += 1
        if guard > 2000:
            break
        for child in children_map.get(node, []):
            if child not in visited:
                queue.append(child)
    return sorted(visited)


def load_expected_q01_exp_01_answer_id() -> int:
    raw = load_json(ANSWERSET_PATH)
    for item in raw.get("items", []):
        if item.get("expansion_id") == "Q1-1":
            value = item.get("answer_event_id")
            if isinstance(value, int):
                return value
    raise RuntimeError("answerset Q1-1 answer_event_id not found")


def find_earliest_event_id(drama_id: int, keys: list[str], target_ids: list[int]) -> int | None:
    if not keys:
        return None
    key_clause = f"er.target_key IN ({sql_in_strings(keys)})"
    target_clause = ""
    if target_ids:
        target_clause = f" AND er.target_id IN ({sql_in_ints(target_ids)})"
    rows = mysql(
        f"""
        SELECT e.id
        FROM event e
        JOIN event_reveal er ON er.event_id = e.id
        WHERE e.drama_id = {drama_id}
          AND e.source_status = 'APPROVED'
          AND er.target_type = 'ATTRIBUTE'
          AND {key_clause}
          {target_clause}
        ORDER BY e.episode_start ASC, e.id ASC
        LIMIT 1;
        """.strip()
    )
    if not rows:
        return None
    return int(rows[0][0])


def count_candidates(drama_id: int, keys: list[str], target_ids: list[int]) -> int:
    if not keys:
        return 0
    key_clause = f"er.target_key IN ({sql_in_strings(keys)})"
    target_clause = ""
    if target_ids:
        target_clause = f" AND er.target_id IN ({sql_in_ints(target_ids)})"
    rows = mysql(
        f"""
        SELECT COUNT(DISTINCT e.id)
        FROM event e
        JOIN event_reveal er ON er.event_id = e.id
        WHERE e.drama_id = {drama_id}
          AND e.source_status = 'APPROVED'
          AND er.target_type = 'ATTRIBUTE'
          AND {key_clause}
          {target_clause};
        """.strip()
    )
    return int(rows[0][0]) if rows else 0


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    question_map = load_json(QUESTION_MAP_PATH)
    taxonomy = load_json(TAXONOMY_PATH)
    ts_text = PHASE1_TS_PATH.read_text(encoding="utf-8")
    bindings = parse_attribute_bindings(ts_text)
    attr_edges = taxonomy.get("domains", {}).get("ATTRIBUTE", {}).get("edges", [])
    children_map = build_children_map(attr_edges)

    # BP3-4 / BP6-2: missing target_key policy
    missing_rows = mysql(
        """
        SELECT e.id, e.drama_id, er.target_id, IFNULL(er.reveal_type,''), e.episode_end
        FROM event_reveal er
        JOIN event e ON e.id = er.event_id
        WHERE er.target_type = 'ATTRIBUTE'
          AND (er.target_key IS NULL OR er.target_key = '')
        ORDER BY e.drama_id ASC, e.episode_end ASC, e.id ASC;
        """.strip()
    )
    missing_in_drama10 = [r for r in missing_rows if int(r[1]) == 10]
    unresolved_legacy = [r for r in missing_rows if int(r[1]) != 10]
    if missing_in_drama10:
        errors.append(f"missing target_key in drama_id=10 rows: {len(missing_in_drama10)}")
    if unresolved_legacy:
        warnings.append(
            f"legacy unresolved ATTRIBUTE rows kept as warning (outside drama10 scope): {len(unresolved_legacy)}"
        )

    # BP4-4: Q01_EXP_01 reproduction
    q1_item = question_map.get("items", {}).get("Q01_EXP_01", {})
    q1_attr_roots = q1_item.get("required_set", {}).get("attribute_set", [])
    q1_expanded = expand_keys(q1_attr_roots, children_map)
    q1_target_ids: list[int] = []
    for key in q1_attr_roots:
        q1_target_ids.extend(bindings.get(key, []))
    q1_target_ids = sorted(set(q1_target_ids))
    expected_q1 = load_expected_q01_exp_01_answer_id()
    earliest_q1 = find_earliest_event_id(10, q1_expanded, q1_target_ids)
    if earliest_q1 is None:
        errors.append("Q01_EXP_01 replay returned no candidates")
    elif earliest_q1 != expected_q1:
        errors.append(f"Q01_EXP_01 earliest mismatch: expected={expected_q1}, got={earliest_q1}")

    # BP6-4: expansion target_key coverage
    items = question_map.get("items", {})
    qids = sorted(items.keys())
    covered = 0
    per_question: dict[str, int] = {}
    for qid in qids:
        attr_roots = items[qid].get("required_set", {}).get("attribute_set", [])
        expanded = expand_keys(attr_roots, children_map)
        target_ids: list[int] = []
        for key in attr_roots:
            target_ids.extend(bindings.get(key, []))
        target_ids = sorted(set(target_ids))
        count = count_candidates(10, expanded, target_ids)
        per_question[qid] = count
        if count > 0:
            covered += 1
    total = len(qids) if qids else 1
    coverage = covered / total
    if coverage < 0.8:
        errors.append(f"expansion coverage below threshold: {coverage:.3f} < 0.800")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "bp3_4_missing_rows_total": len(missing_rows),
        "bp3_4_missing_rows_drama10": len(missing_in_drama10),
        "bp6_2_unresolved_legacy_rows": len(unresolved_legacy),
        "bp4_4_q01_exp_01": {
            "expected_answer_event_id": expected_q1,
            "earliest_replayed_event_id": earliest_q1,
            "expanded_keys": q1_expanded,
            "target_ids": q1_target_ids,
        },
        "bp6_4_coverage": {
            "covered": covered,
            "total": total,
            "ratio": round(coverage, 4),
            "per_question_candidates": per_question,
        },
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
