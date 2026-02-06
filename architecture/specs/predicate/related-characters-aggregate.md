# Related Characters Aggregate (Single Endpoint) - Draft

목적
- “적대자/협력자/관계성” 같은 파생 질문에서 발생하는 N+1 호출(`related-characters` 1회 + `coevents` m회)을 **1회 호출**로 흡수한다.
- Q1~Q15 뿐 아니라, 이후 질문 위젯/QA 라우터에서 “다중사용(multi-use)” 가능한 집계 엔드포인트를 제공한다.

원칙
- 기본 데이터 품질을 훼손하지 않기 위해:
  - `PredicateCode`(폐쇄집합) 기반 집계를 우선한다.
  - `predicate_suggestion`은 `PredicateGroup` 집계에서만 제한적으로 fallback 한다.
- 스포일러 게이트:
  - 모든 집계는 `safeUpToEpisode=K`를 강제 적용한다(episode gate).

관련 문서
- 그룹 정의: `fivecircles/architecture/specs/predicate/groups.md`
- 그룹/승격 전략: `fivecircles/architecture/specs/predicate/README.md`
- Q1~Q15 라우팅(시범용): `fivecircles/architecture/specs/predicate/ex16-q1-q15-구현-라우팅-시범용.md`

---

## 제안 API(초안)

### 1) Aggregate
- `GET /api/event/v2/characters/{characterId}/related-characters/aggregate`

Query params
- `safeUpToEpisode` (required): `K`
- `mode` (required): `ADVERSARY | ALLY | COEVENTS` (확장 가능)
- `limit` (optional): default 30, max 200
- `minScore` (optional): default 0
- `includeEvidenceEventIds` (optional): default false

응답(개념)
```json
{
  "characterId": 100,
  "safeUpToEpisode": 3,
  "mode": "ADVERSARY",
  "items": [
    {
      "otherCharacterId": 200,
      "score": 17,
      "countsByGroup": {
        "BATTLE": 3,
        "ADVERSARY": 2
      },
      "evidenceEventIds": [2052, 2083]
    }
  ]
}
```

### 2) 스코어(권장, 단순)
- score = `sum(groupWeight[g] * countsByGroup[g])`
- groupWeight는 모드별로 고정:
  - ADVERSARY: `ADVERSARY`, `BATTLE` 가중치 높게
  - ALLY: `ALLY`, `AFFILIATION_CHANGE` 가중치 높게
  - COEVENTS: 총 공동 등장 수 기반

#### 기본 가중치 테이블(초안, 팀 합의용)

원칙
- “정확한 분류 신호”에 더 큰 가중치를 준다.
- `predicate_suggestion` fallback에서 잡히는 그룹은 오탐 가능성이 있으므로, 1급 코드 기반 그룹보다 가중치를 낮게 잡는다.
- countsByGroup는 가능한 한 "서로 중복되지 않게" 집계한다.
  - 예: ATTACKS/DEFEATS/KILLS는 BATTLE로만, CAPTURES/BETRAYS는 ADVERSARY로만 집계(중복 카운트 방지).

ADVERSARY
| Group | Weight | Notes |
| --- | ---: | --- |
| ADVERSARY | 8 | 배신/납치/위협 같은 고신뢰 신호를 우선 포함하는 그룹 |
| BATTLE | 5 | 전투/충돌(ATTACKS/DEFEATS/KILLS) 근사 |
| DEATH_EXIT | 2 | 결과(사망/퇴장)는 맥락 없이도 많이 발생할 수 있어 낮게 |

ALLY
| Group | Weight | Notes |
| --- | ---: | --- |
| ALLY | 8 | 협력/동맹 고신뢰 신호 |
| AFFILIATION_CHANGE | 5 | 합류/이탈은 협력 관계 전환을 잘 잡음 |
| COEVENTS | 1 | 단순 공동 등장만으론 협력 의미가 약함(가능 표시용) |

권장 파라미터(기본값)
- `mode=ADVERSARY`: `minScore=10`, `limit=30`
- `mode=ALLY`: `minScore=10`, `limit=30`
  - 초기에는 “근거 이벤트”를 같이 보여주고, minScore는 운영하면서 조정한다.

---

## 집계 로직(요약)

1) 후보군(otherCharacter) 생성
- 같은 drama 내에서 `characterId`와 공동 등장한 character를 집계(episode gate 적용).

2) 증거 이벤트 분류
- 각 공동 등장 이벤트를 `PredicateGroup`으로 분류해서 count 집계.

3) fallback(그룹 집계에서만)
- 이벤트의 `predicate_code=OTHER`인 경우, `predicate_suggestion` 키워드가 그룹의 fallback set에 포함되면 해당 그룹 count에 포함.
- 일반 검색/필터에서는 fallback 금지.

4) 정렬/limit
- score desc, tie-breaker는 `otherCharacterId asc` 같은 안정 정렬.

---

## 주의(품질/운영)

- `predicate_suggestion`은 텍스트이므로 drift(표기 흔들림)가 발생한다.
  - 최소한의 표준화(대문자 키워드, 트리밍, alias 테이블 또는 매핑 파일)가 필요하다.
- 이 엔드포인트는 “정답 확정”이 아니라 “후보 추천/정렬” 목적이다.
  - UI에서는 근거 이벤트(evidenceEventIds)를 함께 노출해 검증 가능하게 한다.
