# Test Server Connection Policy

Purpose
- Define how Team C services connect to test servers without diverging from local defaults.
- Keep connection config explicit and reproducible for integration checks.

Scope
- Applies to event-service and spoiler-policy-service test runs.
- QnA (qa-service) is excluded for now.

Defaults (Local)
- Event service: http://localhost:8089
- Spoiler policy service: http://localhost:8090

Environment Variables
- EVENT_SERVICE_URL: overrides the event-service base URL.
- POLICY_SERVICE_URL: overrides the spoiler-policy-service base URL.

Example (Local)
- EVENT_SERVICE_URL=http://localhost:8089
- POLICY_SERVICE_URL=http://localhost:8090

Example (Remote Test Server)
- EVENT_SERVICE_URL=https://test-event.nospoiler.local
- POLICY_SERVICE_URL=https://test-policy.nospoiler.local

Notes
- Use these variables in service configs when running integration checks.
- Keep the production URLs out of this file.

Compose Location
- Docker compose runs from `~/nospoiler/infra` on the server.
- Use the infra folder for `docker compose up -d --build`.

MySQL Bootstrap (When Volume Exists)
- If the MySQL volume already exists, `docker/mysql/init/init.sql` will NOT run again.
- Ensure required databases exist before starting services:
  - nospoiler_event
  - nospoiler_wiki
  - nospoiler_policy
- Create them (server):
  - `ssh bit-ts "docker exec -i nospoiler-mysql mysql -uroot -proot -e 'CREATE DATABASE IF NOT EXISTS nospoiler_event; CREATE DATABASE IF NOT EXISTS nospoiler_wiki; CREATE DATABASE IF NOT EXISTS nospoiler_policy;'"` 

Remote Branch Sync (Required for Server Tests)
- The server can only pull commits that exist on the remote.
- Push your local branch first, then pull on the server.
- Commit only after explicit approval from the owner.

Frontend Browser Tests (Playwright)
- Push latest commits to the remote before server tests.
- Pull on the server, then run Playwright against http://100.120.44.64:3000/
- For local build tests, run the frontend locally and use http://localhost:3000/

Example (Local -> Remote)
1) `git status`
2) `git add -A`
3) `git commit -m "..."` (if needed)
4) `git push origin docs/next-tasks`

Example (Remote pull + deploy)
1) `ssh bit-ts "cd ~/nospoiler && git fetch origin"`
2) `ssh bit-ts "cd ~/nospoiler && git checkout docs/next-tasks"`
3) `ssh bit-ts "cd ~/nospoiler && git pull origin docs/next-tasks"`
4) `ssh bit-ts "cd ~/nospoiler/infra && docker compose up -d --build"`

Latest Sync Check (Before Any Server Test)
1) `ssh bit-ts "cd ~/nospoiler && git status -sb"`
2) `ssh bit-ts "cd ~/nospoiler && git fetch origin"`
3) `ssh bit-ts "cd ~/nospoiler && git rev-parse HEAD"`
4) `ssh bit-ts "cd ~/nospoiler && git rev-parse origin/develop"`
5) If the two SHAs differ, stop and run:
   - `ssh bit-ts "cd ~/nospoiler && git checkout develop"`
   - `ssh bit-ts "cd ~/nospoiler && git pull origin develop"`
   - `ssh bit-ts "cd ~/nospoiler/infra && docker compose up -d --build"`



🔁 앞으로의 표준 루프 (이것만 쓰면 됨)
Remote Deploy Flow (Server)
Use this flow when deploying from the Mac dev machine to the server.
Preferred: Option 2 (Docker builds only, no host Gradle)
Due to the migration to Tailscale, use this ip and command: ssh -p 2222 bit_@100.120.44.64

  ssh -p 2222 bit_@100.120.44.64 "curl -i -H 'X-User-Id: 13' http://localhost:18080/handovers/310"

updated:

ssh bit-ts 
= ssh -p 2222 bit_@100.120.44.64

# 접속
ssh bit-ts

# 원격에서 레포 상태 확인
ssh bit-ts "cd ~/nospoiler && git status"

# 원격 배포(서버에서 pull + compose)
ssh bit-ts "cd ~/nospoiler/infra && git pull && docker compose up -d --build"

# alias

cat >> ~/.zshrc <<'EOF'
# nospoiler remote control (server: bit-ts, path: ~/nospoiler)
alias np-deploy="ssh bit-ts 'cd ~/nospoiler/infra && git pull && docker compose up -d --build && docker compose ps'"
alias np-ps="ssh bit-ts 'cd ~/nospoiler/infra && docker compose ps'"
alias np-logs="ssh bit-ts 'cd ~/nospoiler/infra && docker compose logs --tail 200'"
alias np-logs-f="ssh bit-ts 'cd ~/nospoiler/infra && docker compose logs -f --tail 200'"
alias np-test="ssh bit-ts 'cd ~/nospoiler/infra && if docker compose config --services | grep -qx test; then docker compose run --rm test; else echo \"No test service in compose. Use: docker compose exec <service> <test-cmd>\"; docker compose config --services; fi'"


alias np-test="ssh bit-ts 'cd ~/nospoiler && ./gradlew test'"
alias np-test-info="ssh bit-ts 'cd ~/nospoiler && ./gradlew test --info'"
