#!/usr/bin/env python3
"""
BP2 local gate: reveal target key codebook alignment.

Checks:
- codebook allow-list is non-empty and normalized (A_* UPPER_SNAKE)
- question map attribute_set keys are in allow-list
- inheritancePhase1 attributeTargetBindings keys are in allow-list
- closure taxonomy ATTRIBUTE nodes contain allow-list keys
- seed SQL uses target_key and values are in allow-list
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CODEBOOK_JSON = ROOT / "fivecircles/architecture/specs/reveals/reveal-target-key-codebook.phase1.json"
QUESTION_MAP = ROOT / "fivecircles/architecture/specs/extension100/question-map.q01-expansion.phase1.json"
TAXONOMY_JSON = ROOT / "fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json"
PHASE1_TS = ROOT / "front/common/productionQ/inheritancePhase1.ts"
SEED_SQL = ROOT / "scripts/ops/seed_expension100_q1_attribute_reveals.sql"

A_KEY_RE = re.compile(r"^A_[A-Z0-9_]+$")
ALL_A_KEY_RE = re.compile(r"\bA_[A-Z0-9_]+\b")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def parse_phase1_binding_keys(ts_text: str) -> set[str]:
    m = re.search(r"const attributeTargetBindings:\s*Record<string,\s*number\[]>\s*=\s*\{(.*?)\};", ts_text, re.S)
    if not m:
        return set()
    block = m.group(1)
    keys = set(re.findall(r"\b(A_[A-Z0-9_]+)\s*:", block))
    return keys


def parse_seed_target_keys(sql_text: str) -> set[str]:
    keys = set(re.findall(r"'(A_[A-Z0-9_]+)'", sql_text))
    return keys


def main() -> int:
    errors: list[str] = []

    codebook = load_json(CODEBOOK_JSON)
    allow_list = set(codebook.get("allow_list", []))
    if not allow_list:
        fail("codebook allow_list is empty", errors)
    for key in allow_list:
        if not A_KEY_RE.match(key):
            fail(f"invalid allow_list key format: {key}", errors)

    qmap = load_json(QUESTION_MAP)
    qmap_keys: set[str] = set()
    for qid, item in qmap.get("items", {}).items():
        attrs = item.get("required_set", {}).get("attribute_set", [])
        for key in attrs:
            qmap_keys.add(key)
            if key not in allow_list:
                fail(f"question-map key not in allow_list: {qid}:{key}", errors)

    taxonomy = load_json(TAXONOMY_JSON)
    attr_edges = taxonomy.get("domains", {}).get("ATTRIBUTE", {}).get("edges", [])
    taxonomy_keys = {k for edge in attr_edges for k in edge if isinstance(k, str) and k.startswith("A_")}
    for key in allow_list:
        if key not in taxonomy_keys:
            fail(f"allow_list key missing in taxonomy ATTRIBUTE edges: {key}", errors)

    ts_text = PHASE1_TS.read_text(encoding="utf-8")
    binding_keys = parse_phase1_binding_keys(ts_text)
    if not binding_keys:
        fail("attributeTargetBindings keys not found in inheritancePhase1.ts", errors)
    for key in binding_keys:
        if key not in allow_list:
            fail(f"inheritancePhase1 binding key not in allow_list: {key}", errors)

    seed_sql = SEED_SQL.read_text(encoding="utf-8")
    if "target_key" not in seed_sql.lower():
        fail("seed sql does not include target_key column", errors)
    seed_keys = parse_seed_target_keys(seed_sql)
    for key in seed_keys:
        if key not in allow_list:
            fail(f"seed sql key not in allow_list: {key}", errors)

    # Drift hint: question-map keys should all be represented in phase1 bindings.
    for key in qmap_keys:
        if key not in binding_keys:
            fail(f"question-map key missing in inheritancePhase1 bindings: {key}", errors)

    result = {
        "status": "PASS" if not errors else "FAIL",
        "allow_list_count": len(allow_list),
        "question_map_key_count": len(qmap_keys),
        "binding_key_count": len(binding_keys),
        "seed_key_count": len(seed_keys),
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
