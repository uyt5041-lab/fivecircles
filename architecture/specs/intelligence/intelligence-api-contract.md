# intelligence-api-contract.md

## 1) Assessment

POST /internal/assessments
- 용도: 재처리/수동 생성(운영)
Request:
{ "wikiEntryId":"string", "dramaId":"string" }
Response:
{ "assessmentId":"string", "status":"CREATED" }

GET /wiki-entries/{wikiEntryId}/assessment/latest
Response:
{
  "wikiEntryId":"string",
  "riskLevel":"LOW|MEDIUM|HIGH",
  "policyVersion":"v1",
  "createdAt":"ISO-8601",
  "reasons":[
    { "ruleId":"R1","severity":10,"message":"string","evidence":{"type":"REVEAL_INDEX","id":"string"} }
  ],
  "suggestions":{
    "suggestedEventType":"REVEAL_HINT|REVEAL_CONFIRM|RELATION_CHANGE|STATUS_CHANGE",
    "suggestedEpisodeRange":{"episodeStart":3,"episodeEnd":4},
    "rewriteHints":["string"]
  },
  "factCandidates":[
    {
      "type":"CHARACTER_ATTRIBUTE",
      "subjectCharacterId":"string",
      "objectCharacterId":null,
      "key":"identity",
      "polarity":"ASSERT",
      "confidence":0.83,
      "evidenceSpan":{"start":10,"end":25},
      "evidenceText":"string"
    }
  ]
}

## 2) Reveal Index(관리)

POST /admin/reveal-index
Request:
{
  "dramaId":"string",
  "targetType":"CHARACTER|ATTRIBUTE|RELATION",
  "targetId":"string",
  "key":"string|null",
  "revealType":"HINT|CONFIRM",
  "episodeStart":1,
  "episodeEnd":1,
  "sourceType":"MANUAL",
  "sourceId":null
}
Response:
{ "revealIndexId":"string" }

GET /admin/reveal-index/search?dramaId=...&q=...&uptoEpisode=K
Response:
[
  {"id":"string","targetType":"CHARACTER","targetId":"string","revealType":"CONFIRM","episodeStart":7,"episodeEnd":7,"status":"ACTIVE"}
]

## 3) Event Search & Q&A

GET /events/search?dramaId=...&q=...&uptoEpisode=K&predicateCode=...
Response:
[
  {
    "id":"string",
    "dramaId":"string",
    "summary":"string",
    "episodeStart":3,
    "episodeEnd":4,
    "sourceType":"WIKI_ENTRY|MANUAL",
    "sourceId":"string|null",
    "predicateCode":"REVEAL_HINT|REVEAL_CONFIRM|RELATION_CHANGE|STATUS_CHANGE|UNKNOWN",
    "sourceStatus":"APPROVED|PENDING|REJECTED"
  }
]

### Event Query Types (V2)
- QueryType mapping and SQL patterns: `fivecircles/architecture/specs/event-v2-plan-map.md`
- Endpoint list (L1–L3): `fivecircles/architecture/specs/event-v2-api.md`

POST /qa/episode-range
Request:
{ "dramaId":"string","queryText":"string","uptoEpisode":6 }
Response:
{ "episodeStart":3,"episodeEnd":4,"confidence":0.62,"message":"이 내용은 3~4화 범위로 추정됩니다.","eventId":"string|null" }

## 4) Projection(재처리)

POST /internal/projections/wiki-entry-approved
Request:
{ "wikiEntryId":"string","dramaId":"string" }
Response:
{ "status":"PROJECTED","eventId":"string" }
