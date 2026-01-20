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
