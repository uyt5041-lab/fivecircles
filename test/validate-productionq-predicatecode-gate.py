#!/usr/bin/env python3
"""
Validate Production Q templates' strict predicate code fields.

Scope (intentionally narrow):
- strict_must.predicateCodeAnyOf
- strict_must.excludePredicateCodeAnyOf

Out of scope:
- qAnyOf
- labels/groups/title/description text
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PREDICATE_CODE_PATH = REPO_ROOT / "common/src/main/java/com/nospoiler/common/PredicateCode.java"
TEMPLATES_PATH = REPO_ROOT / "front/common/productionQ/templates.ts"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_predicate_codes(java_text: str) -> set[str]:
    pattern = re.compile(r"^\s*([A-Z_]+)\s*\(", re.MULTILINE)
    codes: set[str] = set()
    for match in pattern.finditer(java_text):
        name = match.group(1)
        if name in {"if", "for", "switch", "while"}:
            continue
        codes.add(name)
    return codes


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


def extract_codes_from_key(strict_block: str, key: str) -> list[str]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*\[([^\]]*)\]", strict_block, flags=re.DOTALL)
    if not match:
        return []
    inner = match.group(1)
    return re.findall(r"'([^']+)'", inner)


def main() -> int:
    predicate_java = read_text(PREDICATE_CODE_PATH)
    templates_ts = read_text(TEMPLATES_PATH)

    valid_codes = parse_predicate_codes(predicate_java)
    if not valid_codes:
        print("ERROR: PredicateCode enum parse failed (no values found).")
        return 2

    template_blocks = extract_template_blocks(templates_ts)
    if not template_blocks:
        print("ERROR: No template blocks found in templates.ts")
        return 2

    target_keys = ("predicateCodeAnyOf", "excludePredicateCodeAnyOf")
    violations: list[str] = []

    for block in template_blocks:
        template_id = extract_template_id(block)
        strict_block = extract_strict_must_block(block)
        if not strict_block:
            continue
        for key in target_keys:
            for raw in extract_codes_from_key(strict_block, key):
                code = raw.strip().upper()
                if code not in valid_codes:
                    violations.append(
                        f"{template_id}: strict_must.{key} contains invalid PredicateCode '{raw}'"
                    )

    if violations:
        print("FAIL: ProductionQ strict predicate gate violations found.")
        for item in violations:
            print(f"- {item}")
        print(f"Allowed PredicateCode set size: {len(valid_codes)}")
        return 1

    print("PASS: ProductionQ strict predicate gate")
    print(f"- templates checked: {len(template_blocks)}")
    print(f"- keys checked: strict_must.predicateCodeAnyOf, strict_must.excludePredicateCodeAnyOf")
    print(f"- allowed PredicateCode count: {len(valid_codes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
