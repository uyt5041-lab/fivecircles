#!/usr/bin/env python3
"""
Validate Phase2 ATTRIBUTE target_id migration status.

Checks:
- If target_type='ATTRIBUTE' and target_key exists, target_id must equal attribute.id(code=target_key)
- drama10 must have zero missing target_key rows
- unresolved legacy rows are reported as warnings (outside drama10)
"""

from __future__ import annotations

import json
import subprocess
from typing import List

MYSQL_CONTAINER = "nospoiler-mysql"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "nospoiler_event"


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
    out: List[List[str]] = []
    for line in proc.stdout.splitlines():
        if line:
            out.append(line.split("\t"))
    return out


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    mismatched = mysql(
        """
        SELECT er.event_id, e.drama_id, er.target_id, er.target_key, a.id AS expected_attribute_id
        FROM event_reveal er
        JOIN event e ON e.id = er.event_id
        JOIN attribute a ON a.is_active = 1 AND UPPER(a.code) = UPPER(er.target_key)
        WHERE er.target_type = 'ATTRIBUTE'
          AND er.target_key IS NOT NULL
          AND er.target_key <> ''
          AND er.target_id <> a.id
        ORDER BY e.drama_id, e.episode_end, er.event_id;
        """.strip()
    )
    if mismatched:
        errors.append(f"target_id mismatch rows: {len(mismatched)}")

    unknown_key = mysql(
        """
        SELECT er.event_id, e.drama_id, er.target_key
        FROM event_reveal er
        JOIN event e ON e.id = er.event_id
        LEFT JOIN attribute a ON a.is_active = 1 AND UPPER(a.code) = UPPER(er.target_key)
        WHERE er.target_type = 'ATTRIBUTE'
          AND er.target_key IS NOT NULL
          AND er.target_key <> ''
          AND a.id IS NULL
        ORDER BY e.drama_id, e.episode_end, er.event_id;
        """.strip()
    )
    if unknown_key:
        errors.append(f"unknown attribute key rows: {len(unknown_key)}")

    missing_key_drama10 = mysql(
        """
        SELECT COUNT(*)
        FROM event_reveal er
        JOIN event e ON e.id = er.event_id
        WHERE er.target_type = 'ATTRIBUTE'
          AND e.drama_id = 10
          AND (er.target_key IS NULL OR er.target_key = '');
        """.strip()
    )
    drama10_missing = int(missing_key_drama10[0][0]) if missing_key_drama10 else 0
    if drama10_missing > 0:
        errors.append(f"drama10 missing target_key rows: {drama10_missing}")

    missing_key_legacy = mysql(
        """
        SELECT COUNT(*)
        FROM event_reveal er
        JOIN event e ON e.id = er.event_id
        WHERE er.target_type = 'ATTRIBUTE'
          AND e.drama_id <> 10
          AND (er.target_key IS NULL OR er.target_key = '');
        """.strip()
    )
    legacy_missing = int(missing_key_legacy[0][0]) if missing_key_legacy else 0
    if legacy_missing > 0:
        warnings.append(f"legacy missing target_key rows(outside drama10): {legacy_missing}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "mismatch_rows": len(mismatched),
        "unknown_key_rows": len(unknown_key),
        "drama10_missing_key_rows": drama10_missing,
        "legacy_missing_key_rows": legacy_missing,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
