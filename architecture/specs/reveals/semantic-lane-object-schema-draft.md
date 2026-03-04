# Semantic Lane Object Schema Draft

기준일: 2026-03-04

목적
- RDB 메인 레인을 유지한 상태에서, triple store/Fuseki 같은 semantic 보조 레인에 올릴 `object` 타입 축의 초안을 고정한다.
- 현재 reveal/predicate semantic 문서에 흩어진 `CHARACTER`, `ATTRIBUTE`, `RELATION`, `ALIAS`, `LOCATION` 계열을 하나의 object schema로 정리한다.
- 지금 운영에 이미 있는 것과, 아직 draft인 것을 분리해서 적는다.

비범위
- 지금 당장 MySQL 스키마를 바꾸지 않는다.
- `event_reveal.target_type` 런타임 허용값을 즉시 늘리지 않는다.
- strict-first answer selection을 semantic object 질의로 교체하지 않는다.

## 1) 고정 결론

1. 메인 운영 레인은 계속 RDB다.
2. semantic lane은 **RDB에 없는 의미 분류/동일성/상속 구조**를 보조한다.
3. object schema는 semantic lane에서 먼저 넓게 가져가되, runtime RDB는 현재 `CHARACTER | ATTRIBUTE`를 유지한다.
4. `ALIAS`는 독립 object type으로 둘 수 있지만, 현재 문서/운영 상태에선 `IDENTITY/CHARACTER` semantic branch의 하위 의미로 먼저 다루는 편이 안전하다.

## 2) Object Type 초안

| object type | 상태 | 의미 | 현재 RDB 대응 |
| --- | --- | --- | --- |
| `CHARACTER` | implemented | 특정 인물/정체 | `event_reveal.target_type='CHARACTER'`, `target_id=character.id` |
| `ATTRIBUTE` | implemented | 사실/속성/상태/압력/관계 변화 등 | `event_reveal.target_type='ATTRIBUTE'`, `target_key` 또는 phase1 `aboutCharacterId` |
| `RELATION` | draft | 인물 간 관계 자체(부부, 혈연, 동맹, 배신, 소속) | 현재는 `ATTRIBUTE` 또는 relation predicate로 우회 |
| `ALIAS` | draft | 동일 인물의 가명/코드네임/마스크 정체 | 현재는 `CHARACTER reveal` + `RK_ALIAS_IDENTITY` semantic leaf로 우회 |
| `LOCATION` | draft | 장소/거점/은신처/행선지 | 현재는 `ATTRIBUTE` semantic key 후보 |
| `ORG` | draft | 조직/소속/집단 | 현재는 `ATTRIBUTE` 또는 `RELATIONSHIP/AFFILIATION` 의미로 우회 |
| `ITEM` | draft | 물건/증거물/소지품 | 현재는 `ATTRIBUTE` 또는 event summary로 우회 |

## 3) 왜 이렇게 나누는가

### 3.1 운영 구현된 것
- `CHARACTER`
  - identity reveal, partner merge, alias merge의 현재 실구현 축
- `ATTRIBUTE`
  - 사실 공개, 상태 변화, 압력, 관계 프레임 변화의 현재 실구현 축

### 3.2 semantic lane에만 먼저 올릴 것
- `RELATION`
  - object로 두면 “무슨 관계가 드러났는가”를 명시적으로 모델링할 수 있다.
- `ALIAS`
  - `sameAs`, `aliasOf`, `maskIdentityOf` 같은 동일성/가면 관계를 모델링하기 쉽다.
- `LOCATION`, `ORG`, `ITEM`
  - 현재 RDB에는 직접 타입이 없지만, semantic lane에서는 reveal target/object로 다루기 좋다.

## 4) Alias 위치

`ALIAS`는 두 가지 모델이 가능하다.

1. **semantic leaf로만 둔다**
- 예: `R_IDENTITY_REVEAL > RK_ALIAS_IDENTITY`
- 장점: 현재 구현과 충돌이 적다.
- 단점: object type query로는 직접 못 쓴다.

2. **독립 object type으로 승격한다**
- 예: `objectType=ALIAS`, `objectKey=HEISENBERG`
- 장점: alias 중심 질의/동일성 모델링이 쉬움
- 단점: runtime RDB와의 대응 규칙을 새로 만들어야 한다.

현재 추천
- **Phase1/문서 기준은 1번**
- semantic lane이 안정되면 2번 검토

## 5) semantic lane triple 초안

### 5.1 object catalog

```turtle
ns:CHARACTER a ns:ObjectType .
ns:ATTRIBUTE a ns:ObjectType .
ns:RELATION a ns:ObjectType .
ns:ALIAS a ns:ObjectType .
ns:LOCATION a ns:ObjectType .
ns:ORG a ns:ObjectType .
ns:ITEM a ns:ObjectType .
```

### 5.2 object family 예시

```turtle
ns:rk_alias_identity a ns:RevealSemantic ;
  ns:objectType ns:ALIAS ;
  ns:broader ns:r_identity_reveal .

ns:rk_crime_fact a ns:RevealSemantic ;
  ns:objectType ns:ATTRIBUTE ;
  ns:broader ns:r_evidence_reveal .

ns:rk_affiliation a ns:RevealSemantic ;
  ns:objectType ns:RELATION ;
  ns:broader ns:r_relationship_reveal .
```

### 5.3 runtime 매핑 레이어 예시

```json
{
  "objectType": "ATTRIBUTE",
  "runtimeSource": "event_reveal",
  "runtimeTargetType": "ATTRIBUTE",
  "runtimeKeyField": "target_key",
  "runtimeIdField": "target_id"
}
```

## 6) query 해석 규칙

semantic lane에서 object는 이렇게 해석한다.

1. `CHARACTER`
- runtime filter:
  - `target_type='CHARACTER'`
  - `target_id=<character.id>`

2. `ATTRIBUTE`
- runtime filter:
  - `target_type='ATTRIBUTE'`
  - `target_key IN (...)`
  - phase1에선 필요 시 `target_id=aboutCharacterId` fallback

3. `RELATION`
- 현재 runtime 직접 질의 없음
- 우선 semantic overlay / dashboard / explanation용

4. `ALIAS`
- 현재 runtime 직접 질의 없음
- 우선 `CHARACTER reveal + RK_ALIAS_IDENTITY` 조합으로 해석

5. `LOCATION|ORG|ITEM`
- 현재 runtime 직접 질의 없음
- semantic draft / ontology 설계 / future object resolver용

## 7) 현재 문서들과의 관계

이미 구현/고정된 축
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex14-reveal-implementation.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/rdf/inheritance-blueprint.md`

semantic 확장 초안
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/reveals/reveal-semantic-inheritance-draft.md`

object 확장 경로 인덱스
- `/Users/pio/IdeaProjects/nospoiler/fivecircles/architecture/specs/object구현계획-경로.md`

## 8) 추천 운영 해석

지금 당장 semantic lane에 올릴 수 있는 object schema는 다음 순서가 적당하다.

1. `CHARACTER`
2. `ATTRIBUTE`
3. `RELATION`
4. `ALIAS`
5. `LOCATION`
6. `ORG`
7. `ITEM`

단, runtime strict answer lane은 계속 다음 원칙을 유지한다.

- `CHARACTER`, `ATTRIBUTE`는 RDB가 메인
- `RELATION`, `ALIAS`, `LOCATION`, `ORG`, `ITEM`은 semantic lane에서 먼저 정의
- 필요할 때만 runtime materialization 또는 join helper 추가
