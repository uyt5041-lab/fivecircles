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


===== added 20th jan 2026 =====

## Schema Versioning (Event Domain)

### V2 (pre-triple)
Goal: Enable Level2 filtering + explainability + BFS performance, without requiring triple roles.
Adds:
- event.predicate_code (default UNKNOWN)
- event.source_status (default APPROVED)
- event_relation BFS indexes

### V3 (triple-enabled)
Goal: Store triple decomposition (S/O roles) in existing tables.
Adds:
- event_character.role (default INVOLVED; optional SUBJECT/OBJECT)

## Relation Type Policy (MVP)

- Event <-> Character involvement is represented ONLY by event_character.
- Event <-> Event relations are represented ONLY by event_relation.
- event_relation.type allowed values (MVP): PRECEDES
- Related events are derived by shared character involvement (event_character).
- event_reveal exists for reveal semantics; traversal must not use reveal edges.
