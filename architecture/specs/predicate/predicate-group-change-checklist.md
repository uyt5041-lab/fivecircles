# Predicate Group 변경 체크리스트 (FE/BE/QA 공통)

목적: `groups.md` 변경 시 드리프트를 방지하기 위한 공통 체크 템플릿.

## 1) 변경 요약
- 변경일:
- 변경자:
- 변경 그룹:
- 변경 유형: `runtime code 추가/제거` | `fallback token 추가/제거` | `rule 변경`
- 변경 사유:

## 2) 영향 영역 체크
- [ ] FE: 템플릿/라우터(`strict_must`, group fallback, labels) 영향 확인
- [ ] BE: 집계/쿼리(`PredicateGroup`, suggestion token 파싱) 영향 확인
- [ ] QA: 질문셋(Q1~Q15, 확장셋) 회귀 영향 확인
- [ ] 문서: `groups.md`, `p1-predicate-term-mapping.md`, 관련 spec 동기화

## 3) 검증 체크
- [ ] strict 경로에 group/fallback이 새어들지 않는지 확인
- [ ] `predicate_code=OTHER` + `predicate_suggestion` 가드가 유지되는지 확인
- [ ] user-facing 필터에서 `OTHER/UNKNOWN` 노출이 없는지 확인
- [ ] 템플릿 strict predicate 게이트(`validate-productionq-predicatecode-gate.py`) 재실행

## 4) 승인 기준
- [ ] FE/BE/QA 담당 확인 완료
- [ ] 드리프트 없음(문서/코드/템플릿 정합)
- [ ] 롤백 포인트 기록(필요 시)
