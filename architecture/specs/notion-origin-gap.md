# Notion-Origin Gap Notes

> As of 2026-01-30 (local repo)
> Purpose: record differences between Notion-origin specs and current implementation, with guidance.

---

## 1) User Domain
- Notion: `user_state` table exists → current user-service has **no `user_state`**.
  - Note: there is user status/profile data, but not the per-drama watch-state table.
  - Action: **Keep as-is (display only).**
- Notion: roles = VIEWER/CONTRIBUTOR/REVIEWER/ADMIN → current = USER/ADMIN.
  - Action: **Keep as-is (display only).**
- Notion: `password_hash` column → current `users.password`.
  - Action: **Keep as-is (display only).**

---

## 2) No Physical FK Rule
- Notion: **No physical FK** anywhere → current `wiki_submission_verification` has FK to `wiki_submission`.
  - Why this is a problem: FK enforces **strict write order and delete semantics** inside DB.
    - It blocks bulk/backfill ingestion unless parent rows already exist.
    - It introduces **hard coupling** between tables, contrary to the “logical reference only” rule.
    - It can break **eventual consistency** patterns (async workflows, partial restores).
    - `ON DELETE CASCADE` can remove verification history unintentionally.
  - Tag: **[TeamA]** (Discuss in meeting: keep FK or align to no-FK rule.)

---

## 3) Wiki Domain
- Notion: `wiki_submission` includes drama_id/episode/predicate_code from day 1 → actually added by V2/V3.
  - Action: **OK (completed).**
- Notion does not mention `predicate_suggestion` → added in V5.
  - Meaning: when AI/LLM cannot map to a valid `predicate_code`, it returns `OTHER` and stores the raw suggestion (e.g. "KIDNAPS") in `predicate_suggestion`.
  - Purpose: **future ontology expansion** + reviewer UI explanation.

---

## 4) Event Domain
- Notion: `event_character` has no role → current V6 adds `role`.
  - Action: **OK (intentional for V3).**
- Notion: `event_relation` keeps `type` but MVP uses PRECEDES only.
  - Impact: no multi-type per pair is required in MVP.
- `event_reveal` was fixed in V2 to match Notion (target_type, target_id).

---

## 5) API / Feature Scope
- Notion: Q&A page excluded from MVP → current QA service/endpoints exist.
  - Action: **Treat as non-MVP; keep implementation.**
- Notion: Intelligence only `/intelligence/refine` → current `/api/intelligence/v1/refine` plus `/summary`.
  - Action: **Update Notion-origin spec** to include `/summary` (character summary aggregation).
