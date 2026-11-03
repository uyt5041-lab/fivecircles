# FiveCircles

이 폴더는 프로젝트에 “개발 5사이클(+Integrate)” 운영체제를 이식하기 위한 템플릿입니다.

이 `README`는 간략한 안내와 사용설명서 역할을 합니다. FiveCircles의 배경, 설계 개요, 운영 체계에 대한 자세한 설명은 [개요.md](./개요.md)에서 확인할 수 있습니다.

이 프로젝트와 문서가 도움이 되었다면 저장소에 GitHub Star를 남겨주세요!!!

> 이 템플릿은 여러 새 프로젝트를 거치며 점진적으로 진화해왔습니다. 그래서 일부 문서나 구조에는 이전 사용 흔적이 남아 있을 수 있으며, 현재 프로젝트에 맞게 정리·조정해서 사용하는 것을 전제로 합니다.

## License
This project’s design and governance documents are licensed under **CC BY 4.0**.

## 시작하기
- architecture/specs/README.md를 읽고 워크플로우를 초기화합니다.

## 어디에 뭐가 있나
- architecture/specs/README.md 전체 워크플로우를 정의합니다.
- **requirements/**: 프로젝트 요구사항. 사용자와 합의/논쟁(debate)하고 확정하는 공간입니다.
- **architecture/spec/**: architecture/specs/README.md에 명시된 절차에 따라, 요구사항/결정에 기반해 “분석된 기술적 내용”만 기록합니다. (설계·API·DB·성능·보안 등)
- **architecture/todo/**: 작업 배치/태스크 분해(플랜)
- **work/**: 실행 로그(결정, 근거, 결과), 업데이트 기록
- **test/**: 테스트 정책 및 실패 로그, 개선사항 기록/제안
- **maintenance/**: 유지보수/새 요구사항 환류
- **scoring/**: 에이전트 점수 규칙/기록, 더 나은 코딩 절차 제안

## 시작 순서 (사람/에이전트 공통)
1) architecture/specs/README.md
2) agent/agent-guidelines.md
3) requirements/README.md
4) architecture/todolist.md 작성 후 사이클 시작

===

이 섹션은 사람이 읽기위한 정보를 담고 있습니다.(설명서)

## 초기화방법

-에이전트에게 프롬프트 입력:
"fivecircles/README.md를 읽고 운영방침을 초기화하라"
-스킬을 등록했다면 "운영방침 초기화" 만으로 초기화 가능

## 스킬등록방법
- 프롬프트 입력: "agent/skills/ 폴더를 보고 스킬을 등록하세요."
- 스킬설명은 이 문서 하단에 있음.

- 개발시 자주 쓰는 프롬프트들:
"스펙(architecture/specs)의 내용을 확인하고 그대로 개발하라"
    (세세히 명령 가능 예: architecture/specs에서 최신 sql파일을 확인하고 이에 맞게 (기능)을 개발해라)
"투두리스트를 확인하고 다음할일을 정리해라"
"learn-from-log, optimization을 참고하여 개선사항을 제시해라"(에러잡기)
"다음 요구사항을 확인하고 투두리스트 업데이트 후 workpolicy에 따른 사이클대로 개발 진행해라:
{요구사항-적기}"

- 멀티에이전트 협업용 옵션:
경로 `fivecircles/agent/prompts` 에 있는 프롬프트들을 참고하여 사용할 수 있습니다.

기본 구조:

```text
fivecircles/agent/
├── configs/
│   ├── planner-gemini.json
│   ├── coder-claude.json
│   ├── ops-codex.json
│   └── reviewer-claude.json
├── collaboration-protocol.md
└── ...
```

역할 요약:

| Alias | 기본 Agent 예시 | 기본 역할 | 주 담당 |
|------|------------------|-----------|---------|
| `agent-plan` | Gemini | Planner | 전체 조율, 태스크 분배 |
| `agent-code` | Claude | Coder | 기능 구현, 서비스 코드 작업 |
| `agent-codex` | Codex | Ops | Deploy, Git, 문서 편집 |
| `agent-review` | Claude | Reviewer | 코드 리뷰, 테스트, 검증 |

역할은 고정된 것이 아니라 프로젝트 규모, 사용 가능한 모델, 현재 작업 성격에 따라 유동적으로 지정하거나 재배치할 수 있습니다.

작업 흐름:

```text
사용자 -> Planner
            |
    +-------+-------+
    |       |       |
  Coder    Ops   Reviewer
```


중요! 스펙은 항상 최신으로 유지하고 바꿀때마다 인지시켜줘야 합니다.


새로운 세션(에이전트)를 불러와도 fivecircles/readme.md를 읽고 시작하면 컨텍스트 로스를 최소화하여 사용가능합니다.

추가 업데이트 의견: (아래에 적어주세요)

-mcp 서버 기본설정 공유

---

## 에이전트 스킬 (Agent Skills)

- fivecircles에서 사용하는 스킬 내용은 `fivecircles/agent/skills/` 폴더의 파일들에 나와있습니다.

에이전트는 세션 시작 시 `fivecircles/agent/skills/` 폴더의 파일들을 읽고 다음 스킬들을 숙지하여 사용하거나,
또는 에이전트 스킬로 등록해 사용할 수 있습니다(예: codex skills, gemini skills, claude skills)


상세내용:

| 스킬명 | 파일명 | 발동 명령어 | 설명 |
|--------|--------|-------------|------|
| **울트라 기록 (Ultra Record)** | `protocol_ultra_record.md` | `"울트라 기록해"` | 세션 종료 시 로그 작성(Update/Todo), 에러 기록, 스코어링, 동기화를 한 번에 수행합니다. (필수) |
| **빠른 디버깅 (Quick Debug)** | `protocol_quick_debug.md` | `"빠른 디버깅해"` | 에러 발생 시 `mistakes-arrest`, `learn-from-log`를 먼저 검색하여 해결책을 찾습니다. |
| **로그/요약 프로토콜 (Logging & Summary)** | `protocol_logging_summary.md` | `"로그 요약해"` | 작업 종료 시 update/todo/sync/error/mistakes/debate 기록을 표준화합니다. |
| **동료 리뷰 (Peer Review)** | `protocol_peer_review.md` | `"리뷰해"` | debate.md를 중심으로 변경/의사결정을 검토하고 리뷰를 기록합니다. |
| **운영방침 초기화 (Init Ops)** | `protocol_operation_init.md` | `"운영방침 초기화"` | 프로젝트 문서(Readme, Specs, Guidelines)를 읽고 에이전트의 역할과 맥락을 재설정합니다. |
| **테스트 실행 (Test Exec)** | `protocol_test_execution.md` | `"테스트 실행"` | `test-front/server-policy`를 참조하여 규정된 환경과 명령어로 테스트를 수행합니다. |
| **동료 리뷰 (Peer Review)** | `protocol_peer_review.md` | `"리뷰해줘"` | `debate.md`와 참조된 문서를 읽고 정합성, 안전성, 완성도를 평가하여 피드백을 남깁니다. |
| **배포 (Deploy)** | `protocol_deploy.md` | `"배포해"` | 프론트엔드 빌드 상태를 점검하고 Vercel 배포(Push/CLI)를 트리거합니다. |
| **서버 배포 (Deploy Server)** | `protocol_deploy_server.md` | `"서버 배포해"` | SSH를 통해 테스트 서버에 배포(`git pull` & `docker compose up`)를 수행합니다. |
| **스코어링 (Scoring)** | `protocol_agent_scoring.md` | (울트라 기록에 포함) | 작업 성과를 정량적으로 평가하고 `log-score.md`에 기록합니다. |
| **톺아보기 (Read Log)** | `protocol_read_log_setup.md` | `"톺아보기"` | 로그(update, todo, sync)를 읽고 최근 변경사항(예: 포트변경)을 분석하여 다음 작업을 설정합니다. |


## 위험도별 필수 EGM과 구조 설계 (2026-11-03)

- [공통 정책](agent/skills/doc-contract-writer/references/egm-design-review.md): 계약·권한·데이터 변경은 FULL5단계, 작은 수정은 TARGETED, 유효 결과는 재사용합니다.
- [개발 검토 기준](agent/skills/doc-contract-writer/references/engineering-review-standard.md): 리소스·보안 시점·중복·구조·호환성을 확인합니다.
- [구조 설계 스킬](agent/skills/structure-architect/SKILL.md): 작은 변경의 간단한 결과와 전체 구조 설계를 구분합니다. 기존 agent/structure-architect 경로는 안내 진입점으로 유지합니다.
- [계약 작성](agent/skills/doc-contract-writer/SKILL.md), [릴레이](agent/skills/relay-shot/SKILL.md), [원샷 조정](agent/skills/one-shot-delivery-orchestrator/SKILL.md), [실행 양식](agent/skills/protocol_one_shot_delivery.md)이 같은 정책을 참조합니다.

EGM 실행에는 [공식 EGM bundle](https://github.com/google/elephant-goldfish-model)과 호스트의 독립 검토자 실행 도구가 필요합니다. 공식 bundle은 배포 원본·라이선스를 유지하여 별도로 설치합니다. 이 저장소는 해당 bundle이나 외부 실행 도구를 내장하지 않습니다.
릴레이/원샷이 이름으로 참조하는 구현·테스트·리포트 스킬은 호스트에서 확인해 사용합니다. 필요한 스킬/검토 수단이 없으면 해당 단계를 BLOCKED로 기록하고 임의 PASS로 대체하지 않습니다.

[이번 적용과 검증](work/review/egm-structure-2026-11-03.md) · [푸시·머지 기록](work/integrate-log.md)

배포 스킬 식별자는 `relay-shot`이며, 설명의 한국어 호출 키워드 `릴레이샷`은 유지합니다. 기존 로컬 설치의 호출 이름은 이 게시 작업에서 일괄 변경하지 않습니다.
