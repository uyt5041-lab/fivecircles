# Multi-Agent MCP & Workflow Instructions

## 1. Safety Protocol: Concurrent File Access
> **CRITICAL**: When multiple agents (Gemini, Codex) work simultaneously, they MUST adhere to this protocol to prevent race conditions (overwriting each other's work).

### Rule
**NEVER** use standard filesystem tools (`write_file`, `replace_in_file`) for critical file modifications in a multi-agent context.
**ALWAYS** use the **Agent Bridge** safe tools.

### Safe Tools
These tools automatically acquire a file lock before writing and release it afterwards.
- **`safe_write_file`**: Use this to overwrite an entire file or create a new one.
- **`safe_replace_in_file`**: Use this to find and replace text within a file.

---

## 2. Token Optimization: Dynamic Agent Profiles
To save tokens and increase the context window, use the appropriate profile for your task.

### Profiles
| Profile | Description | Included Tools | Use Case |
| :--- | :--- | :--- | :--- |
| **LIGHT** | Minimal footprint | Filesystem, Memory, Terminal | Pure Coding, Refactoring, Planning |
| **FULL** | Maximum capability | All above + **Playwright, Browser Use, Notion** | Web Research, E2E Testing, Documentation |

### How to Switch Profiles
Use the **VS Code Tasks** (Cmd+Shift+P -> `Tasks: Run Task`) to switch modes easily.

#### Codex
1.  **Select Task**:
    -   `Switch Codex to LIGHT`
    -   `Switch Codex to FULL`
2.  **Apply**: The configuration is swapped immediately. You must **Restart** Codex to take effect (see Resume below).

#### Gemini
Gemini does not require a config swap; it supports on-demand flags.
-   **Light Mode**: Run Task `Agents: Gemini (Light)`
-   **Full Mode**: Run Task `Agents: Gemini` (Default)

---

## 3. Resume Workflow (Context Preservation)
You can switch profiles **mid-task** and keep your conversation history.

### Workflow
1.  **Trigger Switch**: Run the appropriate "Switch" task (for Codex) or prepare to restart (for Gemini).
2.  **Resume Session**: Run the Resume task.
    -   `Agents: Codex (Resume)`
    -   `Agents: Gemini (Resume)`
3.  **Result**: The agent restarts with the *new* tool set (Light/Full) but reloads the *previous* chat history.

> **Tip**: Use this pattern to start "Light" for planning/coding, then switch to "Full" only when you specifically need to browse the web or update Notion.
