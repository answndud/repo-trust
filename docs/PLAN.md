# PLAN

앞으로 할 active 작업과 완성품까지의 순차 backlog를 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- `Pending`은 완성품까지의 순차 backlog로 유지한다. 새 작업을 시작할 때 맨 위 항목 하나만 `In Progress`로 승격한다.
- 각 작업에는 status, goal, scope, non-goals, acceptance criteria, verification commands, next action을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

RepoTrust v0.2.0 annotated tag를 생성하고 원격 반영할지 결정한다.

## 현재 우선순위

1. v0.2.0 tag 생성 및 push 여부를 결정한다.

## In Progress

현재 active 작업 없음

## Pending

### v0.2.0 annotated tag 생성 및 push

- Status: `Pending`
- Goal: v0.2.0 release state에 annotated tag를 만들고 GitHub 원격에 반영한다.
- Scope: tag 대상 commit 확인, `v0.2.0` annotated tag 생성, tag push, local/remote tag 검증.
- Non-goals: GitHub release publish, PyPI 배포, 새 기능 추가.
- Acceptance criteria:
  - `v0.2.0` tag가 `0.2.0` package version과 changelog release heading을 포함한 commit을 가리킨다.
  - remote tag 목록에서 `v0.2.0`이 확인된다.
  - 기존 local `v0.1.0` tag는 재사용하거나 이동하지 않는다.
- Verification commands:
  - `git status --short --branch`
  - `git tag --list --sort=version:refname -n`
  - `git push origin v0.2.0`
  - `git ls-remote --tags origin 'refs/tags/v0.2.0*'`
- Next action: 사용자가 tag 생성을 원하면 `git tag -a v0.2.0 -m "RepoTrust v0.2.0"`을 실행한다.

## 다음 실행 순서

1. `v0.2.0 annotated tag 생성 및 push`를 `In Progress`로 승격한다.
2. tag를 만들고 push한 뒤 remote tag를 확인한다.
