# No Physical FK Rule - Meeting Note

Tag: [TeamB]

## Context
Notion-origin specs state: **No physical foreign keys** across tables.
Current implementation includes a physical FK:
- `wiki_submission_verification.submission_id` → `wiki_submission.id` with `ON DELETE CASCADE`.

## Why this can be a problem
- **Write-order coupling**: child rows cannot be inserted before parent exists, which blocks async ingestion/backfill.
- **Operational friction**: restores or partial data loads require strict ordering.
- **Eventual consistency mismatch**: strict FK conflicts with async workflows/mq-based pipelines.
- **Data loss risk**: `ON DELETE CASCADE` can erase verification history unexpectedly.

## What is “verification history”?
Records of who voted on a submission, their agree/disagree status, comments, and timestamps.
These are the audit trail for the review/approval process.

## Possible options
1) **Keep FK** (if we accept hard coupling inside wiki-service for simplicity)
2) **Remove FK** to align with Notion rule (and enforce integrity in application layer)
3) **Soft delete parent** only (avoid cascade)

## Open question
- Do we treat wiki-service as fully isolated so FK is acceptable, or align with no-FK principle across the board?

---

# 무물리 FK 원칙 - 회의 메모 (한국어)

태그: [TeamB]

## 배경
Notion-origin 스펙: **물리 FK 금지** 원칙.
현재 구현: 물리 FK 존재.
- `wiki_submission_verification.submission_id` → `wiki_submission.id` (`ON DELETE CASCADE`)

## 왜 문제가 될 수 있나
- **쓰기 순서 강제**: 부모가 먼저 있어야 자식 삽입 가능 → 비동기/백필 작업 장애
- **운영 복원 어려움**: 부분 복구/데이터 재적재 시 순서 제약 큼
- **점진적 일관성 충돌**: MQ/비동기 파이프라인과 맞지 않음
- **이력 손실 위험**: `ON DELETE CASCADE`로 검증 이력 삭제 가능

## “검증 이력”이란?
위키 제보에 대한 투표 기록(누가/언제/찬성·반대/코멘트)을 의미.
즉, **검수 감사 로그** 성격의 데이터.

## 선택지
1) **FK 유지**: wiki-service 내부 결합을 허용 (간단/안정)
2) **FK 제거**: Notion 원칙에 맞춤 (정합성은 앱 레벨로 보장)
3) **Soft delete만 허용**: 부모 삭제 시 cascade 금지

## 논의 포인트
- wiki-service만 예외로 둘지
- 전 서비스 no-FK 원칙을 강제할지

## 사고 시나리오 (추가)
1) **백필/재적재 실패**: 검증 로그가 먼저 들어오면 FK 제약으로 전체 적재 실패/롤백
2) **이력 손실 사고**: `ON DELETE CASCADE`로 검증 기록(감사 로그) 통째로 삭제
3) **비동기 파이프라인 교착**: MQ 이벤트 순서 역전으로 삽입 실패 → 재시도 적체
4) **부분 복구 순서 의존 문제**: 일부 테이블만 복구 시 FK 불일치로 서비스 기동/쓰기 실패
5) **스냅샷/이관 시 불일치**: FK 무결성 검증이 막혀 데이터 이관 지연/실패
6) **운영 실수 확산**: 제출 행 삭제가 cascade로 대량 삭제로 확대
