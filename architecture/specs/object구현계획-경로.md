# Object 구현계획 경로

## 관련 파일 인덱스

### 스펙 (구현 계획)
- `fivecircles/architecture/specs/reveals/reveals-routing-mvp-and-v3.md` — V3 `target_key`/object 1급 엔티티화 로드맵 (섹션 5~7)
- `fivecircles/architecture/specs/reveals/semantic-lane-object-schema-draft.md` — semantic 보조 레인 object type 초안 (`CHARACTER|ATTRIBUTE|RELATION|ALIAS|LOCATION|ORG|ITEM`)

### 제안/설계 원본
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex04-triplestore.md` — 트리플 구조 `(subject)(predicate)(object)` 원형
- `fivecircles/architecture/proposals/공유-온톨로지레이어구축/15-input-data2.md` — `object_type`, `object_id`, `object_text` 스키마 초안

### 보조
- `fivecircles/architecture/specs/predicate/rdf-owl-extension-notes.md` — object 확장 시 질문 레이어 안정성 원칙
- `fivecircles/architecture/specs/reveals/reveals-classification.md` — ATTRIBUTE target의 세부 key 필요성
- `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md` — object 메타 재사용 케이스

### 검색 정확도 (anti-hallucination)
- `fivecircles/architecture/specs/questions-anti-halus/01query-examples.md` — SPARQL 패턴 → SQL 템플릿 매핑
- `fivecircles/architecture/specs/questions-anti-halus/02exists-limit1.md` — Answerability Gate (exists-safe/exists-any 3상태)
- `fivecircles/work/review/review-anti-haluc.md` — Claude/Codex 리뷰 (probe, 민감도 정책)

---

## 로드맵 요약

| 단계 | object 처리 | 핵심 |
|---|---|---|
| **V2.5 (현재)** | `q` 키워드 + `qAnyOf[]` 유의어로 텍스트 근사 | miss 감수, probe(exists-gate)로 탐지 |
| **V3 최소** | `event_reveal`에 `target_key` 추가 (`CRIME_FACT`, `DRUG_PRODUCTION` 등) | object를 코드화 |
| **V3 정석** | object 1급 엔티티 + `event_object` 조인 테이블 | 완전 구조화, 스키마 `15-input-data2.md` 참고 |

### 핵심 파일: `reveals-routing-mvp-and-v3.md`
- V2.5 Option 1: `ATTRIBUTE target_id = aboutCharacterId` (0 금지)
- V3 Option 2: `target_key` 또는 object 1급 엔티티화
