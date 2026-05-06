---
name: 릴레이샷
description: 릴레이샷, relay-shot, relay shot, 원샷딜 마지막 릴레이, push-after-test relay without time limit. Use after doc-write, implementation, test, and push to inspect remaining TODOs and immediately launch the next implementable task through $one-shot-delivery-orchestrator.
---

# 릴레이샷

This is the default time-unlimited relay skill for one-shot delivery.

Use it at the end of the one-shot delivery flow after push/publication handling when the user asked to keep going, continue, finish remaining TODOs, or run in one-go.

Use `$스케줄릴레이샷` instead when the user provided a work-until time, stop time, deadline, or session end time.

## Invocation aliases

Use this skill when the user says or implies:

- 릴레이샷
- relay-shot
- relay shot
- 계속 릴레이
- 시간제한 없는 릴레이
- 원샷딜 마지막 릴레이
- 테스트/푸시 끝나고 남은 TODO 계속

## Core Rule

At the end of the current one-shot cycle:

1. Confirm documentation, implementation, validation, and push/publication phases reached terminal states.
2. Inspect remaining TODOs, logs, plans, issue notes, failing tests, and unfinished acceptance criteria.
3. Select the highest-value concrete task that can be safely started now.
4. Invoke or follow `$one-shot-delivery-orchestrator` for the selected task.
5. Continue through the full flow again: doc-write, implementation, test, push, relay.

## Stop Conditions

Stop instead of launching the next cycle when:

- no valuable remaining TODO exists
- the next task is ambiguous or outside the requested scope
- the next task is unsafe to start without user input
- the previous push/publication phase is `BLOCKED`
- the user asked to stop
- a time limit exists, in which case hand off to `$스케줄릴레이샷`

## Remaining Work Sources

Inspect the most relevant available sources:

- `todolist.md`
- `TODO.md`
- `fivecircles/architecture/todolist.md`
- `fivecircles/work/`
- `fivecircles/test/errorlogs/`
- `fivecircles/requirements/`
- `fivecircles/architecture/specs/`
- issue or PR notes
- current conversation acceptance criteria

## Output Contract

Report:

- previous phase statuses
- TODO source inspected
- selected next task, if any
- whether another one-shot cycle was launched
- outcome or stop reason
