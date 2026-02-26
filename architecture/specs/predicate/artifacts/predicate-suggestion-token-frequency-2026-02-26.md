# Predicate Suggestion Token Frequency (2026-02-26)

기준
- DB: `nospoiler_event.event`
- 필터: `predicate_code='OTHER'` + `predicate_suggestion` non-empty
- 토큰화: `TOKEN|label` 또는 `TOKEN:label`에서 `TOKEN`만 추출(대문자)

Top tokens

| token | count | action |
| --- | ---: | --- |
| NEW | 532 | 유지(신규 후보 큐), 자동 승격 금지 |
| THREAT | 28 | 기존 코드북 유지, ADVERSARY 세분화군에 포함 |
| BATTLE | 14 | 기존 코드북 유지, BATTLE 세분화군에 포함 |
| PRODUCTION | 13 | 코드북 신규 추가(후속 정확도 점검) |
| ALLY | 2 | 기존 코드북 유지 |
| BLACKMAIL | 2 | 기존 코드북 유지 |
| DEATH_EXIT | 2 | 기존 코드북 유지 |
| AFFILIATION_CHANGE | 2 | 기존 코드북 유지 |

결정
- `PredicateCode`는 유지(폐쇄집합 변경 없음).
- 세분화는 `PredicateSuggestionCode`/taxonomy/group-fallback에서 확장.
- 신규 코드북 추가는 빈도 기반으로 최소(`PRODUCTION`)만 반영.
- 승격 원칙은 기존 문서대로 유지:
  - answerset 기반 빈도/strict 정답 일치율 충족 시 RFC로 enum 승격.
