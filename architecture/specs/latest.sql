-- Latest consolidated SQL for V2.5 (event domain)
-- Source: V3/V4/V5/V6 migrations in event-service

-- event: predicate_code, source_status
ALTER TABLE event
  ADD COLUMN predicate_code VARCHAR(30) NOT NULL DEFAULT 'UNKNOWN';

ALTER TABLE event
  ADD COLUMN source_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED';

-- event_character: role
ALTER TABLE event_character
  ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'INVOLVED' COMMENT 'INVOLVED, SUBJECT, OBJECT';

-- event indexes
CREATE INDEX idx_event_drama_pred_end
  ON event (drama_id, predicate_code, episode_end, episode_start, id);

CREATE INDEX idx_event_drama_end
  ON event (drama_id, episode_end, id);

CREATE INDEX idx_event_drama_status_end
  ON event (drama_id, source_status, episode_end, id);

-- event_relation indexes
CREATE INDEX idx_er_from_type_to
  ON event_relation (from_event_id, type, to_event_id);

CREATE INDEX idx_er_to_type_from
  ON event_relation (to_event_id, type, from_event_id);

-- event_character indexes
CREATE INDEX idx_ec_character_event
  ON event_character (character_id, event_id);

CREATE INDEX idx_ec_role_character
  ON event_character (character_id, role);
