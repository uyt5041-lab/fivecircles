# Multi-Agent MCP & Workflow Instructions

## 0. Tool Discovery (Mandatory for New Agents)
> **CHECK THIS FIRST**: Before claiming "I can't do X" or "I don't have tool Y", verify your environment.

1.  **Check `.mcp.json`**: This file defines all available MCP servers and their configurations.
2.  **Check Available Tools**: Look at the list of tools provided in your system prompt or by running `list_tools` (if available).
3.  **Recognize Aliases**:
    -   `fetch_page` comes from the `playwright` MCP.
    -   `browse_web` comes from `browser-use`.
    -   `safe_write_file` comes from `agent-bridge`.
4.  **Inspect Scripts**: Check `~/nospoiler-mcp-tools/` or `.venv/bin/` for Python scripts or executables that can be run via `run_shell_command`.

---

## 0.1 IDE MCP vs CLI MCP: 분리 구조

> [!CAUTION]
> **Antigravity IDE와 CLI agents는 MCP 설정 소스가 다르다.**

| 환경 | 설정 파일 | 로더 |
|:---|:---|:---|
| **CLI agents** (Gemini, Codex) | `.mcp.json` | 각 에이전트 런타임 |
| **Antigravity IDE** | `~/Library/Application Support/Antigravity/User/mcp.json` | IDE 전용 로더 (UI: Command Palette > MCP) |

### 혼동 방지 규칙

1.  **IDE에서 "MCP server not found"** → 서버 문제가 아니라 **IDE가 해당 서버를 등록 안 한 것**일 가능성 높음
2.  **`.mcp.json` 수정**은 CLI agents에만 영향, IDE는 `User/mcp.json`을 수정하거나 UI로 추가해야 함
3.  **IDE 재시작**으로 `.mcp.json` 서버가 로드되지 않음 (로드 대상 자체가 다름)

---

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

## Profile Switching & Context (WARNING)
Switching profiles (Light <-> Full) requires a **process restart**.

> **⚠️ CAUTION**: 
> Unless your specific client environment explicitly supports "history replay", **ALL CONVERSATION HISTORY IS LOST** upon restart.

### Safe Switching Workflow
1.  **Save State**: Write your current progress, plan, and next steps to a file (e.g., `fivecircles/work/implementation-log.md` or a temp file).
2.  **Trigger Switch**: Run the switch task.
3.  **Restart**: Start the new session.
4.  **Restore**: Read the state file you saved to resume work.

**Do NOT assume memory persists across restarts.**
