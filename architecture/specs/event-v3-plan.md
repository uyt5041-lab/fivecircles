# Event V3 Implementation Plan (Reinforced: V2.5 -> V3 -> RDF/OWL)

Purpose
- Define the minimum required path from V2.5 to V3.
- Add RDF/OWL as a follow-up lane without breaking current service behavior.
- Keep V2 query semantics stable while enabling Level 4 capability.

Scope
- Primary: event-service
- Follow-up lane: RDF/OWL export/validation artifacts (non-user-facing first)

Invariants (Must Keep)
- Exposure queries must apply `episode_end <= :K` AND `source_status = 'APPROVED'`.
- PRECEDES direction is fixed: `from=previous`, `to=next` (reverse uses `to_event_id`).
- V3 does not introduce new relation types such as CAUSES; PRECEDES remains the temporal edge.

## 0) Current Baseline (Already Implemented)

1) SSOT schema baseline is full-sync dump.
- Baseline schema (authoritative): `scripts/ops/2026-02-23-full-sync.sql`
- `event_character.role` default: `INVOLVED`
- Existing index: `idx_ec_role_character (character_id, role)`
- Historical migration provenance: `V6__event_v3_triple_roles.sql` (reference only, not readiness baseline)

2) Runtime is already role-aware through V2 APIs.
- `GET /api/event/v2/events/{eventId}/characters` returns `{ characterId, role }`.
- Entity/DTO/mapper/service paths are already reading/writing role.

3) Public service versions currently in use.
- `/api/event/v1`: CRUD/search
- `/api/event/v2`: query/traversal
- `/api/event/v3`: not released yet

## 1) V2.5 -> V3 Mandatory Work

### 1-1. DB Layer

Required
- No new mandatory role migration if target environment already matches full-sync baseline schema.
- Migration scripts are treated as environment alignment/idempotent tools, not release-readiness source of truth.

Optional (performance tuning only, with evidence)
- Consider adding composite index `(event_id, role, character_id)` if role-filtered event-local queries become hot.
- Keep current index unless profiling proves benefit.

### 1-2. Backend Layer

Required
- Keep role behavior backward-compatible:
  - role omitted -> `INVOLVED` default
  - existing V2 endpoints continue returning compatible payloads
- Preserve spoiler gate and PRECEDES traversal semantics exactly as V2.

Required checks (code-level)
- EVENT_CHARACTERS path returns `character_id + role` under event join gate.
- BFS/traversal applies K+APPROVED during expansion (safe traversal).

### 1-3. API Contract

Principle: Minimal-change contract
- Do not break existing v1/v2 responses.
- Additive fields only where needed.
- V3 API surface (`/api/event/v3/**`) should start as opt-in for Level 4 capability.
- Normative contract for Q16~Q20: `fivecircles/architecture/specs/event-v3-api-contract.md`
- Response boundary normalization for V3:
  - `evidenceEventIds` MUST be serialized as array (`[]` allowed), never `null`.
  - Internal service merge/default paths may use `null`, but controller/DTO boundary must normalize before response.
- Release positioning:
  - V3 core MVP: minimal Q16~Q20 endpoints + strict spoiler gate
  - V3 full quality: richer explainability/modeling follows after MVP gate

### 1-4. Verification Checklist (Release Gate)

1. Baseline role readiness
- In all target environments, schema aligns with full-sync baseline (`2026-02-23-full-sync.sql`) for `event/event_character/event_relation`.
- At minimum, `event_character.role` exists and defaults to `INVOLVED`.

2. Safety gate integrity
- EVENT_CHARACTERS never exposes rows outside `K` or non-APPROVED events.

3. Safe traversal integrity
- PRECEDES BFS enforces K+APPROVED during expansion, not only post-filter.

4. Performance guardrail
- No material regression on character->event reverse lookup and path traversal.

5. Role cardinality/ordering correctness
- One role value per `(event_id, character_id)` row (PK-based uniqueness preserved).
- Response ordering is deterministic when role is present.

6. V2 semantic stability
- Q1~Q15 and V2.5 Q20 outputs stay equivalent pre/post V3 changes (except additive role metadata).

7. RDF lane isolation (non-blocking guarantee)
- If RDF exporter/validator is unavailable, `/api/event/v1` and `/api/event/v2` behavior remains unchanged.
- V3 core release gate must not be blocked by RDF lane failures.

8. Spoiler masking integrity (Level 4 sensitive paths)
- If `existsSafeApproved=false` and `existsAnyApproved=true`, response must be `SPOILER_BLOCKED`.
- In `SPOILER_BLOCKED`, future event summary/title/details must not leak to user-facing payload.

9. Level 4 endpoint contract integrity
- Q16~Q20 endpoints must return `answerabilityStatus` and `evidenceEventIds` per V3 API contract.
- `evidenceEventIds` shape is stable array in all states (`ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA`), with `[]` when unavailable.

10. DTO baseline governance
- Q16~Q20 response shape must conform to baseline examples in `event-v3-api-contract.md`.
- DTO evolution is allowed, but release requires spec update first (to keep FE/BE aligned).

### 1-5. Q16~Q20 Endpoint Acceptance Map (MVP)

- Q16 (Character Rise): `GET /api/event/v3/characters/{characterId}/rise`
  - Required: anchors + evidence IDs under K+APPROVED gate.
- Q17 (Foreshadowed): `GET /api/event/v3/dramas/{dramaId}/foreshadowed`
  - Required: blocked-state masking with `SPOILER_BLOCKED`.
- Q18 (Perspectives): `GET /api/event/v3/events/{eventId}/perspectives`
  - Required: role-based perspective split (`INVOLVED|SUBJECT|OBJECT`).
- Q19 (Conflict Axes): `GET /api/event/v3/dramas/{dramaId}/conflict-axes`
  - Required: axis grouping payload with evidence IDs.
- Q20 (Narrative Distribution): `GET /api/event/v3/characters/{characterId}/narrative-distribution`
  - Required: distribution + explainability evidence.

### 1-6. Regression Repro Procedure (Release Gate)

Baseline dataset
- Use fixed local dump baseline: `scripts/ops/2026-02-23-full-sync.sql`.

Minimum execution checklist
1. Verify v1/v2 regression set (Q1~Q15 + V2.5 Q20) remains stable.
2. Verify V3 Q16~Q20 endpoints return contract fields (`answerabilityStatus`, `evidenceEventIds`).
3. Verify sensitive-path probe mapping (`ANSWERED | SPOILER_BLOCKED | NOT_ENOUGH_DATA`) is deterministic.
4. Record commands/results in `fivecircles/work/update.md` before release sign-off.

## 2) RDF/OWL Follow-up (Phase 4 Lane)

Goal
- Reuse current RDB model (`Event/Character/Relation/role/K-gate`) as RDF artifacts for standardization and validation.
- Start without adding user-facing runtime dependency.
- Classification: this lane is governed as **V3-Advanced**.
- Normative spec: `fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`
- V3-Advanced target goal: Query-only (`RDF query + RDB hydration`) for selected Level 4 read-paths.
- Query-only execution plan: `fivecircles/architecture/specs/event-v3-advanced-query-only-plan.md`

### 2-1. Minimum Artifacts

1. `ontology.ttl`
- OWL vocabulary for Event/Character/Relation/Role terms.

2. `shapes.ttl`
- SHACL constraints (domain/range, enum, temporal constraints, role constraints).

3. `kg.ttl`
- Exported RDF sample from current RDB state.

4. `report.json`
- SHACL validation report for operations/review.

### 2-2. Execution Model (No New Service at Start)

- Exporter (batch/command): RDB -> `kg.ttl`
- Validator (SHACL-first): `kg.ttl` -> `report.json`
- Initial output target: ops/validation workflow (not end-user UI path)

### 2-3. Relation to Level 4 Queries

- Level 4 remains deliverable with RDB + code for initial V3 rollout.
- RDF/OWL first provides value in:
  - schema governance
  - consistency validation
  - explainability artifacts
- SPARQL-driven runtime path is a planned promotion target for V3-Advanced (Query-only), but not part of mandatory V3 core release gate.

### 2-4. Adoption Levels (Decision Aid)

- Export-only: complexity +10
  - RDB is source of truth, RDF for dump/validation/reporting.
- Query-only: complexity +30
  - Selected SPARQL read paths, but RDB remains source of truth.
- Dual-store: complexity +80
  - Operational sync/rollback/recovery across both stores.

## 3) Recommended Shortest Path

1. Close V3 release gate with current role baseline + regression/safety/perf validation.
2. Release V3 core MVP `/api/event/v3/**` contract for Level 4 entrypoints (Q16~Q20).
3. Add RDF exporter + SHACL validator artifacts (`ontology.ttl`, `shapes.ttl`, `kg.ttl`, `report.json`).
4. Promote selected V3 read-paths to Query-only (`RDF candidate query -> RDB hydration`) while keeping contract stable.
5. Keep fallback and gate parity (`K + APPROVED`) to avoid runtime regression during Query-only adoption.
