# ex23 Appendix - Detailed Notes (Reference)

이 문서는 ex23 본문(실행용 단일본)의 보조 자료다.
- 본문과 충돌할 경우 본문 우선
- 본문 범위 밖의 아이디어/예시는 참고용(non-normative)

## A) 상세 설계 근거
- B안 원칙
  - 상속/분류 선언은 RDF(또는 RDF 전개 taxonomy)에서 관리
  - RDF lane SoT는 `predicate_axis_taxonomy.json` 단일 기준으로 사용
  - Executor lane SoT는 `StrictQuerySpec(04 매트릭스/템플릿)` 기준으로 사용(taxonomy 직접 참조 금지)
  - generated JSON은 검증/리뷰용 산출물로 사용
  - strict-first 계약을 유지하고 fallback은 strict miss에서만 사용

## B) 산출물 예시 스켈레톤
실파일 예시:
- `scripts/ops/rdf/taxonomy/predicate_group.generated.example.json`
- `scripts/ops/rdf/taxonomy/predicate_inheritance.example.ttl`

### B-1. generated JSON (예시)
```json
{
  "version": "v0",
  "rules": {
    "strict_first": true,
    "fallback_only_on_strict_miss": true,
    "suggestion_allowed_only_when_predicate_code_is_other": true,
    "aliases": {
      "STATUS_CHANGE": "TRANSFORMS"
    }
  },
  "groups": {
    "ADVERSARY": {
      "runtime_members": ["CAPTURES", "BETRAYS"],
      "fallback_members": ["THREAT", "THREATENS", "THREATENED", "INTIMIDATES", "COERCES", "BLACKMAIL"]
    },
    "ALLY": {
      "runtime_members": ["ALLIES_WITH"],
      "fallback_members": ["ALLY", "ALLIES_WITH", "AFFILIATION_CHANGE", "PARTNERS_WITH", "CO_CONSPIRATOR"]
    },
    "BATTLE": {
      "runtime_members": ["ATTACKS", "DEFEATS", "KILLS"],
      "fallback_members": ["BATTLE", "CONFRONTS"]
    }
  }
}
```
- 참고: axis taxonomy의 ADVERSARY/ALLY 멤버셋과 query-layer group 멤버셋은 목적이 달라 다를 수 있다.

### B-2. inheritance TTL (예시)
```ttl
@prefix ns:   <https://nospoiler.dev/ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ns:ADVERSARY a rdfs:Class .
ns:ALLY a rdfs:Class .
ns:BATTLE a rdfs:Class .

ns:PC_CAPTURES a rdfs:Class ; rdfs:subClassOf ns:ADVERSARY ; ns:kind "RUNTIME" ; ns:code "CAPTURES" .
ns:PS_THREAT   a rdfs:Class ; rdfs:subClassOf ns:ADVERSARY ; ns:kind "SUGGESTION" ; ns:code "THREAT" .

ns:PC_ALLIES_WITH a rdfs:Class ; rdfs:subClassOf ns:ALLY ; ns:kind "RUNTIME" ; ns:code "ALLIES_WITH" .
ns:PS_PARTNERS_WITH a rdfs:Class ; rdfs:subClassOf ns:ALLY ; ns:kind "SUGGESTION" ; ns:code "PARTNERS_WITH" .

ns:PC_ATTACKS a rdfs:Class ; rdfs:subClassOf ns:BATTLE ; ns:kind "RUNTIME" ; ns:code "ATTACKS" .
ns:PS_BATTLE a rdfs:Class ; rdfs:subClassOf ns:BATTLE ; ns:kind "SUGGESTION" ; ns:code "BATTLE" .
```

## C) compile 파이프라인 상세
1. TTL 로드
2. 그룹 루트별 `rdfs:subClassOf*` 순회
3. leaf의 `kind/code` 수집
4. enum 유효성 검증
5. alias 정규화 적용
6. generated JSON 출력
7. drift 검증(TTL 변경 대비 JSON diff)

## D) 다중 소속 정책 상세
- 허용: 하나의 leaf가 여러 그룹에 속할 수 있음
- 런타임 처리: mode별 dedupe 우선순위로 점수 중복 방지
- mode 내 fallback token set은 가능하면 배타적으로 유지해 중복 카운트 리스크를 줄임
- 권장: 집계/추천 레이어에서만 사용, 정답 확정(strict)에는 영향 금지

## F) Suggestion 적용 가드 (구현 정합)
- 저장 가드: `predicate_code=OTHER`일 때만 `predicate_suggestion` 저장.
- 매칭 가드: group fallback 매칭은 `predicate_code=OTHER` 이벤트에서만 수행.
- 입력 소스 고정: fallback 매칭은 `event.predicate_suggestion`의 token(`extractToken`)만 사용.
- 실행 순서: strict hit가 있으면 fallback 미실행, strict miss에서만 suggestion fallback 수행.

## E) 확장 질문(Answer-first) 연결 메모
- ex23은 분류/상속 레이어 문서다.
- Answer-first(T01~T10, 확장 #1~#6)는 별도 문서/아티팩트에서 운영한다.
  - `fivecircles/architecture/specs/predicate/answer-first-backward-design.md`
  - `fivecircles/architecture/specs/predicate/artifacts/answerset-10.json`
  - `fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json`
- reveal 경계/판정은 아래 canonical 기준을 따른다.
  - `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`
  - `fivecircles/architecture/specs/reveals/reveals-classification.md`
  - `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md`
