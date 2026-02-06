# intelligence-events-contract-시범용.md

본 문서는 `ex14-reveal-implementation.md` 기준 정합성 반영을 위한 **시범용 초안**이다.
공식 문서는 팀원 작업과 충돌 방지를 위해 수정하지 않는다.

## 범위
- 포함: `labelDraft.eventType`(내부 분류)와 `event.predicate_code`(저장 표준)의 분리 원칙
- 포함: Predicate 허용값 정렬(TRANSFORMS 표준, STATUS_CHANGE legacy 호환)
- 제외: 캐릭터 해금/타임라인 병합 로직
- 제외: reveal target(`revealTargetId`, `revealTargetType`) 실제 구현/저장 경로

## C가 소비(Consume): B(Core) 발행

wiki_entry.created.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{
    "wikiEntryId":"string",
    "dramaId":"string",
    "characterId":"string",
    "episodeStart":1,
    "episodeEnd":1,
    "status":"PENDING",
    "labelDraft":{"eventType":"REVEAL_HINT","involvedCharacterIds":["string"]}
  }
}

wiki_entry.updated.v1
- 목적: Assessment 재생성

wiki_entry.approved.v1
Payload(data):
{
  "wikiEntryId":"string",
  "dramaId":"string",
  "characterId":"string",
  "episodeStart":1,
  "episodeEnd":2,
  "approvedAt":"ISO-8601",
  "approvedByUserId":"string",
  "labelDraft":{"eventType":"REVEAL_CONFIRM","involvedCharacterIds":["string"]}
}

## Event type mapping (시범용 정합성)
- `labelDraft.eventType`는 **인텔리전스 내부 분류 값**이며, `event.predicate_code`와 1:1 고정 매핑을 강제하지 않는다.
- `event.predicate_code`는 `common/PredicateCode` 폐쇄 집합을 따른다.
- 표준명은 `TRANSFORMS`이며 `STATUS_CHANGE`는 legacy 호환으로만 취급한다.

예시 매핑(운영 정책):
- `REVEAL_HINT`, `REVEAL_CONFIRM` -> `REVEALS`
- `RELATION_CHANGE` -> `JOINS | LEAVES | BETRAYS | ALLIES_WITH` 중 선택
- `STATUS_CHANGE` -> `TRANSFORMS`

저장 원칙:
- write: 신규 저장은 `TRANSFORMS` 사용
- read/filter: 이행 기간 `TRANSFORMS` 조회 시 legacy `STATUS_CHANGE` 함께 매칭 허용

wiki_entry.rejected.v1
- 목적: 선택적으로 Assessment 비활성 처리

## C가 발행(Publish) 옵션

assessment.created.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{"assessmentId":"string","wikiEntryId":"string","riskLevel":"LOW|MEDIUM|HIGH"}
}

event.projected.v1
Payload:
{
  "eventId":"uuid",
  "occurredAt":"ISO-8601",
  "data":{"eventId":"string","sourceWikiEntryId":"string"}
}

## 운영 규칙
- at-least-once 전제, idempotent 필수
  - Assessment: `(wikiEntryId, policyVersion)` upsert
  - Projection: `(sourceType, sourceId)` upsert
- 실패는 DLQ 또는 재처리 API로 회수

## 정합성 갭(시범용 기록)
- wiki/event 서비스 코드에서 reveal 메타(`event_reveal`)의 end-to-end 저장 경로는 협업 이슈로 확인 중
- 본 문서는 갭을 기록만 하며 구현 변경은 하지 않음
