# Strict Filters Contract (S1-1)

기준일: 2026-02-26  
범위: Production Q executor/probe strict 경로의 필터 계약 고정

## 1) Allow-list (canonical)
- 질문 템플릿 `strict_must` 허용 키:
  - `predicateCodeAnyOf`
  - `excludePredicateCodeAnyOf`
  - `qAnyOf`
- Probe `strictFilters` 허용 키(실행 DTO):
  - `dramaId`
  - `subjectCharacterId`
  - `withCharacterIds`
  - `aboutCharacterId`
  - `targetCharacterId`
  - `predicateCodeAnyOf`
  - `excludePredicateCodeAnyOf`
  - `qAnyOf`

## 2) AND/OR semantics (S1-1-0)
- `predicateCodeAnyOf` 내부는 OR
- `qAnyOf` 내부는 OR
- 두 집합 사이는 AND
- `excludePredicateCodeAnyOf`는 최종 후보에서 제외(negative filter)

추가 규칙:
- 구현 우선순위는 단일 쿼리 OR 조건을 우선한다.
- API 제약으로 단일 호출이 어려운 경우(예: `api3`가 `q` 단일 문자열 파라미터만 받는 경로), multi-call union + eventId dedupe를 허용한다.
- 선정은 deterministic 정렬(`episodeStart ASC`, `eventId ASC`)로 earliest를 고정한다.

### 2.1) Evaluation order (N1-1)
- strict 평가 순서는 아래를 따른다.
  1. safe window gate(`safeUpToEpisode` / `K`)
  2. source gate(`source_status='APPROVED'`)
  3. predicate include/exclude
  4. keyword(`qAnyOf`)
  5. deterministic pick (`episodeStart ASC`, tie-break `eventId ASC`)

참고:
- probe 경로는 `exists` 판정이므로 마지막 단계가 `pick`이 아니라 `존재 여부`로 귀결된다.

## 3) Shorthand mapping (S1-1-a)
문서/매트릭스 shorthand는 실행 직전에 아래 키로 변환한다.

| Shorthand | Runtime strictFilters key |
| --- | --- |
| `subject=*` | `subjectCharacterId` |
| `with=[*,*]` | `withCharacterIds` |
| `target=*` | `targetCharacterId` |
| `about=*` | `aboutCharacterId` |
| `predicateCodeAnyOf=[...]` | `predicateCodeAnyOf` |
| `excludePredicateCodeAnyOf=[...]` | `excludePredicateCodeAnyOf` |
| `qAnyOf=[...]` | `qAnyOf` |

## 4) Predicate normalization (S1-1-b)
- canonical code는 `PredicateCode` enum(UPPER_SNAKE) 기준
- legacy alias 입력은 `STATUS_CHANGE -> TRANSFORMS`로 정규화
- `TRANSFORMS` 조회는 이행기간 동안 `STATUS_CHANGE` 레거시 저장 row를 함께 매칭하는 호환 규칙을 유지

정책:
- 템플릿(`strict_must`)에는 canonical code만 작성한다.
- 런타임 입력 파라미터에서는 legacy alias를 허용하되 저장/조회 전에 canonical로 정규화한다.

## 5) 구현/검증 포인트
- FE executor: `front/common/productionQ/executor.ts`
- BE probe/query 정규화: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`
- BE 저장 정규화: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`
- 레거시 조회 호환: `services/event-service/src/main/resources/mapper/event/EventMapper.xml`

## 6) 로컬 게이트
- strict 키 allow-list:
  - `fivecircles/test/validate-productionq-strict-keys-gate.py`
- strict predicate code 폐쇄집합:
  - `fivecircles/test/validate-productionq-predicatecode-gate.py`
