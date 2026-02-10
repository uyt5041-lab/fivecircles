# Predicate Group Strategy (Primary Delivery + Extensibility)

목표
- Primary: 현재 제기된 질문(Q1~Q15, 파생 질문 포함)을 "지금 있는 데이터/코드"로 구현 가능하게 만든다.
- Secondary: `PredicateCode` 폐쇄집합을 유지하면서, `predicate_suggestion` 축적과 승격 프로세스로 확장성/유지보수성을 확보한다.
- Future: RDF/OWL(트리플)로 확장하더라도, 서비스/프론트가 의존하는 "질문 레이어" 인터페이스가 깨지지 않게 한다.

비목표
- `predicate_suggestion`을 user-facing 검색/필터의 1급 조건으로 쓰지 않는다.
- 자동 추론으로 `PredicateCode`를 확정 저장하지 않는다.

관련 문서
- SoT=event 운영: `fivecircles/architecture/specs/predicate/suggestion-sot-event.md`
- Production Q 템플릿 + Intelligence QuerySpec 플랜: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`
- ex14 정합성(TRANSFORMS/REVEALS): `fivecircles/architecture/specs/ex14-consistency-checklist.md`
- Related characters 집계(단일 엔드포인트, N+1 제거): `fivecircles/architecture/specs/predicate/related-characters-aggregate.md`
- 데이터 품질(구조적 결함/방어 설계): `fivecircles/architecture/specs/predicate/data-quality-risks-and-structure.md`

---

## 1) 핵심 개념(3 레이어)

PredicateCode (Closed Set)
- 정의: 검색/필터/집계에서 사용하는 1급 타입.
- 특성: 안정적(stable), 버전 관리 대상, API 계약에 직접 등장.

PredicateSuggestion (Open Vocabulary)
- 정의: `predicate_code=OTHER`일 때 의미를 담는 텍스트(승격 후보 축적).
- 특성: 불안정(unstable), 운영/분석용, user-facing "정확한 필터"로 취급하지 않음.

PredicateGroup (Query Layer Concept)
- 정의: 질문/위젯에서 쓰는 "합성 필터" 이름.
- 예: `BATTLE`, `DEATH_EXIT`, `AFFILIATION_CHANGE`, `ADVERSARY`, `ALLY`
- 구성: `PredicateCode`의 합집합 + (선택) `predicate_suggestion` fallback 키워드 세트.

Candidate Registry (Promotion Input)
- 목표: "새로운 코드가 반복해서 쌓이는지"를 **정량(hit count)** 으로 관측해 승격 후보를 제안한다.
- 권장 저장소(단일 소스): `nospoiler_event` (APPROVED로 publish된 데이터 + 운영 수정/생성 + 백필이 한 카운트로 합쳐짐)
  - 이유: 승격 판단은 결국 “온톨로지 레이어(승인 이벤트)” 기준이 노이즈가 적다.
- 예외적으로 Wiki에서도 필요한 경우(옵션):
  - 목적: PENDING/REJECTED 단계에서 어떤 NEW가 많이 나오는지 관측해 LLM 가이드/프롬프트를 조정(승격 판단과 분리).
  - 주의: Wiki 카운트는 노이즈가 크므로 “승격 기준”으로 직접 쓰지 않는다.
- 구현 원칙
  - 중복 row를 무한히 쌓지 말고, `(drama_id, suggestion_key)` 1행에 `hit_count++`로 누적(upsert)한다.
  - `suggestion_key`는 정규화된 키(토큰/라벨 분리 또는 upper+trim)로 만든다.

---

## 2) 정책(검색 레이어)

OTHER/UNKNOWN 검색 정책
- user-facing 엔드포인트에서 `predicateCode=OTHER|UNKNOWN`은 "필터 미적용(null)"으로 처리한다.
- 이유: OTHER/UNKNOWN은 "미분류 저장용"이지, 사용자가 의도적으로 좁혀 찾는 1급 타입이 아니다.

그룹 조회 예외
- `PredicateGroup`으로 조회하는 경우에만 fallback을 허용한다.
- fallback 정의: `predicate_code='OTHER' AND predicate_suggestion in (keyword set)`를 그룹에 포함.
- 결과: 일반 검색 의미를 깨지 않고, "질문 위젯"에서만 보정적으로 정확도를 올릴 수 있다.

---

## 3) 구현 패턴(질문 -> QuerySpec)

Pattern A: 단일 캐릭터 타임라인 + PredicateCode union
- 예: Q6 소속 변경, Q7 사망/퇴장
- 호출: `GET /api/event/v2/characters/{id}/events?safeUpToEpisode=K&predicateCode=...`를 1~2회 호출하고 FE에서 합친다.
- 장점: 서버 변경 없이 가능, 계약 단순.

Pattern B: 파생 질문(적대자/협력자 등) = 후보 생성 + 증거 집계
- 기본 형태(N+1):
  - 1회: related characters 후보 생성
  - m회: 후보별 coevents 조회 후 그룹 분류로 점수화
- 최적화 형태(권장):
  - 1회: 서버가 후보 생성 + 그룹 집계를 한 번에 수행하는 aggregate 엔드포인트 제공.

Pattern C: PRECEDES 기반 원인/결과(설명 강화)
- 결과 이벤트를 먼저 찾고, 그 이벤트를 기준으로 PRECEDES 탐색(depth=1~2)을 붙여 "계기/직후"를 설명한다.

---

## 4) REVEALS를 "설명용"이라고 부르는 이유

의미
- `REVEALS`는 "드러남"을 나타내는 predicate이지만, "무엇이 드러났는지"가 메타로 고정돼 있지 않으면 검색 키로는 과하게 포괄적이다.
- 그래서 Q4 같은 질문에서 `REVEALS`를 1급 검색 키로 쓰면 오탐이 커질 수 있다.

권장 운영
- 조회/정답 찾기: `DISCOVERS`, `LEARNS` 등 인지 변화 계열(또는 질문 그룹)을 우선 사용한다.
- 설명/근거: 결과 이벤트에 `REVEALS` 및 `event_reveal` 메타(있다면)를 "설명"으로 붙인다.

---

## 5) 표준 그룹 표(초안)

정의는 다음 문서에서 단일 소스로 유지한다.
- `fivecircles/architecture/specs/predicate/groups.md`

승격(확장) 프로세스는 다음 문서에서 단일 소스로 유지한다.
- `fivecircles/architecture/specs/predicate/promotion-process.md`

RDF/OWL 확장 노트는 다음 문서에서 단일 소스로 유지한다.
- `fivecircles/architecture/specs/predicate/rdf-owl-extension-notes.md`

REVEALS 분류(통합 포인트 포함)는 다음 문서에서 단일 소스로 유지한다.
- `fivecircles/architecture/specs/reveals/reveals-classification.md`

REVEALS 재사용 케이스(정책/설명/랭킹/리캡)는 다음 문서에서 단일 소스로 유지한다.
- `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md`
