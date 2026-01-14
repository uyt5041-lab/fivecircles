# Work Folder Policy (Execution)

- Follow specs and implementation-rules when planning/doing tasks.
- Plan work in `architecture/todolist.md` and related plan files; keep them aligned with specs.
- Record the plan for each task in `architecture/todolist.md` before implementation.
- After completing tasks, record work logs in `work/update.md` and update `architecture/todolist.md`.
- Before implementation, review `test/learn-from-log.md` and apply a recurrence-prevention plan based on existing learnings.
- After implementation, proceed to testing.
- Testing follows lines 8–10 of this file and `test/testpolicy.md` (SUCCESS → `work/update.md`, FAIL → `test/errorlogs/`).
- Log errors + fixes under `test/errorlogs/`.
- Then score the work per `scoring/` docs (see `scoring/log-score.md`).
- Before starting implementation, review `test/errorlogs/` and `scoring/optimization.md` to reuse proven fixes and maximize scoring outcomes.
- After scoring, record any higher-score path in `scoring/optimization.md` when applicable.
- Implementation order for UI: progress left-to-right (top-to-bottom) across the page to mirror natural reading flow.
- The `work/` folder is the implementation stage; new or changed requirements return to `maintenance/freshrequest.md`.

## Update Log (Token-lite default)

Use a minimal addendum format to reduce context and duplication.

Template:

```
## Addendum (YYYY-MM-DD) - <short title>
### Frontend
- <one line change> (refs: path1, path2)
### Backend
- <one line change> (refs: path)
### Tests
- <result> (refs: errorlog)
```

Rules:
- Keep each bullet to 140 characters max.
- 1–2 bullets per section; omit sections with no changes.
- Do not copy long descriptions; link to error logs or learn-from-log entries instead.
