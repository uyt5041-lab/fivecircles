# Event V2 API (Level 1–3)

Source
- proposals/공유-온톨로지레이어구축/ex06-lv1-3-query-ex.md

Base URL
- /api/event

Common Rule
- Always apply: episode_end <= K (spoiler gate).
- Character lists are also filtered via event join with K gate.

Level 1 (Direct joins)
1) Character events timeline
GET /v2/characters/{characterId}/events?safeUpToEpisode={K}&limit={N}

2) Event characters
GET /v2/events/{eventId}/characters?safeUpToEpisode={K}

3) Co-appearance events
GET /v2/characters/{aId}/coevents?with={bId}&safeUpToEpisode={K}

4) Drama events by predicate (type)
GET /v2/dramas/{dramaId}/events?predicateCode={CODE}&safeUpToEpisode={K}&limit={N}

5) Safe character list (by involvement)
GET /v2/dramas/{dramaId}/characters?safeUpToEpisode={K}&limit={N}

Level 2 (Range + predicate filters)
6) Events within episode range
GET /v2/dramas/{dramaId}/events?fromEpisode={A}&toEpisode={B}&safeUpToEpisode={K}

7) Character events filtered by predicate
GET /v2/characters/{characterId}/events?predicateCode={CODE}&safeUpToEpisode={K}

8) Top-N characters by involvement
GET /v2/dramas/{dramaId}/characters?safeUpToEpisode={K}&sort=involvement&limit={N}

Level 3 (Relation traversal)
9) Related events (multi-hop)
GET /v2/events/{eventId}/related?depth={D}&safeUpToEpisode={K}&types=PRECEDES,RELATED

10) Event causes (PRECEDES reverse)
GET /v2/events/{eventId}/causes?depth={D}&safeUpToEpisode={K}

11) Event effects (PRECEDES forward)
GET /v2/events/{eventId}/effects?depth={D}&safeUpToEpisode={K}

12) Related characters (co-appearance graph)
GET /v2/characters/{characterId}/related-characters?safeUpToEpisode={K}&limit={N}

13) Character-to-character path (shortest)
GET /v2/characters/path?from={A}&to={B}&maxDepth={D}&safeUpToEpisode={K}

Notes
- Use predicateCode (event.predicate_code) for filtering instead of a separate type field.
- REVEALS edges should be excluded from general traversal unless used for explanations.
