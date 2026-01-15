# Project Role Distribution (R&R) - Source: Notion

> **Synced**: 2026-01-15 (Sprint 1)

오프라인 논의를 통해 결정된 3인 팀(MSA 기반)의 역할 분담 및 서비스 구조입니다.

---

## 👥 팀원별 담당 영역 및 서비스

### 1. 팀원 A: Infra & Identity (System Gateway) - 김현종
사용자 진입점과 시스템의 기반을 담당합니다.
- 담당 서비스: `api-gateway`, `auth-service`, `user-service`, `admin-service`
- 핵심 역할: DevOps Leader (CI/CD, 배포), Security 정책 수립

### 2. 팀원 B: Core Domain (Content & Data) - 김경재
서비스의 핵심 데이터인 드라마 정보와 위키 콘텐츠를 총괄합니다.
- 담당 서비스: `drama-service`(드라마), `character-service` (인물), `wiki-service` (리뷰/글)
- 핵심 역할: Data Architect (DB 설계), Performance (캐싱 전략)

### 3. 팀원 C: Intelligence & Filter (AI & Policy) - 박지수 (YOU)
이 프로젝트의 핵심인 '스포일러 판단' 로직과 AI 기능을 전담합니다.
- 담당 서비스: `event-service`(온톨로지 데이터), `spoiler-policy-service`(판단 규칙), `qa-service`
- 핵심 역할: AI Engineer (프롬프트/검증), Async Processing (비동기 처리 설계)

---

## 🏗️ 서비스 아키텍처 및 흐름 제안

1. 진입: 사용자 -> Gateway (A)
2. 인증: Gateway -> Auth (A)
3. 작성: Gateway -> Wiki (B)
4. 판단 (비동기): Wiki -> (Message Queue) -> Filter (C)
5. 결과: Filter -> Wiki (상태 업데이트: PENDING -> SAFE/SPOILER)

<aside>
💡 초기 단계에서는 운영 복잡도를 줄이기 위해 서비스 개수를 최소화(통합)하는 것을 권장합니다.
</aside>

## 서비스 구조 재편 (2026-01-14 반영)

### 1. Content Service → 분리
- **Drama Service**: 드라마, 에피소드, 메인 노출 로직 담당.
- **Character Service**: 인물 정보 및 관련 로직 담당.
- *분리 사유: 도메인 비대화 방지 및 상이한 캐싱/인덱싱 전략 적용.*

### 2. Filter Service → 분리
- **Event Service**: 온톨로지 데이터 관리 (Fact 관리).
- **Spoiler Policy Service**: 스포일러 판단 규칙 및 정책 관리.

### 3. Admin Service (신설)
- Manual Event Seed 입력, Wiki 승인 모니터링, 드라마/에피소드 Seed 관리 등.
