# Predicate Promotion Process (Suggestion -> PredicateCode)

목적
- `PredicateCode`는 폐쇄집합(검색/필터/집계의 1급 타입)으로 유지한다.
- 분류 불가/애매 케이스는 `predicate_code=OTHER` + `predicate_suggestion`으로 축적한다.
- 충분히 쌓이고 의미가 안정화되면, 심사를 통해 `PredicateCode`로 승격한다.

전제(SoT)
- 운영 편집/검수의 Source of Truth는 `event.predicate_suggestion`이다.
- wiki는 원본/히스토리로만 유지한다.

관련 문서
- `fivecircles/architecture/specs/predicate/suggestion-sot-event.md`

---

## 1) 입력(축적)

Write 정책(권장)
- `predicate_code != OTHER`이면 `predicate_suggestion`은 NULL로 저장한다.
- `predicate_code == OTHER`이면 `predicate_suggestion`을 저장한다.

축적 쿼리(운영/분석)
- 후보 추출 기준: `predicate_code='OTHER' AND predicate_suggestion IS NOT NULL`

---

## 2) 후보 선정(집계)

Candidate list (per drama)
- group by `UPPER(TRIM(predicate_suggestion))`
- count desc

필수 메타(운영 문서로 남길 것)
- 후보 키워드
- 의미 정의(한 문장)
- 기존 PredicateCode로 흡수 가능한지 여부
- 관련 질문/위젯 (Q 번호)

---

## 3) 심사(승격 기준)

승격 최소 기준(초안)
- 의미가 1문장으로 정의 가능하며, 팀 내 합의가 유지된다.
- 기존 `PredicateCode` 합성(group)으로 해결이 불가능하거나 품질이 현저히 떨어진다.
- 드라마별로 빈도가 충분하다(예: drama 단위 N회 이상).

보수적 원칙
- "텍스트 키워드"가 아니라 "사건 타입"으로 승격 가능한 것만 PredicateCode로 추가한다.
- 물질/대상(예: 암페타민, 돈) 같은 "객체"는 predicate 확장만으로 해결하지 않는다.

---

## 4) 승격 실행(코드/문서/데이터)

Step 1: enum 추가
- `common/PredicateCode`에 신규 코드 추가
- 설명(description) 및 그룹 매핑 문서 갱신

Step 2: 라벨링/프롬프트 정렬(있는 경우)
- wiki/intelligence 입력에서 해당 사건을 신규 predicate로 매핑하도록 정렬

Step 3: 백필(선택)
- 과거 `OTHER + predicate_suggestion` 데이터를 신규 predicate로 일괄 변경하는 백필 스크립트/절차
- 백필은 운영 리스크가 있어 옵션으로 둔다.

Step 4: 가드레일
- OTHER/UNKNOWN 필터 정책 유지(일반 검색에서 OTHER를 1급 필터로 만들지 않음)
- 신규 predicate가 들어가더라도 기존 group 동작은 유지

---

## 5) 추적 지표(품질)

추천 지표(초안)
- 후보 키워드 상위 N 목록의 변화량
- 승격된 코드 사용 비율(OTHER 감소율)
- 질문별 결과 hit rate(0건 비율) 및 운영 만족도(정성)
