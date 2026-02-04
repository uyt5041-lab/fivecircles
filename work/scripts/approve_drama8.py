import json
import time
import urllib.request
import urllib.error

BASE = "http://localhost:8080"
DRAMA_ID = 8
TARGET_EPISODE = 1
VOTER_IDS = [10, 11, 12, 13, 14]
AUTHOR_ID = 10


def http_json(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body) if body else None
        except Exception:
            return e.code, {"raw": body}


def get_submissions():
    status, resp = http_json("GET", f"{BASE}/api/wiki/v1/submissions?dramaId={DRAMA_ID}")
    if status != 200 or not resp or resp.get("result") != "SUCCESS":
        raise SystemExit(f"Failed to fetch submissions: {status} {resp}")
    return resp.get("data", [])


def get_characters():
    status, resp = http_json("GET", f"{BASE}/api/character/v1?dramaId={DRAMA_ID}")
    if status != 200 or not resp or resp.get("result") != "SUCCESS":
        raise SystemExit(f"Failed to fetch characters: {status} {resp}")
    return resp.get("data", [])


def approve_submission(submission_id):
    for uid in VOTER_IDS:
        status, vresp = http_json("POST", f"{BASE}/api/wiki/v1/verifications", {
            "submissionId": submission_id,
            "voterId": uid,
            "isAgreed": True
        })
        if status != 200 or not vresp or vresp.get("result") != "SUCCESS":
            raise SystemExit(f"Vote failed for submission {submission_id}, user {uid}: {status} {vresp}")


def main():
    submissions = get_submissions()

    pending_ids = [s["id"] for s in submissions if s.get("status") == "PENDING"]
    print(f"pending submissions (drama {DRAMA_ID}): {pending_ids}")
    for sid in pending_ids:
        print(f"approving pending submission {sid}")
        approve_submission(sid)

    # build approved map for TARGET_EPISODE
    approved_by_char = {}
    for s in submissions:
        if s.get("status") == "APPROVED" and int(s.get("episode", 0)) <= TARGET_EPISODE:
            approved_by_char.setdefault(s.get("characterId"), []).append(s)

    characters = get_characters()
    print(f"characters: {len(characters)}")

    created = 0
    for c in characters:
        cid = c.get("id")
        name = c.get("name")
        if cid in approved_by_char:
            continue

        content = f"{name}에 대한 테스트 요약: {TARGET_EPISODE}화 기준으로 확인된 정보입니다."
        status, sub_resp = http_json("POST", f"{BASE}/api/wiki/v1/submissions", {
            "dramaId": DRAMA_ID,
            "episode": TARGET_EPISODE,
            "characterId": cid,
            "authorId": AUTHOR_ID,
            "content": content,
            "predicateCode": "OTHER"
        })
        if status != 200 or not sub_resp or sub_resp.get("result") != "SUCCESS":
            raise SystemExit(f"Submission failed for character {cid}: {status} {sub_resp}")

        submission_id = sub_resp.get("data")
        approve_submission(submission_id)
        created += 1
        print(f"created+approved submission {submission_id} for character {cid} ({name})")
        time.sleep(0.1)

    print(f"done. created {created} submissions.")


if __name__ == "__main__":
    main()
