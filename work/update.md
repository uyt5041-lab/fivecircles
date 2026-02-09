# Work Update (2026-01-15)

This file summarizes recent updates so other agents can continue without re‑discovering changes.

## 2026-01-15: Sprint 1 Service Implementation (Team Member C)
- **Service Deployment**:
    - `event-service`: Implemented Repository (MyBatis), Service, and Controller layers.
    - `spoiler-policy-service`: Implemented `SpoilerManager` logic and `/check` API.
    - `qa-service`: Initial scaffolding and Health Check API.
- **Infrastructure**:
    - Added all C-team services to `docker-compose.yml` and `settings.gradle`.
    - Integrated `:common` module for unified Error Handling (`ApiResponse`).
- **Documentation & Process**:
    - Established Notion Mirroring policy for `specs/notion-origin-*` (Local only, untracked).
    - Restructured `todolist.md` for team collaboration.
    - Proposed Wiki Schema (`V2`) to Team Member B.

## 2026-01-15: IDE Agent Automation
- **Setup .vscode/tasks.json**:
    - Configured automatic startup for `gemini`, `codex`, and `claude` CLI agents on project open (`runOn: folderOpen`).
    - Implemented **Interactive Mode** (`/bin/zsh -l -i -c`) to ensure compatibility with user's `.zshrc` aliases and functions.
    - Added **Tmux-style Split View** task (`Agents: Start (Tmux Style)`).
    - Fixed "infinite loading spinner" issue for Codex by injecting an initial `echo` command and configuring `problemMatcher`.
    - Recommended Keybindings: `Cmd+Alt+A` (Start All), `Cmd+Alt+T` (Tmux Style).
- **Error Logs Created**: See `fivecircles/test/errorlogs/2026-01-15-ide-task-failure.md`.
- **Knowledge Base Updated**: See `fivecircles/test/learn-from-log.md`.

## Addendum (2026-01-16) - API/QnA + MCP collaboration
### Backend
- Add event search endpoint with `q`/`uptoEpisode` params (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java)
- Add QA episode-range endpoint + DTOs (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/controller/QaController.java)
### Docs
- Add MCP/collaboration configs and prompts; update guide (refs: .mcp.json)

## Addendum (2026-01-16) - Docker deploy attempt
### Backend
- Fix spoiler-policy-service Dockerfile to include `common` module (refs: services/spoiler-policy-service/Dockerfile)

## Addendum (2026-01-16) - C-only Docker deploy (bit-ts)
### Backend
- Add QA Dockerfile + compose service and align QA port mapping (refs: services/qa-service/Dockerfile, infra/docker-compose.yml)
- Set C-only DB port default to 3307 (refs: infra/docker-compose.yml, .env.example)
### Tests
- Event search OK: `GET /events/search?dramaId=1&q=foo&uptoEpisode=1` (refs: fivecircles/architecture/specs/intelligence/intelligence-api-contract.md)
- QA OK: `GET /qa/health`, `POST /qa/episode-range` (refs: fivecircles/architecture/specs/intelligence/intelligence-api-contract.md)

## Addendum (2026-01-17) - QA/Event/Policy integration
### Backend
- Wire QA episode-range flow to event/policy services (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/service/QaService.java)
- Add QA HTTP clients + service URL config (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/client/EventServiceClient.java, services/qa-service/src/main/resources/application.yml)
### Tests
- Not run (not requested)

## Addendum (2026-01-19) - Multi-hop event search
### Backend
- Add multi-hop expansion for event search (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java)
- Add relation/id lookup queries for hop traversal (refs: services/event-service/src/main/resources/mapper/event/EventRelationMapper.xml, services/event-service/src/main/resources/mapper/event/EventMapper.xml)
- Order multi-hop results by hop distance before episode range (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java)
### Tests
- `:services:event-service:test` OK (refs: services/event-service/src/test/java/com/nospoiler/eventservice/service/EventServiceImplTest.java)

## Addendum (2026-01-19) - Test server spec + episode cutoff
### Backend
- Add test server connection spec for Team C services (refs: fivecircles/architecture/specs/test-sever-policy.md)
- Use episode_end as cutoff for event search filters (refs: services/event-service/src/main/resources/mapper/event/EventMapper.xml)
### Tests
- Not run (not requested)

## Addendum (2026-01-20) - Spec alignment (roles + event type)
### Backend
- Align user role enums with notion-origin (refs: fivecircles/architecture/specs/data-model.md)
- Document eventType -> predicate_code mapping for V2 (refs: fivecircles/architecture/specs/intelligence/intelligence-events-contract.md)
### Tests
- Not run (not requested)

## Addendum (2026-01-20) - V2 config + migration
### Backend
- Add Flyway history table override for event/user services (refs: services/event-service/src/main/resources/application.yml, services/user-service/src/main/resources/application.yml)
- Add V2 pre-triple migration for event domain (refs: services/event-service/src/main/resources/db/migration/V3__event_v2_pre_triple.sql)
### Tests
- Not run (not requested)
## Addendum (2026-01-20) - Event V2 fields + specs
### Backend
- V2 predicate fields and search filter (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java)

### Docs
- V2/V3 plans + test server policy updated (refs: fivecircles/architecture/specs/event-v2-plan-map.md)

### Tests
- Event service tests pass (refs: ./gradlew :services:event-service:test)
## Addendum (2026-01-20) - Event search policy apply
### Backend
- Event search uses policy client (refs: services/event-service/src/main/java/com/nospoiler/eventservice/client/PolicyServiceClient.java)

### Tests
- Tests pass after stubbing fix (refs: fivecircles/test/errorlogs/backend/2026-01-20-mockito-unnecessary-stubbing.md)
## Addendum (2026-01-20) - Test server policy sync
### Docs
- Added remote sync + infra compose steps (refs: fivecircles/architecture/specs/test-server-policy-4C.md)
## Addendum (2026-01-20) - Server curl validation
### Backend
- Fix policy service port mapping + compose env (refs: infra/docker-compose.yml)

### Tests
- Server curl checks pass for event + policy (refs: fivecircles/test/errorlogs/backend/2026-01-20-policy-port-mapping.md)
## Addendum (2026-01-20) - Event query APIs
### Backend
- Added L1-3 query endpoints and mappers (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Synced intelligence mapping to V2 query docs (refs: fivecircles/architecture/specs/intelligence/intelligence-api-contract.md)

### Tests
- Event service tests pass (refs: ./gradlew :services:event-service:test)
## Addendum (2026-01-20) - Event V2 queries
### Backend
- Implemented L1-3 query endpoints + mappers (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Added V2 API spec and updated mappings (refs: fivecircles/architecture/specs/event-v2-api.md)

### Tests
- Server curl checks for new endpoints (refs: http://localhost:8089/dramas/1/events?safeUpToEpisode=1&predicateCode=TRANSFORMS)
## Addendum (2026-01-20) - Ignore local proposal drafts
### Docs
- Ignore nospoiler_newspecs proposal folder (refs: .gitignore)
## Addendum (2026-01-20) - Track shared proposal materials
### Docs
- Tracked shared proposal folder + skills (refs: fivecircles/architecture/proposals/공유-온톨로지레이어구축)
## Addendum (2026-01-20) - Server integration checks
### Backend
- Created missing nospoiler_event/wiki DBs on bit-ts for docker tests (refs: fivecircles/test/errorlogs/backend/2026-01-20-mysql-missing-event-wiki-db.md)

### Tests
- Server curl OK: event create/search + policy check (refs: fivecircles/architecture/specs/test-server-policy-4C.md)
- QA and wiki→event integration failed (refs: fivecircles/test/errorlogs/backend/2026-01-20-qa-event-policy-client-mismatch.md, fivecircles/test/errorlogs/backend/2026-01-20-wiki-event-client-mismatch.md)
## Addendum (2026-01-20) - Test server DB bootstrap
### Docs
- Document MySQL volume bootstrap step for event/wiki/policy DBs (refs: fivecircles/architecture/specs/test-server-policy-4C.md)
## Addendum (2026-01-20) - V2 integration checks
### Tests
- Server curl OK: drama-event + character-event (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
- Wiki→event publish fails (404 /api/v1/events) after approval (refs: fivecircles/test/errorlogs/backend/2026-01-20-wiki-event-client-mismatch.md)
## Addendum (2026-01-20) - API contract consolidation
### Backend
- Align policy/event client paths with /api/* prefixes (refs: services/event-service/src/main/java/com/nospoiler/eventservice/client/PolicyServiceClient.java, services/qa-service/src/main/java/com/nospoiler/qaservice/client/EventServiceClient.java, services/qa-service/src/main/java/com/nospoiler/qaservice/client/PolicyServiceClient.java, services/wiki-service/src/main/java/com/nospoiler/wikiservice/client/EventServiceClient.java)

### Docs
- Consolidate intelligence API into api-contract and remove duplicate spec (refs: fivecircles/architecture/specs/api-contract.md, fivecircles/architecture/specs/README.md)

### Tests
- Not run (path changes only)
## Addendum (2026-01-20) - Issue plan + V3 plan update
### Docs
- Update V2 issue-resolution plan, safe traversal gating, and PRECEDES direction rules (refs: fivecircles/architecture/specs/event-v2-plan-map.md)
- Update V3 plan prerequisites and source_status gating (refs: fivecircles/architecture/specs/event-v3-plan.md)
- Remove legacy content-service directory (refs: services/content-service)

### Tests
- Not run (spec updates only)
## Addendum (2026-01-20) - V2 issue resolution prep
### Docs
- Prepared V2 issue resolution plan and V3 prerequisite alignment (refs: fivecircles/architecture/specs/event-v2-plan-map.md, fivecircles/architecture/specs/event-v3-plan.md)

### Tests
- Not run (prep only)
## Addendum (2026-01-20) - V2 issue fixes (phase 1)
### Backend
- Gate event exposure by source_status and safe traversal joins; update relation mapper signature (refs: services/event-service/src/main/resources/mapper/event/EventMapper.xml, services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml, services/event-service/src/main/resources/mapper/event/EventRelationMapper.xml, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java)
- Add Flyway table env to compose and new migration indexes (refs: infra/docker-compose.yml, services/event-service/src/main/resources/db/migration/V4__mig4_event_status_index.sql, services/event-service/src/main/resources/db/migration/V5__mig5_event_character_index.sql)

### Tests
- Not run (schema + mapper changes)
## Addendum (2026-01-20) - V2 migration + gate tests
### Tests
- Server migration applied (V4/V5) and gate checks pass: approved returns, pending excluded (refs: services/event-service/src/main/resources/db/migration/V4__mig4_event_status_index.sql, services/event-service/src/main/resources/db/migration/V5__mig5_event_character_index.sql)
## Addendum (2026-01-20) - V2 traversal tests
### Tests
- Server BFS related/causes gated by K+APPROVED; character path returns safe path (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java)
- V2 seed note: event_character has no role column pre-V3 (refs: fivecircles/test/errorlogs/backend/2026-01-20-v3-role-column-missing.md)
## Addendum (2026-01-20) - V2 role insert fix
### Backend
- Remove role column from event_character insert for V2 (refs: services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml)

### Tests
- Not run (mapper fix only)
## Addendum (2026-01-20) - V2 roleless insert test
### Tests
- Server insert without role works; character events returns seeded event (refs: services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml)
## Addendum (2026-01-20) - Teamwork notes + todo update
### Docs
- Add teamwork notes for findings and API alignment (refs: fivecircles/architecture/teamwork.md)
- Update Team C todo items for alignment fixes (refs: fivecircles/architecture/todolist.md)
## Addendum (2026-01-20) - Teamwork notes language update
### Docs
- Rewrite teamwork notes in Korean (refs: fivecircles/architecture/teamwork.md)
## Addendum (2026-01-20) - Rebase + api-contract alignment
### Docs
- Rebase on develop and align api-contract with event query + internal endpoints (refs: fivecircles/architecture/specs/api-contract.md)

## Addendum (2026-02-05) - Precedes admin + V2 고도화 문서 정리
### Frontend
- Admin Precedes 화면에 캐릭터/관계 관리 보강 (refs: front/features/admin/AdminPrecedesPage.tsx, front/features/admin/services/precedesApi.ts)
### Backend
- PRECEDES 추천/기존 목록 API 보강 및 매퍼 정비 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventRelationController.java, services/event-service/src/main/resources/mapper/event/EventRelationMapper.xml)
- 캐릭터 이름 조인/alias 정비 (refs: services/event-service/src/main/resources/mapper/event/EventMapper.xml)
### Docs
- V2 고도화 명칭/진행축 표현 정리 + 배포 스크립트/스킬 등록 (refs: fivecircles/architecture/specs/v2.5-unify.md, fivecircles/architecture/specs/event-v2-plan-map.md, fivecircles/test/deploy-server.sh)
### Tests
- Not run (not requested)

### Tests
- Pending server retest after rebase
## Addendum (2026-01-20) - Rebase retest
### Tests
- Server search gate still OK after rebase (approved returns, pending excluded)
## Addendum (2026-01-20) - Use develop api-contract
### Docs
- Reset api-contract to develop version (refs: fivecircles/architecture/specs/api-contract.md)
## Addendum (2026-01-20) - Use develop infra docker-compose
### Docs
- Reset infra/docker-compose.yml to develop version (refs: infra/docker-compose.yml)
## Addendum (2026-01-20) - Document V2 query endpoints
### Docs
- Add Event Query (V2) endpoints to api-contract (refs: fivecircles/architecture/specs/api-contract.md)
## Addendum (2026-01-20) - Server deploy attempt
### Tests
- FAIL: SSH to bit-ts denied (refs: fivecircles/test/errorlogs/backend/2026-01-20-ssh-permission-denied.md)
## Addendum (2026-01-20) - Server curl checks
### Tests
- Server curl OK: event search + V2 query + policy check (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java, services/spoiler-policy-service/src/main/java/com/nospoiler/policyservice/controller/SpoilerPolicyController.java)
## Addendum (2026-01-20) - Scope V2 query under event base
### Backend
- Add /api/event/v1 base to EventQueryController (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Update V2 query base URL in api-contract (refs: fivecircles/architecture/specs/api-contract.md)
## Addendum (2026-01-20) - Server V2 query base tests
### Tests
- Server curl OK: /api/event/v1/dramas/events, /events/{id}/characters, /search (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java)
## Addendum (2026-01-20) - Split gateway work to branch
### Docs
- Move api-gateway route changes to chore/gateway-routes and revert on main branch (refs: services/api-gateway/src/main/resources/application.yml)
## Addendum (2026-01-20) - V2 query endpoint tests
### Tests
- Server curl OK: coevents/related/causes/effects/path (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
## Addendum (2026-01-21) - Align V2 query base with develop
### Backend
- Remove /api/event/v1 base from EventQueryController (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Set V2 query base URL to root in api-contract (refs: fivecircles/architecture/specs/api-contract.md)
## Addendum (2026-01-21) - V2 query base revert tests
### Tests
- Server curl OK: root V2 query endpoints (dramas/coevents/related/causes/effects/path) (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
## Addendum (2026-01-21) - Prefix event APIs with /api/event + /v1
### Backend
- Move event controllers under /api/event and add /v1 on endpoints (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Update event base URL and endpoint paths in api-contract (refs: fivecircles/architecture/specs/api-contract.md)
## Addendum (2026-01-21) - Version event APIs
### Backend
- Add /api/event base and move query endpoints to /v2 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)

### Docs
- Align api-contract event base and V2 paths (refs: fivecircles/architecture/specs/api-contract.md)

### Tests
- Server curl OK: /api/event/v1 search and /api/event/v2 queries (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
## Addendum (2026-01-21) - Rename notion-origin specs
### Docs
- Unignore notion-origin mirrors and rename spec files with -v2 (refs: .gitignore, fivecircles/architecture/specs/notion-origin-erd-v2.md, fivecircles/architecture/specs/notion-origin-ontology-layer-v2.md, fivecircles/architecture/specs/notion-origin-requirements-v2.md, fivecircles/architecture/specs/notion-origin-roles-v2.md)
- Refresh references to renamed notion-origin files (refs: fivecircles/architecture/specs/README.md, fivecircles/agent/collaboration-protocol.md, fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex00.md, fivecircles/architecture/proposals/공유-온톨로지레이어구축/Ex07-stepsformigration(editing).md, fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex10-versions(2-4).md)
## Addendum (2026-01-21) - Repeat-mistake tagging
### Docs
- Add category tags rule to repeat-mistakes (refs: fivecircles/agent/repeat-mistakes.md)
## Addendum (2026-01-21) - Align V2 API examples
### Docs
- Update event-v2-api base URL and paths to /api/event/v2 (refs: fivecircles/architecture/specs/event-v2-api.md)
## Addendum (2026-01-21) - Add mistakes arrest guardrail
### Docs
- Add mistakes-arrest guide and register mistakes-arrest skill (refs: fivecircles/agent/mistakes-arrest.md, /Users/pio/.codex/skills/mistakes-arrest/SKILL.md)
## Addendum (2026-01-21) - Replace repeat-mistakes doc
### Docs
- Replace repeat-mistakes with mistakes-repeating (refs: fivecircles/agent/mistakes-repeating.md)
## Addendum (2026-01-21) - Align event-service port for gateway tests
### Backend/Infra
- Parameterize event-service port for docker runtime and align wiki event URL (refs: services/event-service/src/main/resources/application-docker.yml, infra/docker-compose.yml)

### Tests
- Server gateway smoke: auth login -> event search returns 200 with Bearer (refs: services/api-gateway/src/main/resources/application-docker.yml, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventController.java)
## Addendum (2026-01-21) - Align MCP template with local config
### Docs
- Update .mcp.json to include agent-bridge/playwright/browser-use (refs: .mcp.json)

## 2026-01-26: Frontend Compilation Fix & Port Config
- **Goal**: Fix local frontend build error and finalize local-test configuration.
- **Changes**:
  - `front/features/timeline/EventTimelinePage.tsx`: Removed duplicate `Drama` import that caused a build failure (`Identifier 'Drama' has already been declared`).
  - **Environment**: Verified frontend runs on port 3000.
  - **Skill**: Added `protocol_read_log_setup.md` for context restoration.
- **Status**: Frontend compilation error resolved. Server accessible at `http://localhost:3000`.
- **Next**: Revert port configuration for server integration and proceed with testing.

## 2026-01-26: Remote Deployment & 500 Error Fix
- **Goal**: Deploy to `bit-ts`, fix backend 500 errors, and verify frontend connectivity via Playwright.
- **Changes**:
  - **Deployment**: Deployed `feature/experimental-frontend` to `bit-ts` (Docker Compose).
  - **Fix 1 (DB)**: Resolved `character-service` and `drama-service` startup failures (Unknown Database) by manually creating missing databases (`nospoiler_character`, `nospoiler_drama`).
  - **Fix 2 (Port Mismatch)**: Resolved Gateway 500 (Connection Refused) by injecting `SERVER_PORT` and `*_SERVICE_PORT` environment variables in `docker-compose.yml`. Configured services to listen on 808x ports (matching `.env` and Gateway routing) instead of default 8080.
  - **Verification**: Installed Playwright locally (`@playwright/test`) and passed `front/check_console.spec.js`. Verified `character-service` logs show `Tomcat initialized with port 8084`.
  - **Issue**: `auth-service` remains down due to missing OAuth2 environment variables (`KAKAO_CLIENT_ID` etc.).
- **Status**: Core data services active. Login service pending configuration.

## 2026-01-26: DramaSelectionPage Real API Integration & Data Recovery
- **Goal**: Replace mock drama selection with real API and restore DB seed data for production readiness.
- **Changes**:
  - **Frontend**:
    - `DramaSelectionPage.tsx`: Replaced mock data with real API (`dramaApi.getAllDramas()`).
    - Verified UI correctly displays drama list from backend.
  - **Backend**:
    - DB Seed: Injected base drama and character data into remote database to resolve empty screen/404 errors.
    - Verified `drama-service` and `character-service` return valid responses.
  - **Deployment**:
    - Deployed updated frontend code to remote server (bit-ts).
    - Verified data loading in both local and remote environments.
- **Status**: DramaSelectionPage now fully integrated with real backend. Database populated with seed data.
- **Next**: Rebase to develop, then implement QA Context UX and Playwright tests.

## 2026-01-26: Sprint Planning - Rebase & QA UX Enhancement
- **Goal**: Synchronize with develop branch and enhance QA widget context handling.
- **Plan**:
  1. **Rebase**: Rebase `feature/experimental-frontend` onto `origin/develop` to sync latest changes.
  2. **Skills Tracking**: Decided to track `fivecircles/agent/skills/` in Git (no cleanup needed).
  3. **QA Context UX (Q7/Q9)**: Implement eventId context passing from Timeline to QA widgets for auto-filtering.
  4. **Playwright Tests**: Run MVP UI verification tests.
- **Status**: Planning complete. Ready to execute.
- **Next**: Start rebase process.

## 2026-01-26: Rebase onto develop Complete
- **Goal**: Successfully rebase 42 commits from `feature/experimental-frontend` onto `origin/develop`.
- **Changes**:
  - **Conflicts Resolved**:
    - `fivecircles/architecture/todolist.md`: Merged Team B Wiki Service enhancements + MVP Experiment tasks
    - `front/App.tsx`: Combined API logout + clearAuth() for proper token cleanup
    - `front/features/auth/LoginPage.tsx`: Merged OAuth2 integration + userApi.getMe() flow
    - `infra/docker-compose.yml`: Combined Google OAuth2 env vars + LLM API keys + TZ settings
    - `fivecircles/agent/mistakes-arrest.md`: Merged Commit/Server Guardrails + Tool Usage Compliance + Incident logs
    - `services/api-gateway/src/main/java/com/nospoiler/apigateway/config/SecurityConfig.java`: Kept structured pathMatchers with permitAll()
  - **Rebase Stats**: 42/42 commits successfully rebased
  - **Branch**: `feature/experimental-frontend` now synced with latest `origin/develop`
- **Status**: Rebase complete. Branch ready for next sprint tasks.
- **Next**: Implement QA Context UX (Q7/Q9) and run Playwright tests.
## Addendum (2026-01-28) - Branch split logging sync
### Docs
- Align todolist sections by team ownership across baseline/proposal; merge update log entries (refs: fivecircles/architecture/todolist.md, fivecircles/work/update.md)
## Addendum (2026-01-28) - Wiki link check + todo sync
### Docs
- Record wiki-character link verified, note pending wiki→event/intelligence checks; sync Team C todo (refs: fivecircles/architecture/todolist.md, fivecircles/work/update.md)

# Update Log

## 2026-01-22: Frontend-Backend Integration (Phase 1)
- **Goal**: Replace mock character data with real API data and enable Event V2 features in Frontend.
- **Changes**:
  - `front/common/services/characterApi.ts`: Created to fetch characters from `character-service`.
  - `DashboardPage.tsx`: Integrated `characterApi` and `eventV2Api` (getDramaCharacters) for real-time character list and spoiler-safe filtering.
  - `CharacterModal.tsx`: Replaced `MOCK_CHARACTERS` with real data passed from parent; enabled V2 tabs (timeline, coevents, etc.).
  - `EventTimelinePage.tsx`: Integrated `characterApi` for name resolution.
  - `WikiPage.tsx` & `WikiReviewPage.tsx`: Integrated `characterApi` for character selection and display.
- **Status**: Completed. Dashboard now reflects real DB state and spoiler policy.
- **Next**: Fix `mockWikiService` filtering logic and proceed to Wiki API integration.

## 2026-01-22: Wiki Integration & User ID Mapping (Phase 2)
- **Goal**: Connect Wiki pages to real `wiki-service` and ensure valid User IDs are used.
- **Changes**:
  - `front/common/services/wikiApi.ts`: Created client for `/api/wiki/v1` (submissions, verifications).
  - `front/common/services/userApi.ts`: Created client for `/api/user/v1` (getMe).
  - `LoginPage.tsx`: Updated to fetch real user profile (`userApi.getMe()`) after login to secure numeric ID.
  - `App.tsx`: Added session restoration logic (`useEffect`) to refresh user profile on reload.
  - `WikiPage.tsx` & `WikiReviewPage.tsx`: Fully replaced `mockWikiApi` with `wikiApi`.
  - `vite.config.ts`: Configured proxy target via `VITE_API_TARGET` env var.
- **Status**: Completed. Wiki submission and review now interact with real backend DB.
- **Next**: Run end-to-end verification on local/remote env.

## 2026-01-23: Ontology V2.5/V3 Preparation
- **Goal**: Align codebase with V3 Triple-Role plan while supporting V2.5 (Q20) requirements.
- **Changes**:
  - `v2.5-def-plan.md`: Updated to include `role` column strategy (V6) for V3 compatibility.
  - `EventServiceImpl.java`: Corrected hardcoded role from `"PARTICIPANT"` to `"INVOLVED"` to match architectural specs.
  - `WikiSubmissionService.java`: (Merged from develop) Integrated structured event publishing (PredicateCode mapping, involved character list).
- **Status**: Documentation updated. Code alignment in progress.
- **Next**: Create V6 Flyway migration for `event_character.role` column.

## 2026-01-23: Rebase & V3 Preparation Complete
- **Goal**: Merge `origin/develop` (Wiki Ontology) into `new-task` and resolve conflicts.
- **Changes**:
  - **Rebase**: Successfully rebased `new-task` onto `origin/develop`.
  - **Conflict Resolution**:
    - `WikiSubmissionMapper`: Merged Ontology logic (develop) with CRUD endpoints (local).
    - `SecurityConfig`: Merged OAuth2 paths (develop) with CORS/Dev settings (local).
    - `todolist.md`: Consolidated Team B/C tasks.
  - **V3 Prep**: Validated `V6__event_v3_triple_roles.sql` and `RoleType` Enum integration.
- **Status**: Ready for feature implementation (Q20) or deployment.

## 2026-01-23: Branch Cleanup & Ops
- **Goal**: Merge pending maintenance branches into `develop` and clean up.
- **Changes**:
  - **Merged to Develop**: `chore/agent-environment`, `docs/ex13-standard-predicates`, `feat/frontend-smoke-test`.
  - **Cleanup**: Deleted local/remote branches for the above.
  - **Ops**: PR #65 created for `feature/experimental-frontend` (V2.5/V3 integration).

## 2026-01-23: Q20 Implementation & Skill Expansion
- **Goal**: Implement Q20 (Narrative Distribution) and formalize deployment protocols.
- **Changes**:
  - **Frontend**:
    - Implemented `EventQAButton` & `EventQADrawer` (Shared Components).
    - Created `Q20_NarrativeDistribution` widget (Chart visualization).
    - Refactored `QaPage.tsx` to include a V2.5 Playground.
  - **Docs**: Consolidated `frontend-qa-plan` into `v2.5-def-plan.md`.
  - **Skills**: Added `protocol_deploy.md` (Vercel).
- **Status**: V2.5 MVP features implemented on `feature/experimental-frontend`.

## 2026-01-23: Expanded QA Widgets & Build Verification
- **Goal**: Implement Q1, Q2, Q13 widgets and verify code integrity via build.
- **Changes**:
  - **Frontend Widgets**: Created `Q1_CharacterTrace`, `Q2_EventSearch`, `Q13_SpoilerCheck`.
  - **Integration**: Mapped all 4 widgets (including Q20) in `EventQADrawer` with contextual filtering.
  - **Test**: Verified `npm run build` success in the local environment.
  - **Cleanup**: Removed redundant `agent/operational-guidance.md`.
- **Status**: Core V2.5 components ready for runtime testing.

## Addendum (2026-01-24) - QA routing + widgets
### Frontend
- Added Q3/Q5/Q7/Q9/Q11 widgets and drawer mapping (refs: front/features/event/components/EventQADrawer.tsx)
- Added widget components and getEventById client (refs: front/common/services/eventV2Api.ts)
### Backend
- Routed /qa/** to qa-service in gateway configs (refs: services/api-gateway/src/main/resources/application.yml)
- Aligned qa-service base path in api-contract (refs: fivecircles/architecture/specs/api-contract.md)
### Tests
- Frontend build passed (refs: front/package.json)

## Addendum (2026-01-28) - Playwright server check (console)
### Frontend
- Updated Playwright flow to use `domcontentloaded` and fail on console errors (refs: front/check_console.spec.js)
### Tests
- Server browser test passed against http://100.120.44.64:3000 (refs: front/check_console.spec.js)
## Addendum (2026-01-28) - Widget commonization + Playwright output
### Frontend
- Moved event QA widgets to front/common and updated imports (refs: front/common/widgets, front/features/event/components/EventQADrawer.tsx)

### Tests
- Set Playwright outputDir to fivecircles/test/test-results (refs: playwright.config.cjs)
## Addendum (2026-01-28) - Widget QA placement + Playwright runner fix
### Frontend
- Aligned QA widget imports after common move and documented QA drawer entry points (refs: front/common/widgets/Q1_CharacterTrace.tsx, front/common/widgets/Q2_EventSearch.tsx, front/common/widgets/Q13_SpoilerCheck.tsx, front/common/widgets/Q20_NarrativeDistribution.tsx, fivecircles/architecture/specs/frontend.md)

### Tests
- Playwright flow passed when run from front runner (refs: front/check_console.spec.js, playwright.config.cjs, fivecircles/test/errorlogs/frontend/2026-01-28-playwright-runner-mismatch.md)
## Addendum (2026-01-28) - Dashboard QA entry points
### Frontend
- Added QA drawer entry points on dashboard header and character modal (refs: front/features/dashboard/DashboardPage.tsx, front/features/dashboard/components/CharacterModal.tsx)

### Docs
- Noted dashboard QA entry points in frontend spec (refs: fivecircles/architecture/specs/frontend.md)

### Tests
- Playwright console check passed (refs: front/check_console.spec.js)
## Addendum (2026-01-28) - Plenty seed data + dashboard test
### Backend
- Seeded new drama+character+event data via API and added event_relation links on server (dramaId=7, eventIds=1005-1009)
- Verified wiki approval publishes event (submissionId=4 -> eventId=1010)

### Tests
- Playwright dashboard check passed for new drama (refs: front/check_console.spec.js)
## Addendum (2026-01-28) - Wiki/timeline Playwright validation
### Frontend
- Wiki submit/review now use selected dramaId and dynamic character fetch (refs: front/features/wiki/WikiPage.tsx, front/features/wiki/WikiReviewPage.tsx, front/features/wiki/components/WikiCharacterSelectModal.tsx)

### Tests
- Server Playwright wiki+timeline flows passed for seeded drama (refs: front/wiki_flow.spec.js, front/timeline_relations.spec.js)
## Addendum (2026-01-28) - Auth signup smoke
### Backend
- Repaired auth flyway history + created refresh_tokens table (refs: fivecircles/test/errorlogs/backend/2026-01-28-auth-flyway-checksum-mismatch.md)
### Tests
- Signup/login/me verified via gateway for 6@6.com (refs: fivecircles/test/errorlogs/backend/2026-01-28-auth-email-send-failure.md)
## Addendum (2026-01-28) - Frontend console check
### Tests
- Server Playwright console check passed (refs: front/check_console.spec.js)
## Addendum (2026-01-29) - QA widget Playwright
### Tests
- Server Playwright console + QA widget flows passed (refs: front/check_console.spec.js, front/qa_widgets.spec.js)
## Addendum (2026-01-29) - Intelligence prompt + wiki approvals (drama 8)
### Backend
- Added combine summaries prompt for intelligence service and redeployed (refs: services/intelligence-service/src/main/resources/prompts/combine-summaries.txt)
- Repaired auth DB schema (nospoiler_auth) so login works on server
### Tests
- Character summary endpoint returns 200 (refs: /api/intelligence/v1/summary)
- Scripted 5-vote approvals for dramaId=8 submissions so dashboard summaries render (refs: fivecircles/work/scripts/approve_drama8.py)
## Addendum (2026-01-29) - Dashboard summary sources
### Frontend
- Combine approved wiki + event summaries for CharacterModal AI summary (refs: front/features/dashboard/components/CharacterModal.tsx)
## Addendum (2026-01-30) - Relation PK + spec sync
### Backend
- Add V7 migration to allow event_relation PK with type (refs: services/event-service/src/main/resources/db/migration/V7__event_relation_pk_with_type.sql)
### Docs
- Sync migration compendium + FK meeting note (refs: fivecircles/architecture/specs/latest.sql, fivecircles/architecture/specs/latest-db-migrations.md, fivecircles/architecture/specs/no-fk-meeting-note.md)
- Update V2/V2.5 + intelligence specs (/summary, relation type) (refs: fivecircles/architecture/specs/v2.5-unify.md, fivecircles/architecture/specs/event-v2-definition.md, fivecircles/architecture/specs/event-v2-plan-map.md, fivecircles/architecture/specs/notion-origin-intelligence-v1.md, fivecircles/architecture/specs/notion-origin-intelligence-v1-ko.md)
## Addendum (2026-02-04) - QA consistency fixes
### Backend
- QA policy check uses episode_end (fallback start); event_character insert allows null role default (refs: services/qa-service/src/main/java/com/nospoiler/qaservice/service/QaService.java, services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml)
### Infra
- Gateway adds /api/event & /api/policy routes and permits QA health (refs: services/api-gateway/src/main/resources/application.yml, services/api-gateway/src/main/java/com/nospoiler/apigateway/config/SecurityConfig.java)
- QA docker env wires Event/Policy URLs (refs: infra/docker-compose.yml)
### Frontend
- QaPage uses profileImageUrl for character thumbnails (refs: front/features/qa/QaPage.tsx)
## Addendum (2026-02-04) - Relation policy update
### Backend
- Related events now derived by shared characters; PRECEDES-only traversal enforced (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java)
- Related endpoint signature updated to safeUpToEpisode/limit (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
- Add PRECEDES manual insert API + cross-episode suggestion API (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventRelationController.java, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventRelationService.java)
### Tests
- `./gradlew :services:event-service:test` (refs: services/event-service/src/test/java/com/nospoiler/eventservice/service/EventServiceImplTest.java)
### Docs
- Remove RELATED relation type and redefine related as derived rule (refs: fivecircles/architecture/specs/event-v2-definition.md, fivecircles/architecture/specs/v2.5-unify.md, fivecircles/architecture/specs/event-v2-api.md)
## Addendum (2026-02-04) - bit-ts deploy + Event V2 API smoke
### Server
- Deployed feature/qa-tasks on bit-ts with docker compose build (refs: infra/docker-compose.yml)
### Tests
- Event V2 API smoke on bit-ts (Breaking Bad, Jesse, K=7) with PRECEDES create + suggestions (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java, services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventRelationController.java)
### Tests (Detail)
## Addendum (2026-02-04) - PRECEDES UI Enhancement & Bulk Approval
### Frontend
- **Searchable Drama Selection**: Implemented a searchable dropdown in `AdminPrecedesPage.tsx`. Fetches dramas from `dramaApi` and filters by title/ID.
- **Bulk Approval**: Added "전체 승인" (Bulk Approve) button. Sequentially approves all currently filtered suggestions.
- **UI Improvements**: Refactored table layout for better readability (break-words), added status indicators, and updated filtering logic to include both from/to summaries.
- **Port Enforcement**: Configured `vite.config.ts` to strictly use port 3000 (`strictPort: true`).

### Backend
- **suggestions/all API**: Verified and used new endpoint `/api/event/v2/relations/precedes/suggestions/all` which includes `fromSummary`.
- **Deployment**: Successfully rebuilt and restarted `event-service` on `bit-ts` to apply new PRECEDES logic.

### Tests
- **Verification**: Manually verified drama fetching, searchable filtering, individual approval, and bulk approval on local dev server.
- **Remote Verification**: Confirmed API connectivity to `bit-ts` via gateway.

## Addendum (2026-02-04) - PRECEDES Pagination & Fixes
### Frontend
- **Pagination**: Implemented client-side pagination for PRECEDES suggestions (1000 items loaded, 50 items/page view).
- **UI Tweaks**: Added "Items per page" display to pagination controls.
- **Fixes**: Resolved state duplication and TypeErrors in `AdminPrecedesPage.tsx`.

### Backend
- **Fix**: Resolved `SAXParseException` (extra `</select>`) in `EventRelationMapper.xml` which caused 500 error on startup.
- **Deployment**: Redeployed `event-service` to `bit-ts` after fix.

## Addendum (2026-02-04) - Event-service 주석 보강
### Backend
- 이벤트 서비스 전반에 Javadoc/inline 주석 보강 (refs: services/event-service/src/main/java/com/nospoiler/eventservice)

## 2026-02-05: MinIO Refactoring & Multi-Bucket Management
- **Goal**: Centralize MinIO logic into `common` module and implement service-specific bucket management.
- **Changes**:
  - **Common Module**:
    - Created `StorageService` interface and `MinioStorageService` implementation in `com.nospoiler.common.storage`.
    - Added `minio` dependency to `common/build.gradle`.
    - Centralized `MinioConfig` for shared reuse across services.
    - Improved `upload` method to support hierarchical directory structures.
    - Improved `delete` method to handle URLs with subdirectories correctly.
  - **Infrastructure**:
    - Refactored `docker-compose.yml` to initialize three separate buckets: `profile-images`, `drama-images`, and `character-images`.
    - Configured each service (`user-service`, `drama-service`, `character-service`) to use its own dedicated bucket via environment variables.
    - Ensured backward compatibility for existing profile images by preserving the `profile-images` bucket.
  - **Service Layer**:
    - Updated `UserService`, `DramaServiceImpl`, and `CharacterServiceImpl` to use the common `StorageService`.
    - Removed redundant MinIO implementations from individual services.
- **Status**: Backend refactoring complete. Multi-bucket storage is active.
- **Next**: Verify actual file uploads from the Admin UI (Drama/Character) and My Page (User).
## Addendum (2026-02-06) - ex14 TRANSFORMS 정합 + 원격 DB 백필
### Frontend
- Q20 집계에서 `STATUS_CHANGE`를 `TRANSFORMS`로 정규화/합산 처리 (refs: front/common/widgets/Q20_NarrativeDistribution.tsx)
- 타임라인 빠른 필터 칩을 표준 predicate로 교체 (refs: front/features/timeline/EventTimelinePage.tsx)
### Backend
- `PredicateCode` 표준명 `TRANSFORMS` 추가, `STATUS_CHANGE`는 레거시(deprecated) 유지 (refs: common/src/main/java/com/nospoiler/common/PredicateCode.java)
- event-service 호환 레이어: 저장 시 `STATUS_CHANGE` -> `TRANSFORMS` 정규화, 조회 시 `TRANSFORMS`는 `STATUS_CHANGE`도 포함 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java, services/event-service/src/main/resources/mapper/event/EventMapper.xml)
- Search policy: user-facing predicateCode 필터에서 `OTHER|UNKNOWN`은 필터 미적용으로 처리 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java, services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java)
- predicate suggestion(SoT=event) 저장 경로 및 마이그레이션 추가 (refs: services/event-service/src/main/resources/db/migration/V8__add_event_predicate_suggestion.sql, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventRequestDTO.java, services/event-service/src/main/java/com/nospoiler/eventservice/entity/Event.java, services/wiki-service/src/main/java/com/nospoiler/wikiservice/service/WikiSubmissionService.java)
### Server
- bit-ts DB 백필: event/wiki `predicate_code`의 `STATUS_CHANGE` -> `TRANSFORMS` 일괄 변경 (nospoiler_event/nospoiler_wiki)
### Docs
- ex14 정합성 체크리스트/변경계획 정리 (refs: fivecircles/architecture/specs/ex14-consistency-checklist.md)
- suggestion 운영(SoT=event, 승인 시 snapshot) 계획 수립 (refs: fivecircles/architecture/specs/predicate/suggestion-sot-event.md)
- Q6/Q7 문서 정합: enum 밖 코드(AFFILIATION_CHANGE/DEATH/EXIT) 대신 JOINS/LEAVES/DIES 조합으로 정의 (refs: fivecircles/architecture/specs/frontend.md, fivecircles/architecture/specs/v2.5-unify.md)
- Event V2 API 문서에 OTHER/UNKNOWN filter 정책 명시 (refs: fivecircles/architecture/specs/event-v2-api.md)
### Tests
- Local build OK: `./gradlew :common:build`, `front npm run build`

## Addendum (2026-02-06) - Related-characters aggregate + predicate query layer docs
### Backend
- Add `GET /api/event/v2/characters/{characterId}/related-characters/aggregate` (refs: services/event-service/src/main/java/com/nospoiler/eventservice/controller/EventQueryController.java)
- Add aggregate scoring + evidence option (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java)
- Add MyBatis aggregate/evidence queries (refs: services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml)
### Docs
- Add predicate docs folder (group/promotion/reveals/quality/aggregate spec) (refs: fivecircles/architecture/specs/predicate/README.md)
- Add aggregate endpoint to specs: V2/V2.5/api-contract (refs: fivecircles/architecture/specs/event-v2-api.md, fivecircles/architecture/specs/v2.5-unify.md, fivecircles/architecture/specs/api-contract.md)
### Tests
- Local unit/compile OK: `./gradlew :services:event-service:test`

## Addendum (2026-02-06) - Squid Game bulk ingestion dataset copies
### Backend
- Add Squid Game per-episode datasets under wiki-service test resources for ingestion (refs: services/wiki-service/src/test/resources/squid_game_dataset_ep1.json, ingestion/scripts/build_squid_game_bulk_dataset.py)

## Addendum (2026-02-09) - Event reveal N+1 제거 + updateEvent 안전화
### Backend
- Event reveal N+1 제거: revealMap 배치 조회(`IN`) 추가 (refs: services/event-service/src/main/resources/mapper/event/EventRevealMapper.xml)
- updateEvent: summary-only PUT에서 episodes null 덮어쓰기 방지 (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service)
### Tests
- PASS: `./gradlew :services:event-service:test` (refs: services/event-service/src/test/java/com/nospoiler/eventservice/service)
### Server
- bit-ts 배포 + gateway curl 스모크 200 OK (drama events/character events/aggregate) (refs: fivecircles/test/deploy-server.sh, fivecircles/architecture/specs/test-server-policy-4C.md)

## Addendum (2026-02-09) - Admin PRECEDES 리팩터 + bit-ts 배포 스모크
### Frontend
- PRECEDES Admin 페이지 탭 분리 + 훅 분리로 상태/전이 복잡도 축소 (refs: front/features/admin/AdminPrecedesPage.tsx, front/features/admin/precedes/PrecedesQueueTab.tsx, front/features/admin/precedes/PrecedesManualTab.tsx, front/features/admin/precedes/usePrecedesRows.ts, front/features/admin/precedes/useInlineEventSummaryEdit.ts)
- apiClient: query param에 boolean 허용 (refs: front/common/services/apiClient.ts)
### Server
- bit-ts 배포: branch `feature/admin-event-edit`, commit `d361901` (refs: fivecircles/test/deploy-server.sh)
- 스모크(서버 내부): `GET http://localhost:3000` 200, `GET http://localhost:8080/api/drama/v1/health` 200, `GET http://localhost:8080/api/event/v1/health` 200, aggregate 200 + `scoreRule` 확인

## Addendum (2026-02-09) - PRECEDES suggestion 랭킹 강화(액션 가중치) + OTHER suggestion 노출
### Backend
- PRECEDES suggestions: predicate 기반 가중치로 정렬(액션/전환점 boost, OTHER 약한 패널티) (refs: services/event-service/src/main/java/com/nospoiler/eventservice/service/EventRelationService.java)
- PRECEDES suggestion 응답에 from/to predicateCode(+predicateSuggestion) 및 sourceType/sourceId 포함 (refs: services/event-service/src/main/resources/mapper/event/EventMapper.xml, services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventRelationSuggestionResponse.java)
### Tests
- PASS: `./gradlew :services:event-service:test`, `front npm run build`
### Server
- bit-ts 배포 후 `/api/event/v2/relations/precedes/suggestions/all` 200 + 확장 필드 확인, health 200 (Playwright `health_services.spec.js`)

## Addendum (2026-02-09) - Predicate suggestion 코드북 + NEW 후보 등록(운영 확장용)
### Common
- predicateSuggestion 코드북 토큰 whitelist + `TOKEN|한국어` 파싱 유틸 추가 (refs: common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java)
### Intelligence
- OTHER일 때 `TOKEN|한국어` 형식으로 제안(코드북 우선), 코드북에 없으면 `NEW|...`로 후보 등록 유도 (refs: services/intelligence-service/src/main/resources/prompts/refine-fact.txt)
### Wiki-service
- publish 시 predicateSuggestion은 코드북 토큰만 event-service로 전달(그 외는 drop) (refs: services/wiki-service/src/main/java/com/nospoiler/wikiservice/service/WikiSubmissionService.java)
- `NEW|...` 또는 invalid 토큰은 후보 테이블에 적재하여 코드북 확장 backlog로 관리 (refs: services/wiki-service/src/main/resources/db/migration/V7__add_predicate_suggestion_candidates.sql, services/wiki-service/src/main/resources/mapper/wiki/WikiSubmissionMapper.xml)
### Docs
- predicate suggestion 후보 레지스트리 설계 정리: event를 단일 소스로 두고(hit count upsert), wiki는 필요 시 pre-approval 관측용으로만 사용(옵션) (refs: fivecircles/architecture/specs/predicate/README.md, fivecircles/architecture/specs/predicate/suggestion-sot-event.md, fivecircles/architecture/specs/predicate/promotion-process.md)
### Data (bit-ts)
- dramaId=10 백필(데이터 보강): APPROVED + `predicate_code=OTHER` 이벤트 중 `predicate_suggestion`이 비어있는 71건에 대해, WIKI submission의 `predicate_suggestion`을 `NEW|...`로 event에 채움 (PRECEDES suggestion 화면에서 OTHER 컨텍스트 노출 개선). (refs: scripts/ops/backfill_predicate_suggestion_drama10.sql)
- 운영/런타임에서 raw predicateSuggestion을 event-service로 전달하는 변경은 팀 협의사항으로 보류.
### Tests / Safety
- DB에 실제로 붙는 E2E 테스트는 기본 `test`에서 실행되지 않도록 게이트(`-DrunIntegrationTests=true`) 추가 (refs: services/wiki-service/src/test/java/com/nospoiler/wikiservice/service/WikiSubmissionServiceIntegrationTest.java)
### Server
- bit-ts 배포: branch `feature/admin-event-edit`, commit `09db73c` (refs: fivecircles/test/deploy-server.sh)
- curl 스모크 200 OK: `GET http://localhost:3000`, `GET http://localhost:8080/api/event/v1/health`, aggregate, precedes suggestions (gateway)
