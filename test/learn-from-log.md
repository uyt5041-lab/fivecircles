# Learn From Logs

This document records insights gained from errors to prevent recurrence.

## [2026-01-15] VS Code Task Automation for Interactive CLIs
- **Interactive Shell is Key**: When running tasks that depend on `.zshrc` (aliases, functions, PATH), always use `"shell": { "executable": "/bin/zsh", "args": ["-l", "-i", "-c"] }`.
- **Silent Background Tasks**: To prevent the infinite loading spinner on long-running/interactive tasks:
    1. Set `"isBackground": true`.
    2. Provide a `problemMatcher` with `background` patterns.
    3. Ensure the command produces *some* output at startup (e.g., using `echo`) to trigger the pattern matcher.
- **Group vs Independent**: Using `"group": "..."` in presentation settings will split the terminal pane (Tmux-style). To open in new tabs, omit the `group` property or use unique ones.
- **CLI task invocation**: `code --run-task` is not a standard CLI feature for external terminals; prefer IDE-native keybindings or internal task runner.