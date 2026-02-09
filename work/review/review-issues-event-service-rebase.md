# Event-service Rebase Review: 이슈와 수정 플랜

> Author: codex reviewer
> Date: 2026-02-09

## 범위/전제
- 기준 브랜치: `origin/develop`
- 리뷰 대상: `feature/admin-event-edit` 리베이스 후 event-service 변경분
- 목표: 리베이스로 추가된 기능(aggregate, predicateSuggestion, TRANSFORMS 호환)이 기존 REVEALS/해금 로직을 깨지 않게 정합성 보강
- 비목표
  - 팀원이 진행 중인 REVEALS 파이프라인 확장(예: reveal target meta 추가 전파)을 선제 구현하지 않음
  - 캐릭터 해금/타임라인 병합 정책 자체를 변경하지 않음

## 현상(검증 제약)
- 원격 서버(bit-ts) 불안정으로 배포 기반 런타임 스모크가 자주 중단됨
- 로컬에서는 Gradle 빌드가 디스크 부족으로 실패할 수 있음
  - `:services:event-service:test` 실행 시 `No space left on device` 발생 가능

## diff 요약(핵심)
- `EventCharacterMapper.xml`에서 `findRevealPartnerId`의 의미는 유지됨
- 신규 추가: related-characters aggregate용 쿼리 2개
  - `findRelatedCharactersAggregate`
  - `findRelatedCharactersAggregateEvidence`

## 이슈(중요도 순)

### [P0] findRevealPartnerId 결정성/자기자신 partner 리스크
파일: `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml`

- 상태(확인 결과): **이미 방어 로직이 들어가 있음**
- 확인 사항
  - `UNION ALL ... LIMIT 1` 조합에 대해 `ORDER BY (episode_end DESC, event_id DESC, partner_id ASC)`가 존재하여 결과가 결정적임
  - Case2에서 self 제외 조건(`ec.character_id <> #{characterId}`)이 포함되어 자기 자신이 partner로 반환되는 케이스를 방지함
- 결론
  - 이 항목은 "리베이스로 인한 신규 리스크"가 아니라, 현재 코드 기준으로는 **해결됨(Resolved)** 으로 분류 가능

### [P0] aggregate 집계(count)와 evidence 필터의 불일치
파일: `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml`
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`

- 확인 메모(현재 코드 기준)
  - 집계 쿼리는 그룹별 count를 분리해 계산하고(e.g., battle/adversary/deathExit/ally/affiliationChange), evidence 쿼리는 mode별 predicate allowlist로 필터링함.
  - 현재 evidence(ADVERSARY/ALLY)는 "해당 mode에서 점수에 기여하는 그룹들의 합집합"을 의도한 형태로 보이며, **명백한 누락/과포함은 코드만으로는 단정하기 어려움**.
- 남는 리스크
  - 집계 자체가 그룹 overlap(예: `LEAVES`가 deathExit/affiliationChange에 동시에 카운트)일 수 있어, evidence가 맞더라도 "왜 이 이벤트가 두 번 기여했나"가 불명확해질 수 있음.
  - alias/정규화 목록이 집계/evidence에 중복 정의되어 있어 drift 위험이 있음(단일 소스화 필요).

### [P1] aggregate 그룹 overlap(중복 카운트) 정책 부재
파일: `services/event-service/src/main/resources/mapper/event/EventCharacterMapper.xml`
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`

- 문제
  - 하나의 이벤트가 여러 그룹 조건에 동시에 걸리면 score가 과대계산될 수 있음
- 영향
  - 상위 후보가 과대평가되어 품질/신뢰도 저하

### [P1] updateEvent에서 predicateSuggestion 단독 수정이 어려울 수 있음
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`

- 현 상태
  - suggestion 저장 정책: `predicateCode == OTHER`인 경우에만 suggestion 저장
- 문제
  - 요청에서 `predicateCode`를 생략하고 suggestion만 수정하는 경우, 기존 이벤트가 OTHER여도 suggestion이 null 처리될 수 있음
- 영향
  - 운영 UI에서 "suggestion만 다듬기" 워크플로우가 막힐 수 있음

### [P2] APPROVED-only 조회로 인해 update 대상이 제한될 수 있음
파일: `services/event-service/src/main/resources/mapper/event/EventMapper.xml`
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`

- 현 상태
  - `EventMapper.findById`가 `source_status = 'APPROVED'`만 조회
- 영향
  - PENDING/REJECTED 이벤트를 수정하려는 운영 요구가 있을 때 막힘
- 정책 결정 (2026-02-09)
  - “approved만 온톨로지 레이어를 타는 데이터로 취급”은 우리 정책이므로 **현 구현이 맞음**
  - pending 데이터를 다루려면 **별도 흐름/엔드포인트로 분리**해서 다룬다
  - 지금은 필요 없으므로 **정책으로만 표시**하고, 필요해지면 구현한다 (no code change)

### [P2] predicateCode 정규화 정책의 적용 범위가 서비스마다 다를 수 있음
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`
파일: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`

- 현 상태
  - `EventServiceImpl`의 search는 OTHER/UNKNOWN을 filter에서 제외(null 처리)
  - `EventQueryServiceImpl`은 STATUS_CHANGE만 TRANSFORMS로 치환
- 영향
  - 같은 query 파라미터라도 엔드포인트마다 결과가 달라질 수 있음

## 수정 플랜(작업 단위)

### 1) reveal partner 조회 안정화
- `findRevealPartnerId`에 `ORDER BY` 추가 후 `LIMIT 1`
  - 정렬 기준은 1안으로 고정
    - 예: 최신 reveal 우선 `ORDER BY e.episode_end DESC, e.id DESC`
- Case2에 self 제외 조건 추가
  - 예: `AND ec.character_id <> #{characterId}`

### 2) aggregate 정의 일치(count vs evidence)
- evidence 쿼리의 predicate 조건을 집계(count)와 동일한 규칙으로 맞춤
- alias(suggestion 문자열) 매핑 목록을 집계/evidence에서 동일하게 사용

### 3) overlap(중복 카운트) 정책 고정
- "배타 집계" 규칙을 SQL CASE 우선순위로 고정
  - 하나의 이벤트는 최대 1개 그룹에만 카운트되게 처리

### 4) updateEvent suggestion 단독 수정 지원
- request에 `predicateCode`가 null이어도 기존 이벤트가 OTHER면 suggestion 업데이트 가능하게 처리
- 정책 유지: OTHER가 아니면 suggestion은 null로 유지

### 5) (합의 필요) 비승인 이벤트 수정 정책
- `findById`를 APPROVED-only로 유지할지, 운영용 update에 한해 별도 조회를 둘지 결정

## 검증 플랜(서버/로컬)

### 로컬(우선)
- 디스크 공간 확보 후 최소 컴파일/테스트
  - `./gradlew :services:event-service:compileJava`
  - `./gradlew :services:event-service:test`
- MyBatis XML 파싱/매퍼 시그니처 불일치 여부 확인

### 원격(bit-ts) 재가동 시
- `api-gateway(8080)`를 통해 스모크
  - aggregate 엔드포인트 200/400 응답 확인
  - character events에서 partner merge가 안정적으로 동작하는지 확인
