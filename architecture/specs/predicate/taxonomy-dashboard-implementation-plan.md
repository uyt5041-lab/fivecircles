# Implementation Plan: Taxonomy Dashboard

기준일: 2026-03-03

목적
- `taxonomy-dashboard.md` 스펙을 실제 구현 순서로 내린다.
- admin 프론트 페이지와 `event-service` API를 분리된 책임으로 구현한다.
- Phase 1에서는 compile 산출물 추가 없이 기존 taxonomy SoT 파일을 직접 로드해 dashboard를 동작시킨다.
- query axis와 predicate taxonomy category를 분리해 표시한다.

범위
- Admin 프론트: taxonomy dashboard page
- Event service: taxonomy tree / preview / drift API
- Taxonomy loader/service: `predicate_axis_taxonomy.json` 기반 전개
- QA/운영 검증: API 스모크 + 기본 drift 확인

비범위
- OWL reasoner/SPARQL endpoint 도입
- Fuseki 도입
- TTL/OWL 원본을 runtime에서 직접 해석하는 경로
- taxonomy compile 스크립트 신규 도입

관련 문서
- 메인 스펙: `fivecircles/architecture/specs/predicate/taxonomy-dashboard.md`
- Query axis 확장 초안: `fivecircles/architecture/specs/predicate/query-axis-reveal-combined-design.md`
- Predicate README: `fivecircles/architecture/specs/predicate/README.md`
- RDF/OWL 상위 포지셔닝: `fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`
- 상속/분류 운영 기준: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`
- 현재 taxonomy SoT: `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- 현재 loader: `scripts/ops/rdf/predicate_axis_taxonomy.py`

---

## 1) 고정 결정

1. 페이지는 admin 프론트에 둔다.
2. API는 `event-service`에 둔다.
3. API 경로는 아래 3개로 고정한다.
   - `GET /api/event/taxonomy/tree`
   - `POST /api/event/taxonomy/preview`
   - `GET /api/event/taxonomy/drift`
4. Phase 1 SoT는 `predicate_axis_taxonomy.json`이다.
5. Phase 1에서는 별도 `generated.json` compile step을 도입하지 않는다.
6. preview 결과는 최종적으로 RDB 쿼리 결과를 사용한다.
7. dashboard는 운영/검수 도구이며 user-facing runtime과 분리한다.
8. query axis는 `REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES` 4종을 표시한다.
9. Phase 1 taxonomy category source는 `PREDICATE` axis에만 직접 연결한다.

## 2) 구현 전략

### 2.1 Phase 1 전략
- `event-service`가 `predicate_axis_taxonomy.json`을 로드한다.
- admin 프론트는 상단 query axis를 별도 UI 레이어로 가진다.
- server 메모리에서 axis/leaf/implies 관계를 전개한다.
- 전개 결과를 tree/preview/drift endpoint에서 재사용한다.
- admin 프론트는 API 응답을 렌더링만 하고 taxonomy 추론은 최소화한다.

### 2.2 왜 compile을 미루는가
- 현재 SoT JSON이 이미 axis별 `predicateCodes`, `predicateSuggestions`, `impliesAxes`를 가진 전개형 구조다.
- dashboard Phase 1의 핵심 기능(tree/preview/drift)에 별도 build step이 필수는 아니다.
- 먼저 런타임 로더로 기능을 검증하고, taxonomy 깊이/입력원이 늘어날 때 compile 산출물을 도입한다.

## 3) 서버 설계

### 3.1 패키지/구성
- controller
  - `TaxonomyController`
- service
  - `TaxonomyService`
- mapper/repository
  - preview 전용 SQL mapper 추가

### 3.2 입력 SoT
- 파일: `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`
- 로딩 규칙
  - 앱 기동 시 1회 로드 또는 lazy load
  - invalid JSON / missing file은 dashboard API 실패로만 한정
  - user-facing 이벤트 API에는 영향이 없어야 함

### 3.3 전개 규칙
- `axisCode` 선택 시:
  - 해당 axis의 `predicateCodes`
  - 해당 axis의 `predicateSuggestions`
  - `impliesAxes`가 있으면 재귀적으로 포함
- dedupe는 필수
- 순환 감지 필요
- leaf 전개 결과는 API 응답에 명시적으로 포함

### 3.4 Tree API
목표
- admin 페이지가 트리를 즉시 렌더링할 수 있게 한다.

반환 최소 필드
- `axisCode`
- `label`
- `kind`
- `impliesAxes`
- `resolvedPredicateCodes`
- `resolvedPredicateSuggestions`
- `descendantLeafCount`

주의
- 현재 SoT JSON은 엄격한 parent-child tree보다 axis set 구조에 가깝다.
- 따라서 Phase 1 tree는 “계층 시뮬레이션 트리” 또는 “axis graph list” 형태를 허용한다.
- UI가 꼭 진짜 트리여야 하는 것은 아니다. 초기엔 left rail list + detail pane도 허용한다.

### 3.5 Preview API
목표
- 선택 axis가 실제 이벤트 필터 결과로 어떻게 나타나는지 확인한다.

입력
- `axisCode`
- `dramaId?`
- `characterId?`
- `episodeEndMax?`
- `sourceStatus=APPROVED`
- `limit=20`

질의 규칙
- runtime `predicate_code IN resolvedPredicateCodes`
- optional drama filter
- optional character filter
- optional episode gate
- 기본 정렬: `episode_end DESC, event_id DESC`

Phase 1 제한
- `predicateSuggestions` fallback까지 preview에 즉시 넣을지 여부는 분리 구현한다.
- 우선 1차는 `predicate_code` 기반 preview를 먼저 붙인다.
- fallback preview는 기본 preview와 분리된 tab으로 노출한다.
- fallback row에는 `FALLBACK MATCH` 라벨을 붙인다.

### 3.6 Drift API
목표
- taxonomy / enum / RDB 사이 어긋남을 운영자가 점검할 수 있게 한다.

최소 진단 항목
- taxonomy code -> enum missing
- enum code -> taxonomy unclassified
- empty axis
- duplicate resolved code
- cycle detected

Phase 1 원칙
- drift는 파일+enum 정합성을 우선 보여준다.
- RDB coverage count는 있으면 좋지만 필수는 아니다.

## 4) 프론트 설계

### 4.1 페이지 위치
- admin 프론트 내부 route에 taxonomy dashboard page 추가

### 4.2 화면 구성
1. 상단
   - query axis panel (`REVEAL`, `PREDICATE`, `COMBINED`, `PRECEDES`)
2. 좌측
   - `PREDICATE` axis용 taxonomy category list/tree
3. 우측 상단
   - filter form + selected query axis/category summary
4. 우측 하단
   - preview table
5. 하단 또는 별도 tab
   - drift diagnostics

### 4.3 상태 관리
- selected axis
- preview filters
- preview loading / error
- drift loading / error

### 4.4 사용자 액션
- axis 클릭 -> preview 기본 호출
- filter 수정 -> preview 재호출
- drift tab -> 별도 호출

## 5) 단계별 구현 순서

### Step A. 서버 taxonomy read lane
- taxonomy JSON 로더를 `event-service`로 이식 또는 포팅
- axis resolver 구현
- cycle / dedupe / resolved code 계산 유틸 구현

### Step B. tree API
- DTO 정의
- controller/service wiring
- smoke JSON 확인

### Step C. preview API
- request/response DTO 정의
- SQL mapper 구현
- drama/character/episode filter 반영
- smoke SQL 결과 확인

### Step D. drift API
- enum 비교
- taxonomy 구조 진단
- 선택적 RDB count 추가

### Step E. admin page
- route 추가
- tree/list panel
- preview table
- drift tab

### Step F. 검증
- API 수동 스모크
- admin page 렌더 확인
- 잘못된 axis / 빈 결과 / taxonomy 로드 실패 처리 확인

## 6) 위험과 대응

### 위험 1. taxonomy JSON이 query axis 전체가 아니라 predicate group set에 가까움
- 대응
  - Phase 1 UI를 `query axis` + `predicate category browser`로 분리
  - `REVEAL/COMBINED/PRECEDES`는 상단 축으로 먼저 노출하고 데이터 source는 후속 연결

### 위험 2. preview에서 suggestion fallback까지 넣으면 의미가 갑자기 넓어짐
- 대응
  - Phase 1 preview는 runtime `predicate_code` 우선
  - fallback preview는 명시적 옵션으로만 노출

### 위험 3. SoT 파일 경로가 서비스 런타임에서 다를 수 있음
- 대응
  - classpath/resource 복사 또는 명시적 file path 설정 방식을 early spike로 먼저 검증

## 7) 성공 기준

1. `GET /api/event/taxonomy/tree`가 axis 목록과 resolved codes를 반환한다.
2. `POST /api/event/taxonomy/preview`가 선택 axis 기준 이벤트 목록을 반환한다.
3. `GET /api/event/taxonomy/drift`가 최소 정합성 진단을 반환한다.
4. admin 프론트 페이지에서 세 API를 사용해 dashboard를 렌더링한다.
5. user-facing runtime은 dashboard 미구현/장애와 무관하게 유지된다.

## 8) 권장 실행 순서

1. 서버 tree API
2. 서버 preview API
3. admin page 기본 화면
4. drift API
5. drift UI

이 순서가 좋은 이유
- tree + preview만으로도 운영 가치를 빨리 확인할 수 있다.
- drift는 진단 도구라 기능 우선순위상 뒤에 둬도 된다.

## 9) 후속 판단 포인트

- taxonomy JSON이 더 복잡해지면 compile 산출물(`generated.json`) 도입 검토
- fallback preview(suggestion lane)는 분리 tab + `FALLBACK MATCH` 라벨 정책으로 고정
- tree UI를 graph/tree로 승격할지 여부 결정
- `REVEAL` axis용 source(codebook/taxonomy)를 어디에 둘지 결정
- REVEAL/COMBINED axis 연결 시 source 경계와 request contract는 `query-axis-reveal-combined-design.md`를 기준으로 진행
