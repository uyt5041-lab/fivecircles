# Skill: Protocol for Task Completion (Ultra Record)

## Purpose
A high-level integrated protocol to definitively conclude a task. It enforces quality by requiring test success before logging and scoring.

## Usage
Execute this protocol when you believe a task is done.
Command: "Initiate ultra record" or "울트라 기록해".

## Protocol Steps

1.  **Step 1: Test Verification (Blocking)**
    - **Action**: Check if relevant tests (Frontend/Backend) have passed.
    - **Condition**:
        - **If Passed**: Proceed to Step 2.
        - **If Failed/Not Run**: 
            1. Execute `protocol_test_execution.md`.
            2. Fix errors using `protocol_quick_debug.md`.
            3. **LOOP**: Repeat until tests pass. **No Scoring allowed until Success.**

2.  **Step 2: Log & Summary**
    - **Reference**: `fivecircles/agent/skills/protocol_logging_summary.md`
    - **Action**:
        - Update `fivecircles/work/update.md` (What was done).
        - Update `fivecircles/architecture/todolist.md` (Task status).
        - Log any errors to `errorlogs/` and `mistakes-arrest.md`.
        - Update `fivecircles/agent/debate.md` with a summary.

3.  **Step 3: Scoring & Self-Correction**
    - **Reference**: `fivecircles/agent/skills/protocol_agent_scoring.md`
    - **Action**:
        - Calculate session score based on Progress, Quality, and Specs.
        - **Rule**: "Quality" points are valid ONLY if Step 1 (Tests) passed.
        - Record the score in `fivecircles/scoring/log-score.md`.
        - Propose optimizations in `fivecircles/scoring/optimization.md` if applicable.

4.  **Step 4: Final Sync**
    - **Action**:
        - Check `fivecircles/agent/sync.md` and update status if needed.
        - Confirm "Task Completed. Tests Passed. Total Score: [Score]. Ready for next task."
