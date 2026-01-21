# Repeat Mistakes and Fixes

Rule
- Always prefix each mistake with a category tag (e.g., [경로설정], [api분류], [깃], [명령어오류]).

## Mistake
- [경로설정] Touched non-owned areas (ex: drama/character scope) instead of keeping them aligned with develop.

## Why It Happened
- Scope check was skipped before edits and the branch drifted into areas owned by other members.

## Fix (Do This Every Time)
- Before editing, run: `git diff --name-only origin/develop..HEAD`.
- If a file is outside my scope (drama/character), reset it to develop:
  - `git checkout origin/develop -- <path>`
- Re-run the diff and confirm only owned areas are changed.

## Mistake
- [보고형식] User asked for a diff, but I kept giving summaries instead of the raw diff output.

## Why It Happened
- I defaulted to summarizing command output and didn't provide the full diff on the first response.

## Fix (Do This Every Time)
- When the user requests "diff" or "show output", return the raw output first, then summarize only if asked.
