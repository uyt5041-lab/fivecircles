# WHY Output Contract (W1/W2/W3)

기준일: 2026-02-26

## 1) Response Schema (W1-1)
`ProductionQRunResult.why`

- `answer_event`
  - `event_id`
  - `predicate_code`
  - `episode_end`
- `because_chain`
  - PRECEDES 기반 event id 배열
- `reveal_hint`
  - reveal 메타(`reveal_type`, `target_type`, `target_id`)가 있을 때만 채움
- `confidence_note`
  - `STRICT_HIT`
  - `STRICT_MISS_PROBE_LOCKED`
  - `STRICT_MISS_NO_DATA`
- `narrative`
  - `what`
  - `why`
  - `evidence`

## 2) Chain Generation Rule (W1-2)
- source: FE context timeline의 `CAUSE` 블록
- ordering: PRECEDES topo sort
- limit: max hop `3`
- exposure: 본문에는 Top1 체인만 노출

## 3) Text Template (W1-3)
- 3문장 고정:
  - `무엇: ...`
  - `왜: ...`
  - `근거: ...`

## 4) Guardrail (W2)
- strict miss에서는 probe 결과가 있어도 `ANSWERED`로 승격하지 않는다.
- strict miss + `probe.existsSafeApproved=true`는 mismatch로 간주하고 `NOT_ENOUGH_DATA` 유지.
- strict miss + `probe.existsAnyApproved=true`는 `SPOILER_BLOCKED`.
- FE view mapping:
  - `SPOILER_BLOCKED -> LOCKED`
  - `NOT_ENOUGH_DATA -> VISIBLE_NO_DATA`

검증
- local gate: `fivecircles/test/validate-productionq-probe-guard.py`

## 5) FE Ordering (W3-1)
- semantic order: `CAUSE < FOCUS < EFFECT`
- dedup priority: `FOCUS` 우선
- 구현 위치: `front/features/qa/components/ProductionQSection/productionQUtils.ts`

## 6) Mismatch Handling Rule (W3-3)
- 계약 위반(순서/태그/상태 매핑) 시
  - 실행/상태 규칙: executor(owner=BE/FE common)
  - 렌더링 순서/라벨: FE(owner=frontend)
  - 문서 기준 갱신: predicate spec owner
