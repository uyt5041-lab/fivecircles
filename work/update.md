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
