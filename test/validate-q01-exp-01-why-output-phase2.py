#!/usr/bin/env python3
"""
Validate Q01_EXP_01 WHY output readiness (Phase2).

Checks:
- Q01_EXP_01 anchor event exists and is APPROVED in drama10.
- Anchor event has ATTRIBUTE reveal evidence that matches expanded attribute keys.
- PRECEDES causes exist so because_chain can be composed (2~3 length with focus).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set

ROOT = Path(__file__).resolve().parents[2]
QUESTION_MAP_PATH = ROOT / "fivecircles/architecture/specs/extension100/question-map.q01-expansion.phase1.json"
TAXONOMY_PATH = ROOT / "scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json"

MYSQL_CONTAINER = "nospoiler-mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "nospoiler_event"

QID = "Q01_EXP_01"
DRAMA_ID = 10
ANSWER_EVENT_ID = 3033


def mysql(query: str) -> List[List[str]]:
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
    rows: List[List[str]] = []
    for line in proc.stdout.splitlines():
        if line:
            rows.append(line.split("\t"))
    return rows


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_children_map(edges: List[List[str]]) -> Dict[str, List[str]]:
    m: Dict[str, List[str]] = {}
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            continue
        parent = str(edge[0]).strip().upper()
        child = str(edge[1]).strip().upper()
        if parent and child:
            m.setdefault(parent, []).append(child)
    return m


def expand_keys(roots: List[str], children_map: Dict[str, List[str]]) -> List[str]:
    seen: Set[str] = set()
    stack: List[str] = [str(root).strip().upper() for root in roots if str(root).strip()]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for child in children_map.get(node, []):
            if child not in seen:
                stack.append(child)
    return sorted(seen)


def sql_in_strings(values: List[str]) -> str:
    quoted = ["'" + v.replace("'", "''") + "'" for v in values]
    return ", ".join(quoted) if quoted else "''"


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    question_map = load_json(QUESTION_MAP_PATH)
    taxonomy = load_json(TAXONOMY_PATH)
    item = question_map.get("items", {}).get(QID, {})
    attr_roots = item.get("required_set", {}).get("attribute_set", [])
    children_map = build_children_map(taxonomy.get("domains", {}).get("ATTRIBUTE", {}).get("edges", []))
    expanded_keys = expand_keys(attr_roots, children_map)

    answer_row = mysql(
        f"""
        SELECT id, drama_id, source_status, episode_end
        FROM event
        WHERE id = {ANSWER_EVENT_ID};
        """.strip()
    )
    if not answer_row:
        errors.append(f"answer event missing: {ANSWER_EVENT_ID}")
    else:
        drama_id = int(answer_row[0][1])
        source_status = answer_row[0][2]
        if drama_id != DRAMA_ID:
            errors.append(f"answer event drama mismatch: expected={DRAMA_ID}, got={drama_id}")
        if source_status.upper() != "APPROVED":
            errors.append(f"answer event source_status is not APPROVED: {source_status}")

    reveal_count_rows = mysql(
        f"""
        SELECT COUNT(*)
        FROM event_reveal er
        WHERE er.event_id = {ANSWER_EVENT_ID}
          AND er.target_type = 'ATTRIBUTE'
          AND er.target_key IN ({sql_in_strings(expanded_keys)});
        """.strip()
    )
    reveal_count = int(reveal_count_rows[0][0]) if reveal_count_rows else 0
    if reveal_count <= 0:
        errors.append("Q01_EXP_01 answer event has no ATTRIBUTE reveal evidence for expanded keys")

    cause_rows = mysql(
        f"""
        WITH RECURSIVE cause_chain(event_id, depth) AS (
            SELECT er.from_event_id, 1
            FROM event_relation er
            WHERE er.type = 'PRECEDES'
              AND er.to_event_id = {ANSWER_EVENT_ID}
            UNION DISTINCT
            SELECT er2.from_event_id, cc.depth + 1
            FROM event_relation er2
            JOIN cause_chain cc ON er2.to_event_id = cc.event_id
            WHERE er2.type = 'PRECEDES'
              AND cc.depth < 2
        )
        SELECT event_id, MIN(depth) AS depth
        FROM cause_chain
        GROUP BY event_id
        ORDER BY depth ASC, event_id ASC;
        """.strip()
    )
    cause_event_ids = [int(r[0]) for r in cause_rows]
    if len(cause_event_ids) == 0:
        errors.append("Q01_EXP_01 has no PRECEDES causes for because_chain")
    elif len(cause_event_ids) > 2:
        warnings.append(f"multiple causes found ({len(cause_event_ids)}); runtime keeps latest two for chain")

    because_chain_length = min(2, len(cause_event_ids)) + 1
    if because_chain_length < 2 or because_chain_length > 3:
        errors.append(f"because_chain length out of range(2~3): {because_chain_length}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "question_id": QID,
        "answer_event_id": ANSWER_EVENT_ID,
        "expanded_attribute_keys": expanded_keys,
        "reveal_evidence_count": reveal_count,
        "precedes_cause_ids": cause_event_ids,
        "because_chain_length_expected": because_chain_length,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
