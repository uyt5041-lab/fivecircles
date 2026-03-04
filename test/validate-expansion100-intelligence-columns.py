#!/usr/bin/env python3
"""
Validate Expansion100 Q1 ATTRIBUTE injection and intelligence-column contracts.

Checks:
- event exists and APPROVED
- event core columns are valid (summary/source/episode range)
- predicate_code is present and matches expected
- event_reveal row exists with target_type=ATTRIBUTE / reveal_type in (HINT, CONFIRM)
- ATTRIBUTE target_id resolves to attribute.code that matches target_key
- answerset anchor event ids are aligned (drift guard)
- (warn) predicate_suggestion is empty for OTHER rows
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MYSQL_CONTAINER = "nospoiler-mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "nospoiler_event"

REPO_ROOT = Path(__file__).resolve().parents[2]
ANSWERSET_PATH = (
    REPO_ROOT
    / "fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json"
)

ALLOWED_EVENT_SOURCE_STATUS = {"APPROVED"}


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


CASES = [
    {
        "question_id": "Q01_EXP_01",
        "reveal_event_id": 3033,
        "expected_answer_event_id": 3033,
        "target_id": 2,
        "expected_target_key": "A_MORAL_FRAME_SHIFT",
        "expected_reveal_type": "HINT",
        "expected_predicate_code": "OTHER",
    },
    {
        "question_id": "Q01_EXP_02",
        "reveal_event_id": 2376,
        "expected_answer_event_id": 2376,
        "target_id": 3,
        "expected_target_key": "A_VIOLENCE_ADAPTATION",
        "expected_reveal_type": "HINT",
        "expected_predicate_code": "MEETS",
    },
    {
        "question_id": "Q01_EXP_03",
        "reveal_event_id": 2297,
        "expected_answer_event_id": 2297,
        "target_id": 6,
        "expected_target_key": "A_EXTERNAL_PRESSURE",
        "expected_reveal_type": "HINT",
        "expected_predicate_code": "OTHER",
    },
    {
        "question_id": "Q01_EXP_04",
        "reveal_event_id": 2410,
        "expected_answer_event_id": 2410,
        "target_id": 4,
        "expected_target_key": "A_RISK_OR_SURVIVAL_MODE",
        "expected_reveal_type": "HINT",
        "expected_predicate_code": "ATTACKS",
    },
    {
        "question_id": "Q01_EXP_05",
        "reveal_event_id": 3032,
        "expected_answer_event_id": 2292,
        "target_id": 5,
        "expected_target_key": "A_RELATIONSHIP_SHIFT",
        "expected_reveal_type": "CONFIRM",
        "expected_predicate_code": "KILLS",
    },
    {
        "question_id": "Q01_EXP_06",
        "reveal_event_id": 2292,
        "expected_answer_event_id": 3032,
        "target_id": 7,
        "expected_target_key": "A_POINT_OF_NO_RETURN",
        "expected_reveal_type": "CONFIRM",
        "expected_predicate_code": "KILLS",
    },
]

EXPANSION_TO_QUESTION = {
    "Q1-1": "Q01_EXP_01",
    "Q1-2": "Q01_EXP_02",
    "Q1-3": "Q01_EXP_03",
    "Q1-4": "Q01_EXP_04",
    "Q1-5": "Q01_EXP_05",
    "Q1-6": "Q01_EXP_06",
}


def load_answerset_anchor_map() -> dict[str, int]:
    raw = json.loads(ANSWERSET_PATH.read_text(encoding="utf-8"))
    items = raw.get("items", [])
    result: dict[str, int] = {}
    for item in items:
        expansion_id = str(item.get("expansion_id", ""))
        question_id = EXPANSION_TO_QUESTION.get(expansion_id)
        answer_event_id = item.get("answer_event_id")
        if question_id is None or not isinstance(answer_event_id, int):
            continue
        result[question_id] = answer_event_id
    return result


def fetch_event(event_id: int) -> dict | None:
    rows = run_mysql(
        f"""
        SELECT id,
               drama_id,
               predicate_code,
               source_status,
               IFNULL(predicate_suggestion,''),
               summary,
               episode_start,
               episode_end,
               source_type,
               IFNULL(source_id, 0)
        FROM event
        WHERE id = {event_id}
        LIMIT 1;
        """.strip()
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "id": int(r[0]),
        "drama_id": int(r[1]),
        "predicate_code": r[2],
        "source_status": r[3],
        "predicate_suggestion": r[4],
        "summary": r[5],
        "episode_start": int(r[6]),
        "episode_end": int(r[7]),
        "source_type": r[8],
        "source_id": int(r[9]),
    }


def fetch_reveal(event_id: int, target_id: int) -> dict | None:
    rows = run_mysql(
        f"""
        SELECT event_id, target_type, target_id, IFNULL(target_key,''), IFNULL(reveal_type,'')
        FROM event_reveal
        WHERE event_id = {event_id}
          AND target_type = 'ATTRIBUTE'
          AND target_id = {target_id}
        LIMIT 1;
        """.strip()
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "event_id": int(r[0]),
        "target_type": r[1],
        "target_id": int(r[2]),
        "target_key": r[3],
        "reveal_type": r[4],
    }


def fetch_attribute_code(attribute_id: int) -> str | None:
    rows = run_mysql(
        f"""
        SELECT code
        FROM attribute
        WHERE id = {attribute_id}
        LIMIT 1;
        """.strip()
    )
    if not rows:
        return None
    return rows[0][0]


def main() -> int:
    failures = 0
    warnings = 0
    answerset_anchor_map = load_answerset_anchor_map()

    for case in CASES:
        errors: list[str] = []
        warns: list[str] = []

        event = fetch_event(case["reveal_event_id"])
        if event is None:
            errors.append("event_not_found")
        else:
            if event["drama_id"] != 10:
                errors.append("drama_id_mismatch")
            if event["source_status"] not in ALLOWED_EVENT_SOURCE_STATUS:
                errors.append(f"source_status_not_approved:{event['source_status']}")
            if not event["summary"].strip():
                errors.append("summary_empty")
            if event["episode_start"] <= 0 or event["episode_end"] <= 0:
                errors.append("episode_range_not_positive")
            if event["episode_start"] > event["episode_end"]:
                errors.append("episode_range_invalid")
            if not event["source_type"].strip():
                errors.append("source_type_empty")
            if not event["predicate_code"]:
                errors.append("predicate_code_empty")
            elif event["predicate_code"] != case["expected_predicate_code"]:
                errors.append(
                    f"predicate_code_mismatch:{event['predicate_code']}!= {case['expected_predicate_code']}"
                )
            if event["predicate_code"] == "OTHER" and not event["predicate_suggestion"]:
                warns.append("predicate_suggestion_empty_for_OTHER")

        reveal = fetch_reveal(case["reveal_event_id"], case["target_id"])
        if reveal is None:
            errors.append("attribute_reveal_missing")
        else:
            if reveal["target_id"] <= 0:
                errors.append("target_id_not_positive")
            if not reveal["target_key"]:
                errors.append("target_key_missing")
            elif reveal["target_key"] != case["expected_target_key"]:
                errors.append(
                    f"target_key_mismatch:{reveal['target_key']}!= {case['expected_target_key']}"
                )
            if reveal["reveal_type"] not in ("HINT", "CONFIRM"):
                errors.append(f"invalid_reveal_type:{reveal['reveal_type']}")
            if reveal["reveal_type"] != case["expected_reveal_type"]:
                errors.append(
                    f"reveal_type_mismatch:{reveal['reveal_type']}!= {case['expected_reveal_type']}"
                )
            attribute_code = fetch_attribute_code(reveal["target_id"])
            if attribute_code is None:
                errors.append("attribute_id_not_found")
            elif attribute_code != case["expected_target_key"]:
                errors.append(f"attribute_code_mismatch:{attribute_code}!= {case['expected_target_key']}")

        answerset_event_id = answerset_anchor_map.get(case["question_id"])
        if answerset_event_id is None:
            errors.append("answerset_anchor_missing")
        elif answerset_event_id != case["expected_answer_event_id"]:
            errors.append(
                f"answerset_anchor_mismatch:{answerset_event_id}!= {case['expected_answer_event_id']}"
            )

        ok = len(errors) == 0
        if not ok:
            failures += 1
        warnings += len(warns)

        print(
            json.dumps(
                {
                    "status": "PASS" if ok else "FAIL",
                    "question_id": case["question_id"],
                    "reveal_event_id": case["reveal_event_id"],
                    "answer_event_id": case["expected_answer_event_id"],
                    "target_id": case["target_id"],
                    "errors": errors,
                    "warnings": warns,
                },
                ensure_ascii=False,
            )
        )

    summary = {
        "status": "PASS" if failures == 0 else "FAIL",
        "total_cases": len(CASES),
        "failures": failures,
        "warnings": warnings,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
