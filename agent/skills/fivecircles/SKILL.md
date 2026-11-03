---
name: fivecircles
description: Run the fivecircles project workflow for this repo. Use when the user says "fivecircles", "run fivecircles", "skill fivecircles", or asks to start or activate the fivecircles process.
---

# Fivecircles workflow

- Resolve the framework root: use `fivecircles/` when its README exists; otherwise use the repository root when it contains this template README and `agent/workflow.md`. Read that root README as the inventory pointer.
- Under the verified framework root, read `agent/README.md`, `agent/agent-guidelines.md`, `agent/authority.md`, `agent/workflow.md` and `agent/policies.md`. Read root `agent-guidelines.md` and `agent/operational-guidance.md` only if present.
- Check `agent/skills/` under that root and load the matching local skill.
- Follow the authority order from `agent/authority.md` under the verified framework root; resolve conflicts by higher priority.
- Keep context lean: open only the specific spec files needed for the current task.
- Design/contract work must satisfy doc-contract-writer's [mandatory risk-scoped EGM policy](../doc-contract-writer/references/egm-design-review.md): FULL for contract/permission/data changes, TARGETED related stages for proven small changes, and valid receipt reuse. Record risk and required scope separately from execution/reuse; no implicit EGM skip or repeated unaffected review. Keep engineering/security impact checks. Resolve the installed sibling policy if absent locally. Editing a skill alone does not start an implementation relay.
- Use the development cycle and policies defined in `agent/workflow.md` under that same root; update `architecture/todolist.md`, `work/` logs, `test/errorlogs/`, and `scoring/log-score.md` as required.
- Locate the actual spec directory from the current README/inventory and verify it exists before searching. Do not assume `spec` versus `specs`; if neither exists, use current requirements and the architecture TODO, then place any needed task document in an existing approved directory.
