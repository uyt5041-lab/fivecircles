# NoSpoiler Project Total Todo List

> **Principle**: This file (`fivecircles/architecture/todolist.md`) is the **top-level source of truth** for work items.
> - Each member updates their own section.
> - `fivecircles/agent/queue.json` is kept as a **reference/backlog**, not the primary TODO list.
> **Last Updated**: 2026-02-26 (by Codex)

---

## 👥 Team Member A: Infra & Identity (System Gateway)
- [x] API Gateway Scaffolding
- [x] Auth Service Scaffolding
- [x] User Service Scaffolding (Flyway V1)
- [x] Gateway JWT 컨텍스트 전파 (검증/401·403 매핑, X-User-* 헤더 전달, 헬스·레디니스/재시도 설정)
- [x] 인증 API 완성 (/api/auth: signup|login|reissue, 이메일·닉네임 중복 409, 비밀번호 해시, access/refresh 저장)
- [x] 토큰 수명 관리 (리프레시 회전·무효화, clock skew 60s 적용, 인증 이벤트 감사 로그)
- [x] OAuth2 카카오 로그인 연동 완료 (무상태/쿠키 인증, 프론트엔드 리다이렉트 처리, 로그인 화면 강제 옵션 적용)
- [x] 회원가입 이메일 인증 400 원인 조치: SMTP 계정/비밀번호 환경변수 누락(공용 SMTP 설정) 정리 및 재검증, DTO @Setter 추가로 해결, MailHog/Real SMTP 전환 설정 완료
- [x] Refresh Token DB 저장 문제 해결 (Flyway 마이그레이션 스크립트 추가 및 동작 검증)
- [x] OAuth2 구글 로그인 연동 완료 (프론트엔드 버튼, 리다이렉트 처리, 설정 연동)
- [x] OAuth2 카카오 로그인 안정화 (Scope/Grant 오류 수정, 동의 화면 강제 옵션 적용)
- [x] 마이페이지 API 구현 완료 (프로필 조회/수정, 비밀번호 변경, 회원 탈퇴 - 검증 로직 포함)
- [x] OAuth2 예외 처리 강화 (invalid_grant 발생 시 로그인 페이지 강제 리다이렉트 및 안내 메시지)
- [x] 개발 모드 안내 문구 추가 (로그인 페이지: 테스터 계정 전용 안내)
- [x] auth-service Docker 설정 리팩토링 (application-docker.yml 분리 및 적용)
- [x] 세션 유지 및 UX 개선 (새로고침 시 로그인 유지, 드라마 선택 정보 영속화, 초기화 로딩 화면)
- [x] 카카오 로그인 디버깅 및 안정화 (Gateway 'No token' 문제 해결)
  - [x] API Gateway: 상세 필터 로그 추가 (Method, URI, Headers)
  - [x] API Gateway: `JwtTokenProvider` 로직 Auth Service와 동기화 (Clock skew, 키 생성 방식)
  - [x] Frontend: OAuth2 `HashRouter` 리다이렉트 문제 해결 (`/oauth2/redirect` 라우트 추가 및 `index.html` 스크립트 적용)

- [x] **Wiki Review UI & Data Ingestion (New)**
  - [x] Wiki Review 정렬 필터 개편 (단일 선택 방식 및 UI 고도화)
  - [x] 캐릭터 상세 모달 및 위키 캐릭터 선택 모달 UI 정제
  - [x] 드라마 데이터 벌크 인계 스크립트 구축 (`bulk_seed_moving.py`, `bulk_seed_pending.py`, `fetch_info.py`)
  - [x] 무빙 시즌 1 에피소드 데이터 인계 완료 및 시드 데이터 정비

- [x] **마이페이지 기능 구현 (User Service)**
  - [x] API: `GET /api/v1/users/me` (프로필 조회)
  - [x] API: `UPDATE /api/v1/users/me` (프로필 수정 - 닉네임)
  - [x] API: `POST /api/v1/users/me/profile-image` (프로필 이미지 수정 - MinIO 연동 및 DB 컬럼 TEXT로 변경)
  - [x] Storage: MinIO 공통 모듈화 및 폴더 구조화 구현 (`common/storage` 통합 완료)
  - [x] API: `POST /api/auth/v1/password/change` (비밀번호 변경)
  - [x] API: `DELETE /api/v1/users/me` (회원 탈퇴)
  - [x] 로직: 소셜 로그인 유저 비밀번호 변경 제한
  - [x] 버그수정: Flyway 마이그레이션 체크섬 불일치 및 V2 스키마 동기화 해결
  - [x] 버그수정: MinIO URL Localhost 접근 불가 문제 해결 (Docker 호스트네임 치환)
  - [x] Wiki Review 태그 필터 구현 (주요 사건, #사망, #배신, #거래, #명대사)
  - [x] `NotificationList.tsx`: 알림 클릭 시 홈 리다이렉트 로직 제거 및 읽음 표시 강화 (UX 개선)
  - [x] 보안 개선: OAuth2 토큰 URL 파라미터 노출 방지 (HttpOnly 쿠키 도입 완료)
- [x] 보안 개선: 이미지 업로드 클라이언트 유효성 검사 추가 (용량 및 타입 체크)
- [x] **이벤트 반전(Reveal) 로직 개선 및 프롬프트 일반화 (오징어 게임 이슈 해결)**
  - [x] 백엔드: `EventCharacterMapper` 자가-반전(Self-reveal) 제외 로직 수정
  - [x] 프론트엔드: `DashboardPage` 필터 안전장치 추가 & `CharacterModal` 역할 표시 수정 ('미공개 인물')
  - [x] 인텔리전스: `refine-fact.txt` 프롬프트 일반화 (특정 드라마 의존성 제거)
  - [x] 문서: `fivecircles/agent/prompt-optimization-strategy.md` 생성 (프롬프트 최적화 전략)
- [x] **프론트엔드 버그 수정 (2026-02-04)**
  - [x] `CharacterModal.tsx`: 중복 import 제거 및 `combinedSummaries` → `approvedSummaries` 수정 (500 에러 해결)
  - [x] `App.tsx`: `MyPage` 컴포넌트 import 누락 수정 (`ReferenceError` 해결)

---

## 👥 Team Member B: Core Domain (Content & Data)
- [x] Drama Service Scaffolding
- [x] Character Service Scaffolding (Flyway V1, V2)
- [x] Wiki Service Scaffolding (Flyway V1)
- [ ] Wiki Service: `proposeEdit` (Draft creation)
- [ ] Wiki Service: `getCharacterWiki` (Filtered view)
- [x] Wiki Service: **Triple Store Data Structure** (Ontology Support)
  - [x] Defined `PredicateCode` Enum in common module.
  - [x] DB: Add `refined_summary` & `wiki_submission_involved_character` table (Flyway V4).
  - [x] Logic: Merge character lists (main + involved) & PredicateCode Enum integration.
- [ ] **Pending**: Apply Wiki Schema Proposal (V2)
- [x] **Intelligence Service Support** (Assigned to Team B)
  - [x] Scaffolding `intelligence-service` (Port 8090, Dockerized, Gateway routed)
  - [x] Connect Wiki Service -> Intelligence Service (Async Flow)
  - [x] Backend Convention compliance (Removed `@Setter`, private internal port)
  - [x] 드라마별 인물 목록 조회 (Character Service 연동 완료)
  - [x] 실제 LLM API 연동 및 검증 (Smart Mock 구현 및 비동기 파이프라인 검토 완료)
  - [x] 정제 실패 시 재시도 로직 (Spring Retry 적용 완료)
  - [x] (Future) Actual LLM API key integration and Prompt tuning
  - [x] (B) LLM 연동 테스트 (OpenAI 기반): 프롬프트 엔지니어링 및 통합 검증 완료
    - [x] 인물 요약 통합(combineSummaries) 로직 구현 및 테스트 통과
    - [x] Intelligence Service API 엔드포인트 개설 (/api/intelligence/v1/refine, /summary)
    - [x] API 버전 관리 컨벤션 적용 및 .env 자동 로드 설정
  - [ ] (B) 로컬 LLM 통합 조사 (GLM 3.x) 및 Smart Mock 고도화
  - [ ] (Future) 정제 완료 알림 시스템 (WebSocket/SSE 연동)
  - [ ] **인물 요약본 생성 프롬프트 테스트 (Prompt Engineering)**
    - [ ] Wiki DB (`wiki_submission`) 기반 특정 character_id의 에피소드 K 이하 `refined_summary` 추출
    - [ ] 추출된 다수의 요약본을 하나로 통합하는 프롬프트 생성 및 검증
    - [ ] (Future) GLM 3.x 등 로컬 LLM 도입 가능성 조사 및 학습 (Next Week)
  - [x] **Wiki Service Enhancement & Testing (Done)**
    - [x] **Analysis & Design (Done)**
      - [x] Type mismatch: Entity/Request (String) vs LLM DTO (Enum) inconsistency.
      - [x] Async state: Missing `@Transactional` and object state sync in `refineSubmissionAsync`.
      - [x] Logic safety: Robust merging for main/involved characters and summary selection.
  - [x] **Phase 1: Logic Refactoring**
    - [x] Update `WikiSubmission` domain to use `PredicateCode` Enum for type safety.
    - [x] Strengthen `refineSubmissionAsync` (Add `@Transactional`, sync object state).
    - [x] Enhance character merging/summary logic in `checkAndProcessApproval`.
  - [x] **Phase 2: Comprehensive Testing**
    - [x] Implement `WikiSubmissionServiceTest` using Mockito.
    - [x] Validate E2E flow: Submit -> Refine (Mock) -> Vote -> Approve -> Event Publish (Mock).
    - [x] Test Edge Cases: LLM failure, invalid predicate codes, empty character lists.
- [ ] **Frontend Strategy & Implementation** (Team B)
  - [ ] Review existing `frontend.md` spec and align with current backend implementation.
  - [ ] Establish frontend architecture/strategy if missing (requested by Team B).
  - [x] **Admin CRUD Integration (Priority)**
    - [x] Mock Admin Login for development
    - [x] Drama CRUD integration (Admin Page)
    - [x] Character CRUD integration (Admin Page)
    - [x] Integrated image storage service (MinIO) - File upload for Drama/Character images (Common module used)
  - [ ] (Future) Actual frontend development based on strategy.
- [ ] MVP Experiment: Wiki list endpoint (`GET /api/wiki/v1/submissions?dramaId`)
- [ ] MVP Experiment: Wiki update/delete endpoints (if review UI requires)
- [ ] MVP Experiment: Seed drama/character/wiki data for FE smoke
- [ ] Wiki revealEpisode 도입 여부 결정 (event vs wiki, 스키마/UX 영향 검토)
- [ ] Wiki FK 정책 정합성 결정 (no-FK 원칙 vs 현재 FK 유지)

- [ ] **Ontology V3 & Image Spoiler Protection**
  - [ ] **DB Schema**: `character` 테이블에 `is_hidden` (default false), `alias` 컬럼 추가 (Flyway Migration).
  - [ ] **Common Module**: `PredicateCode` Enum에 `IDENTITY_REVEAL` (또는 `FACE_REVEAL`) 추가.
  - [ ] **Event Service**:
    - [ ] `EventQueryServiceImpl`: `REVEALS` 이벤트가 사용자의 safeEpisode 이전에 존재할 경우 `is_hidden` 해제 로직 구현.
    - [ ] DTO response에 `public_image_url`(가명용)과 `image_url`(진짜) 구분 반환 또는 로직 처리.
  - [ ] **Frontend (CharacterCard.tsx)**:
    - [ ] 실루엣 처리 조건 강화: `isLocked || character.isHidden` (등장했더라도 hidden이면 잠금).
    - [ ] Hidden 상태일 때 `public_image_url`(가면/실루엣) 표시, 해금 시 `image_url` 표시 스위칭.
  - [ ] **Wiki Service (Contribution)**:
    - [ ] 기여 화면에 "반전 캐릭터 여부(is_spoiler_identity)" 체크박스 추가.
    - [ ] 검증 로직에 해당 플래그 반영 (`is_hidden` DB 업데이트).

- [ ] **My Page UI Implementation**
  - [ ] Component: Profile View/Edit Form
  - [ ] Component: Password Change Form
  - [ ] Page: `/mypage` Layout & Routing
  - [ ] State: Auth Context Integration (User Info Sync)

---

## 👤 Team Member C: Intelligence & Filter (박지수 - YOU)
> **My Todo**: 이 섹션(C 영역)만 작업
### 1. Infrastructure & Setup - ✅ DONE
- [x] Docker Configuration (Add event, policy services)
- [x] Docker QA service (Dockerfile + compose service)
- [x] Gradle Project Scaffolding (event, policy, qa)
- [x] Register all services in `settings.gradle`

### 2. Core Logic Implementation - ✅ DONE
- [x] `SpoilerManager` Implementation (Policy engine)
- [x] `SpoilerPolicyController` API (`/api/v1/policy/check`)
- [x] Unit Testing for Policy logic

### 3. Ontology Service Implementation - ✅ DONE
- [x] JPA/MyBatis Entity Mapping (event, character, relation, reveal)
- [x] `EventService` & `EventController` API (/api/v1/events)
- [x] DB Schema Fix (V2) for event_reveal

### 4. QA Service (Sprint 1 Goal) - ✅ DONE
- [x] Scaffolding `qa-service`
- [x] Implement Health Check API (/api/v1/qa/health)

### 5. API Refinement & Spec Alignment (Priority: High)
- [x] **Backend Convention Compliance**
    - [x] Add Swagger (`@Tag`, `@Operation`) to Controllers.
    - [x] Refactor DTO/Entity Lombok annotations (`@Data` -> `@Getter`, `@Builder`).
    - [x] Add `springdoc` dependency to `build.gradle`.
- [ ] **Spec Alignment (`intelligence-api-contract.md`)**
    - [x] Remove `/api/v1` prefix from paths (Done in `feature/api-alignment`).
    - [x] Enhance `EventController` search (add `q`, `uptoEpisode` params).
    - [x] Enhance `QaController` (implement `POST /qa/episode-range`).
- [ ] Swagger UI 화면 예시 공유 (모바일 확인용)
- [x] Event relation PK에 type 포함 (V7 migration, type별 중복 허용)

### 6. REVEALS Option1 (V2.5 Data Quality Guardrails)
- [x] (BLOCKER) Intelligence prompt: ATTRIBUTE revealTargetId=aboutCharacterId, 0 금지 (`services/intelligence-service/src/main/resources/prompts/refine-fact.txt`)
- [ ] (BLOCKER) Intelligence mock 정합성: (현재는 원래 Mock 유지) 협의 후 `ATTRIBUTE revealTargetId=0` 제거 또는 fallback 정책 확정 (`services/intelligence-service/src/main/java/com/nospoiler/intelligenceservice/service/OpenAiLlmClient.java`)
- [x] (BLOCKER) event-service createEvent 방어벽: revealTargetId<=0 거부 + ATTRIBUTE about은 characterIds에 포함 강제 (`services/event-service/src/main/java/com/nospoiler/eventservice/service/EventServiceImpl.java`)
- [x] Representative reveal 안정화: reveal 정렬은 CHARACTER 우선 (`services/event-service/src/main/resources/mapper/event/EventRevealMapper.xml`)
- [x] PRECEDES suggestion revealBoost: event_reveal target_type에 ATTRIBUTE도 포함 (aboutCharacterId 가정) (`services/event-service/src/main/resources/mapper/event/EventMapper.xml`)
- [ ] (Policy) 기존 `event_reveal(target_type=ATTRIBUTE,target_id=0)` 데이터 전환 정책 확정(무시/백필/삭제 중 택1)

### 6. Next Steps (Sprint 2)
- [x] **Integration**: Connect QA -> Event -> Policy flow
- [ ] **Core Pipeline (no QA)**: Wiki 승인 → Event 생성 → Policy 태깅 정합성
- [x] 테스트용 서버 연결 스펙 설정
- [x] V2 이벤트 API curl 스모크 테스트 (create/search)
- [x] 이벤트 검색 시 스포일러 정책 연동 로직 업그레이드
- [x] 스포일러 정책 연동 curl 테스트
- [ ] 스포일러 정책 연동 테스트 완료 후 V3 진행 여부 결정
- [x] **위키 검증소 필터 개편**: 칩 방식에서 드롭다운 방식으로 전환 및 회차 필터 옆 배치 완료
- [x] **실시간 탭 카운트**: 필터링 상태에 따른 탭 숫자 실시간 동기화 구현 완료
- [ ] Verify Wiki→Event payload includes characterId; reconcile develop vs experimental contract
- [ ] Verify Wiki→Intelligence publish flow after approval
- [x] (N/A) Fix event-service EventServiceClient default URL (Handled by Docker profiles)
- [ ] Sync auth/gateway/user endpoint mismatches with Team A (auth base URL, TokenDto, logout parsing, reissue validation, gateway secret, user profile path)
- [ ] Fix auth/user mapping: user-service UserAuthResponse.id -> auth-service UserValidationResponse.userId (X-User-Id header missing in gateway)
- [x] **QnA 분리**: QA 연동/정확도 개선은 후순위로 분리
- [x] **Logic**: Multi-hop Ontology Retrieval
  - [x] **Admin/Precedes UI 보강**: 이벤트 summary 인라인 수정 + 데이터 소스 표시 + 탭/훅 분리로 상태 전이 단순화
  - [ ] **Precedes Admin followups (MVP)**:
    - [ ] (Rank) PRECEDES suggestion: 공유 캐릭터 2명 이상이면 추가 가산점 부여 (가까운 이벤트 후보 랭킹 안정화)
    - [ ] (UI) Precedes 페이지에서 predicate 편집 기능 추가 (predicateCode + OTHER일 때 predicateSuggestion)
    - [ ] (Bug) Precedes 페이지 이벤트 편집 아이콘 클릭 안되는 문제 해결 (summary/predicate 편집 진입 UX)
- [x] **ex14 정합성(TRANSFORMS)**: 공통 enum에 `TRANSFORMS` 추가 + `STATUS_CHANGE` 레거시(deprecated) 유지
- [x] **ex14 정합성(TRANSFORMS)**: Q20 집계 키 `STATUS_CHANGE` -> `TRANSFORMS` 정렬(legacy 합산 포함)
- [x] **ex14 정합성 문서화**: 체크리스트/변경 계획 정리 (spec: `fivecircles/architecture/specs/ex14-consistency-checklist.md`)
- [ ] **ex14 문서/스펙 치환(남음)**: `STATUS_CHANGE` 표기 제거 + intelligence `labelDraft.eventType` vs 저장 `predicate_code` 레이어 분리
- [x] **ex14 호환 레이어**: event-service read/write에서 `TRANSFORMS` 요청 시 `STATUS_CHANGE`도 매칭/정규화(이행 기간)
- [x] **ex14 백필(bit-ts)**: `nospoiler_event.event`/`nospoiler_wiki.wiki_submission`의 `predicate_code`를 `STATUS_CHANGE` -> `TRANSFORMS`로 일괄 변경
- [ ] **정합성 갭 체크 (ex14, 협업)**: reveal 메타(event_reveal)가 wiki/intelligence→event 파이프라인에서 실제 전달/저장되는지 “현상 확인”만 하고, 결과를 문서에 상태로만 명시 (구현은 보류)
- [x] **Reveal 입력 정합성(서버)**: `predicateCode=REVEALS` + `revealTargetId`가 있는 요청에서 `revealTargetType`이 없으면 **silent skip 금지**(BusinessException로 실패 처리). (refs: `fivecircles/architecture/specs/reveals/reveals-classification.md`, `fivecircles/architecture/specs/ex14-consistency-checklist.md`)
- [ ] **Reveal type 파이프라인**: `event_reveal.reveal_type(HINT|CONFIRM)`를 event 생성/수정 요청에서 받을 수 있게 DTO/API를 확장하고, 저장까지 end-to-end로 연결(기본값 정책은 질문 구현단계 정밀도 조정(QP1)에서 확정). (refs: `fivecircles/architecture/specs/reveals/reveals-classification.md`, `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md`, `services/event-service/src/main/resources/db/migration/V2__fix_event_reveal_schema.sql`)
- [ ] **Q1~Q15 정합성(별도)**: UI/스펙의 predicateCode(`BATTLE`, `AFFILIATION_CHANGE`, `DEATH`, `EXIT` 등)와 `common/PredicateCode`의 폐쇄 집합을 정렬 (ex14 범위 밖이므로 별도 작업으로 분리)
  - [ ] 게이트: Q1~Q15 템플릿에서 `strict_must.predicateCodeAnyOf` 및 `strict_must.excludePredicateCodeAnyOf`만 runtime `PredicateCode` 폐쇄집합 검사 대상으로 고정하고, group/label/qAnyOf는 검사 범위에서 제외 (검사 스크립트 구현 완료, CI hook 연결 보류)
    - [x] 로컬 게이트 스크립트: `fivecircles/test/validate-productionq-predicatecode-gate.py`
    - [ ] CI/파이프라인 연결: gate fail 시 배포/머지 차단
- [ ] **ex20~22.1 정합화 실행 트랙 (2026-02-26, Q20 우선/DB 최소변경)** (refs: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`, `ex23-RDF-inheritance-appendix.md`, `ex20-axis.md`, `ex21-SPO-N-Y.md`, `ex22-axis-N-Y-scetch.md`, `ex22.1-ops.md`, `fivecircles/architecture/specs/predicate/groups.md`)
  - [x] 1) Q20 기준 축/SPO/Predicate 운영원칙 문서 고정 (Quick20 커버리지 기준, role=`INVOLVED/SUBJECT/OBJECT`, predicate는 현행 `PredicateCode`+`PredicateGroup` 우선)
  - [ ] 2) role 입력 계약+파이프라인 추가 (**보류**: Intelligence 개발자(B)와 `involvedCharacters[{characterId,role}]` 계약 확정 후 재개)
    - [ ] 2-1) B 협의 체크: 응답 필드 추가 여부, `involvedCharacterIds` 호환 유지, role 허용값/기본값, 배포 순서(`intelligence -> wiki -> event`)
  - [ ] 3) relation type 확장 RFC는 보류: 현행 PRECEDES+REVEALS/Group 조합으로 커버리지 검증 후 필요 시 재개
- [ ] **axis/SPO/AND/WHY 구현 체크리스트 (2026-02-26, ex20~23 리뷰 반영)** (refs: `ex23-RDF-inheritance.md`, `ex23-RDF-inheritance-appendix.md`, `ex20-axis.md`, `ex21-SPO-N-Y.md`, `ex22-axis-N-Y-scetch.md`, `ex22.1-ops.md`, `ex22.2-expension-categorized-impl-plan.md`, `ex22.3-expension-expension-qs-imple2.md`, `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`, `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`)
  - [x] R0. RDF 승계(ex23) 선행 게이트 고정 (**최우선**)
    - [x] R0-1a) RDF lane SoT 범위 고정: `predicate_axis_taxonomy.json`은 **RDF query-only 경로**에서만 SoT로 참조
    - [x] R0-1b) Executor lane SoT 범위 고정: executor/classifier는 `StrictQuerySpec(04 매트릭스/템플릿)`만 SoT로 사용하고 taxonomy를 직접 읽지 않음
    - [x] R0-2) Axis(분류/신호) vs Group(필터/집계) 경계 문구를 ex23 기준으로 유지
    - [x] R0-3) Suggestion 가드(`OTHER` 저장/매칭, strict miss 후 fallback)를 구현 규칙과 동기화
    - [x] R0-4) planned/implemented 상태표 및 recursive TODO를 ex23 단일 기준으로 유지
    - [x] R0-5) ex23 참조를 관련 체크리스트/문서 refs 최상단에 고정
    - [x] R0-6) R0 완료 전 S/N/W 전 영역(`S*`, `N*`, `W*`) 계약 고정 금지(드리프트 방지)
  - [x] A-1. Answer-first 실험 세트(10문항) 고정 + 정답 데이터 입력 (**선행 게이트**: R0 완료 후, S/N/W 계약 고정 전에 완료) (refs: `fivecircles/architecture/specs/predicate/answer-first-backward-design.md`)
    - [x] A-1-1) `T01~T10 질문/axis/strictFilters` 스냅샷 파일 생성 (A4/B3/C3 구성, 파일: `artifacts/answerset-10.json`)
    - [x] A-1-2) 각 질문 `answer_event_id` 확정(기준: strict-first + earliest + approved, 증거 이벤트 링크 포함)
      - [x] A-1-2-a) 템플릿 근거(`templates.ts:evidence_event_id`)가 있는 9개 문항은 `answer_event_id` 반영 완료 (`answerset-10.json`)
      - [x] A-1-2-b) `T03(CUSTOM_T03_RV_GAS)` 앵커 확정(`subject+predicate=DIES+qAnyOf[RV,gas,독성]` strict로 `2441`)
    - [x] A-1-3) WHY 문항(`T08~T10`) `because_chain(PRECEDES)` 2~3 hop 구축 (신규 relation type 추가 금지)
    - [x] A-1-4) REVEALS 문항(`T05~T07`) `reveal_hint(attribute 포함)` 최소 1~3개 입력
    - [x] A-1-5) 산출물 스냅샷 저장: `fivecircles/architecture/specs/predicate/artifacts/answerset-10.json`
    - [x] A-1-6) 실패/공백 기록: strict 0건 문항은 `SPOILER_BLOCKED/NOT_ENOUGH_DATA`로만 표기하고 TODO 백로그(`questions-anti-halus/06-1-required-db-values.md`)에 연결 (현재 answerset-10 기준 strict miss 0건)
    - [x] A-1-7) 앵커 승격 규칙 적용: 기존 `PredicateCode` 우선, 미충족은 `OTHER+predicate_suggestion` 후보로 수집 후 **answerset 통계(빈도/strict 정답 일치율)** 기준으로 enum 승격 RFC 작성 (`answerset-10-anchor-promotion-metrics-2026-02-26.md`: 후보 0건)
      - [x] A-1-7-a) 승격 지표 추가: strict miss 시 fallback Top1의 사람 검수 정답 일치율(`precision@1`) 기록 (`N/A`, 표본 0)
  - [x] A-2. 후속 6문항 Answer-set(확장 검증) (**A-1 완료 후**) (refs: `ex22.3-expension-expension-qs-imple2.md`)
    - [x] A-2-1) 후속 #1~#6에 대해 `answer_event_id` 1개씩 확정
    - [x] A-2-2) 문항별 `reveal_attribute` 1~3개 + 필요 시 `because_chain` 2 hop 입력
    - [x] A-2-3) 산출물 스냅샷 저장: `fivecircles/architecture/specs/predicate/artifacts/answerset-6-expansion.json`
  - [x] A0. 기준 고정: Q20을 축/커버리지 기준으로 사용, strict는 `PredicateCode` 우선, group/fallback은 strict 0건 보정으로만 사용
  - [x] A1. axis 매핑표 고정: Q1~Q15(+Q1 확장)별 주축 `REVEALS/STATE/PRESSURE/PRECEDES` 1개를 결정하고 템플릿 id에 연결(설명/WHY/탐색 UI 레이어)
    - [x] A1-0) 레이어 경계 선언: **Axis는 탐색/설명 레이어 정책이며, strict 탐색 결과에는 영향을 주지 않는다.** (`axis-mapping-q1-q15.md` §1)
    - [x] A1-1) 입력 소스 동기화: `templates.ts`, `04-template-strict-must-matrix.md`, ex20 라벨 표를 동일 question_id 기준으로 정렬 (`axis-mapping-q1-q15.md` §2)
    - [x] A1-2) 매핑표 작성: `template_id/question_id/axis/predicate anchor` 4컬럼으로 1차 테이블 확정 (`axis-mapping-q1-q15.md` §3)
    - [x] A1-3) 충돌 검증: 축 다중할당 금지(1문항=주축 1개), Q6/Q7 `LEAVES` 중복은 컨텍스트 분리 태그 부여 (`axis-mapping-q1-q15.md` §4)
    - [x] A1-4) 산출물 고정: axis 매핑표를 단일 문서로 승격하고 변경 owner 지정 (`axis-mapping-q1-q15.md` header/§5)
  - [x] P1. Predicate 정합성 정리(선행, 정책 고정 전): 문서/UI의 `BATTLE/AFFILIATION_CHANGE/DEATH/EXIT`를 runtime `PredicateCode`+Group 레이어로 분리 명시 (ref: `fivecircles/architecture/specs/predicate/p1-predicate-term-mapping.md`)
    - [x] P1-1) 용어 사전 작성: user label <-> runtime code <-> group/fallback 3계층 매핑표 확정 (`p1-predicate-term-mapping.md`)
    - [x] P1-2) Q6/Q7 규칙 명시: `LEAVES` 중복 사용 원칙(소속변경/퇴장 컨텍스트 분리) 문서 고정 (`groups.md` Rule E, `p1-predicate-term-mapping.md`)
    - [x] P1-3) 금지 규칙: user-facing 필터에 `OTHER/UNKNOWN` 직접 노출 금지 재확인 (`검색 정책(OTHER/UNKNOWN)` 완료 항목 + Predicate README 반영)
  - [x] P2. 단일 매핑 소스화(선행): group 매핑 테이블 1곳에서 FE/BE/문서가 공통 참조하도록 정리(드리프트 방지)
    - [x] P2-1) SoT 위치 결정(선행): predicate group canonical 문서 1개를 먼저 지정 (`fivecircles/architecture/specs/predicate/groups.md`)
    - [x] P2-2) 참조 통일: FE 가이드/BE 상수/운영문서가 canonical 문서를 참조하도록 링크 정리 (`predicate/README.md`, `production-q-templates-and-intelligence-queryspec.md`)
    - [x] P2-3) 변경 프로세스: 매핑 변경 시 영향영역(FE/BE/QA) 체크박스 템플릿 추가 (`predicate-group-change-checklist.md`)
  - [ ] S1. SPO strict 필터 고정: `subject/target/with/predicateCodeAnyOf/qAnyOf` 조합을 04 매트릭스와 1:1 동기화(정답 이벤트 탐색 레이어)
    - [ ] S1-1) strictFilters 키 정규화: `subject|target|with|predicateCodeAnyOf|qAnyOf|excludePredicateCodeAnyOf` allow-list 확정
      - [x] S1-1-0) `qAnyOf` 의미 고정: 키워드 OR(기본은 단일 쿼리 OR 조건), 불가한 경우에만 multi-query union 허용. predicate 집합과는 AND 결합 (`strict-filters-contract.md`)
      - [x] S1-1-a) shorthand(`subject=Walter` 등) -> 런타임 필드 매핑표 고정 (`strict-filters-contract.md`)
      - [x] S1-1-b) predicate 대소문자/legacy(`STATUS_CHANGE`) 정규화 규칙 명시 (`strict-filters-contract.md`, `validate-productionq-predicate-normalization-gate.py`)
      - [x] S1-1-c) 로컬 strict 키 게이트 구현: `strict_must` 키 allow-list 검사 스크립트 추가 (`fivecircles/test/validate-productionq-strict-keys-gate.py`)
      - [ ] S1-1-d) CI/파이프라인 연결 보류: gate fail 시 머지/배포 차단
    - [x] S1-2) 템플릿 동기화: FE 템플릿과 문서 strict_must를 diff 기준으로 맞춤 (`validate-productionq-matrix-sync-gate.py` 기준으로 불일치 4건 정렬 완료)
    - [x] S1-3) drift 방지 검증: 템플릿-매트릭스 불일치 시 fail 규칙 추가 (로컬 gate: `fivecircles/test/validate-productionq-matrix-sync-gate.py`, CI 연결은 보류)
  - [x] S2. role 해석 규칙 고정: role 미입력 데이터는 `INVOLVED`로 처리하고, `SUBJECT/OBJECT`는 조회/설명 레이어에서 우선 노출 (refs: `EventV3QueryServiceImpl`, `EventV3QueryServiceImplTest`)
    - [x] S2-1) role 우선순위 표준화: `SUBJECT > OBJECT > INVOLVED` (코드: `roleOrder`)
    - [x] S2-2) 무역할 데이터 처리: role null/blank는 `INVOLVED`로 보정 (코드: `normalizeRole`)
    - [x] S2-3) 설명 노출 규칙: WHY 출력에서 SUBJECT/OBJECT가 있으면 해당 관점 문장을 우선 생성 (코드: `buildPerspectiveExplanation`, 테스트 추가)
  - [x] N1. AND 실행 규칙 고정: `predicateCodeAnyOf AND qAnyOf AND episode/K gate`를 deterministic 순서로 적용 (ref: `strict-filters-contract.md`, `productionQ/executor.ts`)
    - [x] N1-1) 평가 순서 고정: `K gate -> source_status(APPROVED only) -> predicate -> keyword(qAnyOf) -> 정렬` (`strict-filters-contract.md` 2.1)
    - [x] N1-2) AND/OR 의미 고정: `predicateCodeAnyOf`는 OR, `qAnyOf`는 OR, 두 집합 사이는 AND (`strict-filters-contract.md` 2)
    - [x] N1-3) tie-break 고정: `episode asc -> event_id asc`로 earliest deterministic 보장 (`productionQ/executor.ts` `sortEventsAsc`)
  - [x] N2. AND 회귀 테스트: Q6/Q7(`LEAVES` 중복), Q10(excludePredicate), Q14(coevents) 케이스를 스냅샷 검증 (`validate-productionq-and-regression.py`)
    - [x] N2-0) 스냅샷 기준 고정: canonical은 **BE executor 결과 JSON(정렬 포함)** 으로 통일 (`and-regression-q6-q7-q10-q14.json`)
    - [x] N2-1) 최소 fixture 세트: Q6/Q7/Q10/Q14 증거 이벤트 id 고정(+ 검증용 summary 병행)
    - [x] N2-2) 케이스별 기대결과: strict hit/strict miss/probe status를 스냅샷화
    - [x] N2-3) 회귀 게이트: 템플릿 변경 시 스냅샷 재검증 체크리스트 의무화 (`validate-productionq-and-regression.py`)
    - [x] N2-4) `answerset-10.json`을 N2 fixture/expected의 근거 SoT로 사용 (스냅샷 `sources` 명시)
  - [x] W1. WHY 근거 포맷 고정: `strict evidence_event_id + PRECEDES cause/effect + REVEALS 힌트` 3단 구조로 설명문 생성
    - [x] W1-1) WHY 응답 스키마: `answer_event`, `because_chain`, `reveal_hint`, `confidence_note` 필드 정의 (`types.ts`, `why-output-contract.md`)
    - [x] W1-2) 체인 생성 규칙: PRECEDES는 max hop 제한, 분기는 Top1 path만 본문 노출 (`useProductionQ.ts`, max hop=3)
    - [x] W1-3) 텍스트 템플릿: “무엇-왜-근거” 3문장 기본형 고정 (`executor.ts`, `ResultPanel.tsx`)
  - [x] W2. WHY 가드레일: strict 0건이면 `ANSWERED` 금지, probe 상태(`SPOILER_BLOCKED/NOT_ENOUGH_DATA`)만 반환
    - [x] W2-1) strict-first 강제: executor에서 strict miss 시 probe 선행, approx는 내부참고로만 유지 (`executor.ts`)
    - [x] W2-2) 상태 매핑 고정: `SPOILER_BLOCKED -> LOCKED`, `NOT_ENOUGH_DATA -> NO_DATA` (`types.ts`, `executor.ts`, `why-output-contract.md`)
    - [x] W2-3) 금지 규칙: **strict miss + probe hit** 케이스에서도 ANSWERED 전환 금지 테스트 추가 (`validate-productionq-probe-guard.py`, 로컬 gate)
  - [x] W3. WHY 출력 검증: FE `CAUSE/FOCUS/EFFECT` 정렬 우선순위와 문서 템플릿을 동일 규칙으로 통일
    - [x] W3-1) FE 정렬 규칙 점검: `CAUSE < FOCUS < EFFECT` 우선순위 스펙 문서화 (`productionQUtils.ts`, `why-output-contract.md`)
    - [x] W3-2) 샘플 검증: Q1/Q10/Q14 3문항으로 WHY 출력 비교(문서 vs UI) (`why-sample-validation-q1-q10-q14-2026-02-26.md`)
    - [x] W3-3) mismatch 처리: 태그/정렬 불일치 시 수정 주체(FE/BE) 결정 규칙 추가 (`why-output-contract.md` §6)
  - [ ] QP1. 질문 구현단계 정밀도 조정(후순위): reveal 축 정밀도/표현력 기준으로 `reveal_type` 기본값 정책 확정 (refs: `fivecircles/architecture/specs/reveals/reveals-classification.md`, `fivecircles/architecture/specs/reveals/reveals-reuse-cases.md`)
    - [ ] QP1-1) 옵션 비교: `NULL 유지` vs `HINT 자동 coalesce`를 질문 정밀도(오탐/미탐) 기준으로 평가
    - [ ] QP1-2) WHY 영향 검증: `HINT/CONFIRM`에 따른 근거 문장 강도/확신도 차등 규칙 정의
    - [ ] QP1-3) 확정 반영: DTO/쿼리/문서(reveals spec, ex23 연계) 동시 업데이트
- [x] **검색 정책(OTHER/UNKNOWN)**: user-facing predicateCode 필터에서 `OTHER|UNKNOWN`은 필터 미적용(비-1급 필터)으로 처리
- [ ] **품질향상 레이어(구조적 방어) 구현**: evidence-first 응답, group 매핑 단일 소스, suggestion 정규화/alias, 집계 엔드포인트 도입 (spec: `fivecircles/architecture/specs/predicate/data-quality-risks-and-structure.md`, `fivecircles/architecture/specs/predicate/related-characters-aggregate.md`)
- [x] **related-characters/aggregate 롤아웃(서버 스모크 기준)**: /qa 노출(프론트는 Antigravity), 서버 배포 후 curl 스모크로 성공 판정 (spec: `fivecircles/architecture/specs/predicate/rollout-plan-aggregate-qa.md`)
- [ ] **related-characters/aggregate 파인튜닝(데이터 기반)**: 실제 데이터에서 ADVERSARY/ALLY가 0점/빈 결과로 나오는 케이스를 수집하고, groupWeight/그룹 매핑을 조정 (예: 브레이킹 배드 행크 슈레이더 E5에서 ADVERSARY=0)
  - [x] v1) suggestion fallback 토큰 파싱 규칙 통일 적용(`TOKEN|label`, `TOKEN:label`) + SQL 집계 반영
  - [x] v1) 세분화 토큰 확장(ADVERSARY/ALLY/BATTLE fallback set + taxonomy 동기화)
  - [ ] v2) mode별 groupWeight/minScore 재튜닝(실데이터 샘플 30건 기준)
- [ ] **Predicate suggestion 운영(SoT=event)**: `event.predicate_suggestion` 도입(승인 시 snapshot 저장), 운영 편집/집계는 event 기준, wiki는 히스토리만 유지 (spec: `fivecircles/architecture/specs/predicate/suggestion-sot-event.md`)
  - [x] fallback group 매칭은 `event.predicate_suggestion`의 token(`extractToken`)만 사용 (`EventV3QueryServiceImpl`, `predicate_axis_taxonomy.py`)
- [x] **Predicate suggestion(코드/마이그레이션)**: event-service V8 컬럼 추가 + DTO/mapper + wiki 승인 publish payload 반영 (배포/DB 반영은 별도)
- [ ] **ex16 Production Q1~Q15 프리셋 실행 레이어**: Q1~Q15를 QuerySpec으로 고정하고 FE/QA에서 버튼 1개로 실행(api3/api4/api7/api8 조합). (status doc: `fivecircles/architecture/specs/predicate/ex16-production-q1-q15-implementation-status.md`)
- [ ] **ex16 Anti-Halu 재귀 구현 TODO (Q1~Q15)** (refs: `questions-anti-halus/03-implementation-plan.md`, `04-template-strict-must-matrix.md`, `05-v2-v25-adoption-review.md`, `06-answers-for-productionQs.md`, `07-맥락적답변형식.md`, `08-맥락적답변형식-메타모델.md`)
  - [ ] **Phase 0 / Spec Lock**
    - [x] 질문별 Strict/Approx 분리 원칙 고정 (`Strict -> Probe -> Approx`)
    - [x] Q1~Q15 Strict MUST 매트릭스 초안 고정 (`04-template-strict-must-matrix.md`)
    - [x] Q1~Q15 정답 에피소드 앵커 확정 (`06-answers-for-productionQs.md`)
    - [x] V2~V2.5 채택/보강 체크포인트 정리 (`05-v2-v25-adoption-review.md`)
    - [ ] Q1~Q15 템플릿별 `disclosurePolicy` 확정 (`ALLOW_SPOILER_BLOCKED` vs `HIDE_EXISTS_BEYOND_K`) — 04 매트릭스에 초안 있음, 런타임 매핑 확정 필요
    - [ ] `queryKind` + `strictFilters` JSON 스키마 최종 확정 (single probe endpoint 기준)
    - [ ] 05 체크리스트 5개 항목 최종 서명 (probe APPROVED only, StrictQuerySpec 단일화, Strict 0건→ANSWERED 금지, disclosurePolicy 마스킹, QA_MISS 백로그)
  - [ ] **Phase 1 / Backend Probe (event-service)**
    - [x] `POST /api/event/v2/probe` 엔드포인트 추가 (boolean only)
    - [x] Probe 요청 DTO 정의: `queryKind`, `safeUpToEpisode`, `strictFilters`
    - [x] Probe 응답 DTO 정의: `existsSafeApproved`, `existsAnyApproved`
    - [x] `StrictQuerySpec` 단일 빌더 도입 (answer/probe 필터 1:1 동기화 강제)
    - [x] `source_status='APPROVED'` 강제 + safe/any 조건 분기 구현
    - [x] 단위테스트: strict/probe 필터 불일치 방지, APPROVED gate 검증
  - [ ] **Phase 2 / FE Executor**
    - [x] Step1 Strict query 실행 (<=K)
    - [x] Step2 Strict 0건일 때만 probe 호출
    - [x] Step3 Approx 후보 조회(내부 참고용) + `ANSWERED` 금지 규칙 반영
    - [x] `LOCKED`를 FE view-state로 구현 (domain status와 분리)
    - [x] 템플릿(`ProductionQTemplate`)에 `queryKind/strictFilters/approxFilters/disclosurePolicy` 반영
    - [x] Q5~Q15 템플릿 확장 적용 (현재 Q1~Q4 범위에서만 executor 반영)
    - [ ] 04 매트릭스의 `evidence_event_id` TBD 칼럼을 DB 이벤트 ID로 채우기 (Q1~Q15) — 반영 완료: Q01/Q02/Q03/Q05/Q06/Q07/Q08/Q09/Q10/Q11/Q12/Q13/Q15 (남음: Q04,Q14)
    - [ ] 미채움 Q 원인별 보강(토큰/필터/데이터): `06-1-required-db-values.md` 상세 진단표 기준으로 Q04,Q14 우선 처리
    - [x] canonical 불일치 정리: Q08,Q09,Q15의 `canonical_episode` vs strict earliest 충돌 해소(질문 의미 강화 기준 적용)
  - [ ] **Phase 3 / Aggregate Safety**
    - [x] ALLY/ADVERSARY 라벨 확정 게이트 추가 (evidence predicate >= 1)
    - [x] Evidence 미충족 시 COEVENT/UNKNOWN 처리 (점수만으로 라벨 금지) — ADVERSARY/ALLY 모드에서는 무근거 행 제외, 중립은 COEVENTS 모드로 조회
    - [ ] group 매핑/토큰 동기화(동치 fallback only) 규칙 적용
  - [ ] **Phase 4 / Ops Loop**
    - [ ] `NOT_ENOUGH_DATA` 발생 시 `QA_MISS` 로그 적재 (`mustFilters` 스냅샷 포함)
    - [ ] `qAnyOf` 보강 백로그 자동화(동치 토큰 중심)
    - [ ] 운영 가이드 문서화(질문 추가 = Strict MUST 추가)
  - [ ] **Phase 5 / Validation**
    - [ ] 06 정답 기준 검증: Q1~Q15 canonical_episode과 Strict query 결과 1:1 매칭 확인
    - [ ] 시나리오 검증: `ANSWERED / SPOILER_BLOCKED / NOT_ENOUGH_DATA` 3상태 분기
    - [ ] 민감 질문에서 사용자-facing `LOCKED` 마스킹 검증 (Q1,Q2,Q4,Q5,Q7,Q8,Q10~Q15 = `HIDE_EXISTS_BEYOND_K`)
    - [ ] 회귀 검증: Q1~Q4 기존 템플릿 오답/누락 케이스 재현 후 통과 확인
    - [x] FE 로컬 Playwright: `/qa` 템플릿 실행(Q6 등) 후 Context Timeline `Depth=3`(3-hop) 로딩 결과 확인 (spec: `front/productionq_depth3.spec.js`)
    - [ ] 성능 검증: 성공 경로 1콜 유지, 실패 경로 2콜(Strict 0건 시) 확인
    - [ ] 05 최종 체크리스트 6개 항목 통과 확인
  - [ ] **Phase 6 / Contextual Answer Format (Level 1-3 진화형 응답)** (refs: `07-맥락적답변형식.md`, `08-맥락적답변형식-메타모델.md`)
    - [ ] **메타모델 설계 확정**
      - [ ] `structural_weight` (1=점/Anchor, 2=선/Structural Shift, 3=면/Systemic State) 스키마 확정
      - [ ] `domain_type` enum 확정 (THREAT, POWER, MONEY, RELATION, IDENTITY, INVESTIGATION)
      - [ ] predicate_group → 현재 DB `PredicateCode` 매핑 리팩토링 (08 §3 매핑표 기준)
      - [ ] 08의 수도태그(`[수도태그]`) → 실제 PredicateCode 전환 계획 확정 (신규 코드 추가 vs 기존 매핑)
    - [ ] **백엔드 레이어**
      - [ ] Q별 Level 1-3 응답을 반환하는 엔드포인트 설계 (단일 Q → 3 Level 응답)
      - [ ] `anchor_event_ids` 연결: Level별 evidence 이벤트 ID 매핑
      - [ ] hop=1 관계(PRECEDES/REVEALS) 기반 Level 2-3 후보 자동 탐색 (V2.5 범위)
    - [ ] **프론트엔드 레이어**
      - [ ] Level 1-3 단계별 펼침(accordion/progressive disclosure) UI 설계
      - [ ] spoiler gating: 사용자 safeUpToEpisode 이내 Level만 노출
    - [ ] **검증**
      - [ ] 06 정답 + 07 Level 1-3 데이터로 Q1~Q15 전체 응답 샘플 검증
      - [ ] JSON 응답 스키마(`qna.levels.v1`) 확정 및 FE 파싱 테스트
  - [ ] **Phase 6-A / Q1 익스펜션 재귀 실행 (파일럿, 2026-02-25)** (refs: `questions-anti-halus/09-expension-questions.md`, `questions-anti-halus/10-q1-expansion-recursive-run.md`)
    - [x] Cycle 1-1: Q1 후속 6문항에 대한 웹 근거/앵커 후보/도미노 후보를 문서화
    - [x] Cycle 1-2: 현재 DB `event_relation(PRECEDES)` 갭 점검 + 기존 이벤트 기준 relation 시드 SQL 작성
    - [x] Cycle 1-3: Q1 익스펜션 relation 시드 SQL 실행 및 반영 검증
    - [x] Cycle 1-4: S3 이후 strategic-kill 구간 이벤트 신규 시드(없으면 생성) + PRECEDES 연결
    - [x] Cycle 1-5: Story Reminder 템플릿/SPARQL 질의로 Q1-1~Q1-6 실행 경로 고정
    - [x] Cycle 1-6: K gate(절대회차) 기준 `ANSWERED/SPOILER_BLOCKED/NOT_ENOUGH_DATA` 회귀 검증
    - [ ] Follow-up: `/api/event/v2/probe`에서 `strictFilters.qAnyOf` 바인딩/검증 경로 점검 (keyword probe 400/무시 리스크)
  - [ ] **Ops / Local Runtime**
    - [ ] 로컬 Docker 전체 기동(`docker compose up -d --build`) 절차/체크리스트 정리
    - [ ] 로컬 MySQL 스키마 생성(init) 절차 정리 및 재현 스크립트 추가
    - [ ] Production 질문 화면에서 “연관 이벤트(맥락)” 표시가 PRECEDES 기준으로 맞게 나오는지 점검/보정 (depth 1/2)
- [x] **Production Q 템플릿(MVP)**: 브베(dramaId=10) 기준 Q1/Q2/Q3 템플릿 + 실행기(FE) 구현. `api3.q`로 텍스트 object 근사. (spec: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`)
- [ ] **Intelligence QuerySpec(옵션)**: intelligence-service가 “존재하는 API로만 실행 가능한 QuerySpec” 생성 엔드포인트(`/queryspec`) 제공 + executor 가드레일 추가. (spec: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`)
- [x] **Ontology V2.5 (Q20)**:
    - [x] Update V2.5 Plan (v2.5-def-plan.md)
    - [x] Correct EventServiceImpl role string (`PARTICIPANT` -> `INVOLVED`)
    - [x] Create V6 Flyway Migration for `event_character.role`
    - [x] Implement Q20 Narrative Distribution view on QA page
    - [x] Implement Extended QA Widgets (Q3, Q5, Q7, Q9, Q11)
- [ ] **V3-Advanced (RDF/OWL) Recursive TODO (2026-02-23)**
    - [x] **Phase 0 / Spec Lock**
      - [x] `RDF/OWL = V3-Advanced` 규정 문서 생성 (`fivecircles/architecture/specs/event-v3-advanced-rdf-owl.md`)
      - [x] `event-v3-plan.md`에 V3 코어/Advanced 분리 및 비차단 원칙 반영
      - [x] predicate README/notes 참조 체계 정리 (규범 SoT vs 구현 노트)
    - [x] **Phase 1 / Artifact Scaffold**
      - [x] `.../rdf/artifacts/v3-advanced/latest/` 경로 생성
      - [x] 템플릿 4종 생성: `ontology.ttl`, `shapes.ttl`, `kg.ttl`, `report.json`
    - [ ] **Phase 2 / Exporter Wire-up (RDB -> RDF)**
      - [ ] 로컬 Docker MySQL 기준 export 스크립트 초안 작성
      - [ ] `event`, `event_character(role)`, `event_relation(PRECEDES)` 최소 매핑 구현
      - [ ] export 결과를 `latest/kg.ttl`로 출력하는 실행 명령 고정
    - [ ] **Phase 3 / SHACL Validation Wire-up**
      - [ ] validator 실행 스크립트 추가 (`kg.ttl` -> `report.json`)
      - [ ] fail/warn 기준 및 운영 확인 포인트 문서화
      - [ ] 파이프라인 재현성 점검 (local/server-like)
    - [ ] **Phase 4 / V3 Release Gate Proof**
      - [ ] Q1~Q15/Q20 회귀 테스트 실행 및 결과 기록
      - [ ] K+APPROVED + PRECEDES safe traversal 회귀 확인
      - [ ] RDF 레인 실패 시 v1/v2 무영향(비차단) 검증 로그 추가
    - [ ] **Phase 5 / Optional Promotion Decision**
      - [ ] Fuseki 도입 의사결정(추후): Query-only 운영에서 taxonomy/패턴 확장으로 `kg.ttl` 파일 기반 조회 한계가 확인될 때 SPARQL endpoint(Fuseki) 전환 여부를 결정한다.
      - [ ] Export-only(+10) 유지 여부 결정
      - [ ] Query-only(+30) 진입 조건 충족 여부 검토
      - [ ] Dual-store(+80)는 운영 런북/복구 전략 확정 전 보류
- [ ] **Verifying**: API JSON response spoiler hiding
- [x] Event-service 전체 주석 추가

### 6.1 Current Sprint (2026-01-26) - ✅ Complete
**Priority Order**:
1. [x] **Rebase to develop**: Rebase `feature/experimental-frontend` onto `origin/develop` (42 commits rebased)
2. [x] **Skills tracking**: Track `fivecircles/agent/skills/` in Git (Decision made)
3. [x] **QA Context UX (Q7/Q9)**:
   - [x] Add `eventId?: number` to `EventQAButton` and pass into `EventQADrawer` context (Already implemented)
   - [x] Timeline: pass eventId from event cards into `EventQAButton` for auto Q7/Q9
   - [x] Drawer: add event selector (ID input/search) when eventId is missing
   - [x] Filter Q7/Q9 visibility: show only when eventId exists (context or selected)
   - [x] Wire selected eventId into Q7/Q9 widgets (Already implemented)
4. [x] **MVP Experiment**: Playwright checks for MVP UI (1 passed in 6.5s)

### 7. Deploy & Ops (Post-Sprint)
> **Reference**: See `fivecircles/architecture/specs/test-server-policy-4C.md` for remote deploy & test protocols.
- [x] Deploy on bit-ts: `cd ~/nospoiler/infra && docker compose up -d --build` (최근: 2026-02-09)
- [x] Deploy scripts generalized for target branch argument (refs: fivecircles/test/deploy-server.sh, fivecircles/test/deploy-server-4c.sh)
- [ ] If deploy fails with `:common` missing, fix event-service Docker build and re-run (상시체크)
- [x] bit-ts `user-service` Flyway checksum mismatch 복구 후 auth login 스모크 재검증 (refs: fivecircles/test/errorlogs/backend/2026-02-11-user-service-flyway-checksum-login-401.md)
- [x] bit-ts 배포 후 QA E2E 확인 (FE → Gateway → QA/Event/Policy)
- [x] C-only compose run on bit-ts (mysql/event/policy/qa, `DB_PORT=3307`)
- [x] Skills tracking decision (`fivecircles/agent/skills/` will be tracked)
- [ ] 협업으로 온톨로지 로직 검증 (wiki service)
- [x] 프론트 작업 진행 (Dashboard/Timeline API Integration)
- [x] 프론트 MCP 설치 후 테스트
- [x] 남은 로컬 브랜치 정리 (`feature/api-enhancement-full`, `feature/filter-service-working`)
- [x] MVP Experiment: Event V2 code path check (api1-10)
- [x] MVP Experiment: Event V2 runtime smoke (api1-10)
- [x] MVP Experiment: Event V2 readiness smoke (api1-10)
- [x] MVP Experiment: FE integration for Q1-Q15 (dashboard/timeline)
- [x] DramaSelectionPage Real API Integration & DB Seed Data injection
- [x] Fix QA widget endpoints (Q13 policy path, Q2 keyword filter, event_character role insert)
- [x] QA: docker compose에 EVENT_SERVICE_URL/POLICY_SERVICE_URL 주입 (QA→Event/Policy 경로 정렬)
- [x] QA: QaPage 캐릭터 썸네일 필드 정정 (imageUrl -> profileImageUrl)
- [x] QA: QaService 스포일러 판정 기준을 episodeStart -> episodeEnd로 수정
- [x] QA: Health check는 무인증 호출로 전환해 오프라인 오탐 방지
- [x] QA: Q1/Q3/Q5/Q20용 데이터 보강 (event_character, event_relation, predicate_code)
- [ ] QA: Q7/Q9/Q11용 데이터 보강 (event_character, event_relation, predicate_code)
- [ ] QA: Q7/Q9 정확도 개선 (PRECEDES 탐색/정렬/게이트 재검토)
- [x] Admin/UI: PRECEDES 관계 큐레이션 화면 (suggestions 승인, searchable drama selection, bulk approval/delete, pagination, 담당: Antigravity)
- [x] Hotfix(2026-02-11): 프론트 `index.html` 구문 오류 및 gateway `drama/character` 401 차단 해소

### 8. Frontend Widget Placement & Test Plan (Pending)
1) [x] Confirm widget placement per frontend spec (dashboard/timeline/qa) and list target entry points
2) [x] Validate each widget renders with mock/empty states (no crash)
3) [x] Run Playwright flow for key pages and check console errors
4) [x] Capture gaps (missing endpoints/data) and update `frontend.md` if mapping changes
5) [x] Add dashboard QA entry points (global + character modal)

---
