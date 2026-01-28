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
- Server curl checks for new endpoints (refs: http://localhost:8089/dramas/1/events?safeUpToEpisode=1&predicateCode=STATUS_CHANGE)
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
