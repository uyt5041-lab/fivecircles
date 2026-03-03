# Taxonomy Dashboard Specification

기준일: 2026-03-03

## 1) 목적

- ontology 형식으로 관리되는 taxonomy/inheritance 레이어를 운영자가 눈으로 검증할 수 있는 대시보드를 정의한다.
- 대시보드 상단에는 질문 실행용 query axis(`REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`)를 모두 표시한다.
- 현재 taxonomy JSON이 직접 커버하는 범위는 `PREDICATE` axis 내부 category임을 명시한다.
- taxonomy 선택 결과가 실제 event 필터 결과로 어떻게 펼쳐지는지 preview할 수 있어야 한다.
- taxonomy 정의, runtime 전개 결과, 런타임 enum/RDB 사이의 drift를 점검할 수 있어야 한다.

## 2) 위치와 경계

### 2.1 페이지 위치
- 페이지는 admin 프론트에 둔다.
- 이 페이지는 운영/검수 도구이며 일반 사용자 QA 화면에 포함하지 않는다.

### 2.2 API 위치
- API는 `event-service`에 둔다.
- endpoint prefix는 다음으로 고정한다.
  - `GET /api/event/taxonomy/tree`
  - `POST /api/event/taxonomy/preview`
  - `GET /api/event/taxonomy/drift`

### 2.3 책임 분리
- admin 프론트는 시각화와 조작만 담당한다.
- taxonomy 해석, closure 전개, preview 조회, drift 계산은 `event-service`가 담당한다.
- 이 구조는 precedes 운영 페이지와 같은 방향으로 유지한다.

## 3) 운영 원칙

### 3.1 SoT
- Phase 1 taxonomy lane SoT는 `predicate_axis_taxonomy.json`이다.
- 대시보드는 원본 TTL/OWL을 직접 해석하지 않는다.
- 대시보드의 기본 입력은 다음 파일을 사용한다.
  - `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- 이 파일은 현재 `predicateCode/predicateSuggestion` 상속/분류 체계만 표현한다.
- 즉 Phase 1 taxonomy source는 `REVEAL` axis 전체를 직접 다루지 않는다.
- 추후 필요하면 generated taxonomy map을 추가할 수 있지만, 현재 구현 기본값은 direct load다.

### 3.2 런타임 경계
- 이 대시보드는 QA 정답 탐색 런타임의 strict-first 경로를 대체하지 않는다.
- 실제 preview 결과는 최종적으로 RDB 필터 결과를 보여준다.
- triple store, reasoner, SPARQL endpoint 가용성은 본 대시보드의 필수 의존성이 아니다.
- `REVEAL`/`COMBINED` axis의 SoT/source 경계는 `fivecircles/architecture/specs/predicate/query-axis-reveal-combined-design.md`를 따른다.

### 3.3 운영 가드
- preview는 운영 검수용이므로 user-facing spoiler gate와 별도 경계에 둔다.
- 단, 기본 필터는 다음을 유지한다.
  - `source_status = APPROVED`
  - `episode_end` 범위 필터 지원

## 4) 핵심 사용자 시나리오

1. 운영자가 상단 query axis(`REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`) 중 하나를 선택한다.
2. `PREDICATE` axis를 선택한 경우, 시스템은 predicate taxonomy category 목록을 보여준다.
3. 시스템은 선택 category의 closure leaf 목록을 계산해서 보여준다.
4. 운영자가 drama, character, episode 범위를 추가 선택한다.
5. 시스템은 해당 leaf 목록을 `predicate_code IN (...)` 형태로 RDB preview 질의로 변환한다.
6. 운영자는 매칭 이벤트와 개수를 보고 taxonomy 분류가 기대대로 동작하는지 검수한다.
7. 운영자는 drift 탭에서 미분류 코드, 누락 코드, 중복/순환 이상 여부를 확인한다.

## 5) 화면 구성

### 5.1 Query Axis Panel
- 상단에서 질문 실행용 query axis를 모두 표시한다.
- 최소 노출 축:
  - `REVEAL`
  - `PREDICATE`
  - `COMBINED`
  - `PRECEDES`
- Phase 1에서 실제 taxonomy category/preview가 연결되는 축은 `PREDICATE`다.

### 5.2 Category Panel
- `PREDICATE` axis 선택 시 taxonomy/inheritance category 목록을 표시한다.
- 각 category 노드는 다음 정보를 가진다.
  - `axisCode` (category code)
  - label
  - kind(axis/category)
  - descendant leaf count
  - optional matched event count

### 5.3 Preview Filter Panel
- 현재 선택 query axis 표시
- `PREDICATE`일 경우 현재 선택 category 표시
- 추가 필터:
  - `dramaId` optional
  - `characterId` optional
  - `episodeEndMax` optional
  - `sourceStatus` default `APPROVED`
  - `limit` default `20`

### 5.4 Result Preview Panel
- 컬럼:
  - `eventId`
  - `episodeEnd`
  - `predicateCode`
  - `summary`
  - `characters`
- row click 시 event detail drawer 또는 detail panel을 연다.
- detail에는 최소한 다음을 노출한다.
  - event 기본 정보
  - 참여 character
  - relation 요약
  - reveal 요약이 있으면 함께 표시
- fallback preview를 도입할 경우 기본 preview와 분리된 tab으로 노출한다.
- fallback으로 매칭된 결과에는 `FALLBACK MATCH` 라벨을 명시한다.
- `REVEAL`, `COMBINED`, `PRECEDES` axis는 Phase 1에서 placeholder/info panel로 먼저 노출할 수 있다.
- `REVEAL` axis용 category source와 `COMBINED` intersection preview는 후속 Phase에서 `query-axis-reveal-combined-design.md` 기준으로 연결한다.

### 5.5 Drift Panel
- 진단 항목:
  - taxonomy에는 있으나 runtime enum/RDB에 없는 code
  - RDB에는 있으나 taxonomy에 분류되지 않은 code
  - closure 전개 결과의 빈 leaf
  - 중복 leaf
  - 순환 또는 비정상 parent-child 정의

## 6) API Specification

### 6.1 `GET /api/event/taxonomy/tree`

목적
- admin 페이지가 `PREDICATE` axis용 taxonomy category와 기본 메타를 렌더링할 수 있도록 한다.

response 초안
```json
{
  "version": "2026-03-03",
  "source": "predicate_axis_taxonomy.json",
  "nodes": [
    {
      "axisCode": "BATTLE",
      "label": "Moral Frame Shift",
      "kind": "AXIS",
      "impliesAxes": ["ADVERSARY"],
      "resolvedPredicateCodes": ["KILLS", "ATTACKS"],
      "resolvedPredicateSuggestions": ["BATTLE"],
      "descendantLeafCount": 2
    }
  ]
}
```

규칙
- server는 `predicate_axis_taxonomy.json`을 직접 읽고 `impliesAxes`를 재귀 전개한다.
- leaf는 runtime filter에 바로 사용할 수 있는 `predicateCode` 집합으로 반환한다.
- generated taxonomy map은 future option이며 Phase 1 필수 입력이 아니다.
- 이 endpoint는 Phase 1에서 `PREDICATE` query axis의 category source를 제공한다.

### 6.2 `POST /api/event/taxonomy/preview`

목적
- 선택한 axis/leaf가 실제 event 결과로 어떻게 매칭되는지 preview한다.
- Phase 1에서는 `PREDICATE` query axis 아래 category preview에 한정한다.

request 초안
```json
{
  "axisCode": "A_MORAL_FRAME_SHIFT",
  "dramaId": 10,
  "characterId": 1,
  "episodeEndMax": 32,
  "sourceStatus": "APPROVED",
  "limit": 20
}
```

response 초안
```json
{
  "axisCode": "A_MORAL_FRAME_SHIFT",
  "resolvedPredicateCodes": ["KILLS", "ATTACKS"],
  "resolvedPredicateSuggestions": ["BATTLE"],
  "total": 14,
  "items": [
    {
      "eventId": 2292,
      "episodeEnd": 3,
      "predicateCode": "KILLS",
      "summary": "월터가 크레이지-8을 목 졸라 죽인다.",
      "characters": ["월터 화이트", "크레이지-8"]
    }
  ]
}
```

규칙
- server는 `axisCode -> resolvedLeafCodes` 전개를 먼저 수행한다.
- preview 조회는 최종적으로 RDB에서 수행한다.
- 기본 정렬은 `episode_end DESC, event_id DESC`를 권장한다.
- `axisCode`가 leaf인 경우에도 동일 endpoint를 사용한다.
- fallback preview는 기본 runtime `predicate_code` preview와 응답 또는 UI 탭을 분리한다.
- fallback 결과를 노출할 때는 각 row 또는 응답 메타에 `fallback match` 여부를 명시해야 한다.

SQL 해석 원칙
- 핵심 필터:
  - `predicate_code IN (...)`
  - `source_status = 'APPROVED'`
  - optional `episode_end <= :episodeEndMax`
  - optional `drama_id = :dramaId`
  - optional `character_id = :characterId`

### 6.3 `GET /api/event/taxonomy/drift`

목적
- taxonomy 정의와 실제 운영 데이터/코드 사이의 어긋남을 진단한다.

response 초안
```json
{
  "missingPredicateCodesInEnum": ["BETRAYS"],
  "unclassifiedPredicateCodesInTaxonomy": ["PRODUCES"],
  "duplicateResolvedPredicateCodes": [],
  "cycles": [],
  "emptyAxes": ["A_TEMP_UNUSED"]
}
```

규칙
- drift는 운영자가 즉시 조치 가능한 형태로 항목별 배열을 반환한다.
- 상세 설명 문자열보다 코드 리스트와 count를 우선 제공한다.

## 7) 서버 구현 원칙

### 7.1 Controller/Service 경계
- controller는 request validation과 response shaping만 수행한다.
- taxonomy 전개 로직은 별도 service/component로 분리한다.
- preview SQL은 event query mapper/repository 계층에서 담당한다.

### 7.2 데이터 소스 우선순위
1. `predicate_axis_taxonomy.json`
2. runtime enum/closed set
3. RDB event data

- 원본 TTL/OWL은 build/ops 입력이며 dashboard runtime 입력이 아니다.

### 7.3 장애 허용
- taxonomy JSON 로드 실패 시 user-facing API에는 영향이 없어야 한다.
- dashboard API 실패는 admin 기능 장애로 한정되어야 한다.

## 8) 프론트 구현 원칙

### 8.1 페이지 역할
- admin 프론트는 tree selection, filter form, result table, drift diagnostics를 제공한다.
- query axis와 taxonomy category를 혼동하지 않도록 용어를 분리한다.
- 데이터 해석은 API 응답을 그대로 사용하고 프론트의 독자적 taxonomy 추론은 최소화한다.

### 8.2 UX 원칙
- tree에서 노드 선택 시 preview를 자동 조회하거나 명시적 버튼으로 조회할 수 있다.
- drift 결과는 severity 또는 category별로 분리해 한눈에 보이게 해야 한다.
- 결과 table은 CSV export 또는 event id 복사 기능을 제공할 수 있다.

## 9) Non-Goals

- 일반 사용자 질문/답변 UI와의 직접 통합
- strict-first answer selector를 taxonomy dashboard로 대체
- Fuseki/SPARQL endpoint를 필수 런타임 의존성으로 도입
- ontology 편집기까지 본 범위에 포함

## 10) Acceptance

1. admin 페이지에서 query axis 4종을 모두 볼 수 있다.
2. `PREDICATE` axis 선택 시 taxonomy category 목록을 볼 수 있다.
3. 선택한 category의 resolved leaf code 목록을 확인할 수 있다.
4. preview 결과로 event count와 샘플 이벤트를 확인할 수 있다.
5. drift 결과에서 taxonomy/RDB/enum 어긋남을 확인할 수 있다.
6. user-facing event/QA runtime은 dashboard 부재 또는 실패와 무관하게 정상 동작한다.

## 11) 참조

- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex24-toxonomy-dashboard.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex19-rdf-extension-manageability-review.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
