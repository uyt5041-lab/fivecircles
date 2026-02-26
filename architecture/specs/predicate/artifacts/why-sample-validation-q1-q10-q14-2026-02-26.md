# WHY Sample Validation (Q1 / Q10 / Q14)

기준일: 2026-02-26

비교 기준
- 문서: `04-template-strict-must-matrix.md`, `06-answers-for-productionQs.md`
- FE/실행: `front/common/productionQ/executor.ts`, `useProductionQ.ts`, `ResultPanel.tsx`, `productionQUtils.ts`

## Q1
- 문서 앵커: `#2292`
- FE selected anchor: `BB_Q1_WALTER_FIRST_KILL.evidence_event_id=2292`
- WHY 출력:
  - `answer_event.event_id=2292`
  - `because_chain`은 context CAUSE에서 최대 3-hop
  - 렌더 순서 `CAUSE -> FOCUS -> EFFECT`
- 판정: PASS

## Q10
- 문서 앵커: `#2306`
- FE selected anchor: `BB_Q10_WALTER_FIRST_STRUCTURAL_THREAT.evidence_event_id=2306`
- WHY 출력:
  - strict miss 시 `ANSWERED` 승격 금지(guard 적용)
  - `SPOILER_BLOCKED -> LOCKED`, `NOT_ENOUGH_DATA -> VISIBLE_NO_DATA`
  - context 정렬은 PRECEDES topo + semantic block order
- 판정: PASS

## Q14
- 문서 앵커: `#2923`
- FE selected anchor: `BB_Q14_WALTER_SKYLER_RELATION_BREAK.evidence_event_id=2923`
- WHY 출력:
  - coevents 케이스에서도 동일 WHY 계약(`answer_event/because_chain/reveal_hint/confidence_note`) 적용
  - dedup 시 `FOCUS` 우선
- 판정: PASS

결론
- Q1/Q10/Q14 샘플에서 문서 앵커와 FE WHY 규칙이 정합하다.
- 남은 확장은 QP1(reveal_type 정밀도)에서 문장 강도/표현력만 추가 조정한다.
