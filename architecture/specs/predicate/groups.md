# Predicate Groups (Query Layer) - Draft

목적
- Q1~Q15 및 파생 질문에서 쓰는 "합성 필터"를 1급 개념으로 분리한다.
- `PredicateCode` 폐쇄집합을 깨지 않으면서, 필요한 질문 의미를 그룹으로 표현한다.
- `predicate_suggestion` fallback은 그룹 조회에서만 제한적으로 사용한다.

정의
- `PredicateGroup`는 API 계약의 핵심 타입이 아니라, QA/FE 라우터 및 서버 집계 로직에서 사용하는 "질문 레이어" 개념이다.
- 구현 선택지
  - FE union: 다중 `predicateCode` 호출 결과를 병합
  - BE group: 서버에 group 파라미터를 추가해 1회 호출로 처리

---

## 1) 그룹 매핑 표(초안)

| Group | Primary PredicateCodes | Optional Fallback (predicate_code=OTHER AND predicate_suggestion in ...) | Notes |
| --- | --- | --- | --- |
| AFFILIATION_CHANGE | JOINS, LEAVES | AFFILIATION_CHANGE | Q6 대응. "소속 변경"을 합류/이탈로 근사. |
| DEATH_EXIT | DIES, LEAVES | DEATH, EXIT, DEATH_EXIT | Q7 대응. "퇴장"은 LEAVES로 근사. |
| BATTLE | ATTACKS, DEFEATS, KILLS | BATTLE | "전투"의 최소 근사. 필요 시 CAPTURES 등 추가 검토. |
| ADVERSARY | CAPTURES, BETRAYS | THREAT, THREATENED, BLACKMAIL | 파생 질문(적대자). BATTLE과 중복 카운팅을 피하려고 공격/전투는 BATTLE로만 집계. |
| ALLY | ALLIES_WITH | ALLY, ALLIES_WITH | 파생 질문(협력자). AFFILIATION_CHANGE(JOINS/LEAVES)와 중복을 피하려고 JOINS는 제외. |

---

## 2) 사용 규칙

Rule A: 일반 검색은 PredicateCode만
- user-facing 검색/필터에서 group을 노출하지 않는다(운영/QA 레이어).

Rule B: fallback은 그룹에서만
- `predicate_suggestion`은 불안정 텍스트이므로, 일반 검색 조건으로 쓰지 않는다.
- 그룹 조회에서만 "보정" 목적의 fallback을 제한적으로 사용한다.
  - 운영 표기를 위해 `TOKEN|한국어` 같은 structured 형식을 허용할 수 있다(서버는 토큰만 사용).

Rule C: 승격과 분리
- group은 "질문 의미"를 표현하는 단위이고, enum 승격은 "데이터 품질/검색 정확도"를 올리는 작업이다.
- group 자체는 유지하면서 내부 predicate 세트를 조정해도 된다.

Rule D: 템플릿/라우터의 fallback ladder (권장)
- Production Q 템플릿이나 QA 라우터처럼 "질문 레이어"에서 정답을 찾을 때는, 아래 순서로 fallback을 두는 것이 실무적으로 필요하다.
  - 1차(정확): `PredicateCode` 기반 조회 (폐쇄집합, 안정)
  - 2차(보정): `PredicateGroup` 기반 union/집계 + `predicate_suggestion` fallback(그룹에서만)
  - 3차(근사): 키워드 `q` 검색 (summary/predicate_suggestion LIKE). 텍스트 오브젝트가 있는 질문에서만 사용.
- 주의
  - `predicateCode=OTHER`를 user-facing 필터로 쓰는 fallback은 금지한다(정답 검색 품질 악화).
  - 3차(q)는 오탐 가능성이 높으므로, 템플릿은 `qAnyOf[]` 동의어 세트를 최소로 유지하고 "first" 질문은 보수적으로 적용한다.
