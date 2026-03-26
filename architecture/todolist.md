# NoSpoiler Project Total Todo List

> **Principle**: This file (`fivecircles/architecture/todolist.md`) is the **top-level source of truth** for work items.
> - Each member updates their own section.
> - `fivecircles/agent/queue.json` is kept as a **reference/backlog**, not the primary TODO list.
> **Last Updated**: 2026-02-26 (by Codex)

---

### 11. Portable Operations System & Debugging Checklist (New)

- [ ] **일반 디버깅 체크리스트 정리**: 새 프로젝트에서도 그대로 재사용할 수 있는 공통 디버깅 체크리스트를 정리한다.
  - [ ] 재현 → 원인 추적 → 수정 → 검증 → 재발 방지 흐름을 한 번에 따라갈 수 있는 기본 절차 정의
  - [ ] 프로젝트 진행 중 반복적으로 발생했던 일반 버그 유형 정리
  - [ ] 새 프로젝트 온보딩 시 바로 참고할 수 있는 체크 순서와 우선순위 정리
  - [ ] 운영 문서 어디에 둘지, 어떤 문서에서 참조할지 연결 구조 확정

- [ ] **언제든 이식할 수 있는 운영시스템 설계**: 특정 프로젝트에 종속되지 않고 언제든 다른 프로젝트로 옮겨갈 수 있는 FiveCircles 운영 원칙을 정리한다.
  - [ ] 새 프로젝트로 이식할 때 유지해야 할 공통 운영 자산 정의
  - [ ] 제거해야 할 프로젝트 고유 흔적과 예외 규칙 정의
  - [ ] 새 프로젝트 이름/문맥으로 교체해야 할 항목 분류
  - [ ] 이식 전후 점검 절차와 최소 정리 순서 초안 작성

- [ ] **프로젝트 정보 제어 정책 정리**: 새 프로젝트 이식 시 프로젝트 정보를 가져오거나, 버리거나, 수정하거나, 차단하는 기능 요구사항을 정리한다.
  - [ ] 가져오기: 재사용 가능한 운영 규칙, 문서 구조, 작업 절차, 테스트 원칙
  - [ ] 버리기: 이전 프로젝트 고유 이름, 도메인 맥락, 완료 이력, 불필요한 운영 흔적
  - [ ] 수정: 새 프로젝트에 맞춰 치환되어야 하는 경로, 설명, 예시, 역할 배치
  - [ ] 차단: 새 프로젝트에 오염을 일으킬 수 있는 이전 프로젝트 특화 문서, 설정, 예외 규칙
  - [ ] 위 4분류를 실제 문서/설정 파일에 적용할 수 있는 판단 기준표 초안 작성

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
  - [x] 지속참고 기준서 추가: 사실 이벤트/해석 라벨 분리 + `HINT/CONFIRM` 판정/근거 앵커 규칙을 `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`로 고정
- [ ] **Q1~Q15 정합성(별도)**: UI/스펙의 predicateCode(`BATTLE`, `AFFILIATION_CHANGE`, `DEATH`, `EXIT` 등)와 `common/PredicateCode`의 폐쇄 집합을 정렬 (ex14 범위 밖이므로 별도 작업으로 분리)
  - [ ] 게이트: Q1~Q15 템플릿에서 `strict_must.predicateCodeAnyOf` 및 `strict_must.excludePredicateCodeAnyOf`만 runtime `PredicateCode` 폐쇄집합 검사 대상으로 고정하고, group/label/qAnyOf는 검사 범위에서 제외 (검사 스크립트 구현 완료, CI hook 연결 보류)
    - [x] 로컬 게이트 스크립트: `fivecircles/test/validate-productionq-predicatecode-gate.py`
    - [ ] CI/파이프라인 연결: gate fail 시 배포/머지 차단
- [ ] **ex20~22.1 정합화 실행 트랙 (2026-02-26, Q20 우선/DB 최소변경)** (refs: `fivecircles/architecture/proposals/공유-온톨로지레이어구축/ex23-RDF-inheritance.md`, `ex23-RDF-inheritance-appendix.md`, `ex20-axis.md`, `ex21-SPO-N-Y.md`, `ex22-axis-N-Y-scetch.md`, `ex22.1-ops.md`, `fivecircles/architecture/specs/predicate/groups.md`)
  - [x] 1) Q20 기준 축/SPO/Predicate 운영원칙 문서 고정 (Quick20 커버리지 기준, role=`INVOLVED/SUBJECT/OBJECT`, predicate는 현행 `PredicateCode`+`PredicateGroup` 우선)
  - [ ] 2) role 입력 계약+파이프라인 추가 (**보류**: Intelligence 개발자(B)와 `involvedCharacters[{characterId,role}]` 계약 확정 후 재개)
    - [ ] 2-1) B 협의 체크: 응답 필드 추가 여부, `involvedCharacterIds` 호환 유지, role 허용값/기본값, 배포 순서(`intelligence -> wiki -> event`)
  - [ ] 3) relation type 확장 RFC는 보류: 현행 PRECEDES+REVEALS/Group 조합으로 커버리지 검증 후 필요 시 재개
- [ ] **axis/SPO/AND/WHY 구현 체크리스트 (2026-02-26, ex20~23 리뷰 반영)** (refs: `ex23-RDF-inheritance.md`, `ex23-RDF-inheritance-appendix.md`, `ex20-axis.md`, `ex21-SPO-N-Y.md`, `ex22-axis-N-Y-scetch.md`, `ex22.1-ops.md`, `ex22.2-expansion-categorized-impl-plan.md`, `ex22.3-expansion-expansion-qs-imple2.md`, `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`, `fivecircles/architecture/specs/questions-anti-halus/04-template-strict-must-matrix.md`)
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
  - [x] A-2. 후속 6문항 Answer-set(확장 검증) (**A-1 완료 후**) (refs: `ex22.3-expansion-expansion-qs-imple2.md`)
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
  - [ ] **Phase 6-A / Q1 익스펜션 재귀 실행 (파일럿, 2026-02-25)** (refs: `expansion100/09-expansion-questions.md`, `questions-anti-halus/10-q1-expansion-recursive-run.md`)
    - [x] Cycle 1-1: Q1 후속 6문항에 대한 웹 근거/앵커 후보/도미노 후보를 문서화
    - [x] Cycle 1-2: 현재 DB `event_relation(PRECEDES)` 갭 점검 + 기존 이벤트 기준 relation 시드 SQL 작성
    - [x] Cycle 1-3: Q1 익스펜션 relation 시드 SQL 실행 및 반영 검증
    - [x] Cycle 1-4: S3 이후 strategic-kill 구간 이벤트 신규 시드(없으면 생성) + PRECEDES 연결
    - [x] Cycle 1-5: Story Reminder 템플릿/SPARQL 질의로 Q1-1~Q1-6 실행 경로 고정
    - [x] Cycle 1-6: K gate(절대회차) 기준 `ANSWERED/SPOILER_BLOCKED/NOT_ENOUGH_DATA` 회귀 검증
    - [ ] Follow-up: `/api/event/v2/probe`에서 `strictFilters.qAnyOf` 바인딩/검증 경로 점검 (keyword probe 400/무시 리스크)
  - [ ] **Phase 6-B / Expansion100 3축 분류 + 4축 리마인더 UI 전환 (2026-02-26)** (refs: `expansion100/expansion-6of100-q1.md`, `expansion100/expansion100-3axis-4axis-reminder-plan-2026-02-26.md`, `expansion100/question-map.q01-expansion.phase1.json`, `rdf/policy/inheritance-closure-policy.md`, `rdf/policy/inheritance-closure-taxonomy.phase1.json`)
    - [ ] B1) Q1 확장 6개 strict 복구: 문서 서술형 토큰은 `approx_only`, DB hit 토큰은 `strict_must`로 분리
      - [ ] B1-1) `Q01_EXP_01/02/04` strict 토큰을 DB 검증 통과 세트로 복원
      - [ ] B1-2) `Q01_EXP_03/05/06`은 현 앵커 유지 + 동치 토큰만 보강
      - [ ] B1-3) `validate-q1-expansion-gate.py` 케이스를 템플릿 값과 동기화
    - [ ] B2) Expansion100 질문 매핑 SoT 작성 (`question_id -> axis -> required_set`)
      - [ ] B2-1) A축: `event_scope_set` 정의
      - [x] B2-2) B축: `attribute_set` 키를 closure taxonomy(Phase1 JSON) 기준으로 고정
      - [x] B2-2a) `A_* -> event_reveal.target_id` 바인딩 테이블 채움(미입력 시 해당 질문은 `NOT_ENOUGH_DATA`) (`seed_expansion100_q1_attribute_reveals.sql` + `validate-expansion100-intelligence-columns.py`)
      - [x] B2-3) C축: `predicate_set`을 closure taxonomy leaf -> `PredicateCode` 매핑 기준으로 고정
      - [x] B2-3a) `P_*` 직접 조회 금지, `runtime_bindings -> PredicateCode` 변환 규칙 고정
      - [x] B2-4) Q1 확장 canonical SoT 파일 고정: `specs/expansion100/question-map.q01-expansion.phase1.json`
      - [x] B2-5) closure taxonomy canonical SoT 파일 고정: `specs/rdf/policy/inheritance-closure-taxonomy.phase1.json`
      - [ ] B2-6) 후순위 draft map 추가: `Q05/Q08/Q10/Q12` (`specs/expansion100/question-map.q05|q08|q10|q12-expansion.phase1.json`)
    - [ ] B2.5) 상속(승계) 확장 유틸 추가 (**PRECEDES 대체 금지**, policy: `rdf/policy/inheritance-closure-policy.md`)
      - [x] B2.5-1) Phase1 범위 고정(DB 무변경): 기존 `event.predicate_code` + `event_reveal`만 사용
      - [x] B2.5-2) `expand(set)` 구현: parent 입력 시 descendant 포함 집합 반환
      - [x] B2.5-3) B축 조회는 `expanded_attribute_set`만 사용
      - [x] B2.5-4) C축 조회는 `expanded_predicate_set`만 사용
      - [x] B2.5-5) BC축 결합 규칙 고정: 기본 `OR(B ∪ C)`, 질문별 `combine_mode=AND` 허용
      - [x] B2.5-5a) `Q01_EXP_06`은 `BC + AND`로 파일 기준 고정
      - [x] B2.5-6) 안전 게이트 유지 확인: `K + APPROVED` 이후 후보만 노출
      - [ ] B2.5-7) Phase2 스키마 확장(`predicate`, `event_predicate`)은 보류 항목으로 분리
    - [ ] B3) 조회 파이프라인 확장(기존 strict-first 유지)
      - [x] B3-1) `getEventsByRevealAttribute(K, attribute_set, scope)` 추가 (executor axis-lane inline)
      - [x] B3-2) `getEventsByPredicate(K, predicate_set, scope)` 추가 (executor axis-lane inline)
      - [x] B3-3) 축별 miss 정책 고정: A/B/C hit 0 -> `NOT_ENOUGH_DATA`
    - [ ] B4) 리마인더 UI를 lane 구조로 전환
      - [x] B4-1) 결과 모델: `selected_event`, `axis_lane(A/B/C)`, `precedes_lane` 분리
      - [x] B4-2) ResultPanel에 REVEALS/ATTRIBUTE 섹션 추가
      - [ ] B4-3) PRECEDES는 연결선/맥락 보조로만 표시(선정 기준 제외)
    - [ ] B5) 회귀/드리프트 게이트
      - [ ] B5-1) ex22.2/ex22.3 시험 페이지(`/#/qa-story-reminder-test`) 축별 샘플 검증
      - [ ] B5-2) expansion strict hit 회귀 스냅샷(ANSWERED/BLOCKED/NO_DATA) 저장
      - [ ] B5-3) 매핑 SoT와 템플릿 축 불일치 시 fail 게이트 추가
  - [ ] **Ops / Local Runtime**
    - [ ] 로컬 Docker 전체 기동(`docker compose up -d --build`) 절차/체크리스트 정리
    - [ ] 로컬 MySQL 스키마 생성(init) 절차 정리 및 재현 스크립트 추가
    - [ ] Production 질문 화면에서 “연관 이벤트(맥락)” 표시가 PRECEDES 기준으로 맞게 나오는지 점검/보정 (depth 1/2)
- [x] **Production Q 템플릿(MVP)**: 브베(dramaId=10) 기준 Q1/Q2/Q3 템플릿 + 실행기(FE) 구현. `api3.q`로 텍스트 object 근사. (spec: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`)
- [ ] **Intelligence QuerySpec(옵션)**: intelligence-service가 “존재하는 API로만 실행 가능한 QuerySpec” 생성 엔드포인트(`/queryspec`) 제공 + executor 가드레일 추가. (spec: `fivecircles/architecture/specs/predicate/production-q-templates-and-intelligence-queryspec.md`)
- [x] **Taxonomy Dashboard (event API + admin page)**: taxonomy SoT(`predicate_axis_taxonomy.json`)를 기반으로 admin 검수 화면과 event taxonomy API를 구현한다. (spec: `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard.md`, plan: `fivecircles/architecture/specs/taxonomy/taxonomy-dashboard-implementation-plan.md`)
    - [x] TD0. 범위/계약 고정
      - [x] TD0-1. 페이지 위치는 admin 프론트로 고정
      - [x] TD0-2. API 위치는 event-service로 고정
      - [x] TD0-3. API 경로는 `/api/event/taxonomy/tree`, `/api/event/taxonomy/preview`, `/api/event/taxonomy/drift`로 고정
      - [x] TD0-4. Phase 1 SoT는 `scripts/ops/rdf/taxonomy/predicate_axis_taxonomy.json`으로 고정
      - [x] TD0-5. Phase 1은 compile/generated 산출물 없이 runtime load 방식으로 고정
    - [x] TD1. Event-service taxonomy read lane
      - [x] TD1-1. taxonomy JSON 로더 진입 경로 확정(classpath/file path)
      - [x] TD1-2. axis resolver 구현(`predicateCodes`, `predicateSuggestions`, `impliesAxes` 재귀 전개)
      - [x] TD1-3. dedupe/cycle/empty-axis 진단 유틸 구현
      - [x] TD1-4. 실패 범위 고정: dashboard API만 실패하고 user-facing event API는 무영향
    - [x] TD2. Taxonomy tree API
      - [x] TD2-1. request/response DTO 정의
      - [x] TD2-2. `GET /api/event/taxonomy/tree` controller/service 구현
      - [x] TD2-3. resolved code/suggestion/count 필드 계약 고정
      - [x] TD2-4. 로컬 스모크 응답 캡처
    - [x] TD3. Taxonomy preview API
      - [x] TD3-1. `POST /api/event/taxonomy/preview` request/response DTO 정의
      - [x] TD3-2. preview SQL mapper 추가(`predicate_code IN (...)`, `APPROVED`, optional drama/character/episode)
      - [x] TD3-3. 1차 구현은 runtime `predicate_code` preview만 지원
      - [x] TD3-4. 잘못된 axis/빈 결과/limit 처리 규칙 고정
      - [x] TD3-5. 로컬 스모크 응답 캡처
    - [x] TD4. Taxonomy drift API
      - [x] TD4-1. taxonomy vs enum missing/unclassified 진단 구현
      - [x] TD4-2. duplicate resolved code / cycle / empty axis 진단 구현
      - [x] TD4-3. `GET /api/event/taxonomy/drift` controller/service 구현
      - [x] TD4-4. 로컬 스모크 응답 캡처
    - [x] TD5. Admin 프론트 페이지
      - [x] TD5-1. taxonomy dashboard route 추가
      - [x] TD5-2. axis list/tree panel 구현
      - [x] TD5-3. preview filter form 구현
      - [x] TD5-4. preview table 구현
      - [x] TD5-5. drift tab/panel 구현
    - [x] TD6. 검증/운영화
      - [x] TD6-1. tree/preview/drift API 수동 스모크
      - [x] TD6-2. admin 렌더/오류/빈 상태 확인 (build 기준)
      - [x] TD6-3. taxonomy 파일 누락/파손 시 장애 범위 확인 (taxonomy API만 ERROR, 일반 event API는 SUCCESS)
      - [x] TD6-4. 추후 compile 도입 조건 문서화 (`taxonomy-dashboard-implementation-plan.md` §9)
    - [x] TD7. Admin UX polish
      - [x] TD7-1. 실제 운영 접속 기준으로 레이아웃/필터/가독성 점검
        - [x] TD7-1a. preview 모드/필터 상태를 한눈에 보이는 상단 요약 바 추가
        - [x] TD7-1b. 빈 상태/로딩 상태 문구를 preview 모드별로 분리
      - [x] TD7-2. axis 검색/선택/상세 정보 패널의 사용성 보정
        - [x] TD7-2a. axis 상세 카드에 code/suggestion/implies 카운트 요약 추가
        - [x] TD7-2b. preview/fallback 전환 시 선택 axis 맥락이 유지되도록 탭 구조 정리
      - [x] TD7-3. preview 결과 테이블의 밀도/정렬/복사/내보내기 UX 검토
        - [x] TD7-3a. preview 결과 복사(copy ids) 액션 추가
        - [x] TD7-3b. preview 결과 CSV export 액션 추가
    - [x] TD8. Suggestion fallback preview 정책/구현
      - [x] TD8-1. preview에 `predicateSuggestions` fallback을 노출할지 정책 결정 (노출)
      - [x] TD8-2. fallback ON/OFF 또는 별도 탭 방식 중 UI 계약 결정 (별도 탭)
      - [x] TD8-2a. fallback 결과에는 `FALLBACK MATCH` 라벨을 붙이는 정책 고정
      - [x] TD8-3. fallback preview SQL/응답/설명문구 구현 여부 결정
        - [x] TD8-3a. event-service preview request에 `previewMode` 계약 추가
        - [x] TD8-3b. fallback suggestion token SQL/count 쿼리 추가
        - [x] TD8-3c. admin preview에 runtime/fallback 분리 탭 추가
        - [x] TD8-3d. fallback 행에 `FALLBACK MATCH` 라벨/매치 토큰 표시
    - [ ] TD9. Taxonomy evolution follow-up
      - [ ] TD9-1. taxonomy JSON 복잡도 증가 시 compile 산출물 도입 조건 정리
      - [ ] TD9-2. tree UI를 graph/tree 시각화로 승격할지 여부 결정
      - [ ] TD9-2a. production build 전 `front/index.html`의 `cdn.tailwindcss.com` 제거 및 Tailwind 정식 빌드(PostCSS/CLI)로 전환
      - [x] TD9-3. query axis(`REVEAL/PREDICATE/COMBINED/PRECEDES`)와 predicate taxonomy category의 source 경계 정리
        - [x] 기준 문서 생성: `fivecircles/architecture/specs/taxonomy/query-axis-reveal-combined-design.md`
      - [x] TD9-4. `REVEAL` axis tree/preview source를 codebook + `event_reveal` 기반으로 구현
      - [x] TD9-5. `COMBINED` axis intersection preview를 `event_reveal` + `event.predicate_code` 조합으로 구현
      - [ ] TD9-6. 레거시 taxonomy 응답 필드 `axisCode`를 `categoryCode`로 전환
      - [x] TD9-7. PREDICATE axis tree SoT를 `predicate_inheritance.json` 기준으로 cutover
        - [x] TD9-7a. tree/visualization SoT 초안 파일 생성: `scripts/ops/rdf/taxonomy/predicate_inheritance.json`
        - [x] TD9-7b. taxonomy 스펙/플랜/제안 문서에 group SoT vs tree SoT 역할 분리 반영
        - [x] TD9-7c. `/api/event/taxonomy/tree?queryAxis=PREDICATE`를 tree SoT 응답 shape로 전환
        - [ ] DTO/API/프론트 타입에서 `axisCode -> categoryCode` rename 계획 수립
        - [ ] 하위호환 기간 동안 alias 응답 또는 dual field 유지 여부 결정
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
      - [x] Fuseki 런타임 semantic lane Phase 3 기동 (docker-compose + loader + healthcheck)
      - [ ] Fuseki refresh 경로에 기존 exporter(`scripts/ops/rdf/export_v3_advanced.sh`) 재사용 연결
      - [ ] loader가 semantic schema TTL + exported `latest/kg.ttl`를 함께 적재하도록 연결
      - [ ] event-service semantic endpoint에 실제 `S/P/O expand` 추가
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

### 9. Blueprint (Codebook-First) Recursive Execution Plan (2026-02-27)
> refs: `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`, `fivecircles/architecture/specs/rdf/inheritance-blueprint-examples.md`, `fivecircles/architecture/specs/reveals/reveal-evidence-label-policy.md`

- [x] BP0. Scope/Contract Lock (선행 게이트)
  - [x] BP0-1. 운영 계약 고정: `target_type=CHARACTER -> target_id=character_id`, `target_type=ATTRIBUTE -> target_id=aboutCharacterId` 유지
  - [x] BP0-2. `reveal_type` 용도 고정: `HINT|CONFIRM`은 WHY 근거 강도 표시에만 사용(정답 승격 금지)
  - [x] BP0-3. 레인 경계 고정: RDF lane SoT(`predicate_axis_taxonomy.json`) / Executor lane SoT(`StrictQuerySpec`)
  - [x] BP0-4. 비범위 잠금: `attribute/closure` 테이블 도입 및 strict 계약 키 추가는 Phase3 전까지 금지
  - [x] BP0-5. 완료조건: blueprint/ex23/reveals 문서 3종 문구 충돌 0건

- [x] BP1. Schema Minimal Extension (`event_reveal.target_key`) (BP0 이후)
  - [x] BP1-1. migration 추가: `event_reveal.target_key VARCHAR(64) NULL`
  - [x] BP1-2. 인덱스 추가: `(target_type, target_key)`, `(target_type, target_id)`
  - [x] BP1-3. 롤백/재실행 가능한 DDL 스크립트 작성(로컬/도커 검증)
  - [x] BP1-4. 완료조건: 기존 API/쿼리 회귀 없음(기존 필드 read/write 100% 호환)

- [x] BP2. Codebook/Allow-list 정식화 (BP1 이후)
  - [x] BP2-1. reveal target key 코드북 문서 생성 (`fivecircles/architecture/specs/reveals/reveal-target-key-codebook.md`, `A_*` 네이밍/정의/예시/소유자)
  - [x] BP2-2. 실행 맵 동기화: `inheritancePhase1.ts` attribute 상속 엣지/확장셋을 코드북과 1:1 정렬
  - [x] BP2-3. allow-list 검증 함수 추가(안전 모드): `target_type=ATTRIBUTE`일 때 `target_key`가 입력되면 코드북 외 값 reject(미입력 허용, 강제는 BP3-4에서 결정)
  - [x] BP2-4. 로컬 게이트 스크립트 추가: 코드북/템플릿/seed 데이터 `A_*` 키 정합성 검사
  - [x] BP2-5. 완료조건: 키 오타/미등록 입력이 저장 단계에서 차단됨

- [ ] BP3. Write Path 연결 (BP2 이후)
  - [x] BP3-0. Phase1 운영 원칙 고정: `target_key` 실제 데이터 적용/보정은 `scripts/ops` seed/backfill 스크립트 우선(팀간 write-path 변경 최소화)
  - [x] BP3-1. event-service 요청 DTO/검증에 `targetKey` 반영 (`REVEALS + ATTRIBUTE` 검증)
  - [ ] BP3-2. wiki 승인 publish payload에 `target_key` 전달 경로 반영 (**보류: 위키 팀원 영역, 합의 후 재개**)
  - [ ] BP3-3. intelligence 경로는 협의 블로커로 분리(B팀 합의 전 코드 변경 금지) (**보류: 인텔리전스 팀원 영역, 합의 후 재개**)
    - [ ] BP3-3-a. 협의 문서화: 입력 계약/기본값/배포 순서 확정 (**보류**)
    - [ ] BP3-3-b. 합의 후 반영: 프롬프트/파서/DTO 순차 적용 (**보류**)
  - [x] BP3-4. 레거시 호환 정책 확정: `target_key` 누락 row 처리(경고/저장거부) 결정 (`validate-reveal-target-key-runtime-phase1.py` PASS: drama10 fail / legacy warn)
  - [ ] BP3-5. 완료조건: event/wiki 경로에서 `target_key`가 E2E 저장됨 (**보류: wiki 경로 포함 조건은 협의 이후 판정**)

- [x] BP4. Read Path / Q01_EXP_01 동작화 (BP3 이후)
  - [x] BP4-1. B-lane 필터 전환: `target_id 단독` -> `target_key + (옵션) aboutCharacterId` (우선순위: `target_key`, 호환 fallback: `target_id`)
  - [x] BP4-2. WHY `reveal_hint`에 `target_key` 노출
  - [x] BP4-3. strict miss 가드 회귀: reveal/probe hit로 `ANSWERED` 승격 금지 유지 (`validate-productionq-probe-guard.py` PASS)
  - [x] BP4-4. 완료조건: Q01_EXP_01에서 B-lane 후보가 코드북 기반으로 재현됨 (`validate-reveal-target-key-runtime-phase1.py` PASS)

- [x] BP5. WHY Chain (PRECEDES) 보강 (BP4 이후)
  - [x] BP5-1. `Q01_EXP_01` 기준 `because_chain` 2~3 hop 자동 생성 연결
  - [x] BP5-2. 체인 정렬 규칙 고정(episode asc + id asc)
  - [x] BP5-3. WHY 포맷 검증(`answer_event`, `because_chain`, `reveal_hint`, `confidence_note`) (타입/렌더/실행경로 반영)
  - [x] BP5-4. 완료조건: WHY 질문 3개(T08~T10)에서 체인 누락 0건 (로컬 스모크/회귀 통과)

- [x] BP6. Data Backfill / 운영 적용 (BP4 이후, BP5 병행 가능)
  - [x] BP6-1. 기존 `target_type=ATTRIBUTE` 데이터에 `target_key` 백필(가능 row 우선, Phase1 scope)
    - [x] BP6-1-a. Q1 expansion 6문항 anchor row는 ops seed로 선반영 (`run_expansion100_q1_seed_and_validate.sh` PASS)
  - [x] BP6-2. 백필 불가 row 정책 적용(보류/메모/제외) (`validate-reveal-target-key-runtime-phase1.py`: legacy unresolved 6 warn/backlog)
  - [x] BP6-3. Q1 expansion 6문항 answerset 재검증(축/B-lane 동작 확인) (`validate-expansion100-intelligence-columns.py` PASS)
  - [x] BP6-4. 완료조건: expansion answerset에서 B-lane `target_key` 매칭률 80% 이상 달성 (100%, 6/6)

- [x] BP7. 선택 확장 (Phase2+)
  - [x] BP7-1. `reveals[]` 다건 응답 설계/반영(현재 first-row wins 보정)
  - [x] BP7-2. API/프론트 렌더링 다건 reveal 카드 규칙 고정
  - [x] BP7-3. 완료조건: event당 복수 reveal 손실 없이 표시

- [ ] BP8. Quality Gate / Release
  - [x] BP8-1. 로컬 검증 스크립트: 코드북-템플릿-데이터 키 정합성 검사 실행 (`validate-reveal-target-key-gate.py` PASS)
  - [x] BP8-2. 스모크: `safeUpToEpisode` + `source_status=APPROVED` + strict-first 회귀 (`validate-productionq-and-regression.py` PASS)
  - [ ] BP8-3. CI 연결은 보류(사용자 지시 반영), 로컬 게이트 우선 운영
  - [x] BP8-4. 구현 완료 리뷰 문서 작성 및 ex23/blueprint 체크상태 동기화 (`fivecircles/work/review/review-blueprint-bp3-bp8-2026-02-27.md`)
  - [x] BP8-5. 최종 승인조건: 보류 항목(BP3-2/3/5) 제외 범위에서 BP0~BP7 완료 + 회귀 통과 + 문서/코드 정합성 확인

### 10. Phase2 ATTRIBUTE ID/Closure 전환 실행 (2026-02-27)
> refs: `fivecircles/architecture/specs/rdf/inheritance-blueprint.md`, `fivecircles/architecture/specs/reveals/reveal-target-key-codebook.md`

- [x] P0. 계약/범위 고정 (선행)
  - [x] P0-1. 목표 고정: `target_type=ATTRIBUTE`의 최종 의미를 `target_id=attribute.id`로 전환
  - [x] P0-2. dual-read 전환 원칙 고정: Phase2 동안 `target_key` 우선 + legacy fallback 허용
  - [x] P0-3. 보류 범위 고정: wiki/intelligence write-path는 팀 합의 전 변경 금지

- [x] P1. 스키마 기초 도입 (실행 완료)
  - [x] P1-1. Flyway migration 추가: `V11__create_attribute_taxonomy_tables.sql`
  - [x] P1-2. ops apply/rollback/verify 스크립트 추가
  - [x] P1-3. 로컬 도커 mysql apply 검증 PASS (`run_attribute_taxonomy_migration.sh apply`)

- [x] P2. 코드북-DB 연결
  - [x] P2-1. `attribute(code)` seed 스크립트 추가 (`A_*` 코드북 기준)
  - [x] P2-2. `attribute_closure` seed 스크립트 추가 (ancestor/descendant/depth)
  - [x] P2-3. 검증 스크립트: 코드북 key 100% resolve 게이트 (`validate-attribute-taxonomy-phase2.py` PASS)

- [x] P3. Read-path dual lane
  - [x] P3-1. B-lane 매칭 우선순위: `target_key` -> `attribute.id(target_id)` -> legacy fallback
  - [x] P3-2. 플래그 도입: `useAttributeIdLane` (기본 OFF, `VITE_USE_ATTRIBUTE_ID_LANE`)
  - [x] P3-3. Q01_EXP_01~06 회귀 PASS (`validate-reveal-target-key-runtime-phase1.py` PASS)

- [x] P4. 백필
  - [x] P4-1. `event_reveal(target_type=ATTRIBUTE)` 대상 `target_id=attribute.id` 백필 (`backfill_event_reveal_target_id_attribute_phase2.sql`: updated_rows=7)
  - [x] P4-2. 백필 불가 row backlog 분리(자동추정 금지) (`validate-event-reveal-attribute-id-phase2.py`: legacy missing target_key 6 warn)
  - [x] P4-3. drama10 누락 0건 확인 (`validate-event-reveal-attribute-id-phase2.py` PASS)

- [x] P5. WHY 의미 분리
  - [x] P5-1. `selection_why` / `causal_why` 구조 분리 (`front/common/productionQ/types.ts`, `executor.ts`)
  - [x] P5-2. `causal_why`를 PRECEDES + reveal evidence로 생성 (`useProductionQ.ts` because_chain 반영)
  - [x] P5-3. Q01_EXP_01 출력 검증 (`fivecircles/test/validate-q01-exp-01-why-output-phase2.py` PASS)

- [x] P6. 전환 완료
  - [x] P6-1. 플래그 ON 스모크 (`VITE_USE_ATTRIBUTE_ID_LANE=true npm run build` PASS)
  - [x] P6-2. legacy fallback 제거 계획 확정 (`fivecircles/architecture/specs/rdf/attribute-id-lane-cutover-plan.md`)
  - [x] P6-3. 최종 승인(보류 항목 제외) (`validate-attribute-taxonomy-phase2.py`, `validate-event-reveal-attribute-id-phase2.py`, `validate-q01-exp-01-why-output-phase2.py`, `validate-productionq-and-regression.py` PASS; legacy missing target_key 6건은 warning backlog 유지)

---
