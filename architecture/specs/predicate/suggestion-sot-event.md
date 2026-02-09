# Predicate Suggestion 운영 계획 (SoT = Event, Snapshot = Approval)

목적
- `PredicateCode`는 폐쇄 집합(검색/필터에 사용)으로 유지한다.
- 분류 불가/애매 케이스는 `predicate_suggestion`으로 축적하고, 충분히 쌓이면 심사 후 `PredicateCode`로 승격한다.
- suggestion의 **Source of Truth(편집/검수 기준)** 는 `event`로 고정하고, `wiki_submission`은 원본/히스토리로만 유지한다.

핵심 결정
- `wiki_submission.predicate_suggestion`: LLM/제보 시점의 초안 기록(히스토리).
- `event.predicate_suggestion`: 승인 시점의 스냅샷이며, 이후 운영 편집의 단일 기준(SoT).
- 자동 동기화는 하지 않는다.
  - 승인 후 wiki 수정이 event에 자동 전파되지 않는다.
  - 필요 시에만 “재투영(re-project)”을 명시적 작업으로 수행한다.

비목표
- suggestion을 user-facing 검색/필터의 1급 조건으로 쓰지 않는다.
- suggestion을 자동으로 enum 승격하지 않는다.

---

## 1) 데이터 모델 변경

DB (nospoiler_event)
- 테이블: `nospoiler_event.event`
- 컬럼 추가: `predicate_suggestion VARCHAR(255) NULL`
- 인덱스(선택)
  - 운영 집계 쿼리를 자주 하면 `(drama_id, predicate_code, predicate_suggestion)` 또는 `(drama_id, predicate_suggestion)` 인덱스를 검토한다.

DB (nospoiler_wiki)
- 기존 유지: `nospoiler_wiki.wiki_submission.predicate_suggestion`
- (옵션) Pre-approval 관측용(LLM/가이드 튜닝): wiki 레벨의 후보 레지스트리
  - 목적: PENDING/REJECTED까지 포함해 “어떤 NEW가 많이 나오는지”를 관측
  - 주의: 노이즈가 크므로 승격 기준으로 직접 쓰지 않는다(승격은 event 기준)

DB (권장, 단일 소스): 후보 레지스트리 (nospoiler_event)
- 테이블(제안): `nospoiler_event.event_predicate_suggestion_candidate`
- 목적: “새로운 코드가 반복해서 쌓이는지”를 정량(hit count)으로 관측해 승격 후보를 제안한다.
- 원칙: 중복 row를 무한히 쌓지 말고, `(drama_id, suggestion_key)` 1행에 `hit_count++`로 누적(upsert).
  - 승인 이벤트 + 운영 수정/생성 + 백필이 한 카운트로 합쳐진다.

Implementation note
- 초기 프로토타입에서는 wiki DB에 후보 테이블을 먼저 붙일 수 있다(개발/관측 편의).
- 다만 “승격 후보”의 단일 소스는 event(승인 이벤트)로 수렴시키는 것을 목표로 한다.

---

## 2) 파이프라인 규칙 (Snapshot/SoT)

승인 시점 Snapshot
- 위키 승인으로 event-service에 이벤트를 발행할 때:
  - `predicate_code`가 `OTHER`인 경우에만 `predicate_suggestion`을 고려한다.
  - 단, `predicate_suggestion`은 **코드북(codebook) 토큰**으로 정규화된 값만 event-service로 전달한다.
    - 예: `BATTLE` 또는 `BATTLE|전투` (앞 토큰만 저장/활용)
    - 코드북 기준: `common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java`
  - 코드북에 없는 자유 텍스트(예: "KIDNAPS")는 event-service로 전달하지 않는다(데이터 오염 방지).
    - 대신 “승격 후보”로 **후보 레지스트리(hit count)** 에 적재해 backlog로 관리한다(운영 확장).
    - 예: `NEW|...` 또는 invalid token → (권장) event 후보 레지스트리 hit_count++ / (옵션) wiki 관측 레지스트리 hit_count++
  - `predicate_code`가 `OTHER`가 아니면 `predicate_suggestion`은 NULL로 저장한다(정책 단순화).

SoT 위치
- 운영자가 suggestion을 수정/정리할 때는 `event.predicate_suggestion`만 수정한다.
- wiki_submission의 suggestion은 원본 기록이므로 수정 대상이 아니다.

재투영(re-project) 원칙
- 필요하면 “승인된 wiki_submission -> event 재투영”은 별도의 명시적 작업으로만 수행한다.
- 자동 동기화는 하지 않는다(감사/재현성, 예측 불가능한 변경 전파 방지).

---

## 3) API/DTO 변경(계획)

wiki-service -> event-service publish payload 확장
- 파일: `services/wiki-service/src/main/java/com/nospoiler/wikiservice/dto/request/event/EventCreateRequest.java`
- 추가 필드: `String predicateSuggestion`

event-service EventRequestDTO 확장
- 파일: `services/event-service/src/main/java/com/nospoiler/eventservice/dto/EventRequestDTO.java`
- 추가 필드: `String predicateSuggestion`

event-service event entity/mapper 확장
- 파일: `services/event-service/src/main/java/com/nospoiler/eventservice/entity/Event.java`
- 파일: `services/event-service/src/main/resources/mapper/event/EventMapper.xml`
- insert/update/select에 `predicate_suggestion`을 포함한다.

운영 UI(관리자)
- “기타(OTHER)” 이벤트에서 suggestion을 편집/정리할 수 있어야 한다.
- 승격 후보 집계 화면은 event 기준으로 만든다.
  - 예: `predicate_code='OTHER'` AND `predicate_suggestion IS NOT NULL`를 group by count.

---

## 4) 검색 레이어 정책 (명시)

user-facing 검색/필터
- `predicate_code`만 1급 조건으로 사용한다.
- `predicate_code IN ('OTHER','UNKNOWN')`는 “기타/미분류”로만 노출(선택적으로 숨김).
- suggestion 기반 필터는 운영자 화면에서만 사용한다.

Q20 같은 집계
- `OTHER/UNKNOWN`은 별도 바스켓으로 보여줄 수 있으나, 승격 전까지는 “설명용/운영용”으로만 취급한다.

---

## 5) 롤아웃 순서(체크리스트)

P0 (스키마/저장부터)
- [ ] event DB 마이그레이션: `event.predicate_suggestion` 추가
- [ ] event-service entity/mapper/DTO에 필드 추가(저장/조회 포함)
- [ ] wiki-service publish payload에 suggestion 포함

P1 (운영 편집/집계)
- [ ] 운영 UI에서 suggestion 표시/편집 지원(event 기준)
- [ ] suggestion 집계(후보 리스트) 화면/쿼리 추가

P2 (승격 프로세스 고정)
- [ ] 승격 기준(빈도/검수) 문서화
- [ ] 승격 시 작업: enum 추가, 프롬프트 업데이트, 과거 event/wik i 데이터 백필
