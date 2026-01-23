# MCP System Architecture

## Overview
This document describes the **Multi-Agent Collaboration Environment** implemented for the `nospoiler` project. It ensures safe concurrency and resource optimization for multiple agents (Antigravity/Codex, Gemini) working in the same workspace.

## 1. Agent Bridge MCP
The **Agent Bridge** (`agent-bridge-mcp`) acts as a central middleware for inter-agent communication and filesystem safety.

### 1.1 Concurrency Control (File Locking)
To prevent race conditions where agents overwrite each other's changes, the Bridge implements a **Middleware Proxy Pattern**:

-   **Mechanism**: Uses `proper-lockfile` to acquire exclusive locks on files during write operations.
-   **Lock Directory**: `~/.agent-bridge/locks/`
-   **Safe Tools**:
    -   `safe_write_file`: Locks -> Writes -> Unlocks.
    -   `safe_replace_in_file`: Locks -> Reads -> Replaces -> Writes -> Unlocks.
-   **Protocol**: All agents are strictly instructed to use these tools instead of standard `filesystem` MCP tools for critical edits.

## 2. Dynamic Agent Profiles
To optimize token usage and context window availability, agents support "On-Demand" configuration loading.

### 2.1 Problem
Loading all tool schemas (Playwright, Browser Use, Notion, etc.) into the System Prompt consumes thousands of tokens per turn, even when those tools are not in use.

### 2.2 Solution: Light vs Full Profiles
We define two operating modes:
-   **Light**: Essential tools only (Filesystem, Terminal, Memory). ~70% token reduction.
-   **Full**: All tools including huge browser schemas.

### 2.3 Implementation
-   **Gemini**: Uses `--allowed-mcp-server-names` flag to filter tools at runtime.
-   **Codex**: Uses a config swapping mechanism (`config.toml` vs `config.light.toml`) triggered by shell scripts (`switch-codex-mode.sh`).

## 3. Resume Workflow
The **Resume** capability allows agents to switch profiles without losing conversation history (Context).
1.  Agent starts in **Light Mode** (Planning/Coding).
2.  User triggers **Switch to Full** task.
3.  Agent restarts with **Resume** flag (`-r latest`).
4.  Agent wakes up with "Full" tools but remembers the previous plan.

## 4. Components
-   **Source Code**: `nospoiler-mcp-tools/agent-bridge-mcp/` (External)
-   **Middleware**: `agent-bridge-mcp` (Node.js)
-   **Configuration**:
    -   `.vscode/tasks.json`: Automation tasks.
    -   `scripts/switch-codex-mode.sh`: Config swapper.
    -   `agent/mcp-instruction.md`: User manual.
