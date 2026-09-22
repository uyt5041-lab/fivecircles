# Todo List (Implementation)
Detail tasks live in this file under each item.

## 2026-09-22 - 디노킹덤 스킬 동기화

- 구현자/서명: 희동 (Codex), 2026-09-22T16:11:22+09:00.
- 최종수정일시: 2026-09-22T16:17:13+09:00.
- [x] DINO-SYNC-01: 파이어볼/디노스킬등록/디노킹덤 목록과 별도 업데이트 노트 폴더 반영. 형식/UI/ID/시동어/내장·독립 링크22개/원본·전역 사본 일치 PASS. [검증 기록](../work/log_희동/log_DINO-SYNC-01_2026-09-22.md).
- [x] DINO-SYNC-02: 검증 커밋 `c771fc1` 기능 브랜치 푸시, 기존 frontier로 fast-forward 통합/푸시 완료. `git ls-remote`로 두 원격 브랜치가 동일한 전체 SHA임을 확인했다. main 및 제품 배포 변경 없음.

## 2026-09-07 — 협업 스킬 동기화 (CUSTOM)

- [x] 협업/릴레이 스킬 연결을 프로젝트 설치본에 동기화하고 형식·참조·프로젝트 경로를 검증한다.
- 통합 승인: 검증된 스킬과 이번 기록만 현재 브랜치에 커밋하고 같은 이름의 원격 브랜치로 푸시한다. 실제 결과는 Git 영수증으로 확인한다.
- 범위 제외: 제품 코드, 데이터, 기존 미커밋 변경.
- 근거: `work/2026-09-07-collaboration-skill-sync.md`.
