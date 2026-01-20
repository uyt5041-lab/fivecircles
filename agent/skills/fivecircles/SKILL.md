---
name: fivecircles
description: Run the fivecircles project workflow for this repo. Use when the user says "fivecircles", "run fivecircles", "skill fivecircles", or asks to start or activate the fivecircles process.
---

# Fivecircles workflow

- Read `fivecircles/specs/README.md` first; treat it as the authority index and process contract.
- Read `fivecircles/agent-guidelines.md` next for agent-only operational guidance.
- Follow the authority order from `fivecircles/specs/README.md`; resolve conflicts by higher priority.
- Keep context lean: open only the specific spec files needed for the current task.
- Use the development cycle and policies defined in specs (requirements -> architecture -> work -> test -> maintenance); update `architecture/todolist.md`, `work/` logs, `test/errorlogs/`, and `scoring/log-score.md` as required.
- Use `rg -n "keyword" fivecircles/specs` to locate authoritative details quickly.
