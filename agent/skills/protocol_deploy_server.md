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
    - Run the helper script: `fivecircles/test/deploy-server.sh`
    - This script will:
        - Check for uncommitted changes.
        - Push the current branch to `origin`.
        - SSH into the server (`bit-ts`).
        - Checkout/Pull the same branch.
        - Rebuild and restart containers (`docker compose up -d --build`).

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
