#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTOR_PATH = REPO_ROOT / "front/common/productionQ/executor.ts"


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> int:
    text = EXECUTOR_PATH.read_text(encoding="utf-8")

    # Resolve function must map safe probe hit to NOT_ENOUGH_DATA in strict-miss flow.
    safe_to_no_data = re.search(
        r"const\s+answerabilityStatus:\s*AnswerabilityStatus\s*=\s*probe\.existsSafeApproved\s*\?\s*'NOT_ENOUGH_DATA'",
        text,
    )
    if not safe_to_no_data:
        fail("resolveProbeStatus no longer maps probe.existsSafeApproved to NOT_ENOUGH_DATA")

    if "WARNING: strict miss + probe safe=true 감지. ANSWERED 승격 금지 규칙으로 NOT_ENOUGH_DATA 유지" not in text:
        fail("strict-miss probe guard warning note missing (expected guardrail marker)")

    print("[PASS] strict-miss + probe hit guard is locked (no ANSWERED promotion).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
