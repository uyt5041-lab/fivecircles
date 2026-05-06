# Fivecircles - Specification Index

This folder contains technical analysis and implementation contracts derived
from confirmed requirements. Operational guidance belongs in `fivecircles/agent/`;
this folder is for product, API, data, architecture, security, performance, and
workflow contracts.

## Boot Order

- Read `fivecircles/agent-guidelines.md` for root compatibility guidance.
- Read `fivecircles/agent/README.md` and `fivecircles/agent/agent-guidelines.md`.
- Read the relevant local skill under `fivecircles/agent/skills/` before execution.
- Use this README to locate the authoritative technical contract for the task.

## Authority Order

If documents conflict, prefer the higher-priority source.

0. Latest explicit user instruction in the current thread.
1. `fivecircles/requirements/decisions.md`
2. `fivecircles/requirements/current.md`
3. Feature requirement docs under `fivecircles/requirements/`
4. This specification index and the relevant files under `fivecircles/architecture/specs/`
5. `fivecircles/architecture/todolist.md`
6. `fivecircles/work/worklog.md` and `fivecircles/work/update.md`
7. Runtime evidence from tests, API responses, browser checks, and database readback.

Confirmed requirements outrank implementation notes. Runtime evidence can prove
that an implementation is broken, but it does not change requirements by itself.

## Spec Inventory

- `agent-orchestrator.md`: active agent roles and session management.
- `buisiness-workflow.md`: workflow by requirements and analysis.
- `implementation-rules.md`: implementation rules.
- `git.md`: git workflow.
- `data-model.md`: entity meaning and field semantics.
- `api-contract.md`: REST endpoints and request/response DTOs.
- `docker.md`: Docker specs.
- `frontend.md`: frontend specs.
- `evaluatenvolve.md`: evolution structure and economy.

## Language Policy

- Technical contracts should be clear enough for implementation without chat context.
- English file names are preferred for stable references.
- Korean notes are allowed when they preserve user intent or domain nuance.

## Agent Constraint

- Do not modify requirements, specs, policy files, or `architecture/todolist.md`
  unless the user asks for planning/docs work or the current task requires
  those updates.
- Do not place agent behavior rules in spec files; put them under
  `fivecircles/agent/`.
- Do not create parallel spec folders unless the user explicitly asks.

## Work Folder Policy

- Planning tasks are tracked in `fivecircles/architecture/todolist.md`.
- Implementation logs and closeout notes are recorded under `fivecircles/work/`.
- Runtime failures and regression learnings are recorded under `fivecircles/test/`.
- Work logs must align with confirmed requirements and relevant spec contracts.

## Development Cycle

1. Requirements: clarify or confirm under `fivecircles/requirements/`.
2. Design: update relevant files under `fivecircles/architecture/specs/`.
3. Planning: decompose into batches in `fivecircles/architecture/todolist.md`.
4. Implementation: change code in the smallest safe slice.
5. Test: run targeted tests, smoke checks, and browser/Playwright checks when relevant.
6. Integrate: record results in `fivecircles/work/` and update TODO status.
7. Maintenance: feed repeated failures into specs or `test/learn-from-log.md`.

## Requirements Governance

- New requests start with requirements analysis unless they are direct fixes.
- Confirmed decisions are recorded in `fivecircles/requirements/decisions.md`.
- Based on confirmed rules, tasks are extracted into `architecture/todolist.md`.
- After implementation, tests and error logs must update the todo state.
- Repeated failures should become either spec constraints or learn-from-log entries.

## Runtime Stack Policy

- Follow the runtime stack documented in the relevant specs.
- Keep gateway/service/runtime choices explicit in the spec that owns them.
- Browser automation should use Playwright when repeatable UI evidence is needed.

## Test Policy

- Test policy is defined in `fivecircles/test/testpolicy.md`.
- Runtime lessons are recorded in `fivecircles/test/learn-from-log.md` when present.
- For browser behavior, prefer repeatable browser evidence over chat-only claims.

## Agent Scoring

- Use scoring only when the active workflow asks for it.
- Record scoring under `fivecircles/scoring/` when applicable.
- Optimize for correct, verified, logged work with the fewest avoidable retries.
