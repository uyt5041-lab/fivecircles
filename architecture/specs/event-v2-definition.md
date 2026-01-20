# Event V2 Definition (Level 3 Queries)

Source
- proposals/공유-온톨로지레이어구축/ex03-quick20Qs.md

Scope
- V2 implementation targets Level 3 (relation-based traversal) questions.
- Level 1/2 data and filters are assumed as prerequisites.
- All user-facing exposure must still respect episode_end <= K.

Level 3 Questions (from ex03)
11. 이 사건의 원인이 된 이전 사건들을 보여줘
12. 이 사건 이후에 파생된 사건들을 보여줘
13. 인물 A → 사건 X → 인물 B로 이어지는 관계 경로를 보여줘
14. 인물 A와 관계있는 인물들을 모두 보여줘
15. 인물 A가 원인이 된 사건들을 간접 포함해서 보여줘

Implementation Notes
- Use event_relation traversal (PRECEDES/RELATED).
- BFS with hop limit and visited dedup by event_id.
- Apply spoiler policy / episode gate after traversal.
