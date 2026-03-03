# Attribute ID Lane Cutover Plan (P6-2)

기준일: 2026-02-27  
범위: event-service + front read-path only (wiki/intelligence write-path 제외)

## 1. 목적
- `target_type=ATTRIBUTE` 조회에서 legacy aboutCharacter fallback(`target_id=character_id`)을 제거한다.
- 최종 조회 기준을 `target_key` + `target_id=attribute.id` 2축으로 고정한다.

## 2. 선행 게이트 (모두 PASS 필요)
- `fivecircles/test/validate-attribute-taxonomy-phase2.py`
- `fivecircles/test/validate-event-reveal-attribute-id-phase2.py`
- `fivecircles/test/validate-q01-exp-01-why-output-phase2.py`
- front build smoke:
  - `npm run build`
  - `VITE_USE_ATTRIBUTE_ID_LANE=true npm run build`

## 3. 컷오버 절차
1. Stage/QA 환경에서 `VITE_USE_ATTRIBUTE_ID_LANE=true`를 기본값으로 적용한다.
2. ProductionQ ATT_REVL lane 매칭 우선순위를 아래로 고정한다.
   - `target_key` -> `attribute.id(target_id)`
   - legacy about fallback 제거
3. 회귀 검증:
   - Q01_EXP_01~06 실행 결과에서 `ATT_REVL` 후보 0건 케이스를 수집
   - 누락은 데이터(backfill/codebook)로 보강하고 로직 fallback은 재도입하지 않는다.

## 4. 코드 변경 포인트
- `front/common/productionQ/executor.ts`
  - ATT_REVL 매칭의 마지막 분기(`legacyAboutIdSet`) 제거
- `front/common/productionQ/inheritancePhase1.ts`
  - `resolveAttributeTargetIds`는 deprecated 표시 후 참조 제거
- 문서 동기화:
  - `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`
  - `fivecircles/architecture/todolist.md`

## 5. 롤백 원칙
- 롤백은 로직 복원보다 데이터 보강을 우선한다.
- 긴급 롤백이 필요하면 `VITE_USE_ATTRIBUTE_ID_LANE=false`로 플래그만 내리고 코드 롤백은 배포창에서 별도 수행한다.

## 6. 비범위
- wiki/intelligence publish payload 변경
- reveal write-path 계약 변경

