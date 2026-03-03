#!/usr/bin/env python3
"""
Validate Q1 expansion template gate behavior from DB truth tables.

This script does not call /probe. It computes strict-first statuses directly from
nospoiler_event rows (APPROVED + optional K gate) so we can regression-check:
- ANSWERED
- SPOILER_BLOCKED
- NOT_ENOUGH_DATA
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Optional

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


def find_earliest(
    *,
    subject_id: int,
    safe_up_to_episode: Optional[int],
    predicate_codes: list[str],
    q_any_of: list[str],
) -> Optional[dict]:
    where = [
        "e.drama_id = 10",
        "e.source_status = 'APPROVED'",
        f"ec.character_id = {int(subject_id)}",
    ]

    if safe_up_to_episode is not None:
        where.append(f"e.episode_end <= {int(safe_up_to_episode)}")

    if predicate_codes:
        codes = ",".join([f"'{mysql_escape(code.upper())}'" for code in predicate_codes])
        where.append(f"e.predicate_code IN ({codes})")

    if q_any_of:
        likes = []
        for token in q_any_of:
            t = mysql_escape(token)
            likes.append(f"e.summary LIKE '%{t}%' OR e.predicate_suggestion LIKE '%{t}%' ")
        where.append("(" + " OR ".join([f"({x})" for x in likes]) + ")")

    query = f"""
    SELECT e.id, e.episode_start, e.episode_end, e.predicate_code, e.summary
    FROM event e
    JOIN event_character ec ON ec.event_id = e.id
    WHERE {' AND '.join(where)}
    ORDER BY e.episode_start ASC, e.id ASC
    LIMIT 1;
    """.strip()

    rows = run_mysql(query)
    if not rows:
        return None
    row = rows[0]
    return {
        "id": int(row[0]),
        "episodeStart": int(row[1]),
        "episodeEnd": int(row[2]),
        "predicateCode": row[3],
        "summary": row[4],
    }


def resolve_status(safe_event: Optional[dict], any_event: Optional[dict]) -> str:
    if safe_event is not None:
        return "ANSWERED"
    if any_event is not None:
        return "SPOILER_BLOCKED"
    return "NOT_ENOUGH_DATA"


def main() -> int:
    cases = [
        {
            "id": "Q1E1_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["OTHER"],
            "qAnyOf": ["접시 조각", "Why?"],
            "expectStatus": "ANSWERED",
            "expectEventId": 3033,
        },
        {
            "id": "Q1E2_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["MEETS"],
            "qAnyOf": ["직접 투코의 사무실로 찾아간다", "투코의 사무실로 찾아간다"],
            "expectStatus": "ANSWERED",
            "expectEventId": 2376,
        },
        {
            "id": "Q1E3_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["OTHER"],
            "qAnyOf": ["고순도 메스암페타민 유통자를 추적"],
            "expectStatus": "ANSWERED",
            "expectEventId": 2297,
        },
        {
            "id": "Q1E4_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["ATTACKS"],
            "qAnyOf": ["숨겨둔 무기로 월터를 공격하려다 발각"],
            "expectStatus": "ANSWERED",
            "expectEventId": 2410,
        },
        {
            "id": "Q1E5_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["KILLS"],
            "qAnyOf": ["Krazy-8", "크레이지-8"],
            "expectStatus": "ANSWERED",
            "expectEventId": 2292,
        },
        {
            "id": "Q1E6_K6",
            "subjectId": 17,
            "safeUpToEpisode": 6,
            "predicateCodeAnyOf": ["KILLS"],
            "qAnyOf": ["게일 제거", "Full Measure"],
            "expectStatus": "SPOILER_BLOCKED",
            "expectEventId": None,
        },
        {
            "id": "Q1E6_K33",
            "subjectId": 17,
            "safeUpToEpisode": 33,
            "predicateCodeAnyOf": ["KILLS"],
            "qAnyOf": ["게일 제거", "Full Measure"],
            "expectStatus": "ANSWERED",
            "expectEventId": 3032,
        },
        {
            "id": "CONTROL_NO_DATA",
            "subjectId": 17,
            "safeUpToEpisode": 33,
            "predicateCodeAnyOf": ["OTHER"],
            "qAnyOf": ["@@NO_MATCH_TOKEN_Q1_EXP@@"],
            "expectStatus": "NOT_ENOUGH_DATA",
            "expectEventId": None,
        },
    ]

    failures = 0
    for case in cases:
        safe_event = find_earliest(
            subject_id=case["subjectId"],
            safe_up_to_episode=case["safeUpToEpisode"],
            predicate_codes=case["predicateCodeAnyOf"],
            q_any_of=case["qAnyOf"],
        )
        any_event = find_earliest(
            subject_id=case["subjectId"],
            safe_up_to_episode=None,
            predicate_codes=case["predicateCodeAnyOf"],
            q_any_of=case["qAnyOf"],
        )
        actual_status = resolve_status(safe_event, any_event)
        actual_event_id = safe_event["id"] if safe_event else None

        ok = actual_status == case["expectStatus"]
        if case["expectEventId"] is not None:
            ok = ok and (actual_event_id == case["expectEventId"])

        row = {
            "status": "PASS" if ok else "FAIL",
            "case": case["id"],
            "safeUpToEpisode": case["safeUpToEpisode"],
            "expectStatus": case["expectStatus"],
            "actualStatus": actual_status,
            "expectEventId": case["expectEventId"],
            "actualEventId": actual_event_id,
            "safeEvent": safe_event,
            "anyEvent": any_event,
        }
        print(json.dumps(row, ensure_ascii=False))
        if not ok:
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
