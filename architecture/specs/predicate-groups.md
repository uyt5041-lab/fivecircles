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
| ADVERSARY | ATTACKS, DEFEATS, KILLS, CAPTURES, BETRAYS | THREAT, THREATENED, BLACKMAIL, BATTLE | 파생 질문(적대자). 1급 predicate 확장은 승격 프로세스로. |
| ALLY | ALLIES_WITH, JOINS | ALLY, ALLIES_WITH, JOINS | 파생 질문(협력자). MEETS는 보조 증거로만 사용 권장. |

---

## 2) 사용 규칙

Rule A: 일반 검색은 PredicateCode만
- user-facing 검색/필터에서 group을 노출하지 않는다(운영/QA 레이어).

Rule B: fallback은 그룹에서만
- `predicate_suggestion`은 불안정 텍스트이므로, 일반 검색 조건으로 쓰지 않는다.
- 그룹 조회에서만 "보정" 목적의 fallback을 제한적으로 사용한다.

Rule C: 승격과 분리
- group은 "질문 의미"를 표현하는 단위이고, enum 승격은 "데이터 품질/검색 정확도"를 올리는 작업이다.
- group 자체는 유지하면서 내부 predicate 세트를 조정해도 된다.

