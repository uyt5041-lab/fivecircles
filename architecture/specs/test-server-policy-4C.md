# Test Server Connection Policy

Purpose
- Define how Team C services connect to test servers without diverging from local defaults.
- Keep connection config explicit and reproducible for integration checks.

Scope
- Applies to event-service and spoiler-policy-service test runs.
- QnA (qa-service) is excluded for now. 단, /qa 화면이 호출하는 event-service query 엔드포인트 스모크는 이 문서의 범위에 포함한다.

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

Schema Drift (Ops / Backfill Tables)
- Flyway is the source of truth for application schemas. Avoid creating/changing app tables manually.
- However, some **ops-only** backfill runs may create temporary/audit tables (e.g., `ops_*`) to record what changed.
  - This is a deliberate "drift": Flyway does not manage these tables.
  - It should never block Flyway, but it can make the DB look "non-identical" across environments.
- Rules:
  - Only create ops tables on test servers unless explicitly approved.
  - Prefix ops tables with `ops_` and keep the run id in the name (easy to find/drop later).
  - Always record the run in `fivecircles/work/update.md` with:
    - table name(s)
    - target DB/schema
    - selection criteria (what rows were touched)
    - rollback path (how to restore / whether safe to drop the table)
  - Put reproducible scripts under `scripts/ops/` and reference the script path in the update log.

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

Smoke Checks (Event Query API, via Gateway)
- related-characters aggregate (ADVERSARY)
  - `ssh bit-ts "curl -sS -i 'http://localhost:8080/api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode={K}&mode=ADVERSARY&limit=30'"`
- related-characters aggregate (ALLY)
  - `ssh bit-ts "curl -sS -i 'http://localhost:8080/api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode={K}&mode=ALLY&limit=30'"`
- evidence 포함
  - `ssh bit-ts "curl -sS -i 'http://localhost:8080/api/event/v2/characters/{id}/related-characters/aggregate?safeUpToEpisode={K}&mode=ADVERSARY&includeEvidenceEventIds=true'"`



🔁 앞으로의 표준 루프 (이것만 쓰면 됨)
Remote Deploy Flow (Server)
Use this flow when deploying from the Mac dev machine to the server.
Preferred: Option 2 (Docker builds only, no host Gradle)
Due to the migration to Tailscale, use this ip and command: ssh -p 2222 bit_@100.120.44.64
Note: `100.120.44.64` is the Windows host. Ubuntu/WSL base: `http://100.79.74.49:8080`. DB connections should use the Ubuntu host address (`DB_HOST`), not this IP.

  ssh -p 2222 bit_@100.120.44.64 "curl -i -H 'X-User-Id: 13' http://localhost:18080/handovers/310"

updated:

ssh bit-ts 
= ssh -p 2222 bit_@100.120.44.64

# 접속
ssh bit-ts

# 원격에서 레포 상태 확인
ssh bit-ts "cd ~/nospoiler && git status"

# 원격 배포 (권장: 4C fast-build)
# - 공유 파일(기본 docker-compose.yml / 서비스 Dockerfile) 변경 없이, override 파일로만 동작
# - `*.4c` 파일은 gitignore 대상(생성 파일)이라서, 배포 시 스크립트가 서버에서 생성함
#
# 로컬 스크립트:
#   fivecircles/test/deploy-server-4c.sh event-service api-gateway

# (Fallback) 기본 전체 리빌드 배포
# - 느리지만 가장 단순/안전. 4C 경로가 깨지면 이걸로 돌아감.
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

# Automated Script
For convenience, use `fivecircles/test/deploy-server-4c.sh` (preferred) or `fivecircles/test/deploy-server.sh` (fallback).
