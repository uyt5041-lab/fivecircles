# Reveal Target Key Codebook (Phase1)

기준일: 2026-02-27  
소유: QA/Predicate-Reveal 정책 레이어(공동)

## 1) 목적
- `target_type=ATTRIBUTE` reveal의 의미 축을 `target_key`로 고정한다.
- 질문 템플릿/상속맵/seed 입력에서 동일 키를 사용해 드리프트를 방지한다.

## 2) 운영 계약 (MUST)
- `target_type=CHARACTER`이면 `target_key`는 비워도 된다.
- `target_type=ATTRIBUTE`이면 `target_key`는 필수다.
- `target_key`는 이 코드북 allow-list에 있어야 한다.
- `reveal_type(HINT|CONFIRM)`은 근거 강도 축이며, `target_key` 의미 축을 대체하지 않는다.
- Phase1 운영 적용은 `scripts/ops` seed/backfill 스크립트 경로를 우선한다.

## 2.1) Phase1 누락값 정책(BP3-4/BP6-2)
- `target_type=ATTRIBUTE` + `target_key` 누락 row는 Phase1에서 **경고 + 백필 대상**으로 처리한다.
- 단, drama10(Q1 expansion) 범위에서는 누락을 허용하지 않는다(검증 fail).
- drama10 외 누락 row는 코드북 키 확장 전까지 보류(backlog)로 유지하고, strict 정답 승격에 사용하지 않는다.

## 3) Phase1 Allow-list (저장 허용 키)
- `A_MORAL_FRAME_SHIFT`
- `A_VIOLENCE_ADAPTATION`
- `A_RISK_OR_SURVIVAL_MODE`
- `A_RELATIONSHIP_SHIFT`
- `A_EXTERNAL_PRESSURE`
- `A_POINT_OF_NO_RETURN`

## 4) 키 정의
| Key | 의미 | 대표 질문 |
|---|---|---|
| `A_MORAL_FRAME_SHIFT` | 정당화 프레임/도덕 판단 전환 | `Q01_EXP_01`, `Q01_EXP_04` |
| `A_VIOLENCE_ADAPTATION` | 폭력 적응/위협 도구화 징후 | `Q01_EXP_02`, `Q01_EXP_06` |
| `A_RISK_OR_SURVIVAL_MODE` | 생존/리스크 허용 모드 전환 | `Q01_EXP_03`, `Q01_EXP_04` |
| `A_RELATIONSHIP_SHIFT` | 관계 권력/신뢰 변화 | `Q01_EXP_05` |
| `A_EXTERNAL_PRESSURE` | 외부 위협/수사/조직 압력 | `Q01_EXP_03`, `Q01_EXP_05`, `Q01_EXP_06` |
| `A_POINT_OF_NO_RETURN` | 되돌릴 수 없음 전환 | `Q01_EXP_06` |

## 5) 참조 SoT
- 상속 트리: `fivecircles/architecture/specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
- 질문 매핑: `fivecircles/architecture/specs/expension100/question-map.q01-expansion.phase1.json`
- 실행 맵: `front/common/productionQ/inheritancePhase1.ts`
- 검증 스크립트: `fivecircles/test/validate-reveal-target-key-gate.py`
- 런타임 검증 스크립트: `fivecircles/test/validate-reveal-target-key-runtime-phase1.py`
- 운영 입력 스크립트: `scripts/ops/seed_expension100_q1_attribute_reveals.sql`, `scripts/ops/run_expension100_q1_seed_and_validate.sh`
- 운영 백필 스크립트: `scripts/ops/backfill_event_reveal_target_key_phase1.sql`

## 6) 변경 규칙
- 키 추가/수정/삭제 시 아래 4개를 같은 PR에서 함께 갱신한다.
1. 이 코드북 문서
2. `inheritance-closure-taxonomy.phase1.json`
3. `question-map.q01-expansion.phase1.json`
4. `inheritancePhase1.ts` + 로컬 게이트 통과 결과
