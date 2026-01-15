# Error Log: IDE Agent Automation Failure (2026-01-15)

## 1. Issue: CLI Command Not Found / Wrong Version
- **Symptoms**: `which codex` returned no path or executed an old system version instead of the user's `.zshrc` function.
- **Root Cause**: VS Code Tasks run in a non-interactive shell by default, skipping user-defined aliases and functions in `.zshrc`.
- **Fix**: Changed shell options to `/bin/zsh` with `-l` (login) and `-i` (interactive) arguments.

## 2. Issue: Infinite Loading Spinner in Terminal Tab
- **Symptoms**: The terminal tab title showed a spinning icon indefinitely.
- **Root Cause**: Interactive CLI processes do not exit. VS Code treats "running" tasks as "not yet finished".
- **Fix**: Added `"isBackground": true` and a dummy `problemMatcher` to mark the task as "ready" immediately.

## 3. Issue: `codex` specifically kept spinning
- **Symptoms**: Unlike Gemini/Claude, Codex did not stop the spinner even with `isBackground`.
- **Root Cause**: `problemMatcher` background detection requires some output to trigger. Codex was silent on startup.
- **Fix**: Prepended `echo 'Starting Codex...';` to the command string.

## 4. Issue: Keybinding Conflict
- **Symptoms**: `Cmd+Shift+R` did not trigger the task.
- **Root Cause**: Conflict with IDE built-in commands (Refactor/Reload).
- **Fix**: Switched to `Cmd+Alt+A`.
