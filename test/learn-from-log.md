# Learn From Logs

This document records insights gained from errors to prevent recurrence.

## [2026-01-15] VS Code Task Automation for Interactive CLIs
- **Interactive Shell is Key**: When running tasks that depend on `.zshrc` (aliases, functions, PATH), always use `"shell": { "executable": "/bin/zsh", "args": ["-l", "-i", "-c"] }`.
- **Silent Background Tasks**: To prevent the infinite loading spinner on long-running/interactive tasks:
    1. Set `"isBackground": true`.
    2. Provide a `problemMatcher` with `background` patterns.
    3. Ensure the command produces *some* output at startup (e.g., using `echo`) to trigger the pattern matcher.
- **Group vs Independent**: Using `"group": "..."` in presentation settings will split the terminal pane (Tmux-style). To open in new tabs, omit the `group` property or use unique ones.
- **CLI task invocation**: `code --run-task` is not a standard CLI feature for external terminals; prefer IDE-native keybindings or internal task runner.

## [2026-01-16] Docker build failed due to missing common module
- **Root cause**: Service Dockerfile built an isolated Gradle project without including `:common`, so Gradle could not resolve the module.
- **Prevention**: Standardize Dockerfiles to copy `common/` and add `include 'common'` + `include 'services:<name>'` before running `bootJar`. (refs: fivecircles/test/errorlogs/backend/2026-01-16-spoiler-policy-common-missing.md)

## [2026-01-16] QA docker build failed due to missing Lombok
- **Root cause**: `qa-service` used Lombok annotations without Lombok dependencies in Gradle.
- **Prevention**: Add Lombok `compileOnly` + `annotationProcessor` for services using Lombok. (refs: fivecircles/test/errorlogs/backend/2026-01-16-qa-lombok-missing.md)

## [2026-01-16] QA port mapping mismatch
- **Root cause**: App listened on 8091 while compose mapped `8091:8080`, causing connection resets.
- **Prevention**: Align app port, Dockerfile `EXPOSE`, and compose port mapping. (refs: fivecircles/test/errorlogs/backend/2026-01-16-qa-port-mismatch.md)

## [2026-01-16] MySQL port conflict on bit-ts
- **Root cause**: Host 3306 already bound; compose could not publish MySQL.
- **Prevention**: Use `DB_PORT=3307` for C-only runs and document the default. (refs: fivecircles/test/errorlogs/backend/2026-01-16-mysql-port-conflict.md)
### Mockito unnecessary stubbing in event-service tests
Cause:
- policyServiceClient stubs were added for tests where uptoEpisode was null

Preventive rule:
- Only stub methods exercised in the test path or use lenient() for optional calls
### Spoiler policy port mismatch in docker-compose
Cause:
- compose mapped 8090:8080 while app listens on 8090

Preventive rule:
- Align compose ports with app server.port or add application-docker.yml
### MySQL volume skips init.sql
Cause:
- Existing mysql volume prevents init.sql from creating nospoiler_event/nospoiler_wiki

Preventive rule:
- Ensure DBs exist before service start or recreate mysql volume
### Flyway history table collision risk
Cause:
- Multiple services share flyway_schema_history in one DB

Preventive rule:
- Set SPRING_FLYWAY_TABLE per service and keep default in application.yml (refs: fivecircles/test/errorlogs/backend/2026-01-20-flyway-history-collision-risk.md)
### Exposure queries missing source_status gate
Cause:
- Event exposure queries did not filter APPROVED only

Preventive rule:
- Apply source_status='APPROVED' + episode_end<=K to all exposure queries and join event for character lists (refs: fivecircles/test/errorlogs/backend/2026-01-20-source-status-gate-missing.md)
### Traversal must expand safe graph
Cause:
- BFS expansion happened without K/APPROVED gating

Preventive rule:
- Join event in relation queries and apply K + APPROVED during traversal (refs: fivecircles/test/errorlogs/backend/2026-01-20-bfs-safe-graph-missing.md)
### PRECEDES direction ambiguity
Cause:
- from/to semantics not fixed, making reverse traversal unclear

Preventive rule:
- Define PRECEDES as from=previous, to=next and use to_event_id for reverse traversal (refs: fivecircles/test/errorlogs/backend/2026-01-20-precedes-direction-ambiguous.md)
### Character-event reverse index missing
Cause:
- event_character lacked character_id->event_id index for timeline queries

Preventive rule:
- Add idx_ec_character_event (character_id, event_id) migration (refs: fivecircles/test/errorlogs/backend/2026-01-20-character-event-index-missing.md)
### V2 event_character insert should not include role
Cause:
- V2 schema lacks event_character.role but mapper attempted role insert

Preventive rule:
- Use role-less insert in V2; add role only after V3 migration (refs: fivecircles/test/errorlogs/backend/2026-01-20-v3-role-column-missing.md)
### MCP tools not exposed in Codex session
Cause:
- MCP collab flag off and local MCP template drifted from ~/.codex/config.toml

Preventive rule:
- Enable collab before session start; keep .mcp.json mirrored; verify .mcp-env.sh is sourced
### Playwright strict mode with duplicate labels
Cause:
- getByText("타임라인") matched both nav and modal tab during dashboard checks

Preventive rule:
- Scope Playwright locators to the modal/section container when labels repeat (refs: fivecircles/test/errorlogs/frontend/2026-01-22-playwright-strict-mode.md)
### Playwright timeline list assertion before data load
Cause:
- Timeline list asserted before /api/event/v2 response completed

Preventive rule:
- Wait for API response and list render before counting items (refs: fivecircles/test/errorlogs/frontend/2026-01-22-playwright-timeline-wait.md)
