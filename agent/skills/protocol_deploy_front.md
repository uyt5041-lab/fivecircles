# Skill: Deploy Frontend (Local Dev Server)

## Purpose
Start the Vite dev server for the frontend with network access enabled, so it can be accessed from both localhost and mobile devices on the same network.

## Usage
Execute when the user says "프론트 띄워", "deploy front", "dev 서버", or `/deploy-front`.

## Access URLs
| Target | URL |
|---|---|
| Local (PC) | http://localhost:3000/ |
| Network (Phone) | http://<your-network-ip>:3000/ |

## Protocol Steps

// turbo-all

1. **Stop Docker frontend container** (if running, to free port 3000)
   ```bash
   docker stop nospoiler-frontend 2>/dev/null || true
   ```

2. **Kill any process on port 3000** (if still occupied)
   ```bash
   lsof -ti :3000 | xargs kill -9 2>/dev/null || true
   ```

3. **Start Vite dev server with network access**
   ```bash
   cd <project-root>/front && npm run dev -- --host 0.0.0.0 --port 3000
   ```

4. **Verify**
   - Confirm output shows `Local: http://localhost:3000/` and `Network:` URLs.
   - Report both URLs to the user for PC and phone access.

## Notes
- `--host 0.0.0.0` opens the server to all network interfaces (required for phone access).
- The Docker `nospoiler-frontend` container also binds to port 3000, so it must be stopped first.
- Phone must be on the same Wi-Fi/network as the dev machine.
- Replace `<your-network-ip>` with the actual IP of your development machine.
