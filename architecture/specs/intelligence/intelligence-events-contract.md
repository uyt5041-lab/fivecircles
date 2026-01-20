# intelligence-events-contract.md

## C가 소비(Consume): B(Core) 발행

wiki_entry.created.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{
    "wikiEntryId":"string",
    "dramaId":"string",
    "characterId":"string",
    "episodeStart":1,
    "episodeEnd":1,
    "status":"PENDING",
    "labelDraft":{"eventType":"REVEAL_HINT","involvedCharacterIds":["string"]}
  }
}

wiki_entry.updated.v1
- 목적: Assessment 재생성

wiki_entry.approved.v1
Payload(data):
{
  "wikiEntryId":"string",
  "dramaId":"string",
  "characterId":"string",
  "episodeStart":1,
  "episodeEnd":2,
  "approvedAt":"ISO-8601",
  "approvedByUserId":"string",
  "labelDraft":{"eventType":"REVEAL_CONFIRM","involvedCharacterIds":["string"]}
}

## Event type mapping (V2)
- labelDraft.eventType is stored as event.predicate_code.
- Allowed values: REVEAL_HINT, REVEAL_CONFIRM, RELATION_CHANGE, STATUS_CHANGE.

wiki_entry.rejected.v1
- 목적: 선택적으로 Assessment 비활성 처리

## C가 발행(Publish) 옵션

assessment.created.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{"assessmentId":"string","wikiEntryId":"string","riskLevel":"LOW|MEDIUM|HIGH"}
}

event.projected.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{"eventId":"string","sourceWikiEntryId":"string"}
}

## 운영 규칙
- at-least-once 전제, idempotent 필수
  - Assessment: (wikiEntryId, policyVersion) upsert
  - Projection: (sourceType, sourceId) upsert
- 실패는 DLQ 또는 재처리 API로 회수
