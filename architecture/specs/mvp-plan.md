# MVP Plan (Experiment)

Purpose
- Deliver the smallest working UI that answers Q1-Q15 using Event V2 endpoints.
- Tests run against the remote server per `test-server-policy-4C.md`.

Scope
- Frontend plus Team B backend (drama-service, character-service, wiki-service).
- No new routes. Use /#/dashboard and /#/timeline for all question entry points.
- Output is list-first (no charts/graphs unless trivial).
- Exclude idea-wikipage flow from MVP (discussion-only).

Assumptions
- Event V2 API is reachable at /api/event/v2.
- safeUpToEpisode == currentEpisode from the UI flow.
- If any endpoint is missing, allow temporary mock data.

Plan (Step-by-step)

Step 0) Alignment and contracts (Owner: All)
Tasks
- Confirm request/response fields for drama, character, wiki, and event.
- List missing endpoints vs current api-contract and mark MVP-only additions.
- Decide fallback rules for authorName and myVote (if wiki list is required).

Recursive Flow Policy
- Execute steps in small slices (design -> implement -> verify) per feature.
- After each slice, update findings and decide whether to proceed or loop.
- If any error occurs, pause the flow, investigate the root cause, and discuss with the user before continuing.
- Commit locally at the end of each completed step.

Step 1) Team B backend foundations (Owner: Team B)
Tasks
- Drama service: ensure GET /api/drama/v1 returns list for landing.
- Character service: ensure GET /api/character/v1?dramaId for dashboard list.
- Wiki service: add list endpoint for review page (GET /api/wiki/v1/submissions?dramaId).
- Wiki service: add optional update/delete if review UI requires it (PUT/DELETE /submissions/{id}).
- Seed minimal drama/character/wiki data so FE can render without mocks.
- Update api-contract if MVP-only endpoints are added.

Step 2) Event V2 readiness (Owner: Team C)
Tasks
- Verify api1-api10 are reachable and gated by safeUpToEpisode.
- Provide minimal event data tied to seeded dramas/characters.
- If any endpoint is missing, expose a stub response for MVP.

Step 3) Frontend integration (Owner: FE)
Tasks
- Add Event V2 client wrapper with defaults (safeUpToEpisode, limit).
- Replace mock drama/character lists with real endpoints when available.
- /#/dashboard:
  - Q1: api3 timeline list.
  - Q2: api4 co-appearance list.
  - Q3/Q6/Q7: api3 + predicateCode filters.
  - Q13: api10 path result (simple list).
  - Q14: api9 related characters.
  - Q15: api3 then api8 for impact chain.
- /#/timeline:
  - Filter bar (predicateCode, fromEpisode, toEpisode).
  - Q5/Q9: api1 with filters.
  - Event detail panel: api5 characters, api7/api8 causes/effects, predicate badge.
  - Q8: compare two predicate codes (api1 x2) with counts and lists.

Page-level recursive execution
- For each page: define a mini plan -> implement -> verify -> log -> commit.
- Order: /#/dashboard -> /#/timeline -> /#/qa (optional).

Page plan: /#/dashboard
- Data: api3, api4, api9, api10, api8.
- UI: character modal tabs (timeline, co-appearance, predicate filter, related, path, impact chain).
- Implementation: lazy-load per tab, show lists only.
- Verify: Playwright on server opens modal and renders at least one tab.

Page plan: /#/timeline
- Data: api1, api5, api7, api8.
- UI: filter bar + event detail panel.
- Implementation: list-first, use badge for predicateCode.
- Verify: Playwright on server filters and opens detail.
  Mini plan (Cycle 1)
  - Hook filter bar (q/predicate/from/to) to api1 with safeUpToEpisode.
  - Add predicate compare panel (Q8) via api1 x2.
  - Add event detail panel: api5 characters + api7/api8 causes/effects + predicate badge.
  - Verify on server with Playwright and log results.

Step 4) QA alternative (Owner: FE, optional)
Tasks
- If time is tight, move Q2/Q8/Q13 to /#/qa and keep CTA only on pages.

Step 5) Verification (Owner: FE)
Tasks
- Playwright checks:
  - /#/dashboard opens and loads at least one tab.
  - /#/timeline filters fetch results.
  - Event detail panel shows characters and causes/effects.

Deliverables
- Working UI entry points for Q1-Q15.
- Minimal loading/empty/error states.
