# Todo List (Implementation)
Detail tasks live in this file under each item.

## 1. Spec Analysis & Update
- [ ] **Analyze & Update Business Workflow**
    - [ ] Map `requirements/current.md` to `specs/buisiness-workflow.md` (Safe Browsing, Wiki Contribution, QA flow).
- [ ] **Define Data Model**
    - [ ] Update `specs/data-model.md` with entities: `Drama`, `Episode`, `Character`, `WikiEntry`, `Event`, `Ontology Relations`.
- [ ] **Define API Contract**
    - [ ] Update `specs/api-contract.md` for Main Page (Filtering), Wiki (Draft/Approve), QA (Inference).
- [ ] **Define Ontology & Matching Rules**
    - [ ] Update `specs/matching-rules.md` (Episode range logic) and Ontology constraints.

## 2. Infrastructure & Schema
- [ ] **Database Schema**
    - [ ] Create `schema.sql` and `lnf-migration.sql` reflecting the new Data Model.
- [ ] **Docker Environment**
    - [ ] Verify/Update `specs/docker.md` and compose files for necessary services (DB, Gateway, etc.).

## 3. Implementation (Backend)
- [ ] **Domain: Core Logic**
    - [ ] Implement `EpisodeRange` value object and overlap logic.
    - [ ] Implement User State (K) management.
- [ ] **Service: Content/Filter**
    - [ ] Implement `Drama`/`Character` retrieval with filtering logic.
    - [ ] Implement "Safe Summary" projection based on K.
- [ ] **Service: Wiki**
    - [ ] Implement `WikiEntry` CRUD with versioning/drafts.
    - [ ] Implement Approval Workflow (N reviewers).
    - [ ] Implement Event generation trigger upon approval.
- [ ] **Service: QA/Search**
    - [ ] Implement simple Event-based search (MVP: Keyword/Tag matching).
    - [ ] Implement Episode Range inference for queries.

## 4. Implementation (Frontend)
- [ ] **Main Page (S-1)**
    - [ ] Drama/Episode selection UI.
    - [ ] Dynamic Character list (Filtered).
- [ ] **Wiki Page (S-3)**
    - [ ] Contribution Form (with Range/Event inputs).
    - [ ] Review Interface.
- [ ] **Q&A Page (S-2)**
    - [ ] Chat/Search Interface with spoiler guards.

## 5. Testing & Validation
- [ ] **Unit Tests**
    - [ ] Verify Filtering Logic (Boundary tests for Episode Ranges).
- [ ] **Integration Tests**
    - [ ] Test full flow: Wiki Draft -> Approve -> Event -> Search.
- [ ] **Performance Check**
    - [ ] Verify Main Page load time <= 1.5s.

