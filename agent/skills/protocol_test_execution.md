# Skill: Protocol for Test Execution

## Purpose
Standardize the testing workflow for Frontend and Backend services, ensuring compliance with Team C's policies.

## Usage
Execute this protocol when verifying features, running regression tests, or preparing for deployment.

## Protocol Steps

1.  **Identify Test Scope**
    - Determine if the task involves Frontend, Backend, or End-to-End integration.

2.  **Read Policy Documents**
    - **Frontend**: Read `fivecircles/architecture/specs/test-front-policy-4c.md`.
        - Check for: Playwright setup, Mock vs Real API mode, Local vs Remote targets.
    - **Backend**: Read `fivecircles/architecture/specs/test-server-policy-4C.md`.
        - Check for: `./gradlew test` commands, Docker environment (`bit-ts`), Port configurations.

3.  **Execute Tests**
    - Follow the exact commands listed in the policy files.
    - **Do NOT** invent new test commands (e.g., `npm test` vs `npx playwright test`) without verifying the policy first.
    - For Remote Tests (`bit-ts`): Ensure SSH access and Docker state before running.

4.  **Log Results**
    - **Success**: Update `todolist.md` or `update.md`.
    - **Failure**: 
        - Create a log in `fivecircles/test/errorlogs/`.
        - Create a `learn-from-log.md` entry if it's a recurring or structural issue.
