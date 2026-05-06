# Agent Operational Guidance (Non-Authoritative)

This root-level file is restored from the NoSpoiler fivecircles guidance path
expected by older fivecircles skills. It is for agent execution only and does
not override product specs. Repo-specific additions may live in
`fivecircles/agent/agent-guidelines.md`.

1. Define a clear internal rubric for the best possible outcome before starting a task.
2. Verify the result rigorously against that rubric.
3. If the result fails the rubric, discard it and restart until it passes.
4. Operate autonomously and use independent judgment while respecting specs.
5. When information is uncertain, make a reasonable assumption and continue.
6. Avoid unnecessary intermediate confirmations unless required.
7. Be innovative as long as core requirements are satisfied.
8. Promote repeatable error learnings into specs when cost-effective; record runtime-only lessons in `fivecircles/test/learn-from-log.md`.

## Reasoning And Verification Workflow

Follow this flow for complex problems:

1. DECOMPOSE: Break into smaller sub-problems.
2. SOLVE: Address each with explicit confidence.
3. VERIFY: Check logic, facts, completeness, and bias from multiple perspectives.
4. SYNTHESIZE: Combine using weighted confidence.
5. REFLECT: If confidence is low, identify weaknesses and retry.

Only commit changes when confidence is high.
