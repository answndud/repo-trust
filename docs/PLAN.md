# PLAN

앞으로 할 active 작업과 완성품까지의 순차 backlog를 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- credential, production publish, 보안/권한 결정처럼 진행 불가한 항목은 `In Progress` 아래에 두고 status를 `Blocked`로 표시한다.
- `Pending`은 완성품까지의 순차 backlog로 유지한다. 새 작업을 시작할 때 맨 위 항목 하나만 `In Progress`로 승격한다.
- 각 작업에는 status, goal, scope, non-goals, acceptance criteria, verification commands, next action을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

현재 active 작업 없음.

## 현재 우선순위

현재 active 작업 없음.

## In Progress

현재 active 작업 없음.

## Pending

- status: pending
- goal: v0.2.9 release prep
- scope:
  - `next-steps` command와 HTML/JSON next-steps integration을 patch release로 정리한다.
  - package/runtime version, README install URL, CLI version tests, CHANGELOG를 `0.2.9`에 맞춘다.
  - build, clean wheel smoke, self-scan을 수행한다.
- non-goals:
  - PyPI/TestPyPI 배포는 하지 않는다.
  - 추가 기능 구현은 release prep 범위에 포함하지 않는다.
- acceptance criteria:
  - 전체 테스트, build, clean wheel smoke, self-scan이 통과한다.
  - release candidate 문서가 `docs/COMPLETED.md`에 archive된다.
  - publish는 별도 승인 전까지 진행하지 않는다.
- verification commands:
  - `git diff --check && .venv/bin/python -m pytest -q`
  - `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.9/dist`

## 다음 실행 순서

1. 다음 작업을 시작하면 v0.2.9 release prep을 In Progress로 승격한다.
2. version/README/CHANGELOG/tests를 `0.2.9`에 맞춘다.
3. build와 clean wheel smoke 후 publish 승인 대기 상태로 정리한다.
