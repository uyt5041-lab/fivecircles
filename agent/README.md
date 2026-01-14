# Agent Command Center (Start Here)

당신은 이 저장소에서 “개발 운영”을 수행하는 코딩 에이전트입니다.
가장 중요한 목표는: **요구사항을 명확히 하고, 작은 배치로 구현하며, 테스트 통과 상태를 커밋/푸시로 고정**하는 것입니다.

## Mandatory Read Order
1) agent/authority.md
2) agent/workflow.md
3) agent/policies.md
4) agent/methodology.md
5) agent/operational-guidance.md
6) test/testpolicy.md
7) requirements/* (현재 유효한 요구사항)

## Working Mode
- 모든 작업은 `architecture/todolist.md`의 **Batch** 단위로 수행합니다.
- 작업 중 의사결정/충돌/근거는 `work/worklog.md`에 남깁니다.
- 기술적 분석 결과는 `spec/`에 정리합니다. (agent 문서에 기술 분석을 쓰지 않습니다.)

## Debate Mode (Requirements)
- 요구사항이 불명확/모순/충돌이면, 먼저 `requirements/debates/`에 논쟁 기록을 생성합니다.
- 합의된 결론은 `requirements/decisions.md`에 “확정”으로 남깁니다.
- 확정 이후에만 spec/에 기술 설계를 고정합니다.

## Cycle (6-stage)
Requirements → Design → Implementation → Test → Integrate(Commit/Push) → Maintenance

## What you do first
1) requirements/README.md 확인
2) requirements/current.md에서 현재 요구사항 읽기
3) architecture/todolist.md에 Batch 1을 작성
4) work/worklog.md에 Stage=Design 엔트리 추가
