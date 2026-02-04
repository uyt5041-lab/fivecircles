# 18 - Ingestion + Intelligence + Export Workflow (아이디어 메모)

> 이 문서는 구현 결정을 위한 **아이디어 정리**이며, 실제 구현 여부/범위는 추후 결정한다.

## 목적
- 대량 적재(ingestion) → 후보 생성(candidate) → LLM 정제 → 검증소 승인 → 이벤트 반영(export) 흐름을 한 문서에 정리
- LLM 호출 지연/대기 시간을 고려한 처리 방식(비동기/상태 관리) 개요 제시

## 범위
- `event-service`의 Export 모듈
- `ingestion/scripts/*` 기반 파이프라인
- `intelligence-service`의 LLM refine API
- 검증소(위키/QA) 승인 흐름

## 현재 코드 기준 흐름(요약)
1. **Script Line 적재**
   - `ingestion/scripts/ingest_script_line_jsonl.py`
   - JSONL → `script_line` 테이블
2. **Candidate 생성**
   - `ingestion/scripts/build_candidates.py`
   - `script_line` → `script_candidate`
3. **Export**
   - `event-service` Export API 또는 `ingestion/scripts/export_events.py`
   - `script_candidate(APPROVED)` → `event` 생성 + `event_id` 링크

## Intelligence(LLM) 연동 고려
- `intelligence-service /api/intelligence/v1/refine`가 LLM API 호출 수행
- 호출 지연/대기 시간이 존재하므로 **비동기 처리 + 상태 관리**가 필요

### 상태 관리(아이디어)
다음 중 하나 선택:
- **별도 테이블** `script_candidate_refine`
  - `candidate_id`, `status(PENDING|PROCESSING|DONE|FAILED)`,
    `refined_summary`, `predicate_code`, `involved_ids`,
    `requested_at`, `completed_at`, `retry_count`, `error`
- **script_candidate에 상태 컬럼 추가**
  - `refine_status`, `refined_summary`, `refined_predicate`, `refined_involved_ids`

### 처리 흐름(아이디어)
1. 후보 생성 후 `refine_status = PENDING`
2. Worker/Batch가 `PENDING` 선별 → LLM 호출
3. 완료 시 `DONE`, 실패 시 `FAILED` (재시도 가능)
4. 검증소는 `DONE` 상태만 검토/승인

## 검증소 승인 + Export 조건(아이디어)
Export 조건 예시:
- `script_candidate.status = APPROVED`
- `refine_status = DONE`
- `event_id IS NULL`

검증소 승인과 LLM 정제가 모두 완료된 상태만 Export 처리.

## Candidate 생성 로직 API화 가능성
현재 후보 생성은 `ingestion/scripts/build_candidates.py`에 의존.
향후 다음 형태로 **API화** 가능:
- `event-service`에 Batch/Job 엔드포인트 추가
  - 입력: `dramaId`, `seasonNo`, `episodeNo`, `windowSize`, `pipelineVersion` 등
  - 결과: 생성된 `script_candidate` 수, 실패 건수
- 장점: 스크립트 제거, 서버 측 일원화, 감사/로깅/권한 관리 용이

## 결정 보류 사항
- Candidate 생성 로직을 API로 이관할지 여부
- LLM 결과 저장 스키마(별도 테이블 vs 컬럼 추가)
- 검증소 승인과 Export 자동화 연결 여부
- 처리 방식(배치/큐/스케줄러) 선택
