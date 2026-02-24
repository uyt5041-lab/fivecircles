# Event V3 API Contract (Level 4 Questions)

Purpose
- Define the minimal `/api/event/v3` contract for Level 4 questions (Q16~Q20).
- Keep v1/v2 behavior stable and non-breaking.
- Reuse existing RDB + V2 query/probe capabilities first.

Base URL
- `/api/event/v3`

Status
- Contract draft: implementation target for V3 core.
- Runtime rule: V3 is opt-in and must not change v1/v2 semantics.
- DTO baseline note: response DTO examples in this document are the current baseline.
  - They may evolve later, but any change must update this document first to avoid FE/BE drift.

Invariants
- Apply spoiler gate on all user-facing reads: `episode_end <= safeUpToEpisode`.
- Apply approval gate on all user-facing reads: `source_status = 'APPROVED'`.
- PRECEDES policy is unchanged (`from=previous`, `to=next`).
- V3 does not introduce new relation type (no `CAUSES` edge).

---

## 1) Shared Request/Response Rules

Request (common)
- `safeUpToEpisode` is required for user-facing queries.
- `dramaId` is required for drama-scoped analysis endpoints.
- character/event IDs are required for subject-scoped endpoints.

Response envelope
- Keep existing service envelope: `ApiResponse<T>`.
- Level 4 result payload must include:
  - `answerabilityStatus`: `ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA`
  - `evidenceEventIds`: `long[]` (empty when unavailable)
    - V3 norm: MUST always be an array in API response (`[]` allowed), never `null`.
    - Internal service code may temporarily hold `null`, but response boundary must normalize to `[]`.
  - `explanation`: short text for operator/debug UX

Disclosure policy
- Sensitive prompts must support masking when `existsAnyApproved=true` but `existsSafeApproved=false`.
- User-facing render can map to `LOCKED` view state, but API status remains `SPOILER_BLOCKED`.

---

## 2) Endpoint Set (Minimal V3 Core)

### 2-1. Q16 Character Rise

Question intent
- "Show how character A rose to key status through events."

Endpoint
- `GET /characters/{characterId}/rise`

Params
- `dramaId` (required)
- `safeUpToEpisode` (required)
- `limit` (optional)

Payload
- `answerabilityStatus`
- `evidenceEventIds`
- `anchors`: timeline events that explain rise turning points
- `context`: optional PRECEDES-based supporting events (depth 1~2)

Notes
- Initial implementation may compose existing v2 timeline + causes/effects.

### 2-2. Q17 Foreshadowed-But-Not-Yet-Visible

Question intent
- "Which events are inevitably foreshadowed but not yet directly shown?"

Endpoint
- `GET /dramas/{dramaId}/foreshadowed`

Params
- `safeUpToEpisode` (required)
- `limit` (optional)

Payload
- `answerabilityStatus`
- `evidenceEventIds` (safe-side hint anchors only)
- `items`: masked-safe hints (no future event spoiler text)

Notes
- If only out-of-gate evidence exists: return `SPOILER_BLOCKED`.
- Do not leak future event summary/title in blocked state.

### 2-3. Q18 Multi-Perspective Reconstruction

Question intent
- "Reconstruct the same event from multiple character perspectives."

Endpoint
- `GET /events/{eventId}/perspectives`

Params
- `safeUpToEpisode` (required)

Payload
- `answerabilityStatus`
- `evidenceEventIds`
- `baseEvent`
- `perspectives[]`:
  - `characterId`
  - `role` (`INVOLVED | SUBJECT | OBJECT`)
  - `supportingEventIds` (optional)

Notes
- Reuse `event_character.role` as the primary split key.

### 2-4. Q19 Conflict Axis Grouping

Question intent
- "Group events across episodes by the same conflict axis."

Endpoint
- `GET /dramas/{dramaId}/conflict-axes`

Params
- `safeUpToEpisode` (required)
- `axis` (optional; e.g. `ADVERSARY | ALLY | BATTLE`)
- `limit` (optional)

Payload
- `answerabilityStatus`
- `evidenceEventIds`
- `axes[]`:
  - `axisCode`
  - `eventIds`
  - `score`

Notes
- Initial implementation can reuse existing aggregate/group logic from v2.

### 2-5. Q20 Narrative Distribution (Advanced)

Question intent
- "Analyze which event categories dominate character A's narrative."

Endpoint
- `GET /characters/{characterId}/narrative-distribution`

Params
- `dramaId` (required)
- `safeUpToEpisode` (required)

Payload
- `answerabilityStatus`
- `evidenceEventIds`
- `distribution`: category counts/ratios
- `explainability`: top evidence events per dominant category

Notes
- V2.5 has baseline distribution; V3 extends explainability.

---

## 3) Probe/Strict Integration Rule

Rule
- For sensitive Level 4 responses, use strict existence probe before returning final visibility.

Current reusable endpoint
- `POST /api/event/v2/probe`

Mapping
- `existsSafeApproved=false`, `existsAnyApproved=true` -> `SPOILER_BLOCKED`
- `existsSafeApproved=false`, `existsAnyApproved=false` -> `NOT_ENOUGH_DATA`
- `existsSafeApproved=true` -> `ANSWERED`

---

## 4) Backward Compatibility

- `/api/event/v1` and `/api/event/v2` contracts remain unchanged.
- V3 adds new endpoints only; no behavioral changes to v1/v2 responses.
- V2 aggregate endpoint may keep current `includeEvidenceEventIds=false -> null/omitted` behavior by existing contract.
- V3 endpoints must keep `evidenceEventIds` array shape regardless of internal merge/default paths.
- V2/V3 difference (`evidenceEventIds`) lock:
  - V2 aggregate: `includeEvidenceEventIds=false` -> field omitted or `null`.
  - V3: `evidenceEventIds` is always present; use empty array (`[]`) when none.

---

## 5) Release Gate for V3 API Contract

1. Q16~Q20 endpoints exist with stable DTOs.
2. `answerabilityStatus` behavior matches probe policy.
3. K+APPROVED gate is verified in endpoint-level tests.
4. v1/v2 regression suite passes unchanged.
5. RDF lane unavailability does not block V3 core runtime.

---

## 6) DTO Baseline Examples (Q16~Q20)

Guideline
- These examples define the current baseline contract for integration.
- Future changes are allowed, but must be versioned via spec update first.

Q16 `GET /characters/{characterId}/rise`
```json
{
  "success": true,
  "data": {
    "answerabilityStatus": "ANSWERED",
    "evidenceEventIds": [2307, 2343],
    "explanation": "Rise is inferred from approved timeline anchors.",
    "anchors": [
      { "eventId": 2307, "episode": 1, "summary": "..." },
      { "eventId": 2343, "episode": 2, "summary": "..." }
    ],
    "context": {
      "depth": 2,
      "eventIds": [2333, 2376]
    }
  }
}
```

Q17 `GET /dramas/{dramaId}/foreshadowed`
```json
{
  "success": true,
  "data": {
    "answerabilityStatus": "SPOILER_BLOCKED",
    "evidenceEventIds": [2452],
    "explanation": "Only beyond-K approved evidence exists.",
    "items": [
      { "hint": "갈등의 축이 강화됨", "masked": true }
    ]
  }
}
```

Q18 `GET /events/{eventId}/perspectives`
```json
{
  "success": true,
  "data": {
    "answerabilityStatus": "ANSWERED",
    "evidenceEventIds": [2376],
    "explanation": "Perspective split by event_character.role.",
    "baseEvent": { "eventId": 2376, "summary": "..." },
    "perspectives": [
      { "characterId": 17, "role": "SUBJECT", "supportingEventIds": [2307] },
      { "characterId": 18, "role": "OBJECT", "supportingEventIds": [2333] },
      { "characterId": 25, "role": "INVOLVED", "supportingEventIds": [] }
    ]
  }
}
```

Q19 `GET /dramas/{dramaId}/conflict-axes`
```json
{
  "success": true,
  "data": {
    "answerabilityStatus": "ANSWERED",
    "evidenceEventIds": [2307, 2333, 2376],
    "explanation": "Grouped by conflict-axis scoring over approved events.",
    "axes": [
      { "axisCode": "ADVERSARY", "eventIds": [2307, 2376], "score": 17 },
      { "axisCode": "BATTLE", "eventIds": [2333], "score": 8 }
    ]
  }
}
```

Q20 `GET /characters/{characterId}/narrative-distribution`
```json
{
  "success": true,
  "data": {
    "answerabilityStatus": "ANSWERED",
    "evidenceEventIds": [2307, 2333, 2448],
    "explanation": "Distribution computed on approved events up to K.",
    "distribution": [
      { "category": "TRANSFORMS", "count": 4, "ratio": 0.4 },
      { "category": "ADVERSARY", "count": 3, "ratio": 0.3 },
      { "category": "BATTLE", "count": 3, "ratio": 0.3 }
    ],
    "explainability": [
      { "category": "TRANSFORMS", "topEventIds": [2448, 2449] },
      { "category": "ADVERSARY", "topEventIds": [2307] }
    ]
  }
}
```
