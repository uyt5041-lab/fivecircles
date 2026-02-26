#!/usr/bin/env python3
"""
Validate strict_must predicate codes use canonical normalized tokens.

Checks:
- token must be UPPER_SNAKE
- legacy alias STATUS_CHANGE must not appear in templates
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_PATH = REPO_ROOT / "front/common/productionQ/templates.ts"
TARGET_KEYS = ("predicateCodeAnyOf", "excludePredicateCodeAnyOf")


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


def extract_codes_from_key(strict_block: str, key: str) -> list[str]:
    match = re.search(rf"\b{re.escape(key)}\s*:\s*\[([^\]]*)\]", strict_block, flags=re.DOTALL)
    if not match:
        return []
    inner = match.group(1)
    return re.findall(r"'([^']+)'", inner)


def is_upper_snake(token: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z0-9_]*", token))


def main() -> int:
    text = read_text(TEMPLATES_PATH)
    blocks = extract_template_blocks(text)

    violations: list[str] = []
    checked = 0
    for block in blocks:
        template_id = extract_template_id(block)
        strict = extract_strict_must_block(block)
        if strict is None:
            continue
        checked += 1
        for key in TARGET_KEYS:
            for raw in extract_codes_from_key(strict, key):
                token = raw.strip()
                if not is_upper_snake(token):
                    violations.append(
                        f"{template_id}: strict_must.{key} contains non-UPPER_SNAKE token '{raw}'"
                    )
                    continue
                if token == "STATUS_CHANGE":
                    violations.append(
                        f"{template_id}: strict_must.{key} uses legacy token STATUS_CHANGE (use TRANSFORMS)"
                    )

    if violations:
        print("FAIL: Predicate normalization gate violations found.")
        for v in violations:
            print(f"- {v}")
        return 1

    print("PASS: Predicate normalization gate")
    print(f"- templates checked: {checked}")
    print(f"- checked keys: {list(TARGET_KEYS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
