# Event V2 API (Level 1–3)

Source
- proposals/공유-온톨로지레이어구축/ex06-lv1-3-query-ex.md

Base URL
- /api/event/v2

Common Rule
- Always apply: episode_end <= K (spoiler gate).
- Character lists are also filtered via event join with K gate.

Level 1 (Direct joins)
1) Character events timeline
GET /characters/{characterId}/events?safeUpToEpisode={K}&limit={N}

2) Event characters
GET /events/{eventId}/characters?safeUpToEpisode={K}

3) Co-appearance events
GET /characters/{aId}/coevents?with={bId}&safeUpToEpisode={K}

4) Drama events by predicate (type)
GET /dramas/{dramaId}/events?predicateCode={CODE}&safeUpToEpisode={K}&limit={N}

5) Safe character list (by involvement)
GET /dramas/{dramaId}/characters?safeUpToEpisode={K}&limit={N}

Level 2 (Range + predicate filters)
6) Events within episode range
GET /dramas/{dramaId}/events?fromEpisode={A}&toEpisode={B}&safeUpToEpisode={K}

7) Character events filtered by predicate
GET /characters/{characterId}/events?predicateCode={CODE}&safeUpToEpisode={K}

8) Top-N characters by involvement
GET /dramas/{dramaId}/characters?safeUpToEpisode={K}&sort=involvement&limit={N}

Level 3 (Relation traversal)
9) Related events (derived by shared characters)
GET /events/{eventId}/related?safeUpToEpisode={K}&limit={N}

10) Event causes (PRECEDES reverse)
GET /events/{eventId}/causes?depth={D}&safeUpToEpisode={K}

11) Event effects (PRECEDES forward)
GET /events/{eventId}/effects?depth={D}&safeUpToEpisode={K}

12) Related characters (co-appearance graph)
GET /characters/{characterId}/related-characters?safeUpToEpisode={K}&limit={N}

13) Character-to-character path (shortest)
GET /characters/path?from={A}&to={B}&maxDepth={D}&safeUpToEpisode={K}

14) Create PRECEDES relation (manual curation)
POST /relations/precedes
Body: { "fromEventId": X, "toEventId": Y }

15) PRECEDES suggestions (cross-episode only)
GET /relations/precedes/suggestions?eventId={E}&safeUpToEpisode={K}&limit={N}

Notes
- Use predicateCode (event.predicate_code) for filtering instead of a separate type field.
- Search policy: `predicateCode=OTHER|UNKNOWN` is treated as "no filter" in user-facing endpoints (unclassified is not a first-class filter).
  - 의미: 클라이언트가 `predicateCode=OTHER`를 보내더라도, 서버는 이를 필터로 쓰지 않고 `predicateCode=null`처럼 처리한다.
  - 이유: OTHER/UNKNOWN은 “미분류 저장용”이지, 사용자가 의도적으로 좁혀 찾는 1급 분류로 취급하지 않는다.
- REVEALS edges should be excluded from general traversal unless used for explanations.
- Related events are derived by shared character involvement (event_character).
- PRECEDES suggestions are cross-episode only; same-episode links require manual curation.
