# Event V3-Advanced Specification (RDF/OWL)

Purpose
- Define RDF/OWL adoption as **V3-Advanced** (not V3 core release gate).
- Keep V3 core delivery fast/safe with RDB + existing query/runtime semantics.
- Provide a staged path to gain ontology value without immediate dual-store risk.

Status
- Version tier: `V3-Advanced`
- Release criticality: optional for V3 core release
- Initial audience: ops/review/validation workflow

Authority
- This document is the normative spec for RDF/OWL positioning in V3.
- Supporting implementation notes:
  - `fivecircles/architecture/specs/predicate/rdf-owl-extension-notes.md`
  - Query-only promotion execution plan:
    - `fivecircles/architecture/specs/event-v3-advanced-query-only-plan.md`
  - Manageability/reasoner priority review proposal:
    - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex19-rdf-extension-manageability-review.md`

---

## 1) Positioning Rule

V3 core
- RDB source of truth.
- Existing service contract stability (`/api/event/v1`, `/api/event/v2`) must be preserved.
- V3 Level 4 capability can start with RDB + code path.

V3-Advanced (this spec)
- RDF/OWL is introduced as an extension lane.
- Initial adoption must not block core user-facing runtime path.
- Runtime serving dependency on triple store is deferred until explicit promotion.

---

## 2) Scope and Non-Scope

Scope
- RDF vocabulary/model definition for current domain entities.
- SHACL-based consistency validation pipeline.
- Export and report artifacts for ops/review use.
- Optional promotion path to SPARQL read-path and later dual-store.

Non-scope (initial V3-Advanced)
- Immediate replacement of RDB query/runtime with SPARQL.
- Mandatory dual-write in core transaction path.
- Forcing user-facing endpoints to depend on triple store availability.

---

## 3) Invariants (Must Keep)

- V2/V3 core spoiler gate semantics remain unchanged:
  - `episode_end <= K`
  - `source_status = 'APPROVED'`
- PRECEDES direction policy remains unchanged.
- Existing API compatibility policy remains additive/non-breaking.

---

## 4) Minimal Deliverables (Phase 4 Baseline)

1) `ontology.ttl`
- OWL vocabulary for Event/Character/Relation/Role and related terms.

2) `shapes.ttl`
- SHACL constraints for domain/range, enums, temporal constraints, and role constraints.

3) `kg.ttl`
- Exported RDF sample/output from current RDB state.

4) `report.json`
- SHACL validation report artifact for ops/review.

Artifact location (fixed rule)
- Run folder: `fivecircles/architecture/specs/rdf/artifacts/v3-advanced/{run-date}/`
- `{run-date}` format: `YYYY-MM-DD` (example: `2026-02-23`)
- Each run folder must contain all four files:
  - `ontology.ttl`
  - `shapes.ttl`
  - `kg.ttl`
  - `report.json`
- Latest pointer folder: `fivecircles/architecture/specs/rdf/artifacts/v3-advanced/latest/`
- `latest/` must mirror the most recent successful run with the same four filenames.

---

## 5) Execution Model (Initial)

Exporter lane
- Batch/command process exports RDB snapshots to RDF (`kg.ttl`).

Validator lane
- SHACL-first validation produces `report.json`.

Consumption lane
- Output is consumed by ops/review/quality workflow first.
- User-facing runtime path remains independent from RDF lane.

Reference scripts (local Docker MySQL baseline)
- `scripts/ops/rdf/export_v3_advanced.sh`
- `scripts/ops/rdf/validate_v3_advanced.sh`
- `scripts/ops/rdf/run_v3_advanced_pipeline.sh`

---

## 6) Adoption Levels and Complexity

Level A: Export-only (`+10`)
- RDB stays SoT.
- RDF used for dump/validation/reporting only.

Level B: Query-only (`+30`)
- Selected read paths may use SPARQL.
- RDB remains SoT.

Level C: Dual-store (`+80`)
- Write/sync/recovery/rollback managed across both stores.
- Requires explicit operational readiness gate.

---

## 7) Promotion Gates

Gate A (to Query-only)
- Export + SHACL reports are stable over repeated runs.
- Mapping quality is accepted by review.
- No core runtime regressions introduced.

Gate B (to Dual-store)
- Sync strategy is defined and tested.
- Partial-failure and rollback runbooks are approved.
- Backup/restore and monitoring are proven for both stores.

---

## 8) Acceptance Criteria (V3-Advanced Baseline)

1. Artifacts generated: `ontology.ttl`, `shapes.ttl`, `kg.ttl`, `report.json`.
2. Validation pipeline reproducible in local and server-like environment.
3. Core runtime behavior unchanged when RDF pipeline is unavailable.
4. Ops can inspect validation findings without impacting user APIs.
5. Artifact output path follows fixed rule under `.../rdf/artifacts/v3-advanced/{run-date}/` and `.../latest/`.

---

## 9) Out of Band Notes

- This spec does not alter current Flyway/version order by itself.
- This spec does not mandate `/api/event/v3` SPARQL endpoints in baseline.
