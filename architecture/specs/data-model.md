# Data Model Specification

## User (Auth)
Represents a registered user of the system.

**Fields:**
- `id` (PK): Long (Auto Increment)
- `email`: String (Unique, Email format)
- `password`: String (Encrypted)
- `nickname`: String (Unique)
- `socialType`: Enum (EMAIL, GOOGLE, KAKAO, NAVER)
- `socialId`: String (Nullable)
- `role`: Enum (USER, ADMIN)
- `createdAt`: DateTime
- `updatedAt`: DateTime

## RefreshToken (Auth)
Stores JWT refresh tokens.

**Fields:**
- `key`: String (Email)
- `value`: String (Token)

