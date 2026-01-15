# Todo List (Team Member C: Intelligence & Filter)

> **Role**: AI Engineer & Filter Policy
> **Services**: `event-service`, `spoiler-policy-service`, `qa-service`
> **Goal**: Implement Spoiler Filtering Logic and Ontology Infrastructure.

## 1. Infrastructure & Setup (Priority: High) - ✅ DONE
- [x] **Docker Configuration**
    - [x] Add `event-service` to `docker-compose.yml`.
    - [x] Add `spoiler-policy-service` to `docker-compose.yml`.
- [x] **Project Structure Refactoring**
    - [x] Create `event-service` and `spoiler-policy-service` Gradle projects.
    - [x] Register all services in `settings.gradle`.
    - [x] Move/Re-implement `SpoilerManager` in `spoiler-policy-service`.

## 2. Core Logic Implementation (Priority: High) - ✅ DONE
- [x] **Spoiler Policy Logic**
    - [x] Implement `SpoilerManager` in `spoiler-policy-service`.
    - [x] Define `SpoilerEvaluationRequest` and `SpoilerEvaluationResponse` DTOs.
    - [x] Implement `SpoilerPolicyController` API (`/api/v1/policy/check`).
- [x] **Unit Testing (with Mocks)**
    - [x] Create unit tests for `SpoilerManager`.
    - [x] Verify tests pass with `./gradlew test`.

## 3. Ontology Service Implementation (Priority: Medium) - ✅ DONE
- [x] **JPA/MyBatis Entity Mapping (`event-service`)**
    - [x] Map `Event` table to Entity & Mapper.
    - [x] Map `EventCharacter` table to Entity.
    - [x] Map `EventRelation` & `EventReveal` tables.
- [x] **Service & Controller**
    - [x] Implement `EventService` logic.
    - [x] Implement `EventController` API (`/api/v1/events`).

## 4. Collaboration & Proposals - ✅ DONE
- [x] **Wiki Service Schema Proposal**
    - [x] Draft `V2__create_wiki_entry.sql` matching `notion-origin-erd.md`.
    - [x] Placed proposal in `fivecircles/architecture/proposals/`.

## 5. QA Service (Sprint 1 Goal) - ✅ DONE
- [x] **Initial Setup**
    - [x] Scaffolding `qa-service` project.
    - [x] Implement Health Check API (`/api/v1/qa/health`).

---

## 🚀 Next Steps (Sprint 2 / Refinement)
- [ ] **Integration Testing**
    - [ ] Run full stack with `docker-compose up`.
    - [ ] Verify inter-service communication (QA -> Event -> Policy).
- [ ] **QA Service Logic**
    - [ ] Implement search logic using `event-service` data.
    - [ ] Connect with `spoiler-policy-service` for filtering.
- [ ] **API Documentation**
    - [ ] Setup Swagger/OpenAPI for new services.