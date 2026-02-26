# Axis Mapping (Q1~Q15 + Q1 Expansion)

기준일: 2026-02-26  
owner: Team C (박지수, Predicate/Executor lane)

## 1) Layer Boundary (A1-0)
- Axis는 탐색/설명(WHY/UI) 레이어 정책이며, strict 탐색 결과에는 영향을 주지 않는다.
- strict 정답 탐색은 `StrictQuerySpec(templates + 04 matrix)`만 따른다.

## 2) Input Sync Scope (A1-1)
- `front/common/productionQ/templates.ts`
- `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex20-axis.md`

정렬 기준
- `question_id` 오름차순(`Q01..Q15`, `Q01_EXP_01..06`)
- predicate anchor는 strict `predicateCodeAnyOf` 우선, 없으면 `evidence_event_id`의 실제 predicate를 사용한다.

## 3) Mapping Table (A1-2)
| template_id | question_id | axis | predicate_anchor |
| --- | --- | --- | --- |
| `BB_Q1_WALTER_FIRST_KILL` | `Q01` | `PRECEDES` | `KILLS` |
| `BB_Q2_FIRST_AMPHETAMINE_COOK` | `Q02` | `PRECEDES` | `MEETS` |
| `BB_Q3_FIRST_MEET_TUCO` | `Q03` | `REVEALS` | `MEETS` |
| `BB_Q4_SKYLER_DISCOVERS_CRIME` | `Q04` | `REVEALS` | `DISCOVERS|LEARNS` |
| `BB_Q5_WALTER_FIRST_CRIME_DECISION` | `Q05` | `PRECEDES` | `MEETS` |
| `BB_Q6_WALTER_JESSE_FIRST_PARTNERSHIP` | `Q06` | `STATE` | `ALLIES_WITH|JOINS|MEETS` |
| `BB_Q7_WALTER_FIRST_LIE_EXPOSED` | `Q07` | `STATE` | `OTHER` |
| `BB_Q8_WALTER_FAMILY_MOTIVE_CRACK` | `Q08` | `STATE` | `OTHER` |
| `BB_Q9_HANK_INVESTIGATION_PIVOT` | `Q09` | `REVEALS` | `DISCOVERS` |
| `BB_Q10_WALTER_FIRST_STRUCTURAL_THREAT` | `Q10` | `PRESSURE` | `ATTACKS|CAPTURES|BETRAYS|KILLS` |
| `BB_Q11_FIRST_SUSPECT_WALTER` | `Q11` | `REVEALS` | `OTHER` |
| `BB_Q12_WALTER_FIRST_POWER_SHIFT` | `Q12` | `STATE` | `TRANSFORMS` |
| `BB_Q13_WALTER_FIRST_REVENUE_FLOW` | `Q13` | `STATE` | `OTHER` |
| `BB_Q14_WALTER_SKYLER_RELATION_BREAK` | `Q14` | `STATE` | `BETRAYS|LEARNS|DISCOVERS` |
| `BB_Q15_WALTER_FIRST_COVERUP` | `Q15` | `PRECEDES` | `OTHER` |
| `BB_Q1_EXP_01_SELF_JUSTIFICATION` | `Q01_EXP_01` | `STATE` | `OTHER` |
| `BB_Q1_EXP_02_VIOLENCE_ADAPTATION_SIGN` | `Q01_EXP_02` | `STATE` | `MEETS` |
| `BB_Q1_EXP_03_EXTERNAL_PRESSURE` | `Q01_EXP_03` | `PRESSURE` | `OTHER` |
| `BB_Q1_EXP_04_FIRST_CALCULATED_KILL_CHOICE` | `Q01_EXP_04` | `PRECEDES` | `ATTACKS` |
| `BB_Q1_EXP_05_SECONDARY_RIPPLES` | `Q01_EXP_05` | `REVEALS` | `KILLS` |
| `BB_Q1_EXP_06_THREE_TURNING_TRIGGERS` | `Q01_EXP_06` | `PRECEDES` | `KILLS` |

## 4) Conflict Validation (A1-3)
- 1문항 1주축 원칙: 전체 21문항 검증 완료(중복 주축 없음).
- `LEAVES` 컨텍스트 분리 태그:
  - `Q06` 계열: `LEAVES_CONTEXT=AFFILIATION_CHANGE`
  - `Q07` 계열: `LEAVES_CONTEXT=DEATH_EXIT`

## 5) Governance (A1-4)
- 본 문서를 axis 단일 산출물(SoT)로 사용한다.
- 변경 시 아래를 동시에 갱신한다:
  - `templates.ts`
  - `04-template-strict-must-matrix.md`
  - `fivecircles/architecture/todolist.md`의 A1 체크 상태
