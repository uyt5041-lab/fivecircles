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
- `role`: Enum (VIEWER, CONTRIBUTOR, REVIEWER, ADMIN)
- `createdAt`: DateTime
- `updatedAt`: DateTime

## RefreshToken (Auth)
Stores JWT refresh tokens.

**Fields:**
- `key`: String (Email)
- `value`: String (Token)

## Schema Versioning (Event Domain)

### V2 (pre-triple)
- Event 중심 데이터(episode range + summary)로 스포일러 게이트/기본 질의 지원
- Event type / Character role 없음

### V3 (triple-enabled)
Triple decomposition is stored in existing tables:
- P (Predicate) -> event.predicate_code (default: UNKNOWN)
- S/O participant set -> event_character.role (default: INVOLVED; SUBJECT/OBJECT optional)

Notes:
- summary is display text; triple fields are query structure.
- All exposure rules still use episode_end <= K.
