# NoSpoiler Project Total Todo List

> **Principle**: Each member updates their own section.
> **Last Updated**: 2026-01-22

---

## 👥 Team Member A: Infra & Identity (System Gateway)

- [x] API Gateway Scaffolding
- [x] Auth Service Scaffolding
- [x] User Service Scaffolding (Flyway V1)
- [x] Gateway JWT 컨텍스트 전파 (검증/401·403 매핑, X-User-\* 헤더 전달, 헬스·레디니스/재시도 설정)
- [x] 인증 API 완성 (/api/auth: signup|login|reissue, 이메일·닉네임 중복 409, 비밀번호 해시, access/refresh 저장)
- [x] 토큰 수명 관리 (리프레시 회전·무효화, clock skew 60s 적용, 인증 이벤트 감사 로그)
- [x] OAuth2 카카오 로그인 연동 완료 (무상태/쿠키 인증, 프론트엔드 리다이렉트 처리, 로그인 화면 강제 옵션 적용)

---

## 👥 Team Member B: Core Domain (Content & Data)

- [x] Drama Service Scaffolding
- [x] Character Service Scaffolding (Flyway V1, V2)
- [x] Wiki Service Scaffolding (Flyway V1)
- [ ] Wiki Service: `proposeEdit` (Draft creation)
- [ ] Wiki Service: `getCharacterWiki` (Filtered view)
- [x] Wiki Service: **Triple Store Data Structure** (Ontology Support)
  - [x] Defined `PredicateCode` Enum in common module.
  - [x] DB: Add `refined_summary` & `wiki_submission_involved_character` table (Flyway V4).
  - [x] Logic: Merge character lists (main + involved) & PredicateCode Enum integration.
- [ ] **Pending**: Apply Wiki Schema Proposal (V2)
- [x] **Intelligence Service Support** (Assigned to Team B)
  - [x] Scaffolding `intelligence-service` (Port 8090, Dockerized, Gateway routed)
  - [x] Connect Wiki Service -> Intelligence Service (Async Flow)
  - [x] Backend Convention compliance (Removed `@Setter`, private internal port)
  - [x] 드라마별 인물 목록 조회 (Character Service 연동 완료)
  - [x] 실제 LLM API 연동 및 검증 (Smart Mock 구현 및 비동기 파이프라인 검토 완료)
  - [x] 정제 실패 시 재시도 로직 (Spring Retry 적용 완료)
  - [x] (Future) Actual LLM API key integration and Prompt tuning
  - [ ] (Future) 정제 완료 알림 시스템 (WebSocket/SSE 연동)
  - [x] **Wiki Service Enhancement & Testing (Done)**
    - [x] **Analysis & Design (Done)**
      - [x] Type mismatch: Entity/Request (String) vs LLM DTO (Enum) inconsistency.
      - [x] Async state: Missing `@Transactional` and object state sync in `refineSubmissionAsync`.
      - [x] Logic safety: Robust merging for main/involved characters and summary selection.
  - [x] **Phase 1: Logic Refactoring**
    - [x] Update `WikiSubmission` domain to use `PredicateCode` Enum for type safety.
    - [x] Strengthen `refineSubmissionAsync` (Add `@Transactional`, sync object state).
    - [x] Enhance character merging/summary logic in `checkAndProcessApproval`.
  - [x] **Phase 2: Comprehensive Testing**
    - [x] Implement `WikiSubmissionServiceTest` using Mockito.
    - [x] Validate E2E flow: Submit -> Refine (Mock) -> Vote -> Approve -> Event Publish (Mock).
    - [x] Test Edge Cases: LLM failure, invalid predicate codes, empty character lists.
- [ ] **Frontend Strategy & Implementation** (Team B)
  - [ ] Review existing `frontend.md` spec and align with current backend implementation.
  - [ ] Establish frontend architecture/strategy if missing (requested by Team B).
  - [ ] (Future) Actual frontend development based on strategy.

---

## 👤 Team Member C: Intelligence & Filter (박지수 - YOU)

> **My Todo**: 이 섹션(C 영역)만 작업

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

- [x] **Backend Convention Compliance**
  - [x] Add Swagger (`@Tag`, `@Operation`) to Controllers.
  - [x] Refactor DTO/Entity Lombok annotations (`@Data` -> `@Getter`, `@Builder`).
  - [x] Add `springdoc` dependency to `build.gradle`.
- [ ] **Spec Alignment (`intelligence-api-contract.md`)**
  - [x] Remove `/api/v1` prefix from paths (Done in `feature/api-alignment`).
  - [x] Enhance `EventController` search (add `q`, `uptoEpisode` params).
  - [x] Enhance `QaController` (implement `POST /qa/episode-range`).
- [ ] Swagger UI 화면 예시 공유 (모바일 확인용)

### 6. Next Steps (Sprint 2)

- [x] **Integration**: Connect QA -> Event -> Policy flow
- [ ] **Core Pipeline (no QA)**: Wiki 승인 → Event 생성 → Policy 태깅 정합성
- [x] 테스트용 서버 연결 스펙 설정
- [x] V2 이벤트 API curl 스모크 테스트 (create/search)
- [x] 이벤트 검색 시 스포일러 정책 연동 로직 업그레이드
- [x] 스포일러 정책 연동 curl 테스트
- [ ] 스포일러 정책 연동 테스트 완료 후 V3 진행 여부 결정
- [ ] Fix QA service client URLs/paths for docker (event search + policy check)
- [ ] Fix wiki approval -> event publish (client path + request mapping)
- [ ] Fix wiki approval -> event publish (client path + request mapping)
- [x] Align wiki->event request/response contract (DTO mapping)
  - [x] Updated `EventRequestDTO` to use `PredicateCode` Enum for strong typing.
- [ ] Fix event-service EventServiceClient default URL (8083 -> correct base)
- [ ] Sync auth/gateway/user endpoint mismatches with Team A (auth base URL, TokenDto, logout parsing, reissue validation, gateway secret, user profile path)
- [ ] **QnA 분리**: QA 연동/정확도 개선은 후순위로 분리
- [x] **Logic**: Multi-hop Ontology Retrieval
- [ ] **Verifying**: API JSON response spoiler hiding

### 7. Deploy & Ops (Immediate)

- [ ] Deploy on bit-ts: `cd ~/nospoiler/infra && docker compose up -d --build`
- [ ] If deploy fails with `:common` missing, fix event-service Docker build and re-run
- [x] C-only compose run on bit-ts (mysql/event/policy/qa, `DB_PORT=3307`)
- [ ] Decide whether to track or clean `fivecircles/agent/skills/`
- [ ] 협업으로 온톨로지 로직 검증 (wiki service)
- [ ] 프론트 작업 진행
- [ ] 프론트 MCP 설치 후 테스트
- [ ] 남은 로컬 브랜치 정리 (`feature/api-enhancement-full`, `feature/filter-service-working`)
