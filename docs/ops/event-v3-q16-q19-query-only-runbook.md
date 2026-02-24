# Event V3 Q16/Q19 Query-only Runbook

## Scope
- Endpoints:
  - Q16: `/api/event/v3/characters/{characterId}/rise`
  - Q19: `/api/event/v3/dramas/{dramaId}/conflict-axes`
- Runtime switches:
  - `EVENT_V3_Q16_SOURCE_MODE` = `rdb | rdf-candidate | auto-fallback`
  - `EVENT_V3_Q19_SOURCE_MODE` = `rdb | rdf-candidate | auto-fallback`
  - `EVENT_V3_FORCE_RDB` = `true | false` (highest priority)
  - `EVENT_V3_Q17_RDF_KG_PATH` = readable `kg.ttl` path (shared query-only RDF source)

## Important Runtime Rule
- Flags are read at process start.
- Any mode change requires event-service restart.
- Docker Compose에서는 `EVENT_V3_Q17_RDF_KG_PATH`를 컨테이너 내부 경로로 사용해야 한다.

## Fast Restart (No Build)
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_Q16_SOURCE_MODE=auto-fallback \
EVENT_V3_Q19_SOURCE_MODE=auto-fallback \
EVENT_V3_FORCE_RDB=false \
EVENT_V3_Q17_RDF_KG_PATH=/tmp/v3-advanced-kg.ttl \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-build --no-deps --force-recreate event-service

docker cp /Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/kg.ttl \
  nospoiler-event-service:/tmp/v3-advanced-kg.ttl
```

## Emergency Rollback
```bash
cd /Users/pio/IdeaProjects/nospoiler
EVENT_V3_FORCE_RDB=true \
EVENT_V3_Q16_SOURCE_MODE=rdb \
EVENT_V3_Q19_SOURCE_MODE=rdb \
docker compose -f infra/docker-compose.yml --env-file .env \
  up -d --no-build --no-deps --force-recreate event-service
```

## Smoke Requests
```bash
# Q16
curl -sS "http://localhost:8080/api/event/v3/characters/17/rise?dramaId=10&safeUpToEpisode=6&limit=10"

# Q19
curl -sS "http://localhost:8080/api/event/v3/dramas/10/conflict-axes?safeUpToEpisode=6&limit=10"
```

## Log Check
```bash
docker logs nospoiler-event-service --tail 300 \
  | rg "eventV3.q16 sourceMode|eventV3.q16.shadow|eventV3.q19 sourceMode|eventV3.q19.shadow"
```

Expected fields:
- `sourceMode`
- `sourceUsed`
- `fallbackTrigger`
- `answerabilityStatus`
- shadow parity line:
  - Q16: `statusParity`, `anchorParity`, `contextParity`, `evidenceJaccard`
  - Q19: `statusParity`, `axisParity`, `evidenceJaccard`

## Replay Support
- Q16 replay: `scripts/ops/rdf/replay_v3_advanced_q16_parity.sh`
- Q19 replay: `scripts/ops/rdf/replay_v3_advanced_q19_parity.sh`
- Unified replay: `scripts/ops/rdf/replay_v3_advanced_all.sh`
