# Fuseki Runtime Semantic Lane Runbook

기준일: 2026-03-04

목적
- `event-anchored RDF + runtime semantic lane` 구조에서 Fuseki를 로컬 docker-compose로 올리고, 최소 TTL을 적재한 뒤 SPARQL smoke query까지 확인하는 절차를 정리한다.

구성
- compose file:
  - `/Users/pio/IdeaProjects/nospoiler/infra/docker-compose.yml`
- loader script:
  - `/Users/pio/IdeaProjects/nospoiler/infra/scripts/fuseki-load.sh`
- seed TTL:
  - `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/semantic-lane-object-schema.draft.ttl`

서비스
- `nospoiler-fuseki`
- `nospoiler-fuseki-loader`

기본 포트
- `3030`

기동
```bash
docker compose -f /Users/pio/IdeaProjects/nospoiler/infra/docker-compose.yml up -d fuseki
docker compose -f /Users/pio/IdeaProjects/nospoiler/infra/docker-compose.yml up --abort-on-container-exit fuseki-loader
```

현재 구현 메모
- Fuseki 바이너리는 컨테이너 내부 `/opt/fuseki`에 둔다.
- dataset/운영 데이터는 host `infra/data/fuseki` -> container `/fuseki-data`로 분리 마운트한다.
- `RDB -> TTL export -> Fuseki load` 구조에서, 현재 Phase 3은 seed TTL 1개를 loader가 적재하는 상태다.

헬스체크
```bash
curl -fsS http://localhost:3030/$/ping
```

샘플 SPARQL
```bash
curl -G 'http://localhost:3030/nospoiler/query' \
  --data-urlencode 'query=PREFIX ns: <https://nospoiler.dev/ns#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT ?objectType ?label WHERE { ?objectType rdf:type ns:ObjectType ; rdfs:label ?label . } ORDER BY ?label' \
  -H 'Accept: application/sparql-results+json'
```

스모크 완료 기준
- `http://localhost:3030/$/ping` 응답
- `nospoiler` dataset이 `/fuseki-data/databases/nospoiler`에 생성
- object type 쿼리에서 `CHARACTER`, `ATTRIBUTE`, `RELATION`, `ORG` 등 라벨이 반환

주의
- 현재 Phase 3은 semantic lane 인프라만 붙인다.
- strict answer selection은 계속 RDB다.
- Fuseki가 내려가도 runtime main lane은 죽지 않게 설계해야 한다.

## Refresh
- event-anchored TTL export + reload: `/Users/pio/IdeaProjects/nospoiler/infra/scripts/fuseki-refresh.sh`
