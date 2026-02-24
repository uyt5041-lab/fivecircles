# Event V3-Advanced Query-only Promotion Plan

Purpose
- Define the concrete path from Export-only (`+10`) to Query-only (`+30`) for V3-Advanced.
- Keep external `/api/event/v3` contracts unchanged while changing internals to `RDF candidate query -> RDB hydration`.

Status
- Draft date: 2026-02-24
- Current level: Export-only (`+10`)
- Query-only PoC status: implemented for Q17 in ops lane (`scripts/ops/rdf/query_v3_advanced_q17_poc.sh`)

---

## 1) Scope

In scope
- First promoted read-path: Q17 (`/api/event/v3/dramas/{dramaId}/foreshadowed`)
- Candidate extraction from RDF graph with SPARQL semantics.
- Final response hydration from RDB with existing gate semantics.

Out of scope
- Contract changes for Q16~Q20 payloads.
- Dual-store write path.
- Mandatory runtime dependency without fallback.

---

## 2) Serving Pattern (Target)

1. RDF query step
- Query graph for candidate event IDs / edge groups.
- Apply semantic filters as **soft filters only** (candidate reduction only; never used for final user-facing decision).
- Candidate safety cap:
  - `maxCandidateEventIds`: 200
  - If RDF candidate count exceeds cap, skip RDF result and fallback to RDB-only path.

2. RDB hydrate step
- Hydrate candidate IDs via existing mapper/service queries.
- Re-apply hard gate in runtime (`episode_end <= K`, `source_status='APPROVED'`) for parity safety.
- Hard gate and final status decision are enforced exclusively after RDB hydration.
- Hydration must be executed as a single batched query per request (no per-id/N+1 query).

3. Response assembly
- Return existing V3 contract fields unchanged.
- Keep `evidenceEventIds` as always-array rule.
- `answerabilityStatus` must follow the existing probe mapping contract exactly (no Query-only reinterpretation):
  - `existsSafeApproved=false`, `existsAnyApproved=true` -> `SPOILER_BLOCKED`
  - `existsSafeApproved=false`, `existsAnyApproved=false` -> `NOT_ENOUGH_DATA`
  - `existsSafeApproved=true` -> `ANSWERED`
  - Reference: `fivecircles/architecture/specs/event-v3-api-contract.md` section "Probe/Strict Integration Rule".

4. Fallback
- If RDF query fails/timeouts/no source, fallback to existing RDB-only path.
- Log source (`rdf` vs `rdb-fallback`) for observability.
- Auto-fallback trigger set (closed):
  - `SOFT_TIMEOUT`, `HARD_TIMEOUT`, `RDF_QUERY_ERROR`, `CANDIDATE_CAP_OVERFLOW`, `HYDRATION_ERROR`
  - Any new trigger requires spec update before release.
- Runtime SLO (Q17 first rollout, timeout model fixed):
  - `rdfCandidateSoftTimeoutMs`: 120 (soft timeout: start RDB fallback immediately)
  - `rdfCandidateHardTimeoutMs`: 300 (hard timeout: stop waiting for RDF result)
  - `rdfCandidateRetryCount`: 0
  - `fallbackRequired`: true
  - `fallbackMaxAdditionalLatencyMs`: 150 (measured after soft-timeout fallback starts)
  - `endpointP95RegressionLimit`: +15% vs RDB baseline
- Latency metric definition lock:
  - `fallbackMaxAdditionalLatencyMs` is measured as
    `(completion time of RDB fallback path) - (time when soft-timeout triggers and fallback starts)`.

5. Emergency rollback switch (no deploy/image rebuild)
- Scope: Q17 only (`/api/event/v3/dramas/{dramaId}/foreshadowed`)
- Config keys:
  - `EVENT_V3_FORCE_RDB` (default: `false`) - highest priority kill-switch
  - `EVENT_V3_Q17_SOURCE_MODE` (default: `rdb`) - `rdb | rdf-candidate | auto-fallback`
  - `EVENT_V3_Q17_RDF_KG_PATH` (default: empty) - RDF candidate source path for `kg.ttl`
- Config source and apply rule:
  - Source of truth: event-service runtime environment variables.
  - Flags are read at process start.
  - Rollback requires service restart only (no image rebuild/redeploy).
  - Clarification: "no deploy" in this document means "restart-only with changed env vars."
- Evaluation priority:
  1. `EVENT_V3_FORCE_RDB=true` -> always `rdb`
  2. else `EVENT_V3_Q17_SOURCE_MODE` value applies
  3. invalid/missing value -> `rdb`

---

## 3) Milestones

### M0: Baseline Hardening (Done)
- RDF export integrity guard added (orphan detection fail-fast).
- SHACL pipeline green and reproducible.
- Alert hook added in validation lane (non-blocking).

### M1: Query-only PoC (Done, Ops Lane)
- Q17 candidate extraction implemented with RDF/SPARQL + RDB hydration.
- Artifact output: `.../v3-advanced/{run-date}/q17-query-only-poc.json`
- Script:
  - `scripts/ops/rdf/query_v3_advanced_q17_poc.py`
  - `scripts/ops/rdf/query_v3_advanced_q17_poc.sh`

### M2: Shadow Mode (Next)
- Add runtime-internal shadow execution for Q17:
  - primary answer from existing RDB path
  - parallel RDF candidate run (non-user-facing)
  - compare candidate overlap and status parity in logs
- Cohort tagging for parity analytics:
  - `NORMAL`, `CAP_OVERFLOW`, `FALLBACK_OTHER` (`timeout/error`)
- Exit criteria:
  - sample size >= 500 requests (and >= 50 per top drama in replay set)
  - status coverage minimum:
    - `SPOILER_BLOCKED` samples >= 30
    - `NOT_ENOUGH_DATA` samples >= 30
  - `answerabilityStatus` exact-match rate >= 99.5%
  - Status parity metrics are computed on `NORMAL` cohort only.
  - `CAP_OVERFLOW` cohort parity is reported separately as reference.
  - `evidenceEventIds` overlap (Jaccard) >= 0.85
  - Jaccard definition lock:
    - both empty -> `1.0`
    - exactly one empty -> `0.0`
    - both non-empty -> `|A∩B| / |A∪B|`
  - Evidence parity evaluation applies only when `answerabilityStatus` exact-match is true.
  - no latency regression above agreed budget (`endpointP95RegressionLimit`)

### M3: Opt-in Serve Mode (Next)
- Add config flag for Q17 source selection:
  - `rdb` (default)
  - `rdf-candidate` (opt-in)
  - `auto-fallback` (recommended)
- Keep fallback mandatory.

### M4: Production Promotion (Later)
- Promote selected tenant/environment to `auto-fallback`.
- Observe for 1 release window.
- If stable, expand to additional Level 4 paths (Q16/Q19 candidates first).

---

## 4) Acceptance Gates

Gate A: Functional parity
- `answerabilityStatus` parity with RDB baseline for target replay set.
- Probe mapping equivalence is enforced (contract-locked, not heuristic).
- `evidenceEventIds` shape and masking policy unchanged.
- `NOT_ENOUGH_DATA` parity requires both paths to return `evidenceEventIds=[]` (not null, not omitted).

Gate B: Safety
- Runtime gate parity (`K + APPROVED`) proven in source=`rdf-candidate`.
- Fallback success rate and error handling validated.
- Candidate cap overflow handling verified (`maxCandidateEventIds` 초과 시 강제 fallback).
- When candidate cap overflow triggers fallback, the request is counted as
  `sourceUsed=rdb-fallback` and excluded from RDF-vs-RDB evidence overlap evaluation.
- `candidateCapOverflowRate` must remain <= 5% on the replay/observation window
  (overflow rate above threshold blocks promotion to `auto-fallback`).

Gate C: Performance
- P95 latency within budget vs current RDB path.
- No sustained increase in DB load from hydration stage.
- Budget values for Q17:
  - RDF candidate soft timeout 120ms, hard timeout 300ms, retry 0
  - endpoint P95 regression <= +15%
  - fallback additional latency <= 150ms (post soft-timeout)
- Baseline fix rule:
  - Baseline environment: `staging` (same build/profile as rollout candidate).
  - Baseline window: trailing 7 days before enabling `rdf-candidate`/`auto-fallback`.
  - Baseline sample: Q17 requests only, minimum n=1000 (or keep collecting until n=1000).
  - Baseline aggregation must match rollout parameter distribution
    (`drama_id`, `safeUpToEpisode` buckets, `limit` buckets).

Gate D: Ops readiness
- Alerting + runbook available for RDF query/validation failures.
- On-call can force source to `rdb` without image rebuild/redeploy
  using `EVENT_V3_FORCE_RDB=true` (service restart required).
- Minimum observability fields (log/metric):
  - `sourceMode` (`rdb|rdf-candidate|auto-fallback`)
  - `sourceUsed` (`rdf|rdb-fallback`)
  - `fallbackTrigger` (`NONE|SOFT_TIMEOUT|HARD_TIMEOUT|RDF_QUERY_ERROR|CANDIDATE_CAP_OVERFLOW|HYDRATION_ERROR`)
  - `rdfCandidateCount`
  - `rdfTimeMs`, `hydrateTimeMs`, `totalTimeMs`
  - `answerabilityStatus`

---

## 5) Immediate Next Tasks

Status update (2026-02-24)
- [x] Implement Q17 shadow-mode comparator in event-service (internal log only).
  - refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventV3QueryServiceImpl.java`
- [x] Add source flag with fixed keys:
  - `EVENT_V3_Q17_SOURCE_MODE` (`rdb|rdf-candidate|auto-fallback`, default `rdb`)
  - `EVENT_V3_FORCE_RDB` (`true|false`, default `false`, highest priority)
  - `EVENT_V3_Q17_RDF_KG_PATH` (runtime `kg.ttl` path, required for RDF path)
  - refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventV3QueryServiceImpl.java`, `infra/docker-compose.yml`
- [x] Add replay harness for Q17 parity report (status + evidence IDs overlap).
  - refs: `scripts/ops/rdf/replay_v3_advanced_q17_parity.py`, `scripts/ops/rdf/replay_v3_advanced_q17_parity.sh`
- [x] Document rollback command and runbook in ops docs.
  - refs: `fivecircles/docs/ops/event-v3-q17-query-only-runbook.md`
