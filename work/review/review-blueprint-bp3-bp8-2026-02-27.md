# Review: Blueprint BP3~BP8 (2026-02-27)

## 범위
- 포함: `event/front/spec/ops/test` 레이어
- 제외(보류): wiki/intelligence 팀원 영역(`BP3-2`, `BP3-3`, `BP3-5`)

## 구현/검증 요약
1. BP3-4 누락 정책 고정
- `target_type=ATTRIBUTE` + `target_key` 누락은 Phase1에서
  - drama10(Q1 expansion): fail
  - 그 외 legacy: warn + backlog

2. BP4-3 strict miss 가드 회귀 확인
- `validate-productionq-probe-guard.py` PASS
- strict miss + probe hit에서도 ANSWERED 승격 없음

3. BP4-4 Q01_EXP_01 코드북 재현 확인
- `validate-reveal-target-key-runtime-phase1.py` PASS
- `Q01_EXP_01` earliest replay 이벤트가 `2293`으로 answerset과 일치

4. BP5 WHY because_chain 자동화
- `useProductionQ`에서 PRECEDES 기반 cause chain 자동 생성 유지
- 규칙: causes tail + focus 포함, 최대 3-hop
- Q1 expansion 기본 context depth=3

5. BP6 데이터 보강/정책
- `backfill_event_reveal_target_key_phase1.sql` 실행(결정론 anchor 백필)
- drama10 누락 0건 유지
- legacy 미해결 6건은 보류 정책으로 분리
- Q1 expansion B-lane coverage 100%(6/6)

6. BP7 다건 reveal 렌더링 규칙
- WHY 영역에서 `reveal_hint` 다건(최대 5건) 표시
- `target_key` 포함 출력
- 라우팅 문서에 `reveals[]` 우선 규칙 반영

7. BP8 스모크
- `validate-reveal-target-key-gate.py` PASS
- `run_expansion100_q1_seed_and_validate.sh` PASS
- `npm run build` PASS

## 잔여 리스크
- legacy ATTRIBUTE rows(6건)는 codebook 외 도메인이라 자동 백필 불가
- wiki/intelligence 경로는 보류 상태이므로 E2E write 완료 판정은 범위 밖

## 결론
- 보류 항목 제외 범위(BP3-4, BP4, BP5, BP6, BP7, BP8-2/4/5)는 실행 가능 상태로 통과.
