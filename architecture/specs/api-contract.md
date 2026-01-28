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

### GET /{id}

- **Description**: Get event details by ID.
- **Response**: `ApiResponse<EventResponseDTO>`

### GET /search

- **Description**: Search events (Spoiler-aware).
- **URL Params**: `dramaId`, `q` (optional), `uptoEpisode` (optional)
- **Response**: `ApiResponse<List<EventResponseDTO>>`

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
