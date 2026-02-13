#!/usr/bin/env python3
"""
Validate filled evidence_event_id candidates for anti-halu Production Q templates.

Runs against gateway on bit-ts:
  - login
  - strict query reconstruction per selected Q
  - compare selected event id with expected evidence_event_id
"""

import json
import sys
import urllib.parse
import urllib.request
from typing import Optional

BASE_URL = "http://localhost:8080"
SAFE_UP_TO_EPISODE = 100


def post_json(path: str, payload: dict, token: Optional[str] = None) -> dict:
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
    )
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(path: str, params: Optional[dict] = None, token: Optional[str] = None) -> dict:
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None}
        )
    req = urllib.request.Request(BASE_URL + path + query, method="GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def unwrap_api_result(payload: dict):
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def sort_key(event: dict) -> tuple[int, int]:
    return (event.get("episodeStart") or 10**9, event.get("id") or 0)


def pick_earliest(events: list[dict]) -> Optional[dict]:
    if not events:
        return None
    return sorted(events, key=sort_key)[0]


def includes_any(event: dict, tokens: list[str]) -> bool:
    if not tokens:
        return True
    haystack = f"{event.get('summary') or ''} {event.get('predicateSuggestion') or ''}".lower()
    return any(token.lower() in haystack for token in tokens)


def resolve_event_character_ids(event_id: int, token: str, cache: dict[int, set[int]]) -> set[int]:
    if event_id in cache:
        return cache[event_id]
    rows = unwrap_api_result(
        get_json(
            f"/api/event/v2/events/{event_id}/characters",
            {"safeUpToEpisode": SAFE_UP_TO_EPISODE},
            token,
        )
    ) or []
    ids = {row["characterId"] for row in rows}
    cache[event_id] = ids
    return ids


def run_character_predicate(
    token: str,
    subject_id: int,
    predicate_codes: list[str],
    q_any_of: list[str],
    target_id: Optional[int] = None,
    exclude_codes: Optional[list[str]] = None,
) -> Optional[dict]:
    exclude = set(exclude_codes or [])
    if predicate_codes and q_any_of:
        pairs = [(code, q) for code in predicate_codes for q in q_any_of]
    elif predicate_codes:
        pairs = [(code, None) for code in predicate_codes]
    else:
        pairs = [(None, q) for q in q_any_of]

    selected: list[dict] = []
    character_cache: dict[int, set[int]] = {}
    for code, q in pairs:
        events = unwrap_api_result(
            get_json(
                f"/api/event/v2/characters/{subject_id}/events",
                {
                    "safeUpToEpisode": SAFE_UP_TO_EPISODE,
                    "predicateCode": code,
                    "q": q,
                    "includeRevealPartner": "false",
                    "limit": 200 if target_id is not None else 1,
                },
                token,
            )
        ) or []
        if exclude:
            events = [e for e in events if (e.get("predicateCode") or "") not in exclude]
        if target_id is not None:
            events = [
                e
                for e in events
                if target_id in resolve_event_character_ids(e["id"], token, character_cache)
            ]
        picked = pick_earliest(events)
        if picked is not None:
            selected.append(picked)
    return pick_earliest(selected)


def run_character_keyword(
    token: str,
    subject_id: int,
    q_any_of: list[str],
    predicate_codes: Optional[list[str]] = None,
    target_id: Optional[int] = None,
) -> Optional[dict]:
    selected: list[dict] = []
    character_cache: dict[int, set[int]] = {}
    codes = predicate_codes or []
    for q in q_any_of:
        for code in (codes if codes else [None]):
            events = unwrap_api_result(
                get_json(
                    f"/api/event/v2/characters/{subject_id}/events",
                    {
                        "safeUpToEpisode": SAFE_UP_TO_EPISODE,
                        "predicateCode": code,
                        "q": q,
                        "includeRevealPartner": "false",
                        "limit": 200 if target_id is not None else 1,
                    },
                    token,
                )
            ) or []
            if target_id is not None:
                events = [
                    e
                    for e in events
                    if target_id in resolve_event_character_ids(e["id"], token, character_cache)
                ]
            picked = pick_earliest(events)
            if picked is not None:
                selected.append(picked)
    return pick_earliest(selected)


def run_coevents(
    token: str,
    a_id: int,
    b_id: int,
    predicate_codes: list[str],
    q_any_of: list[str],
    prefer_codes: list[str],
) -> Optional[dict]:
    events = unwrap_api_result(
        get_json(
            f"/api/event/v2/characters/{a_id}/coevents",
            {"with": b_id, "safeUpToEpisode": SAFE_UP_TO_EPISODE, "limit": 200},
            token,
        )
    ) or []
    strict = events
    if predicate_codes:
        strict = [e for e in strict if (e.get("predicateCode") or "") in predicate_codes]
    if q_any_of:
        strict = [e for e in strict if includes_any(e, q_any_of)]
    if prefer_codes:
        preferred = [e for e in strict if (e.get("predicateCode") or "") in prefer_codes]
        picked = pick_earliest(preferred)
        if picked is not None:
            return picked
    return pick_earliest(strict)


def main() -> int:
    login = post_json("/api/auth/v1/login", {"email": "1@1.com", "password": "1"})
    token = login["data"]["accessToken"]

    checks = [
        {
            "qid": "Q01",
            "expected": 2292,
            "runner": lambda: run_character_predicate(token, 17, ["KILLS"], []),
        },
        {
            "qid": "Q02",
            "expected": 2449,
            "runner": lambda: run_character_keyword(
                token, 17, ["처음으로 메스암페타민", "직접 제조한다"]
            ),
        },
        {
            "qid": "Q03",
            "expected": 2450,
            "runner": lambda: run_coevents(
                token, 17, 25, [], ["폭발"], ["MEETS"]
            ),
        },
        {
            "qid": "Q04",
            "expected": 2922,
            "runner": lambda: run_character_predicate(
                token,
                19,
                ["DISCOVERS", "LEARNS"],
                ["meth", "메스", "암페타민", "제조", "마약", "범죄"],
            ),
        },
        {
            "qid": "Q05",
            "expected": 2283,
            "runner": lambda: run_character_predicate(
                token,
                17,
                ["LEARNS", "DISCOVERS"],
                ["결심", "동업", "제조 시작", "암 진단", "DEA", "단속", "도주", "제시"],
            ),
        },
        {
            "qid": "Q06",
            "expected": 2448,
            "runner": lambda: run_coevents(
                token, 17, 18, ["ALLIES_WITH", "JOINS", "MEETS"], [], []
            ),
        },
        {
            "qid": "Q07",
            "expected": 2343,
            "runner": lambda: run_character_predicate(
                token,
                17,
                [],
                ["거짓말", "휴대폰", "실종", "추궁", "의심", "행동 이상", "불신"],
            ),
        },
        {
            "qid": "Q08",
            "expected": 2428,
            "runner": lambda: run_character_keyword(
                token, 17, ["Elliott", "전액을 지원", "치료비 전액"], ["RECOVERS"]
            ),
        },
        {
            "qid": "Q09",
            "expected": 2369,
            "runner": lambda: run_character_predicate(
                token, 20, ["TRANSFORMS"], ["고순도"]
            ),
        },
        {
            "qid": "Q10",
            "expected": 2306,
            "runner": lambda: run_character_predicate(
                token,
                17,
                ["ATTACKS", "CAPTURES", "BETRAYS", "KILLS"],
                ["투코", "공급 계약", "보복"],
                exclude_codes=["DISCOVERS", "LEARNS"],
            ),
        },
        {
            "qid": "Q11",
            "expected": 2343,
            "runner": lambda: run_character_predicate(
                token,
                19,
                [],
                ["의심", "휴대폰", "실종", "행동 이상", "불신"],
                target_id=17,
            ),
        },
        {
            "qid": "Q12",
            "expected": 2450,
            "runner": lambda: run_character_predicate(token, 17, [], ["폭발"], target_id=25),
        },
        {
            "qid": "Q13",
            "expected": 2307,
            "runner": lambda: run_character_predicate(
                token, 17, [], ["대량 공급", "계약", "정기 수익", "주 단위"]
            ),
        },
        {
            "qid": "Q14",
            "expected": 2923,
            "runner": lambda: run_coevents(
                token, 17, 19, ["BETRAYS", "LEARNS", "DISCOVERS"], ["별거", "신뢰 붕괴", "집에서 나가"], []
            ),
        },
        {
            "qid": "Q15",
            "expected": 2289,
            "runner": lambda: run_character_predicate(token, 17, [], ["산성 용액", "용해", "시신 처리"]),
        },
    ]

    failures = 0
    for check in checks:
        event = check["runner"]()
        actual = event["id"] if event else None
        status = "PASS" if actual == check["expected"] else "FAIL"
        if status == "FAIL":
            failures += 1
        print(
            json.dumps(
                {
                    "status": status,
                    "question_id": check["qid"],
                    "expected_event_id": check["expected"],
                    "actual_event_id": actual,
                    "episode": event.get("episodeStart") if event else None,
                    "predicateCode": event.get("predicateCode") if event else None,
                    "summary": event.get("summary") if event else None,
                },
                ensure_ascii=False,
            )
        )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
