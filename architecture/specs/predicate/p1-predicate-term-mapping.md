# P1 Predicate 용어 사전 (user label ↔ runtime code ↔ group/fallback)

기준일: 2026-02-26  
목적: Q1~Q15 운영에서 혼용되던 용어(`BATTLE`, `AFFILIATION_CHANGE`, `DEATH`, `EXIT`)를 runtime `PredicateCode` + query-layer `PredicateGroup` + suggestion fallback으로 분리 고정한다.

## 1) 고정 원칙
- 런타임 정답 탐색(strict)은 `PredicateCode` 폐쇄집합만 사용한다.
- `PredicateGroup`/fallback은 strict miss 이후 질문 레이어(집계/보정)에서만 사용한다.
- user-facing 필터에 `OTHER/UNKNOWN`은 직접 노출하지 않는다.
- alias 정규화: `STATUS_CHANGE -> TRANSFORMS`.

## 2) 3계층 매핑표 (Canonical)
| User label(질문/문서) | Runtime PredicateCode (strict) | Query Group | Suggestion fallback token (`predicate_code=OTHER`) | 비고 |
| --- | --- | --- | --- | --- |
| 소속 변경 | `JOINS`, `LEAVES` | `AFFILIATION_CHANGE` | `AFFILIATION_CHANGE` | 합류/이탈 질문 |
| 사망 | `DIES` | `DEATH_EXIT` | `DEATH`, `DEATH_EXIT` | 사망 확정 질문 |
| 퇴장 | `LEAVES` | `DEATH_EXIT` | `EXIT`, `DEATH_EXIT` | 이야기 축 이탈(팀/현장/관계) |
| 사망/퇴장 | `DIES`, `LEAVES` | `DEATH_EXIT` | `DEATH`, `EXIT`, `DEATH_EXIT` | Q7류 통합 표현 |
| 전투/충돌 | `ATTACKS`, `DEFEATS`, `KILLS` | `BATTLE` | `BATTLE`, `CONFRONTS` | 공격/대치 이벤트 |
| 적대/압박 | `CAPTURES`, `BETRAYS` | `ADVERSARY` | `THREAT`, `THREATENS`, `THREATENED`, `INTIMIDATES`, `COERCES`, `BLACKMAIL`, `MANIPULATES`, `SEIZES_CONTROL`, `DOMINATES`, `POWER_SHIFT`, `TRUST_COLLAPSE`, `RELATIONSHIP_DAMAGE` | 집계 전용 보정 |
| 협력/동맹 | `ALLIES_WITH` | `ALLY` | `ALLY`, `ALLIES_WITH`, `PARTNERS_WITH`, `CO_CONSPIRATOR`, `SUPPLY_CONTRACT`, `RECURRING_DEAL` | 집계 전용 보정 |

## 3) LEAVES 중복 사용 규칙 (Q6/Q7 혼선 방지)
- 원칙: `LEAVES` 자체는 다의적이므로, 질문 의도는 group + 문맥 토큰으로 분리한다.
- 문맥 A(소속/파트너십 변화): `AFFILIATION_CHANGE` 레이어로 해석한다.
- 문맥 B(관계 단절/퇴장 결과): `DEATH_EXIT` 레이어로 해석한다.
- strict에서는 질문 의미에 맞는 최소 코드셋만 사용하고, ambiguous case는 `qAnyOf`로 문맥을 고정한다.

## 4) 적용 범위
- 템플릿 strict 필드: `strict_must.predicateCodeAnyOf`, `strict_must.excludePredicateCodeAnyOf`
- 그룹 집계/보정: `groups.md` 규칙 및 `PredicateSuggestionCode` 코드북
- 참고: `PredicateSuggestionCode`는 `predicate_code=OTHER` 이벤트에만 적용

## 5) 참조
- `common/src/main/java/com/nospoiler/common/PredicateCode.java`
- `common/src/main/java/com/nospoiler/common/PredicateSuggestionCode.java`
- `fivecircles/architecture/specs/predicate/groups.md`
- `fivecircles/architecture/todolist.md` (P1 블록)
