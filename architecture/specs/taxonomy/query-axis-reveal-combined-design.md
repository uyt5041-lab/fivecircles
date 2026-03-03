# Query Axis Extension Draft: REVEAL + COMBINED

기준일: 2026-03-03

## 1) 목적

- taxonomy dashboard의 상단 query axis(`REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`) 중, 아직 source가 직접 연결되지 않은 `REVEAL`/`COMBINED` 축의 설계 초안을 고정한다.
- `query axis`와 `taxonomy category source`를 분리해, Phase 1의 taxonomy dashboard와 향후 reveal/codebook 레인이 섞이지 않게 한다.
- reveal 축의 SoT, runtime preview source, combined preview 조합 규칙을 문서 기준으로 먼저 고정한다.

비범위
- strict answer selection 로직 변경
- OWL reasoner/SPARQL 도입
- user-facing QA runtime 계약 변경
- reveal 쓰기 파이프라인 재설계

## 2) 관련 문서

- 축 스케치: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`
- 축/커버리지 스케치: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex22-axis-N-Y-scetch.md`
- RDF/taxonomy 레인 경계: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- 현재 대시보드 스펙: `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard.md`
- 현재 대시보드 플랜: `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard-implementation-plan.md`
- reveal 지속 기준서: `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
- reveal routing 기준: `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
- reveal 분류 초안: `fivecircles/architecture/specs/reveals/reveals-classification.md`
- reveal target key SoT: `fivecircles/architecture/specs/reveals/reveal-target-key-codebook.md`
- closure taxonomy SoT: `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- inheritance blueprint: `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
- attribute id cutover plan: `fivecircles/architecture/specs/rdf/attribute-id-lane-cutover-plan.md`

## 3) 고정 결론

### 3.1 query axis와 category source는 다르다

- 상단 query axis(`REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`)는 질문 실행 레이어다.
- 각 axis 내부에서 쓰는 category source는 축마다 다를 수 있다.
- 따라서 현재 `predicate_axis_taxonomy.json`에 있는 상위 분류(`BATTLE`, `ADVERSARY`, `ALLY` 등)는 query axis가 아니라 `PREDICATE axis` 내부 category다.
- 현재 구현/API에서 쓰는 `axisCode`는 legacy 필드명으로 유지되지만, 의미상으로는 `predicate category code`로 읽는다.

### 3.2 `PREDICATE` axis는 group SoT와 tree SoT를 분리한다

- group/filter SoT: `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- tree/visualization SoT(draft): `scripts/ops/rdf/taxonomy/predicate_inheritance.json`
- runtime preview source: `event.predicate_code`, `event.predicate_suggestion`
- 현재 구현된 taxonomy dashboard preview는 group/filter SoT를 기준으로 유지한다.
- tree panel은 후속 cutover에서 tree SoT를 읽는 방향으로 전환한다.

### 3.3 `REVEAL` axis는 codebook-first가 맞다

- semantic/source SoT:
  - allow-list/codebook: `fivecircles/architecture/specs/reveals/reveal-target-key-codebook.md`
  - closure taxonomy: `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- runtime preview source:
  - 기본: `event_reveal`
  - gate/join: `event`, `event_character`
- reveal 축은 `predicate_axis_taxonomy.json`을 재사용하지 않는다.

### 3.4 `COMBINED` axis는 `REVEAL lane + PREDICATE lane`의 조합 preview다

- semantic/source SoT:
  - reveal 쪽은 `target_key` codebook/closure
  - predicate 쪽은 `predicate_axis_taxonomy.json`
- runtime preview source:
  - reveal 조건은 `event_reveal`
  - predicate 조건은 `event`
- 기본 조합 방식은 **같은 event에 두 조건이 동시에 걸리는 intersection preview**로 시작한다.

### 3.5 strict-first 경계는 그대로 유지한다

- 본 문서는 dashboard/운영 preview 설계 문서다.
- `REVEALS`와 `target_key`는 answer selection strict SoT를 대체하지 않는다.
- strict miss 상태에서 reveal hit만으로 `ANSWERED` 승격을 허용하지 않는다.

## 4) Axis별 Source Matrix

| Query Axis | Semantic SoT | Runtime Preview Source | Phase 상태 |
|---|---|---|---|
| `REVEAL` | `reveal-target-key-codebook.md`, `inheritance-closure-taxonomy.phase1.json` | `event_reveal` + `event` + `event_character` | Draft |
| `PREDICATE` | group closure: `predicate_axis_taxonomy.json`, tree: `predicate_inheritance.json` | `event.predicate_code`, `event.predicate_suggestion` | Implemented |
| `COMBINED` | REVEAL SoT + PREDICATE SoT | `event_reveal` join `event` | Draft |
| `PRECEDES` | 별도 taxonomy 없음 | `event_relation(type=PRECEDES)` + `event` | Placeholder |

## 5) `REVEAL` Axis 설계

### 5.1 source 모델

`REVEAL` axis는 아래 두 source를 함께 본다.

1. 의미 축(codebook)
- `target_type=ATTRIBUTE`의 의미는 `target_key`로 본다.
- allow-list는 `reveal-target-key-codebook.md`를 따른다.
- 계층/상속 확장은 `inheritance-closure-taxonomy.phase1.json`을 따른다.

2. 런타임 메타
- 실제 preview hit는 `event_reveal` row를 기준으로 계산한다.
- 필수 조인:
  - `event_reveal.event_id = event.id`
  - optional character filter는 `event_character`로 건다.

### 5.2 category 구성(초안)

`REVEAL` axis의 category는 아래 2종으로 시작한다.

1. `CHARACTER reveal`
- 의미: 정체/동일인/캐릭터 공개
- runtime filter:
  - `event_reveal.target_type = 'CHARACTER'`

2. `ATTRIBUTE reveal`
- 의미: 속성/사실/상태 공개
- runtime filter:
  - `event_reveal.target_type = 'ATTRIBUTE'`
  - `event_reveal.target_key IN expanded_keys`

권장 노드 예시
- `R_CHARACTER_REVEAL`
- `A_STATE_REVEAL`
- `A_MORAL_FRAME_SHIFT`
- `A_VIOLENCE_ADAPTATION`
- `A_RISK_OR_SURVIVAL_MODE`
- `A_RELATIONSHIP_SHIFT`
- `A_EXTERNAL_PRESSURE`
- `A_POINT_OF_NO_RETURN`

주의
- `target_type=ATTRIBUTE`인데 `target_key`가 비어 있는 legacy row는 preview 기본 결과에 포함시키지 않는다.
- 이 row는 drift/diagnostics에서 `unclassified reveal rows`로 따로 보여주는 편이 안전하다.

### 5.3 preview 규칙

- 기본 gate:
  - `event.source_status = 'APPROVED'`
  - optional `event.episode_end <= K`
  - optional `event.drama_id = :dramaId`
  - optional `event_character.character_id = :characterId`
- 정렬:
  - `event.episode_end DESC, event.id DESC`
- reveal strength(`HINT|CONFIRM`)는 preview badge/정렬 보조로는 쓸 수 있지만, 기본 필터의 1급 축으로 승격하지 않는다.

### 5.4 Phase2 read-path 메모

- Phase1/운영 preview는 `target_key` 우선으로 읽는다.
- Phase2 이후에는 `target_key + target_id(attribute.id)` dual-read 검증 후 전환한다.
- 단, 대시보드 UI 계약은 `REVEAL axis` 자체를 유지하고 내부 read-path만 바꾼다.

## 6) `COMBINED` Axis 설계

### 6.1 목적

- 같은 event가
  - 어떤 reveal category를 가지면서
  - 동시에 어떤 predicate category에도 속하는지
를 운영자가 한 번에 검수할 수 있게 한다.

### 6.2 기본 모드

Phase 1.5 기본 모드는 아래 1개로 시작한다.

- `INTERSECTION`
  - 같은 `event_id`가 reveal filter와 predicate filter를 동시에 만족해야 한다.

비범위(후속)
- `CHAIN`
  - answer event와 reveal evidence event를 PRECEDES/MEETS로 묶는 체인형 combined preview
- `RANKED OR`
  - 둘 중 하나만 맞아도 보여주고 점수로 정렬하는 mode

### 6.3 request 초안

```json
{
  "queryAxis": "COMBINED",
  "revealAxisCode": "A_MORAL_FRAME_SHIFT",
  "predicateAxisCode": "BATTLE",
  "previewMode": "RUNTIME",
  "dramaId": 10,
  "characterId": 1,
  "episodeEndMax": 32,
  "sourceStatus": "APPROVED",
  "limit": 20
}
```

### 6.4 response 초안

```json
{
  "queryAxis": "COMBINED",
  "mode": "INTERSECTION",
  "revealAxisCode": "A_MORAL_FRAME_SHIFT",
  "predicateAxisCode": "BATTLE",
  "resolvedRevealKeys": ["A_MORAL_FRAME_SHIFT"],
  "resolvedPredicateCodes": ["ATTACKS", "KILLS"],
  "items": [
    {
      "eventId": 2292,
      "episodeEnd": 3,
      "predicateCode": "KILLS",
      "summary": "월터가 크레이지-8을 살해한다.",
      "matchedRevealKey": "A_MORAL_FRAME_SHIFT",
      "matchedRevealType": "CONFIRM"
    }
  ]
}
```

### 6.5 SQL 해석 원칙

- predicate lane:
  - `event.predicate_code IN resolvedPredicateCodes`
  - fallback 탭에서는 `predicate_suggestion` fallback을 별도 lane으로만 사용
- reveal lane:
  - `exists (select 1 from event_reveal er where er.event_id = event.id and ...)`
- combined intersection:
  - 한 event가 두 lane을 동시에 만족하는지 `EXISTS + predicate filter`로 판정

## 7) API 확장 초안

현재 API를 깨지 않고 아래처럼 확장하는 방향을 권장한다.

### 7.1 tree API

- 현행:
  - `GET /api/event/taxonomy/tree`
- 확장 초안:
  - `GET /api/event/taxonomy/tree?queryAxis=PREDICATE|REVEAL`

원칙
- `PREDICATE`면 현재 구현을 그대로 사용한다.
- `REVEAL`이면 reveal category/codebook tree를 반환한다.
- `COMBINED`는 tree 단일 응답보다 두 source 선택 UI가 자연스럽기 때문에 별도 tree 응답을 강제하지 않는다.

### 7.2 preview API

- 현행:
  - `POST /api/event/taxonomy/preview`
- 확장 초안:
  - request body에 `queryAxis` 추가
  - `REVEAL`일 때 `revealAxisCode`
  - `COMBINED`일 때 `revealAxisCode + predicateAxisCode`

### 7.3 drift API

drift는 Phase를 나눠서 보는 편이 낫다.

1. predicate drift
- 지금 구현된 `taxonomy vs enum vs RDB`

2. reveal drift
- `target_key` allow-list 밖 값
- `target_type=ATTRIBUTE`인데 `target_key` 누락
- closure taxonomy에 없는 key

3. combined drift
- 별도 SoT drift보다는 조합 preview 0건/과다건을 운영 점검 항목으로 본다.

## 8) UI 초안

### 8.1 상단 query axis

- `REVEAL`
- `PREDICATE`
- `COMBINED`
- `PRECEDES`

### 8.2 좌측 source panel

- `PREDICATE`
  - 현재 구현된 predicate taxonomy category list
- `REVEAL`
  - reveal category/codebook list
- `COMBINED`
  - 좌측 2단 selector
  - reveal category 1개 + predicate category 1개를 함께 선택

### 8.3 우측 preview panel

- runtime / fallback 탭 분리 유지
- combined에서도 fallback은 predicate lane에만 붙인다.
- fallback row에는 현재 정책대로 `FALLBACK MATCH` 라벨을 유지한다.

## 9) 구현 순서 제안

1. `TD9-3` 범위
- query axis와 source boundary를 본 문서 기준으로 고정

2. REVEAL axis source
- `GET /api/event/taxonomy/tree?queryAxis=REVEAL`
- reveal drift 진단 추가

3. REVEAL preview
- `queryAxis=REVEAL` preview 구현
- `event_reveal` gate/diagnostics 정리

4. COMBINED preview
- `INTERSECTION` mode만 먼저 구현
- fallback 탭은 predicate lane에만 연결

## 10) 수용 기준

- 팀 문서에서 `axis`와 `predicate taxonomy category`를 더 이상 같은 말로 쓰지 않는다.
- `REVEAL axis`의 SoT가 `predicate_axis_taxonomy.json`이 아니라 `target_key` codebook/closure임이 명시된다.
- `COMBINED axis`가 reveal lane과 predicate lane의 조합 preview라는 점이 문서로 고정된다.
- strict-first answer selection과 dashboard preview가 다른 레인이라는 점이 명시된다.
