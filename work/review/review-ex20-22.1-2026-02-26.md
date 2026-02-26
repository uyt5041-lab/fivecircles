# Review: ex20~ex22.1 Alignment Check (2026-02-26)

## Scope
- Reviewed proposal docs:
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex21-SPO-N-Y.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22-axis-N-Y-scetch.md`
  - `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22.1-ops.md`
- Checked implementation/spec alignment for:
  - relation model, role model, predicate taxonomy, reveal pipeline, RDF/SPARQL lane, runtime endpoints.

## Findings (ordered by severity)

### [HIGH] Role vocabulary mismatch makes ex21/ex22.1 not executable as written
- Proposals require `SUBJECT/OBJECT/PARTICIPANT` (`ex22.1-ops.md:41`, `ex22-axis-N-Y-scetch.md:45`).
- Current code/spec use `INVOLVED/SUBJECT/OBJECT`, not `PARTICIPANT`:
  - `common/.../RoleType.java:9-11`
  - `V6__event_v3_triple_roles.sql:5`
  - `event-v3-api-contract.md:109`
- Impact: if proposal text is implemented literally, API/data contract diverges immediately.

### [HIGH] Role fill policy is not wired in current write path
- Proposal says immediately define role fill rules (`ex22.1-ops.md:39-41`).
- Current create/update hardcode `INVOLVED` only:
  - `EventServiceImpl.java:101-108`, `EventServiceImpl.java:187-194`
- Event create DTO has no subject/object role payload:
  - `EventRequestDTO.java:26-31`
  - `wiki-service EventCreateRequest.java:15-25`
- Impact: SPO-based search/perspective quality cannot improve without upstream contract and ingestion changes.

### [HIGH] ex20 relation-type expansion conflicts with PRECEDES-only runtime
- ex20 proposes extending relation types to `{PRECEDES, REVEALS, CAUSES_STATE, INCREASES_PRESSURE}` and meta field (`ex20-axis.md:69-79`).
- Runtime currently enforces PRECEDES-only traversal/ops:
  - `EventRelationService.java:31-43`
  - `EventQueryServiceImpl.java:55-57`
  - `EventRelationController` PRECEDES-only annotations (`EventRelationController.java:25,36,67`)
- `event_relation` has no `meta` column in schema migrations (`V1__init_event_schema.sql:22-27`, `V7__event_relation_pk_with_type.sql:4-6`).
- Impact: this is a major schema+API+algorithm refactor, not a near-term policy toggle.

### [HIGH] Predicate examples in proposal set are partially outside closed enum
- Proposal examples include direct filters like `AFFILIATION_CHANGE`, `DEATH/EXIT` (`ex20-axis.md:159-169`) and verbs like `COOKS`, `SUSPECTS`, `NEGOTIATES_WITH`, `INCAPACITATES` (`ex21-SPO-N-Y.md:155-170`).
- Closed enum is different (`DIES`, `JOINS`, `LEAVES`, etc.): `PredicateCode.java:13-40`.
- Impact: if implemented literally, query filters fail or require uncontrolled OTHER/suggestion fallback.

### [MEDIUM] Governance claim "Quick20 as SSOT" is not aligned with authority hierarchy
- Proposal claims Quick20 should be SSOT (`ex22-axis-N-Y-scetch.md:7,12,100-103`).
- Official authority order is Notion / notion-origin / specs chain (`specs/README.md:12-53`).
- Impact: decision conflicts are likely unless this is reframed as "query-coverage benchmark" rather than SSOT.

### [MEDIUM] SPARQL "reveal evidence" use case is not yet supported by current RDF export
- Proposal pushes SPARQL for reveal evidence (`ex22.1-ops.md:23-27`, `ex22-axis-N-Y-scetch.md:157-161`).
- Current RDF exporter exports `event`, `event_character(role)`, PRECEDES only; no `event_reveal` triples:
  - `export_v3_advanced.py:68-103`, `177-187`
- Impact: reveal-grounded SPARQL paths are not executable without exporter/schema mapping extension.

### [LOW] Some proposal API labels are stale/ambiguous against current V2 numbering
- Proposal references API aliases like api6/8/10 in mixed context (`ex20-axis.md:193,207`).
- Current contract uses concrete paths and numbering updated in `event-v2-api.md:14-77`.
- Impact: onboarding confusion, but easy doc cleanup.

## What is already aligned
- PRECEDES-only core and K+APPROVED gate are consistent with proposal final ops direction:
  - `ex22.1-ops.md:19-23`
  - `v2.5-unify.md:111-113,139-141`
- SQL as canonical + optional RDF lane is already reflected in V3-Advanced specs and implementation:
  - `event-v3-advanced-rdf-owl.md:26-35,111-119`
  - `EventV3QueryServiceImpl` source-mode + fallback (`217-240`, `312-384`, `1935-1961`)

## Decision
- **REQUEST_CHANGES**
- Reason: docs are directionally valuable, but currently not implementation-ready due to role/predicate/relation-contract mismatches.

## Next actions
1. Normalize term set in proposals: `PARTICIPANT` -> `INVOLVED`, and predicate examples to enum-safe vocabulary.
2. Split roadmap explicitly:
   - Track A (near-term): PRECEDES-only + REVEALS(ATTRIBUTE) + current enum.
   - Track B (expansion): relation type extension (`CAUSES_STATE/INCREASES_PRESSURE`) with schema/API migrations.
3. If SPO filtering is a true goal, add write-path contract first:
   - event create/update payload for per-character role,
   - wiki/intelligence publish path role emission,
   - backfill policy for existing `INVOLVED` rows.
4. For SPARQL reveal-evidence features, extend RDF exporter to include `event_reveal` mapping before UI/API promises.
