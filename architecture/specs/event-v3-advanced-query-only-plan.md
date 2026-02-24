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
- Apply semantic filters in query stage where possible (dramaId, approved, K boundary hints).

2. RDB hydrate step
- Hydrate candidate IDs via existing mapper/service queries.
- Re-apply hard gate in runtime (`episode_end <= K`, `source_status='APPROVED'`) for parity safety.

3. Response assembly
- Return existing V3 contract fields unchanged.
- Keep `evidenceEventIds` as always-array rule.

4. Fallback
- If RDF query fails/timeouts/no source, fallback to existing RDB-only path.
- Log source (`rdf` vs `rdb-fallback`) for observability.

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
- Exit criteria:
  - parity >= target threshold over replay set
  - no latency regression above agreed budget

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
- `evidenceEventIds` shape and masking policy unchanged.

Gate B: Safety
- Runtime gate parity (`K + APPROVED`) proven in source=`rdf-candidate`.
- Fallback success rate and error handling validated.

Gate C: Performance
- P95 latency within budget vs current RDB path.
- No sustained increase in DB load from hydration stage.

Gate D: Ops readiness
- Alerting + runbook available for RDF query/validation failures.
- On-call can force source to `rdb` without deploy.

---

## 5) Immediate Next Tasks

1. Implement Q17 shadow-mode comparator in event-service (internal log only).
2. Add source flag (`rdb`/`rdf-candidate`/`auto-fallback`) with default `rdb`.
3. Add replay harness for Q17 parity report (status + evidence IDs overlap).
4. Document rollback command and runbook in ops docs.
