# Inheritance Blueprint Examples (Codebook + Minimal Schema)

기준일: 2026-02-27  
범위: Phase1 운영(테이블 추가 최소)에서 바로 적용 가능한 예시만 다룬다.

연결 문서:
- `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
- `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`

## 1) 핵심 전제
- strict 정답 탐색은 기존 `PredicateCode + StrictQuerySpec` 경로 유지
- reveal 확장은 `event_reveal.target_key` 코드북으로 수행
- `target_type=ATTRIBUTE`일 때 `target_id`는 현행처럼 aboutCharacterId로 사용
- `source_status='APPROVED'`, `episode_end <= K` 게이트 유지

## 2) 최소 스키마 확장 예시

```sql
ALTER TABLE event_reveal
  ADD COLUMN target_key VARCHAR(64) NULL COMMENT 'ATTRIBUTE semantic key (A_*)';

CREATE INDEX idx_event_reveal_type_key ON event_reveal(target_type, target_key);
CREATE INDEX idx_event_reveal_type_target ON event_reveal(target_type, target_id);
```

운영 규칙:
- `target_type=CHARACTER`: `target_key`는 NULL
- `target_type=ATTRIBUTE`: `target_key` 필수 권장
- `reveal_type`: `HINT|CONFIRM`만 허용

## 3) 코드북 상속 확장 예시

예시 맵(문서/코드 상수):

```ts
const revealKeyEdges: Array<[string, string]> = [
  ['A_STATE_REVEAL', 'A_MORAL_FRAME_SHIFT'],
  ['A_MORAL_FRAME_SHIFT', 'A_SELF_JUSTIFICATION_ON'],
  ['A_MORAL_FRAME_SHIFT', 'A_KILLING_AS_OPTION_ON'],
  ['A_MORAL_FRAME_SHIFT', 'A_GUILT_SUPPRESSED'],
];
```

질문이 `A_MORAL_FRAME_SHIFT`를 요구하면:
- 확장 결과: `A_MORAL_FRAME_SHIFT`, `A_SELF_JUSTIFICATION_ON`, `A_KILLING_AS_OPTION_ON`, `A_GUILT_SUPPRESSED`
- B-lane 필터에서 `target_key IN (...)` 사용

## 4) Q01_EXP_01 B-lane 조회 예시

```sql
SELECT DISTINCT e.id, e.summary, e.episode_start, e.episode_end, e.predicate_code
FROM event e
JOIN event_character ec ON ec.event_id = e.id
JOIN event_reveal er ON er.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.source_status = 'APPROVED'
  AND e.episode_end <= :K
  AND ec.character_id = :subjectCharacterId
  AND er.target_type = 'ATTRIBUTE'
  AND er.target_id = :aboutCharacterId
  AND er.target_key IN (:expandedAttributeKeys)
ORDER BY e.episode_start ASC, e.episode_end ASC, e.id ASC;
```

설명:
- `er.target_id`는 aboutCharacterId(현행 계약)
- 의미 구분은 `target_key`로 수행

## 5) C-lane 조회 예시 (현행 PredicateCode)

```sql
SELECT DISTINCT e.id, e.summary, e.episode_start, e.episode_end, e.predicate_code
FROM event e
JOIN event_character ec ON ec.event_id = e.id
WHERE e.drama_id = :dramaId
  AND e.source_status = 'APPROVED'
  AND e.episode_end <= :K
  AND ec.character_id = :subjectCharacterId
  AND e.predicate_code IN (:expandedPredicateCodes)
ORDER BY e.episode_start ASC, e.episode_end ASC, e.id ASC;
```

## 6) WHY payload 예시 (strict-first 유지)

```json
{
  "answer_event": { "event_id": 2292, "predicate_code": "KILLS", "episode_end": 3 },
  "because_chain": [2289, 2291, 2292],
  "reveal_hint": [
    {
      "event_id": 2291,
      "target_type": "ATTRIBUTE",
      "target_id": 17,
      "target_key": "A_SELF_JUSTIFICATION_ON",
      "reveal_type": "CONFIRM"
    }
  ],
  "confidence_note": "STRICT_HIT"
}
```

규칙:
- `reveal_type`는 카드 강도 표시에만 사용
- strict miss이면 `reveal_hint`가 있어도 `ANSWERED` 승격 금지

## 7) 구현 체크리스트 (파일 단위)

1. `event_reveal`에 `target_key` 추가 + 인덱스 생성  
2. 입력/검증 경로에서 `target_type=ATTRIBUTE`일 때 `target_key` allow-list 검증 추가  
3. `inheritancePhase1.ts`의 B-lane 바인딩을 `target_id` 단독 매칭에서 `target_key` 중심 매칭으로 전환  
4. `executor.ts`에서 WHY `reveal_hint`에 `target_key` 노출  
5. `source_status`/episode gate/strict-first 승격 금지 규칙 회귀 확인

## 8) 비고
- 이 문서는 Phase1 기준이다.
- `attribute`/`attribute_closure` 테이블은 Phase3 승격 후보이며, 지금은 도입하지 않는다.
