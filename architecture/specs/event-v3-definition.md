# Event V3 Definition (Level 4 Capability)

Source
- proposals/공유-온톨로지레이어구축/ex03-quick20Qs.md

Purpose
- Define V3 as a **capability target** for Level 4 reasoning/analytics.
- Keep current V2 behavior stable while preparing V3 semantics incrementally.

Current Runtime Status (As Implemented)
- Public event APIs are currently exposed as:
  - `/api/event/v1` (CRUD/search)
  - `/api/event/v2` (query/traversal)
- There is no dedicated `/api/event/v3` endpoint yet.
- V3 should currently be interpreted as:
  - data/model readiness + Level 4 capability backlog,
  - not a released API version.

V3 Capability Scope
- Requires additional semantics or aggregation beyond V2 traversal.
- Uses triple-role semantics (`event_character.role`) as a foundational building block.

Level 4 Questions (from ex03)
16. 인물 A가 어떤 사건들을 통해 중요 인물로 부상했는지 보여줘
17. 아직 직접 등장하지 않았지만, 필연적으로 예고된 사건들은 무엇인가
18. 같은 사건을 서로 다른 인물 관점에서 재구성해줘
19. 서로 다른 에피소드지만 동일한 갈등 축에 속한 사건들을 묶어줘
20. 특정 인물의 서사가 어떤 사건 카테고리에 가장 많이 걸쳐 있는지 분석해줘

Implementation split note
- Q20 has a basic aggregate path in V2.5 (`predicate_code` distribution on character events).
- V3 scope for Q20 is advanced interpretation/explainability beyond simple distribution.

Invariants (Carry-over from V2)
- Exposure queries must apply `episode_end <= K` and `source_status = 'APPROVED'`.
- PRECEDES direction is fixed (`from=previous`, `to=next`).
- V3 does not introduce a CAUSES edge type; causes/effects remain PRECEDES interpretation.

Notes
- Level 4 questions remain non-MVP unless extra labeling/modeling is added.
