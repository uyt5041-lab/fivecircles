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

---

## Event Service

Base URL: `/api/event`

### POST /v1

- **Description**: Create a new ontology event.
- **Request**: `EventRequestDTO`
- **Response**: `ApiResponse<EventResponseDTO>`

### GET /v1/{id}

- **Description**: Get event details by ID.
- **Response**: `ApiResponse<EventResponseDTO>`

### GET /v1/search

- **Description**: Search events (Spoiler-aware).
- **URL Params**: `dramaId`, `q` (optional), `uptoEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

---

## Event Query Service (V2)

Base URL: `/api/event`

### GET /v2/dramas/{dramaId}/events

- **Description**: Filter events by drama and predicate/episode range.
- **URL Params**: `safeUpToEpisode` (optional), `predicateCode` (optional), `fromEpisode` (optional), `toEpisode` (optional), `limit` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/dramas/{dramaId}/characters

- **Description**: Characters seen up to K by involvement.
- **URL Params**: `safeUpToEpisode` (optional), `limit` (optional), `sort` (optional)
- **Response**: `ApiResponse<List<CharacterInvolvementResponse>>`

### GET /v2/characters/{characterId}/events

- **Description**: Events involving the character.
- **URL Params**: `safeUpToEpisode` (optional), `predicateCode` (optional), `limit` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/characters/{characterId}/coevents

- **Description**: Events where two characters appear together.
- **URL Params**: `with`, `safeUpToEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/events/{eventId}/characters

- **Description**: Characters involved in the event.
- **URL Params**: `safeUpToEpisode` (optional)
- **Response**: `ApiResponse<List<EventCharacterResponse>>`

### GET /v2/events/{eventId}/related

- **Description**: Traverse related events (multi-hop).
- **URL Params**: `depth` (optional, default 1), `safeUpToEpisode` (optional), `types` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/events/{eventId}/causes

- **Description**: Traverse PRECEDES edges in reverse.
- **URL Params**: `depth` (optional, default 1), `safeUpToEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/events/{eventId}/effects

- **Description**: Traverse PRECEDES edges forward.
- **URL Params**: `depth` (optional, default 1), `safeUpToEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

### GET /v2/characters/{characterId}/related-characters

- **Description**: Characters related via co-appearance.
- **URL Params**: `safeUpToEpisode` (optional), `limit` (optional)
- **Response**: `ApiResponse<List<CharacterRelationResponse>>`

### GET /v2/characters/path

- **Description**: Shortest path between characters via events.
- **URL Params**: `from`, `to`, `maxDepth` (optional), `safeUpToEpisode` (optional)
- **Response**: `ApiResponse<CharacterPathResponse>`

---

## Wiki Service

Base URL: `/api/wiki/v1`

### POST /submissions

- **Description**: Submit a new fact for a character.
- **Request**: `SubmissionRequest`
- **Response**: `ApiResponse<Long>` (Submission ID)

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
