# API Contracts (v1)

## Auth Service

Base URL: `/api/auth/v1`

### POST /signup

- **Description**: Register a new user.
- **Request**: `SignupRequest` (email, password, nickname)
- **Response**: `ApiResponse<Long>` (User ID)

### POST /login

- **Description**: Authenticate user and return tokens.
- **Request**: `LoginRequest` (email, password)
- **Response**: `ApiResponse<TokenDto>`

### POST /reissue

- **Description**: Reissue access token using refresh token.
- **Request**: `TokenRequestDto` (accessToken, refreshToken)
- **Response**: `ApiResponse<TokenDto>`

### POST /logout

- **Description**: Logout user by deleting refresh token.
- **Request**: Header `Authorization: Bearer <token>`
- **Response**: `ApiResponse<Void>`

### POST /password/reset-request

- **Description**: Request a password reset code via email.
- **Request**: `PasswordResetRequest` (email)
- **Response**: `ApiResponse<Void>`

### POST /password/reset

- **Description**: Reset password using the received code.
- **Request**: `PasswordResetConfirmRequest` (email, code, newPassword)
- **Response**: `ApiResponse<Void>`

---

## User Service

Base URL: `/api/user/v1`

### GET /me

- **Description**: Get current user profile.
- **Request**: Header `X-User-Id`
- **Response**: `ApiResponse<UserResponse>`

### GET /{userId}

- **Description**: Get user details by ID.
- **Response**: `ApiResponse<UserResponse>`

### PATCH /me

- **Description**: Update user profile.
- **Request**: `UserUpdateRequest`
- **Response**: `ApiResponse<Long>`

### POST /users/me/profile-image

- **Description**: Update user profile image.
- **Request**: Multipart file
- **Response**: `ApiResponse<String>` (Image URL)

### DELETE /me

- **Description**: Withdraw user account (Soft Delete).
- **Response**: `ApiResponse<Void>`

---

## Drama Service

Base URL: `/api/drama/v1`

### POST /

- **Description**: Create a new drama.
- **Request**: `DramaRequestDTO`
- **Response**: `ApiResponse<DramaResponseDTO>`

### GET /

- **Description**: Get all dramas.
- **Response**: `ApiResponse<List<DramaResponseDTO>>`

### GET /{id}

- **Description**: Get drama details by ID.
- **Response**: `ApiResponse<DramaResponseDTO>`

### GET /search

- **Description**: Search dramas by title keyword.
- **URL Params**: `keyword`
- **Response**: `ApiResponse<List<DramaResponseDTO>>`

### PUT /{id}

- **Description**: Update an existing drama.
- **Request**: `DramaRequestDTO`
- **Response**: `ApiResponse<DramaResponseDTO>`

### DELETE /{id}

- **Description**: Delete a drama.
- **Response**: `ApiResponse<Void>`

---

## Character Service

Base URL: `/api/character/v1`

### POST /

- **Description**: Create a new character.
- **Request**: `CharacterRequestDTO`
- **Response**: `ApiResponse<CharacterResponseDTO>`

### GET /

- **Description**: Get characters by drama ID.
- **URL Params**: `dramaId`
- **Response**: `ApiResponse<List<CharacterResponseDTO>>`

### GET /{id}

- **Description**: Get character details by ID.
- **Response**: `ApiResponse<CharacterResponseDTO>`

### PUT /{id}

- **Description**: Update an existing character.
- **Request**: `CharacterRequestDTO`
- **Response**: `ApiResponse<CharacterResponseDTO>`

### DELETE /{id}

- **Description**: Delete a character.
- **Response**: `ApiResponse<Void>`

---

## Event Service

Base URL: `/api/event/v1`

### POST /

- **Description**: Create a new ontology event.
- **Request**: `EventRequestDTO`
- **Response**: `ApiResponse<EventResponseDTO>`
  - Reveal metadata (optional):
    - When `predicateCode=REVEALS` and `revealTargetId` is provided, `revealTargetType` is required.
    - `revealType` is optional (`HINT|CONFIRM`) and is stored in `event_reveal.reveal_type` when provided.

### GET /{id}

- **Description**: Get event details by ID.
- **Response**: `ApiResponse<EventResponseDTO>`

### PUT /{id}

- **Description**: Update an existing ontology event.
- **Request**: `EventRequestDTO` (partial update allowed)
- **Response**: `ApiResponse<EventResponseDTO>`
- **Semantics**:
  - PATCH-like behavior: omitted fields keep existing values.
  - `null` values are treated as "not provided" (no field-clearing via null).

### GET /search

- **Description**: Search events (Spoiler-aware).
- **URL Params**: `dramaId`, `q` (optional), `uptoEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

---

## Event Query API (V2)

Base URL: `/api/event/v2`

Note
- This section documents "query" endpoints used by QA/FE widgets (Level 1-3).
- Spoiler gate: `safeUpToEpisode=K` is applied on all query endpoints.

### GET /characters/{characterId}/events

- **Description**: Character events timeline (optional keyword/predicate filters).
- **URL Params**:
  - `safeUpToEpisode` (optional but recommended): spoiler gate K
  - `predicateCode` (optional): filter by `event.predicate_code`
  - `q` (optional): keyword filter (matches `summary` OR `predicate_suggestion`)
  - `includeRevealPartner` (optional, default `true`)
    - when `true`, timeline may include REVEALS "partner" events (for explanations)
    - templates that need a clean "first/earliest" should pass `false`
  - `limit` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /characters/{characterId}/coevents

- **Description**: Co-appearance events where `characterId` and `with` appear together.
- **URL Params**:
  - `with` (required): other character ID
  - `safeUpToEpisode` (optional but recommended): spoiler gate K
  - `limit` (optional)
    - server-side cap: max 200
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /characters/{characterId}/related-characters

- **Description**: Related characters via co-appearance graph.
- **URL Params**: `safeUpToEpisode` (optional), `limit` (optional)
- **Response**: `ApiResponse<List<CharacterRelationResponse>>`

### GET /characters/{characterId}/related-characters/aggregate

- **Description**: Single-call aggregation for derived questions (ALLY/ADVERSARY/etc). Avoids N+1 coevents calls.
- **URL Params**: `safeUpToEpisode` (required), `mode` (required), `minScore` (optional), `limit` (optional), `includeEvidenceEventIds` (optional)
- **Response**: `ApiResponse<RelatedCharactersAggregateResponse>` (draft)
- **Spec**: `fivecircles/architecture/specs/predicate/related-characters-aggregate.md`

RelatedCharactersAggregateResponse (draft)
- `characterId: long`
- `safeUpToEpisode: int`
- `mode: string` (one of `ADVERSARY|ALLY|COEVENTS`)
- `scoreRule?: string`
  - score 계산식 표시용. FE drift 방지를 위해 서버가 내려준다.
- `items: RelatedCharactersAggregateItem[]`

RelatedCharactersAggregateItem (draft)
- `otherCharacterId: long`
- `score: int`
- `countsByGroup: map<string,int>`
- `evidenceEventIds?: long[]`
  - present only when `includeEvidenceEventIds=true`

Example
```json
{
  "success": true,
  "data": {
    "characterId": 100,
    "safeUpToEpisode": 3,
    "mode": "ADVERSARY",
    "scoreRule": "score = 8*ADVERSARY + 5*BATTLE + 2*DEATH_EXIT",
    "items": [
      {
        "otherCharacterId": 200,
        "score": 17,
        "countsByGroup": {
          "BATTLE": 3,
          "ADVERSARY": 2
        },
        "evidenceEventIds": [2052, 2083]
      }
    ]
  }
}
```

---

## Wiki Service

Base URL: `/api/wiki/v1`

### POST /submissions

- **Description**: Submit a new fact for a character.
- **Request**: `SubmissionRequest`
- **Response**: `ApiResponse<Long>` (Submission ID)

### GET /submissions

- **Description**: List submissions by drama (optional).
- **URL Params**: `dramaId` (optional)
- **Response**: `ApiResponse<List<SubmissionResponse>>`

### PUT /submissions/{submissionId}

- **Description**: Update submission content.
- **Request**: `SubmissionUpdateRequest`
- **Response**: `ApiResponse<Void>`

### DELETE /submissions/{submissionId}

- **Description**: Delete a submission.
- **Response**: `ApiResponse<Void>`

### POST /verifications

- **Description**: Vote on a submitted fact.
- **Request**: `VerificationRequest`
- **Response**: `ApiResponse<SubmissionResponse>`

### GET /submissions/{submissionId}

- **Description**: Get submission details and vote status.
- **Response**: `ApiResponse<SubmissionResponse>`

---

## Spoiler Policy Service

Base URL: `/api/policy/v1`

### POST /check

- **Description**: Check if content is a spoiler for the user.
- **Request**: `SpoilerEvaluationRequest` (revealEpisode, userCurrentEpisode)
- **Response**: `ApiResponse<SpoilerEvaluationResponse>` (isSpoiler, reason)

---

## QA Service

Base URL: `/api/qa/v1`

### GET /health

- **Description**: Health check for QA service.
- **Response**: `ApiResponse<String>`

### POST /episode-range

- **Description**: Estimate episode range for a query.
- **Request**: `QaRequestDTO`
- **Response**: `ApiResponse<QaResponseDTO>`
---

## Intelligence Service

Base URL: `/api/intelligence/v1`

### POST /refine

- **Description**: 자연어 제보 내용을 분석하여 구조화된 온톨로지 정보(인물 ID, 서술어 코드, 정제된 요약)로 변환합니다.
- **Request**: `RefineRequest` (content, context)
- **Response**: `ApiResponse<RefineResponse>` (predicateCode, involvedCharacterIds, refinedSummary)

### POST /summary

- **Description**: 특정 인물의 여러 사건 요약본을 하나의 일관된 스토리라인(문단)으로 통합합니다.
- **Request**: `CharacterSummaryRequest` (characterName, episodeK, summaries)
- **Response**: `ApiResponse<String>` (Unified Summary text)

---

## Notification Service

Base URL: `/api/notifications/v1`

### GET /subscribe
- **Description**: Subscribe to real-time notifications via SSE.
- **Headers**: `X-User-Id`
- **Response**: Event Stream

### GET /
- **Description**: Get notification list for current user.
- **Headers**: `X-User-Id`
- **Response**: `ApiResponse<Slice<NotificationResponse>>`

### PATCH /{id}/read
- **Description**: Mark a notification as read.
- **Response**: `ApiResponse<Void>`

### GET /unread-count
- **Description**: Get the count of unread notifications.
- **Headers**: `X-User-Id`
- **Response**: `ApiResponse<Long>`

### POST /internal/v1/notifications/send (Internal)
- **Description**: Send a notification to a specific user.
- **Request**: `NotificationRequest` (receiverId, title, content, type, relatedUrl)
- **Response**: `ResponseEntity<Void>`
