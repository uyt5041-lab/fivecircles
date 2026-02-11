## 배경/목표
- Admin PRECEDES 수동매칭/큐 작업 효율 개선
- Predicate 품질관리(codebook + suggestion) 기반 마련
- Related-characters aggregate(Q3) 위젯/응답 스펙 drift 방지(`scoreRule`)
- Production Q 템플릿 실행기(정해진 API 쿼리 템플릿 + `q` 검색) 기반 추가
- 데이터 보강/정리 ops 스크립트 추가

## 변경 요약(카테고리별)

### PRECEDES
- 관련 문서
  - fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex15-precedes.md
  - fivecircles/architecture/specs/event-v2-plan-map.md
  - fivecircles/architecture/specs/event-v2-api.md
- FE (AdminPrecedesPage)
  - 수동매칭 `To 후보`에 키워드 검색(`q`) 추가: 후보 이벤트를 summary 기준으로 빠르게 필터링
  - 이미 존재하는 from→to 페어 선택 시 `ALREADY_EXISTS` 표시(서버에서 거부될 요청을 UI에서 먼저 노출)
  - 후보/기존 관계 row에 `REVEAL HIT` 배지 표시: `event_reveal` 기반 연관 신호를 운영자가 즉시 파악
  - 상태/로직 일부를 훅으로 분리해 유지보수성 개선(행 계산/인라인 수정 등)
  - (추가) PRECEDES Queue에서 `predicateCode/predicateSuggestion`을 빠르게 고칠 수 있도록 **Predicate 편집 모달** 추가(From/To 각각 편집)
  - (추가) 편집 아이콘 클릭 동작/버블링 문제를 수정해, 행 선택/편집이 의도대로 동작하도록 개선
- BE (event-service)
  - PRECEDES suggestion/관계 조회 응답에 `revealTargetHit` 포함
    - 의미: from/to 이벤트가 동일 reveal 타겟을 공유하면 hit=1
    - 사용처: FE 배지 표시 + 랭킹/정렬 신호
  - 정렬/점수식 개선: shared character 2명 이상이면 비선형 보너스를 부여해(동일 에피소드 tie-break) 같은 스토리라인 후보가 더 위로 오도록 보정

### PREDICATE
- 관련 문서
  - fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex13-standard-predicates.md
  - fivecircles/architecture/specs/predicate/README.md
  - fivecircles/architecture/specs/predicate/groups.md
  - fivecircles/architecture/specs/predicate/promotion-process.md
  - fivecircles/architecture/specs/predicate/data-quality-risks-and-structure.md
  - fivecircles/architecture/specs/predicate/suggestion-sot-event.md
- 공통 codebook 정리
  - `PredicateCode` 정리/보강
  - `PredicateSuggestionCode` 신설: 정규 코드 vs 제안 코드 분리(품질관리/승격 프로세스 기반)
- event-service 저장/전달 경로
  - 이벤트 DTO에 `predicateSuggestion` 포함(원천 제안/운영 입력을 손실 없이 보관)
  - Flyway V9: event에 predicateSuggestion 저장 필드 추가
- 범위 고정
  - wiki-service publish payload/후보 테이블 신설 등은 **보류**(wiki-service는 develop 상태 유지)

### AGGREGATE (Related Characters Aggregate / Q3)
- 관련 문서
  - fivecircles/architecture/specs/predicate/related-characters-aggregate.md
  - fivecircles/architecture/specs/predicate/rollout-plan-aggregate-qa.md
  - fivecircles/architecture/specs/api-contract.md
- BE
  - aggregate 응답 DTO에 `scoreRule` 필드 추가(클라이언트 drift 방지)
  - aggregate 계산/응답 구조 정리 + 테스트 보강
- FE
  - QA에 Q3 위젯 추가(관계 캐릭터 집계를 시각화)
  - evidence는 `includeEvidenceEventIds=true`일 때 `evidenceEventIds`를 텍스트로 표시(타임라인 UI는 보류/되돌림)

### PRODUCT (ProductionQ/QA)
- 관련 문서
  - fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex16-production-Q15s.md
  - fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md
  - fivecircles/architecture/specs/predicate/ex16-production-q1-q15-implementation-status.md
- productionQ 템플릿/타입/실행기(`front/common/productionQ/*`) 추가
- QA 페이지에서 템플릿 선택 + 파라미터 입력으로 정해진 API 쿼리 실행
- 후보 이벤트는 타임라인 형태로 보여주고, 선택 이벤트는 원인/결과(causes/effects) 맥락을 함께 노출(가능한 경우)

### INTELLIGENCE (Prompt/Contract)
- 관련 문서
  - fivecircles/architecture/specs/intelligence/intelligence-events-contract-시뮬레이션.md
  - fivecircles/architecture/specs/intelligence/intelligence-db-schema-시뮬레이션.md
  - fivecircles/architecture/specs/notion-origin-intelligence-v1.md
  - fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md
  - fivecircles/work/review/review-reveals-attribute-option1-2026-02-10.md
- `prompts/refine-fact.txt` 변경(출력 계약/품질 영향)
  - REVEALS의 Fact Reveal(ATTRIBUTE) 규칙 강화
    - 기존: `revealTargetId=0`
    - 변경: `revealTargetId`는 0 금지, `involvedCharacterIds` 중 about 캐릭터 1명을 선택해 채움
    - about 캐릭터 특정 불가 시 추측 금지, `revealTargetId` 생략(null)
  - `OTHER`의 `predicateSuggestion` 포맷 표준화
    - `TOKEN|한국어 설명` (예: `BATTLE|전투`)
    - 원칙: codebook token 목록에서만 선택, 불가 시 `NEW|...`로 등록(후속 승격 후보)
- 합의 상태
  - ATTRIBUTE revealTargetId를 실제 파이프라인에서 0 금지로 강제하는 코드는 아직 **협의 전**이라 적용하지 않음(관련 내용은 주석으로만 유지)

### OPS(DATA)
- 관련 문서
  - fivecircles/docs/incidents/2026-02-10-ghost-suggestions.md
- `scripts/ops/*` 데이터 보강/정리/백필/재정렬 스크립트 추가

## 스키마/마이그레이션
- event-service Flyway: `V8__create_script_ingest_tables.sql`, `V9__add_event_predicate_suggestion.sql`

## API 계약 변화
- aggregate 응답에 `scoreRule` 추가(문서 반영 포함)

## 되돌림/스코프 확인
- wiki-service: develop 상태 유지(추가 테이블/흐름 없음)
- notification-service/프론트 notification 삭제는 복구됨
- auth/gateway의 불필요 변경은 develop로 복구됨

## 테스트
- `./gradlew :services:event-service:test :services:intelligence-service:test --no-daemon` OK
- `npm --prefix front run build` OK
- 참고: `./gradlew test`는 로컬에서 wiki-service 통합 테스트가 MySQL 필요로 실패할 수 있음(환경 의존)
