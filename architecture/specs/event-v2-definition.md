# Event V2 Definition (Level 3 Queries)

Source
- proposals/공유-온톨로지레이어구축/ex03-quick20Qs.md

Scope
- V2 implementation targets Level 1–3 questions.
- Level 4 is deferred to V3.
- All user-facing exposure must still respect episode_end <= K.

Level 1 Questions (from ex03)
1. 인물 A가 직접 참여한 모든 사건을 시간순으로 보여줘
2. 인물 A와 인물 B가 함께 등장한 사건만 보여줘
3. 인물 C가 참여한 모든 전투(특정 사건 유형)를 보여줘
4. 이 사건에 직접 등장하는 인물들을 모두 보여줘
5. 특정 사건 유형(전투/배신/공개 등)의 이벤트만 모아서 보여줘

Level 2 Questions (from ex03)
6. 인물 A의 소속이 바뀐 사건들만 보여줘
7. 인물 A가 죽거나 퇴장한 사건만 보여줘
8. 같은 유형의 사건들(배신/전투 등)을 모아 비교해줘
9. 특정 에피소드 범위 안에서 발생한 사건들만 보여줘
10. 이 사건이 어떤 유형(카테고리)에 속하는지 알려줘

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
- QueryType mapping and SQL patterns live in event-v2-plan-map.md.
- API examples are captured in event-v2-api.md.
