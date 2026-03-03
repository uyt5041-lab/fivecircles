#!/usr/bin/env python3
"""
Phase2 validator: codebook A_* keys must resolve in attribute/attribute_closure.
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

ROOT = Path(__file__).resolve().parents[2]
CODEBOOK_PATH = ROOT / "fivecircles/architecture/specs/reveals/reveal-target-key-codebook.phase1.json"


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


def main() -> int:
    raw = json.loads(CODEBOOK_PATH.read_text(encoding="utf-8"))
    allow_list: list[str] = [str(x).strip().upper() for x in raw.get("allow_list", []) if str(x).strip()]
    allow_set = set(allow_list)

    errors: list[str] = []
    warnings: list[str] = []

    attr_rows = mysql("SELECT code FROM attribute WHERE is_active = 1;")
    attr_codes = {r[0].strip().upper() for r in attr_rows if r and r[0].strip()}

    missing_codes = sorted(code for code in allow_set if code not in attr_codes)
    if missing_codes:
        errors.append(f"allow_list codes missing in attribute table: {missing_codes}")

    closure_rows = mysql(
        """
        SELECT a.code, COUNT(*)
        FROM attribute a
        LEFT JOIN attribute_closure ac ON ac.ancestor_id = a.id
        WHERE a.is_active = 1
        GROUP BY a.code;
        """.strip()
    )
    zero_closure_codes = sorted(r[0] for r in closure_rows if int(r[1]) == 0)
    if zero_closure_codes:
        errors.append(f"codes with zero closure rows: {zero_closure_codes}")

    orphan_rows = mysql(
        """
        SELECT c.code
        FROM attribute c
        LEFT JOIN attribute p ON p.id = c.parent_id
        WHERE c.parent_id IS NOT NULL
          AND p.id IS NULL;
        """.strip()
    )
    if orphan_rows:
        errors.append(f"orphan parent links: {[r[0] for r in orphan_rows]}")

    root_rows = mysql(
        """
        SELECT COUNT(*)
        FROM attribute
        WHERE parent_id IS NULL
          AND is_active = 1;
        """.strip()
    )
    root_count = int(root_rows[0][0]) if root_rows else 0
    if root_count == 0:
        errors.append("no active root node in attribute taxonomy")
    elif root_count > 3:
        warnings.append(f"active root node count is high: {root_count}")

    result = {
        "status": "PASS" if not errors else "FAIL",
        "allow_list_count": len(allow_set),
        "attribute_active_count": len(attr_codes),
        "active_root_count": root_count,
        "warnings": warnings,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
