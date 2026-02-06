# intelligence-db-schema.md

## 1) Assessment(검수 보조)

### assessment
- id (PK)
- drama_id
- wiki_entry_id
- risk_level: LOW/MEDIUM/HIGH
- policy_version
- model_version NULL
- created_at, updated_at

INDEX
- (wiki_entry_id, created_at)
- (drama_id, created_at)

### assessment_reason
- id (PK)
- assessment_id (FK)
- rule_id (R0~R6)
- severity (가중치)
- message
- evidence_ref_type: REVEAL_INDEX | EVENT | WIKI_ENTRY | NONE
- evidence_ref_id NULL
- created_at

INDEX
- (assessment_id)

### fact_candidate
- id (PK)
- assessment_id (FK)
- type: CHARACTER_ATTRIBUTE | CHARACTER_RELATION | STATUS | EVENT_CLAIM
- subject_character_id NULL
- object_character_id NULL
- key NULL (attributeKey/relationType)
- polarity: ASSERT | DENY | UNKNOWN
- confidence (0~1)
- span_start, span_end NULL
- evidence_text NULL
- created_at

INDEX
- (assessment_id)
- (subject_character_id)

## 2) Reveal Index(드러남 타임라인)

### reveal_index
- id (PK)
- drama_id
- target_type: CHARACTER | ATTRIBUTE | RELATION
- target_id
- key NULL (RELATION이면 relationType 권장)
- reveal_type: HINT | CONFIRM
- episode_start, episode_end
- source_type: MANUAL | WIKI_ENTRY | EVENT
- source_id NULL
- created_by_user_id NULL
- approved_by_user_id NULL
- status: ACTIVE | DEPRECATED
- created_at, updated_at

CONSTRAINT
- UNIQUE(drama_id, target_type, target_id, key, reveal_type)

INDEX
- (drama_id, episode_end)
- (drama_id, target_type, target_id)

## 3) Event Read Model(온톨로지)

### event
- id (PK)
- drama_id
- summary
- episode_start, episode_end
- source_type: WIKI_ENTRY | MANUAL
- source_id NULL
- predicate_code: REVEAL_HINT | REVEAL_CONFIRM | RELATION_CHANGE | STATUS_CHANGE | UNKNOWN
- source_status: APPROVED | PENDING | REJECTED
- created_at

INDEX
- idx_event_drama_range (drama_id, episode_start, episode_end)
- idx_event_drama_pred_end (drama_id, predicate_code, episode_end, episode_start, id)
- idx_event_drama_end (drama_id, episode_end, id)

### event_character
- event_id, character_id (PK)
- role NULL

### event_relation
- from_event_id, to_event_id (PK)
- type: PRECEDES

### event_reveal (옵션)
- event_id, target_type, target_id (PK)
- reveal_type: HINT | CONFIRM
