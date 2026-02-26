# Answerset-10 Anchor Promotion Metrics (2026-02-26)

입력
- `fivecircles/architecture/specs/predicate/artifacts/answerset-10.json`

집계 결과
- total questions: `10`
- status=`ANSWERED`: `10`
- `anchor_source=ENUM`: `10`
- `anchor_source=OTHER_SUGGESTION_CANDIDATE`: `0`
- strict miss (`SPOILER_BLOCKED`/`NOT_ENOUGH_DATA`): `0`

승격(RFC) 판단
- 이번 배치에서는 `OTHER+predicate_suggestion` 후보가 없어 enum 승격 RFC 대상이 없다.
- 따라서 answerset 기반 빈도/strict 정답 일치율 산출도 N/A 처리한다.

precision@1 (fallback Top1 vs human answer)
- 표본 수: `0` (`strict miss + fallback 실행` 케이스 없음)
- 결과: `N/A`

결론
- A-1 배치에서는 기존 `PredicateCode`만으로 10/10 ANSWERED를 달성했다.
- 승격 평가는 다음 배치(`answerset-6-expansion`)에서 재측정한다.
