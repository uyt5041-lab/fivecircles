# Skill: Protocol for Operation Initialization

## Purpose
Initialize the agent's mental model, operational boundaries, and context by loading the core project documentation in the correct order. Use this to minimize context loss when starting a new session.

## Usage
Execute this protocol at the beginning of a session or when instructed to "Initialize operational policy" (운영방침 초기화).

## Protocol Steps

1.  **Bootstrapping (`fivecircles/readme.md`)**
    - Read the root documentation to understand the file structure (`requirements/`, `architecture/`, `work/`, `test/`) and the "Five Circles" methodology.

2.  **Workflow & Guidelines**
    - Read `fivecircles/architecture/specs/README.md` to define the project workflow.
    - Read `fivecircles/agent/agent-guidelines.md` to understand behavioral rules and limits.

3.  **Multi-Agent Context**
    - Read `fivecircles/agent/멀티에이전트설명서.md` to identify:
        - Available MCP tools and aliases.
        - Your specific role (Planner, Coder, Ops, Reviewer).
        - Collaboration protocols (`sync.md`, `queue.json`).
        - **Team Scope**: Confirm strict adherence to **Team C (Intelligence, Filter, QA)** scope.

4.  **Load Current Status**
    - Read `fivecircles/work/update.md` to grasp the latest progress.
    - Read `fivecircles/architecture/todolist.md` to identify pending tasks.

5.  **Ready State**
    - After reading, confirm: "Operational context initialized. I am [Role] for Team C. Current focus is [Task from Todo]."
