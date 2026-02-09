# Review: Production Q Templates (MVP) + Defect Fixes
> Reviewer: codex-ops | Date: 2026-02-09

## Scope
- Plan doc: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`
- Target: Template MVP for dramaId=10 (Q1/Q2/Q3)
- Constraint: Use existing APIs (api3/api4/api7/api8) + `q` keyword filter; no Intelligence wiring in this task.

## Findings (Ordered)

### 1) api3 subject contamination risk (HIGH)
- 현재 `api3` 구현(`getEventsByCharacter`)은 REVEALS 파트너 캐릭터 이벤트를 합칠 수 있다.
- 템플릿이 `EARLIEST + limit=1`을 사용하면 “first” 질문이 파트너 이벤트로 오염될 수 있음.

**Fix (Applied in plan + implementation direction)**:
- 템플릿/프리셋 실행기는 `includeRevealPartner=false`로 api3를 호출해 “subject 단독 타임라인”을 강제한다.
- 기존 동작 호환을 위해 기본값은 `true`로 유지한다(기존 위젯 영향 최소화).

### 2) coevents 무제한 결과 비용 (MEDIUM)
- `api4` coevents는 limit 파라미터가 없어 큰 드라마에서 비용/응답이 커질 수 있다.

**Fix (Applied)**:
- `api4`에 `limit` optional 파라미터를 추가하고, 템플릿은 기본 limit(예: 200)로 호출한다.

### 3) 범용 템플릿을 위한 캐릭터 식별 (MEDIUM)
- 캐릭터 ID는 환경/시드에 따라 달라질 수 있어서 템플릿에서 id 하드코딩은 금지해야 범용화된다.

**Recommendation**:
- 템플릿은 `CharacterRef(name + aliases[])`로만 정의하고, 실행 시 드라마 캐릭터 목록에서 resolve한다.

### 4) 텍스트 오브젝트(q) 정확도 (MEDIUM)
- Q2 같은 텍스트 오브젝트는 결국 `summary/predicate_suggestion` 텍스트에 의존.

**Mitigation**:
- `qAnyOf[]`로 동의어를 여러 번 호출해 OR를 흉내내고, 결과를 합쳐 earliest 1개 선택.
- 실패 케이스는 “데이터 보강” 또는 “템플릿 키워드 세트 확장”로 해결(운영 레벨).

---

## Follow-up Review (After Defect Fixes)
- api3 `includeRevealPartner` / api4 `limit`은 구현 반영 완료(템플릿에서 사용 가능).
- 아래는 템플릿 실행기(프론트 구현)에서 남아있는 설계 구멍이다.

### 5) `qAnyOf[]` OR 다중 호출의 중복 제거 미정의 (MEDIUM)
- 같은 이벤트가 여러 키워드에 매칭될 수 있음.
- executor union 시 `Set<eventId>`로 중복 제거 후 `episodeStart ASC, id ASC`로 earliest를 고르는 규칙을 고정해야 함.

### 6) characterResolver 모호성 처리 (MEDIUM)
- MVP 목표가 “프리셋 버튼 1개로 실행”이면, 모호성 UI는 Phase 2로 미루는 게 일관적.
- MVP 권장: exact match only(name 또는 aliases의 정확 일치)로 제한하고, 모호하면 실패 메시지 + 템플릿 실행 중단.

### 7) Q3 "처음 만남" 정확도 한계 (LOW-MEDIUM)
- `MEETS` 데이터가 없으면 earliest coevent는 “첫 만남”을 보장하지 않음.
- Known risk로 문서화하고, 데이터 보강/승격은 후순위.

### 8) Intelligence QuerySpec 스키마 확정 시점 (LOW)
- Phase 1(템플릿 MVP) 결과를 보고 Phase 3(QuerySpec) 스키마를 확정하는 게 안전함.

### 9) Claude review 요청 상태
- `TASK-012` 리뷰가 완료되었고, 본 문서 하단 "Peer Review (TASK-012) by Claude" 섹션에 반영됨.

## Decision
- **APPROVE WITH NOTES** (BE 결함 수정 반영 완료. FE executor 구현 시 MEDIUM(5,6) 체크 필수)

## Next Actions (Implementation)
| # | Action | Owner | Priority |
|---|--------|-------|----------|
| 1 | FE: `productionQ/executor.ts` 구현 (qAnyOf 중복 제거 + Promise.all 병렬) | antigravity | HIGH |
| 2 | FE: `productionQ/characterResolver.ts` (exact match only, MVP) | antigravity | HIGH |
| 3 | FE: `productionQ/templates.ts` (Q1/Q2/Q3 브베 템플릿 데이터) | antigravity | HIGH |
| 4 | FE: QaPage에 Production Q 섹션 UI 추가 | antigravity | HIGH |

---

## Peer Review (TASK-012) by Claude
> Reviewer: claude-reviewer | Date: 2026-02-09

### Code Verification Summary

코드 기준으로 플랜 문서와 기존 리뷰(codex-ops) 지적사항을 대조 확인했다.

#### A. BE 파라미터 구현 확인 (CONFIRMED)

| 파라미터 | 파일 | 상태 | 비고 |
|----------|------|------|------|
| `includeRevealPartner` | `EventQueryController.java:73` | ✓ 구현 완료 | `defaultValue="true"`, 기존 호출 영향 없음 |
| partner skip 로직 | `EventQueryServiceImpl.java:114-117` | ✓ 정상 동작 | `false`일 때 `partnerId=null`로 merge 완전 차단 |
| api4 `limit` | `EventQueryController.java:89` | ✓ 구현 완료 | optional, 기본값 없음(전체 반환) |
| limit SQL | `EventMapper.xml:175-177` | ✓ 안전 | `#{limit}` 파라미터화, null이면 LIMIT 절 생략 |
| `q` keyword | `EventMapper.xml:140-145` | ✓ 구현 완료 | `summary` + `predicate_suggestion` 양쪽 LIKE 검색 |

#### B. 하위 호환성 (CONFIRMED SAFE)

- **FE 기존 호출**: `Q1_CharacterTrace.tsx:19`, `Q5_CoEvents.tsx:44`, `Q20_NarrativeDistribution.tsx:43`, `CharacterModal.tsx:52` — 모두 `includeRevealPartner`/`limit`을 명시하지 않아 기본값(`true`/전체)으로 동작. 기존 동작 변경 없음.
- **SQL 인젝션**: `#{keyword}` MyBatis 파라미터화로 안전.

#### C. 새로 발견한 이슈

**C-1. api4 limit 서버 캡 부재 (MEDIUM)**
- `limit` 파라미터에 상한이 없어 클라이언트가 `limit=999999`를 보내도 그대로 실행됨.
- api3는 `EventQueryServiceImpl`에서 `DEFAULT_LIMIT=30`, `MAX_LIMIT=200` 캡핑이 있지만, api4(coevents)에는 없음.
- **권장**: Service 레이어에서 `Math.min(limit, MAX_LIMIT)` 캡 추가. 또는 MVP에서는 FE에서 200 고정으로 충분.

**C-2. Character alias 미지원 (MEDIUM — MVP blocker 가능성)**
- `Character` 엔티티(`character-service`)에 `aliases` 필드가 없음. `name`, `actorName`, `description`만 존재.
- 플랜의 `CharacterRef(name, aliases[])` 설계는 DB 스키마 변경 없이는 불가.
- **MVP 대안**: FE 템플릿 데이터에 aliases를 하드코딩하고, resolver가 `character.name`과 template.aliases를 대조. DB 변경은 Phase 2.
  ```ts
  // templates.ts 예시
  { ref: { name: "월터 화이트", aliases: ["Walter White", "하이젠베르그", "Heisenberg"] } }
  ```
- resolver는 `characterApi.getDramaCharacters(dramaId)` 결과에서 `name` 일치만 확인(MVP).

**C-3. 테스트 커버리지 부재 (MEDIUM)**
- `EventQueryService`의 `includeRevealPartner=false` 케이스에 대한 단위 테스트 없음.
- `q` keyword 필터 + `predicateCode` 조합 테스트 없음.
- coevents `limit` 테스트 없음.
- **권장**: MVP 구현 전에 최소한 `includeRevealPartner=false`가 partner event를 제외하는지 검증하는 테스트 1건 추가.

**C-4. `includeRevealPartner=false`일 때 잔여 leak 가능성 (LOW)**
- `partnerId=null`이면 partner merge는 완전히 skip됨 → 주요 오염 경로 차단.
- 단, character 자체가 REVEALS 이벤트의 당사자인 경우(자기 자신이 revealer이면서 동시에 revealed), 그 이벤트는 `findByCharacterId`에 포함됨. 이는 "오염"이 아니라 정상 동작이지만, "순수 subject 타임라인"의 의미를 명확히 해둘 필요가 있음.

#### D. 플랜 평가

| 항목 | 판정 | 근거 |
|------|------|------|
| Phase 분리(Template MVP → QuerySpec) | ✓ 적절 | MVP 결과 없이 LLM 스키마 확정은 위험 |
| `qAnyOf[]` OR 다중 호출 전략 | ✓ 현실적 | 서버 OR 미지원이므로 FE executor에서 합치는 게 최선 |
| characterResolver exact match only (MVP) | ✓ 적절 | alias DB 없으므로 FE 하드코딩 + exact match가 MVP에 합리적 |
| Q3 earliest coevent 근사 | ✓ 수용 가능 | MEETS 데이터 부재 시 차선, known risk 문서화됨 |
| Fallback ladder (predicate → group → keyword) | ⚠️ 주의 | 과도한 fallback은 오탐 증가. MVP에서는 1차(predicate/keyword) 실패 시 "결과 없음" 표시가 더 안전 |

### Final Verdict
- **APPROVE** — BE 구현은 검증 완료, FE executor MVP 진행 가능.
- **조건**: C-1(limit 캡) + C-2(alias 하드코딩 전략 확정) + C-3(최소 테스트 1건)을 FE 구현 전 또는 병렬로 해결.

### Follow-up (codex-ops, 2026-02-09)
- [Done] C-1: api4 `limit`은 서비스 레이어에서 max 200으로 캡핑 적용. (refs: `services/event-service/src/main/java/com/nospoiler/eventservice/service/EventQueryServiceImpl.java`)
- [Done] C-2: 플랜 문서에 “aliases는 템플릿 데이터(하드코딩)”로만 유지(MVP) 명시. (refs: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`)
- [Done] C-3: `includeRevealPartner=false` / coevents limit cap 단위 테스트 추가. (refs: `services/event-service/src/test/java/com/nospoiler/eventservice/service/EventQueryServiceImplTest.java`)
