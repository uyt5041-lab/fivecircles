# Agent Operational Guidance (Non-Authoritative)

These notes are for agent execution only and do not override product specs.

1. Define a clear internal rubric for the best possible outcome before starting a task.
2. Verify the result rigorously against that rubric.
3. If the result fails the rubric, discard it and restart until it passes.
4. Operate autonomously and use independent judgment while respecting specs.
5. When information is uncertain, make a reasonable assumption and continue.
6. Avoid unnecessary intermediate confirmations unless required.
7. Be innovative as long as core requirements are satisfied.
8. Promote repeatable error learnings into specs when cost-effective; record runtime-only lessons in `fivecircles/test/learn-from-log.md`.

10. **Reasoning & Verification Workflow**
    - Follow this flow for complex problems:
        1. **DECOMPOSE**: Break into smaller sub-problems.
        2. **SOLVE**: Address each with explicit confidence (0.0-1.0).
        3. **VERIFY**: Check logic, facts, completeness, and bias from multiple perspectives.
        4. **SYNTHESIZE**: Combine using weighted confidence.
        5. **REFLECT**: If confidence < 0.8, identify weaknesses and retry.
    - Only commit changes when confidence is high.
    - **Output Standard**: Always provide a clear answer, the confidence level, and key caveats.
