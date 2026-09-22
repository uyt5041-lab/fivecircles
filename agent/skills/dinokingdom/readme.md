# 디노킹덤 (공룡왕국)

- 구현자/서명: 희동 (Codex)
- 작성일시: 2026-09-22T16:04:20+09:00
- 최종수정일시: 2026-09-22T16:11:22+09:00

**디노킹덤은 Fivecircles workframe 기반의 레이어별 오딧 자동화 스킬셋입니다.**

요구사항, 구조, 구현, 테스트, 전달 등 각 레이어에서 확인한 상태와 부족한 점을
오딧으로 남기고, 이를 설계·계약·TODO·구현·검증으로 이어가는 작업 체계입니다.
스킬별 역할과 시동어를 분리하며 기존 Fivecircles 도구와 프로젝트 계약을 재사용합니다.

이 README는 디노킹덤의 스킬 등록부입니다. 전체 Fivecircles 스킬을 자동으로 포함하지
않으며 실제 등록한 스킬만 아래에 적습니다. 목록 등록은 해당 기능의 운영 검증이나
배포 완료를 의미하지 않습니다. 세부 실행 규칙은 각 스킬의 `SKILL.md`가 기준입니다.

## 스킬 등록 방법

등록 스킬은 **디노스킬등록 (`regdinoskill`)**입니다.
[등록 스킬의 설명과 규칙](../regdinoskill/SKILL.md)을 따라 이 README의 목록을 갱신합니다.

```text
디노스킬등록 fireball
regdinoskill fivecircles/agent/skills/fireball/SKILL.md
$regdinoskill 파이어볼의 설명과 시동어를 현재 SKILL.md 기준으로 갱신해
```

등록할 스킬 이름 또는 `SKILL.md` 경로를 주면 실제 내용을 확인해 **스킬 ID, 이름,
담당 레이어, 간략 설명, 시동어, 위치 링크**를 넣습니다. 같은 ID가 이미 있으면
중복 행을 만들지 않고 갱신합니다. 파일이나 필수 정보가 없으면 보완할 내용을 알려줍니다.
등록은 목록 편집이며, 대상 스킬의 실행·전역 설치·파일 이동은 별도 요청입니다.

## 스킬 목록

<!-- dinokingdom:skills:start -->
| 스킬 ID | 이름 | 담당 레이어 | 간략 설명 | 시동어 | 위치 |
| --- | --- | --- | --- | --- | --- |
| `fireball` | 파이어볼 | 구현·전달 | audit/request를 입력으로 새 워크트리에서 Graft 조사, 구조 설계, 계약, 구현·검증과 승인된 Git/CD를 진행합니다. | `구현자 시동`, `구현 파이어볼`, `파이어볼`, `$fireball` | [fireball/SKILL.md](../fireball/SKILL.md) |
| `regdinoskill` | 디노스킬등록 | 스킬셋 관리 | 실제 스킬 문서를 확인해 이 README에 설명·시동어·위치를 등록하거나 갱신합니다. | `디노스킬등록`, `regdinoskill`, `$regdinoskill` | [regdinoskill/SKILL.md](../regdinoskill/SKILL.md) |
<!-- dinokingdom:skills:end -->

## 위치 기준

- 이 등록부: `fivecircles/agent/skills/dinokingdom/readme.md`.
- 프로젝트 스킬: `fivecircles/agent/skills/{skill-id}/SKILL.md`. 기존 위치는 옮기지 않고 링크로 연결합니다.
- 전역 스킬을 사용하더라도 등록 대상 README는 **현재 선택한 프로젝트/worktree**에서 찾습니다.
- 독립 Fivecircles 저장소에서는 저장소 자체가 문서 루트이므로 위 경로에서 `fivecircles/` 접두사를 뺍니다. 폴더를 중첩 생성하지 않습니다.
- Fivecircles 전체 안내: [fivecircles/README.md](../../../README.md).

## 업데이트 노트

스킬 추가·변경 내용은 [업데이트 노트 폴더](update-notes/readme.md)에 날짜별로 남깁니다.
