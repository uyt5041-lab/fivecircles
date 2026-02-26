#!/usr/bin/env python3
"""
Validate Production Q template strict_must keys against allow-list.

Scope:
- front/common/productionQ/templates.ts
- strict_must object keys only
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_PATH = REPO_ROOT / "front/common/productionQ/templates.ts"
ALLOWED_STRICT_KEYS = {"predicateCodeAnyOf", "qAnyOf", "excludePredicateCodeAnyOf"}


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


def extract_template_id(block: str) -> str:
    match = re.search(r"\bid\s*:\s*'([^']+)'", block)
    return match.group(1) if match else "<unknown-template-id>"


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


def extract_object_keys(block: str) -> list[str]:
    keys: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*") or not stripped:
            continue
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", stripped)
        if m:
            keys.append(m.group(1))
    return keys


def main() -> int:
    ts_text = read_text(TEMPLATES_PATH)
    blocks = extract_template_blocks(ts_text)

    violations: list[str] = []
    checked = 0
    for block in blocks:
        template_id = extract_template_id(block)
        strict = extract_strict_must_block(block)
        if strict is None:
            continue
        checked += 1
        for key in extract_object_keys(strict):
            if key not in ALLOWED_STRICT_KEYS:
                violations.append(
                    f"{template_id}: strict_must contains disallowed key '{key}' "
                    f"(allowed={sorted(ALLOWED_STRICT_KEYS)})"
                )

    if violations:
        print("FAIL: strict_must key allow-list violations found.")
        for v in violations:
            print(f"- {v}")
        return 1

    print("PASS: strict_must key allow-list gate")
    print(f"- templates checked: {checked}")
    print(f"- allowed keys: {sorted(ALLOWED_STRICT_KEYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
