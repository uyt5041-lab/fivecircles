# API Contracts

## Auth Service
Base URL: `/api/auth`

### POST /signup
- **Description**: Register a new user.
- **Request**:
  - `email`: String (Required, Email format)
  - `password`: String (Required, Min 8 chars)
  - `nickname`: String (Required, Min 2 chars)
- **Response**: `ApiResponse<Long>` (User ID)

### POST /login
- **Description**: Authenticate user and return tokens.
- **Request**:
  - `email`: String
  - `password`: String
- **Response**: `ApiResponse<TokenDto>`
  - `accessToken`: String
  - `refreshToken`: String
  - `grantType`: String (Bearer)
  - `expiresIn`: Long

### POST /reissue
- **Description**: Reissue access token using refresh token.
- **Request**:
  - `accessToken`: String
  - `refreshToken`: String
- **Response**: `ApiResponse<TokenDto>`


