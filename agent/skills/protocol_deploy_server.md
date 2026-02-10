# Skill: Protocol for Server Deployment (SSH)

## Purpose
Standardize the backend/server deployment workflow using SSH to the test server.

## Usage
Execute this protocol when the user asks to "Server Deploy" (서버 배포해) or when backend changes need to be tested on the remote server.

## Protocol Steps

1.  **Preparation**
    - Ensure all local changes are committed.
    - Confirm the current branch is correct.

2.  **Execution (Automated)**
    - Prefer 4C fast-build deploy (keeps shared Dockerfiles/compose untouched; generates `*.4c` on server):
      - `fivecircles/test/deploy-server-4c.sh`
    - Fallback to default deploy:
      - `fivecircles/test/deploy-server.sh`

3.  **Manual Execution (Fallback)**
    - If the script fails, execute manually:
        ```bash
        # 1. Push
        git push origin <current_branch>
        
        # 2. SSH & Deploy
        ssh bit-ts "cd ~/nospoiler/infra && git fetch && git checkout <current_branch> && git pull && docker compose up -d --build"
        ```

4.  **Log**
    - Record the deployment status in `update.md`.
