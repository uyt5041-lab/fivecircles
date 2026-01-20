# Event V3 Implementation Plan

Purpose
- Define the V3 (triple roles) implementation plan.
- Build on V2 without changing the V2 query semantics.

Scope
- event-service (ontology/event domain)

1) Flyway migration (event-service)

Path
- services/event-service/src/main/resources/db/migration/

V4__event_v3_triple_roles.sql (triple roles)
```sql
ALTER TABLE event_character
  ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED';

CREATE INDEX idx_ec_event_role_character
  ON event_character (event_id, role, character_id);

CREATE INDEX idx_ec_character_role_event
  ON event_character (character_id, role, event_id);
```

2) Query pattern delta (V3)

EVENT_CHARACTERS (V3)
```sql
SELECT ec.character_id, ec.role
FROM event_character ec
JOIN event e ON e.id = ec.event_id
WHERE ec.event_id = :eventId
  AND e.episode_end <= :K
ORDER BY ec.role ASC, ec.character_id ASC;
```

3) Triple role usage
- S/O participant sets map to event_character.role.
- Default role remains INVOLVED when not specified.

4) Implementation notes
- Update event_character entity + mapper to include role.
- Keep predicate_code in event table from V2.
- Maintain K gating with episode_end.
