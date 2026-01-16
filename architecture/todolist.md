# NoSpoiler Project Total Todo List

> **Principle**: Each member updates their own section.
> **Last Updated**: 2026-01-16

---

## 👥 Team Member A: Infra & Identity (System Gateway)
- [x] API Gateway Scaffolding
- [x] Auth Service Scaffolding
- [x] User Service Scaffolding (Flyway V1)
- [ ] Security Policy Implementation (JWT)
- [ ] Admin Service Implementation

---

## 👥 Team Member B: Core Domain (Content & Data)
- [x] Drama Service Scaffolding
- [x] Character Service Scaffolding (Flyway V1, V2)
- [x] Wiki Service Scaffolding (Flyway V1)
- [ ] Wiki Service: `proposeEdit` (Draft creation)
- [ ] Wiki Service: `getCharacterWiki` (Filtered view)
- [ ] **Pending**: Apply Wiki Schema Proposal (V2)

---

## 👤 Team Member C: Intelligence & Filter (박지수 - YOU)
### 1. Infrastructure & Setup - ✅ DONE
- [x] Docker Configuration (Add event, policy services)
- [x] Docker QA service (Dockerfile + compose service)
- [x] Gradle Project Scaffolding (event, policy, qa)
- [x] Register all services in `settings.gradle`

### 2. Core Logic Implementation - ✅ DONE
- [x] `SpoilerManager` Implementation (Policy engine)
- [x] `SpoilerPolicyController` API (`/api/v1/policy/check`)
- [x] Unit Testing for Policy logic

### 3. Ontology Service Implementation - ✅ DONE
- [x] JPA/MyBatis Entity Mapping (event, character, relation, reveal)
- [x] `EventService` & `EventController` API (/api/v1/events)
- [x] DB Schema Fix (V2) for event_reveal

### 4. QA Service (Sprint 1 Goal) - ✅ DONE
- [x] Scaffolding `qa-service`
- [x] Implement Health Check API (/api/v1/qa/health)

### 5. API Refinement & Spec Alignment (Priority: High)
- [ ] **Backend Convention Compliance**
    - [ ] Add Swagger (`@Tag`, `@Operation`) to Controllers.
    - [ ] Refactor DTO/Entity Lombok annotations (`@Data` -> `@Getter`, `@Builder`).
    - [ ] Add `springdoc` dependency to `build.gradle`.
- [ ] **Spec Alignment (`intelligence-api-contract.md`)**
    - [x] Remove `/api/v1` prefix from paths (Done in `feature/api-alignment`).
    - [x] Enhance `EventController` search (add `q`, `uptoEpisode` params).
    - [x] Enhance `QaController` (implement `POST /qa/episode-range`).

### 6. Next Steps (Sprint 2)
- [ ] **Integration**: Connect QA -> Event -> Policy flow
- [ ] **Logic**: Multi-hop Ontology Retrieval
- [ ] **Verifying**: API JSON response spoiler hiding

### 7. Deploy & Ops (Immediate)
- [ ] Deploy on bit-ts: `cd ~/nospoiler/infra && docker compose up -d --build`
- [ ] If deploy fails with `:common` missing, fix event-service Docker build and re-run
- [x] C-only compose run on bit-ts (mysql/event/policy/qa, `DB_PORT=3307`)
