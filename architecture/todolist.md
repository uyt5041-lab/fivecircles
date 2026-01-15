# NoSpoiler Implementation Plan

## Team Member A: Identity & Admin Services

### Service: Auth Service (Port: 8081)
- [x] Project Setup
- [x] Implement Domain Entity (RefreshToken)
- [x] Implement Feign Client (UserServiceClient)
- [x] Implement Service (Login with Feign)
- [x] Implement Controller (AuthController)

### Service: User Service (Port: 8082)
- [x] Project Setup
- [x] Domain Entity (User) & DB Schema
- [x] Implement Repository/Mapper
- [x] Internal API (Validate User by Email)
- [ ] CRUD API (Signup, Update Profile)

### Service: Admin Service (Port: 8087)
- [x] Project Setup
- [ ] Admin Dashboard Data API
- [ ] User Management API (Block/Unblock)


## Team Member C: Intelligence & Filter Services

> **Role**: AI Engineer & Filter Policy
> **Services**: `event-service`, `spoiler-policy-service`, `qa-service`
> **Goal**: Implement Spoiler Filtering Logic and Ontology Infrastructure.

### 1. Infrastructure & Setup (Priority: High)
- [x] **Docker Configuration**
    - [x] Add `event-service` to `docker-compose.yml`.
    - [x] Add `spoiler-policy-service` to `docker-compose.yml`.
- [x] **Project Structure Refactoring**
    - [x] Create `event-service` and `spoiler-policy-service` Gradle projects.
    - [x] Register all services in `settings.gradle`.
    - [x] Move/Re-implement `SpoilerManager` in `spoiler-policy-service`.

### 2. Core Logic Implementation (Priority: High)
- [x] **Spoiler Policy Logic**
    - [x] Implement `SpoilerManager` in `spoiler-policy-service`.
    - [x] Define `SpoilerEvaluationRequest` and `SpoilerEvaluationResponse` DTOs.
- [x] **Unit Testing (with Mocks)**
    - [x] Create unit tests for `SpoilerManager`.
    - [x] Verify tests pass with `./gradlew test`.

### 3. Ontology Service Implementation (Priority: Medium)
- [x] **JPA/MyBatis Entity Mapping (`event-service`)**
    - [x] Map `Event` table to Entity & Mapper.
    - [x] Map `EventCharacter` table to Entity.
- [ ] **Extended Relations**
    - [ ] Map `EventRelation` & `EventReveal` tables.

### 4. Collaboration & Proposals
- [x] **Wiki Service Schema Proposal**
    - [x] Draft `V2__create_wiki_entry.sql` matching `notion-origin-erd.md`.
    - [x] Placed proposal in `services/wiki-service/.../db/migration/`.

### 5. QA Service (Future - Sprint 2)
- [ ] Basic keyword search implementation using `event-service`.
