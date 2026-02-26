#!/usr/bin/env python3
"""
Regression snapshot validator for Q6/Q7/Q10/Q14 strict-first AND behavior.

Compares DB-derived strict/probe status to snapshot:
- ANSWERED
- SPOILER_BLOCKED
- NOT_ENOUGH_DATA
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = REPO_ROOT / "fivecircles/architecture/specs/predicate/artifacts/and-regression-q6-q7-q10-q14.json"

MYSQL_CONTAINER = "nospoiler-mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "nospoiler_event"


def mysql_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def run_mysql(query: str) -> list[list[str]]:
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


def resolve_status(safe_event_id: Optional[int], any_event_id: Optional[int]) -> str:
    if safe_event_id is not None:
        return "ANSWERED"
    if any_event_id is not None:
        return "SPOILER_BLOCKED"
    return "NOT_ENOUGH_DATA"


def get_event_summary(event_id: int) -> Optional[str]:
    query = f"SELECT summary FROM event WHERE id = {int(event_id)} LIMIT 1;"
    rows = run_mysql(query)
    if not rows:
        return None
    return rows[0][0]


def token_like_clause(tokens: list[str], alias: str = "e") -> str:
    if not tokens:
        return "1=1"
    likes = []
    for t in tokens:
        et = mysql_escape(t)
        likes.append(f"{alias}.summary LIKE '%{et}%'")
        likes.append(f"{alias}.predicate_suggestion LIKE '%{et}%'")
    return "(" + " OR ".join(likes) + ")"


def in_clause(values: list[str]) -> str:
    if not values:
        return ""
    return "(" + ",".join(f"'{mysql_escape(v.upper())}'" for v in values) + ")"


def find_character_predicate_earliest(
    *,
    subject_id: int,
    safe_up_to_episode: Optional[int],
    predicate_codes: list[str],
    exclude_predicate_codes: list[str],
    q_any_of: list[str],
) -> Optional[int]:
    where = [
        "e.drama_id = 10",
        "e.source_status = 'APPROVED'",
        f"ec.character_id = {subject_id}",
    ]
    if safe_up_to_episode is not None:
        where.append(f"e.episode_end <= {safe_up_to_episode}")
    if predicate_codes:
        where.append(f"e.predicate_code IN {in_clause(predicate_codes)}")
    if exclude_predicate_codes:
        where.append(f"e.predicate_code NOT IN {in_clause(exclude_predicate_codes)}")
    where.append(token_like_clause(q_any_of))

    query = f"""
    SELECT e.id
    FROM event e
    JOIN event_character ec ON ec.event_id = e.id
    WHERE {' AND '.join(where)}
    ORDER BY e.episode_start ASC, e.id ASC
    LIMIT 1;
    """.strip()
    rows = run_mysql(query)
    return int(rows[0][0]) if rows else None


def find_coevents_earliest(
    *,
    a_id: int,
    b_id: int,
    safe_up_to_episode: Optional[int],
    predicate_codes: list[str],
    q_any_of: list[str],
) -> Optional[int]:
    where = [
        "e.drama_id = 10",
        "e.source_status = 'APPROVED'",
        f"ec1.character_id = {a_id}",
        f"ec2.character_id = {b_id}",
    ]
    if safe_up_to_episode is not None:
        where.append(f"e.episode_end <= {safe_up_to_episode}")
    if predicate_codes:
        where.append(f"e.predicate_code IN {in_clause(predicate_codes)}")
    where.append(token_like_clause(q_any_of))

    query = f"""
    SELECT e.id
    FROM event e
    JOIN event_character ec1 ON ec1.event_id = e.id
    JOIN event_character ec2 ON ec2.event_id = e.id
    WHERE {' AND '.join(where)}
    ORDER BY e.episode_start ASC, e.id ASC
    LIMIT 1;
    """.strip()
    rows = run_mysql(query)
    return int(rows[0][0]) if rows else None


def execute_case(case_id: str, safe_up_to_episode: int) -> dict:
    if case_id.startswith("Q06"):
        strict = {
            "a_id": 17,
            "b_id": 18,
            "predicate_codes": ["ALLIES_WITH", "JOINS", "MEETS"],
            "q_any_of": ["협박", "제안", "동업"],
        }
        safe_event_id = find_coevents_earliest(safe_up_to_episode=safe_up_to_episode, **strict)
        any_event_id = find_coevents_earliest(safe_up_to_episode=None, **strict)
    elif case_id.startswith("Q07"):
        strict = {
            "subject_id": 17,
            "predicate_codes": [],
            "exclude_predicate_codes": [],
            "q_any_of": ["Which one", "어느 폰", "두 번째 폰", "두 번째 휴대폰"],
        }
        safe_event_id = find_character_predicate_earliest(safe_up_to_episode=safe_up_to_episode, **strict)
        any_event_id = find_character_predicate_earliest(safe_up_to_episode=None, **strict)
    elif case_id.startswith("Q10"):
        strict = {
            "subject_id": 17,
            "predicate_codes": ["ATTACKS", "CAPTURES", "BETRAYS", "KILLS"],
            "exclude_predicate_codes": ["DISCOVERS", "LEARNS"],
            "q_any_of": ["투코", "구타", "폭력", "위협"],
        }
        safe_event_id = find_character_predicate_earliest(safe_up_to_episode=safe_up_to_episode, **strict)
        any_event_id = find_character_predicate_earliest(safe_up_to_episode=None, **strict)
    elif case_id.startswith("Q14"):
        strict = {
            "a_id": 17,
            "b_id": 19,
            "predicate_codes": ["BETRAYS", "LEARNS", "DISCOVERS"],
            "q_any_of": ["별거", "신뢰 붕괴", "집에서 나가", "집에서 내보내"],
        }
        safe_event_id = find_coevents_earliest(safe_up_to_episode=safe_up_to_episode, **strict)
        any_event_id = find_coevents_earliest(safe_up_to_episode=None, **strict)
    else:
        raise ValueError(f"Unsupported case id: {case_id}")

    return {
        "safe_event_id": safe_event_id,
        "any_event_id": any_event_id,
        "actual_status": resolve_status(safe_event_id, any_event_id),
        "actual_event_id": safe_event_id,
    }


def main() -> int:
    snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []

    for case in snapshot.get("cases", []):
        result = execute_case(case["case_id"], int(case["safe_up_to_episode"]))
        expected_status = case["expected_status"]
        expected_event_id = case["expected_event_id"]
        ok = result["actual_status"] == expected_status and result["actual_event_id"] == expected_event_id
        expected_summary_contains = case.get("expected_summary_contains")
        actual_summary = None
        summary_ok = True
        if expected_summary_contains and result["actual_event_id"] is not None:
            actual_summary = get_event_summary(result["actual_event_id"])
            summary_ok = actual_summary is not None and expected_summary_contains in actual_summary
            ok = ok and summary_ok
        line = {
            "case_id": case["case_id"],
            "expected_status": expected_status,
            "actual_status": result["actual_status"],
            "expected_event_id": expected_event_id,
            "actual_event_id": result["actual_event_id"],
            "expected_summary_contains": expected_summary_contains,
            "actual_summary": actual_summary,
            "summary_match": summary_ok,
            "safe_event_id": result["safe_event_id"],
            "any_event_id": result["any_event_id"],
            "pass": ok,
        }
        print(json.dumps(line, ensure_ascii=False))
        if not ok:
            failures.append(case["case_id"])

    if failures:
        print(f"FAIL: {len(failures)} regression case(s) mismatched: {failures}")
        return 1

    print("PASS: productionQ AND regression snapshots (Q6/Q7/Q10/Q14)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
