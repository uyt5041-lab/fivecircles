# Event V2 Implementation Plan Map

Purpose
- Capture the V2 implementation plan (pre-triple).
- Keep the plan aligned with Notion-origin specs and repo layout.

Scope
- event-service (ontology/event domain)
- user-service (Flyway table separation)

2) Config changes (code/config only, no migration)

Add to each service's application.yml or application.properties.

- event-service
  - spring.flyway.table=flyway_schema_history_event

- user-service
  - spring.flyway.table=flyway_schema_history_user

Rationale
- A shared Flyway history table in one DB causes version collisions.
- This is the primary safety guardrail for multi-service DB usage.

3) Flyway migration (event-service)

Path
- services/event-service/src/main/resources/db/migration/

V3__event_v2_pre_triple.sql (before triples)
```sql
-- 1) predicate_code (Level2 filter)
ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN';

-- 2) source_status (Explainability: review status)
ALTER TABLE event
  ADD COLUMN source_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED';

-- 3) event query index (common filters)
CREATE INDEX idx_event_drama_pred_end
  ON event (drama_id, predicate_code, episode_end, episode_start, id);

CREATE INDEX idx_event_drama_end
  ON event (drama_id, episode_end, id);

-- 4) BFS performance indexes
CREATE INDEX idx_er_from_type_to
  ON event_relation (from_event_id, type, to_event_id);

CREATE INDEX idx_er_to_type_from
  ON event_relation (to_event_id, type, from_event_id);
```

4) "20 questions -> 6 queryType" mapping (doc-only)

Query Types
- CHARACTER_EVENTS: events involving character A
- EVENT_CHARACTERS: characters in event E
- CHARACTER_AND_CHARACTER_EVENTS: events involving A and B
- EVENT_CAUSES: prior events of E (PRECEDES reverse, depth)
- EVENT_EFFECTS: subsequent events of E (PRECEDES forward, depth)
- PATH_BETWEEN_CHARACTERS: shortest path between A and B (bipartite, depth)

Mapping (sample 20)
- A가 K화까지 관여한 사건 전부 -> CHARACTER_EVENTS
- A의 사건 중 특정 predicate(KILLS/BATTLE)만 -> CHARACTER_EVENTS (+predicateCode)
- 사건 E에 등장한 인물 전부 -> EVENT_CHARACTERS
- A와 B가 같이 나온 사건만 -> CHARACTER_AND_CHARACTER_EVENTS
- A와 B가 처음 같이 등장한 사건 -> CHARACTER_AND_CHARACTER_EVENTS (sort then top1)
- 사건 E의 직전 사건들(1 hop) -> EVENT_CAUSES (depth=1)
- 사건 E의 원인 체인(depth=3) -> EVENT_CAUSES
- 사건 E 이후 사건들(depth=2) -> EVENT_EFFECTS
- A에서 B까지 연결 경로 -> PATH_BETWEEN_CHARACTERS
- A와 B를 잇는 최단 경로만 -> PATH_BETWEEN_CHARACTERS (BFS shortest)
- "왜 A가 B와 엮이게 됐는지" -> PATH_BETWEEN_CHARACTERS (explain rendering)
- A가 사건 E에 포함되는지 확인 -> EVENT_CHARACTERS (contains)
- K화 기준 스포일러 없이 A 사건 나열 -> CHARACTER_EVENTS (K gate)
- 특정 사건 타입의 연쇄(선후)만 -> EVENT_EFFECTS / EVENT_CAUSES
- A 관련 사건 중 선후 관계까지 보기 -> CHARACTER_EVENTS + relation join
- 사건 E 이전에 필수 선행 사건 topN -> EVENT_CAUSES (depth + topN)
- A 사건들의 타입 분포(집계) -> CHARACTER_EVENTS results aggregated in BFF
- 사건 E 주변 1~2 hop만 빠르게 -> EVENT_CAUSES / EVENT_EFFECTS
- A와 B가 같이 엮이는 빈도 높은 구간 -> CHARACTER_AND_CHARACTER_EVENTS (aggregation)
- A가 관여한 사건의 등장 인물 동반 조회 -> CHARACTER_EVENTS + EVENT_CHARACTERS (batch)

5) Query patterns (spec-only)

Common rule
- Always apply: episode_end <= :K

1) CHARACTER_EVENTS
```sql
SELECT e.*
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
  AND ec.character_id = :characterId
  AND (:predicateCode IS NULL OR e.predicate_code = :predicateCode)
ORDER BY e.episode_start ASC, e.id ASC;
```

2) EVENT_CHARACTERS (V2)
```sql
SELECT ec.character_id
FROM event_character ec
JOIN event e ON e.id = ec.event_id
WHERE ec.event_id = :eventId
  AND e.episode_end <= :K
ORDER BY ec.character_id ASC;
```

3) CHARACTER_AND_CHARACTER_EVENTS
```sql
SELECT e.*
FROM event e
JOIN event_character ec1 ON ec1.event_id = e.id AND ec1.character_id = :a
JOIN event_character ec2 ON ec2.event_id = e.id AND ec2.character_id = :b
WHERE e.drama_id = :dramaId
  AND e.episode_end <= :K
ORDER BY e.episode_start ASC, e.id ASC;
```

4) EVENT_CAUSES (PRECEDES reverse BFS)
```sql
SELECT r.from_event_id, r.to_event_id
FROM event_relation r
WHERE r.to_event_id IN (:frontierIds)
  AND r.type = 'PRECEDES';
```

5) EVENT_EFFECTS (PRECEDES forward BFS)
```sql
SELECT r.from_event_id, r.to_event_id
FROM event_relation r
WHERE r.from_event_id IN (:frontierIds)
  AND r.type = 'PRECEDES';
```

6) PATH_BETWEEN_CHARACTERS (BFS on bipartite graph)
- Step A: character -> events (event_character)
- Step B: event -> next events (event_relation PRECEDES/RELATED)
- Step C: event -> characters (event_character)
- Output nodes: {node_type, node_id, hop_distance}

Notes
- Keep REVEALS in event_reveal and use it for explanations only.
- Do not expose future events in user-facing results without K gating.
