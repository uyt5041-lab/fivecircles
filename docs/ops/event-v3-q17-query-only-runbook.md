# Event V3 Q17 Query-only Runbook

## Scope
- Endpoint: `/api/event/v3/dramas/{dramaId}/foreshadowed` (Q17 only)
- Runtime switches:
  - `EVENT_V3_Q17_SOURCE_MODE` = `rdb | rdf-candidate | auto-fallback`
  - `EVENT_V3_FORCE_RDB` = `true | false` (highest priority)
  - `EVENT_V3_Q17_RDF_KG_PATH` = readable `kg.ttl` absolute path (required when source mode is `rdf-candidate` or `auto-fallback`)

## Important Runtime Rule
- Flags are read at **process start**.
- Any mode change requires **event-service restart**.
- "No deploy" means "restart-only" (no image rebuild required).
- When running with Docker Compose, `EVENT_V3_Q17_RDF_KG_PATH` must be a **container-internal path** (host absolute path is not readable inside container).

## Local/Compose Rollout

### 0) Fast path (cached image, no build)
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_Q17_SOURCE_MODE=auto-fallback \
EVENT_V3_FORCE_RDB=false \
EVENT_V3_Q17_RDF_KG_PATH=/tmp/v3-advanced-kg.ttl \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-build --no-deps --force-recreate event-service

docker cp /Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/kg.ttl \
  nospoiler-event-service:/tmp/v3-advanced-kg.ttl
```

### 1) Default-safe mode (RDB)
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_Q17_SOURCE_MODE=rdb \
EVENT_V3_FORCE_RDB=false \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-deps --force-recreate event-service
```

### 2) Query-only candidate test mode
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_Q17_SOURCE_MODE=rdf-candidate \
EVENT_V3_FORCE_RDB=false \
EVENT_V3_Q17_RDF_KG_PATH=/tmp/v3-advanced-kg.ttl \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-deps --force-recreate event-service

docker cp /Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/kg.ttl \
  nospoiler-event-service:/tmp/v3-advanced-kg.ttl
```

### 3) Recommended serve mode (with fallback)
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_Q17_SOURCE_MODE=auto-fallback \
EVENT_V3_FORCE_RDB=false \
EVENT_V3_Q17_RDF_KG_PATH=/tmp/v3-advanced-kg.ttl \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-deps --force-recreate event-service

docker cp /Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/kg.ttl \
  nospoiler-event-service:/tmp/v3-advanced-kg.ttl
```

## Emergency Rollback (Immediate)
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_FORCE_RDB=true \
EVENT_V3_Q17_SOURCE_MODE=rdb \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-deps --force-recreate event-service
```

## Verify After Restart

### 1) Service log check
```bash
docker logs nospoiler-event-service --tail 200 \
  | rg "eventV3.q17 sourceMode|eventV3.q17.shadow"
```

### 2) Expected observability fields
- `sourceMode`
- `sourceUsed`
- `fallbackTrigger`
- `rdfCandidateCount`
- `rdfTimeMs`, `hydrateTimeMs`, `totalTimeMs`
- `answerabilityStatus`

## Replay Parity Report (Ops)
```bash
cd /Users/pio/IdeaProjects/nospoiler
scripts/ops/rdf/replay_v3_advanced_q17_parity.sh
```

Output:
- `fivecircles/architecture/specs/rdf/artifacts/v3-advanced/{RUN_DATE}/q17-query-only-replay-report.json`
