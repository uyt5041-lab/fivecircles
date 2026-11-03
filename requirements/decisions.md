# Decisions (Confirmed)

## Format
- [YYYY-MM-DD] Decision:
  - Context:
  - Options:
  - Chosen:
  - Reason:
  - Impact:


## 2026-11-03 — 필수 EGM 위험도별 범위와 구조 스킬 보정
- Context: 사용자 요청으로 EGM 필수 사용을 유지하면서 위험도별 범위·재사용을 적용하고 structure-architect에도 실제 적용 후 공개 프레임워크에 푸시·머지·기록한다.
- Chosen: 계약·권한·데이터 의미 변경 FULL, 작은 수정은 관련 단계 TARGETED, 유효한 결과 재사용. 구조 점수·MSA·문서 산출은 실제 범위에 맞춘다.
- Scope: 프레임워크 스킬·연결 문서·검증 근거·통합 기록. 제품 코드·개별 프로젝트의 내부 정보는 제외한다.
- DoD: 대표 상황의 독립 적용 검증, 링크·형식·공개 범위 확인, 원격 branch/main 반영과 merge commit 확인, 실제 결과만 integrate-log에 기록.
