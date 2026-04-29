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

RepoTrust v0.2.0 release metadata commit을 원격에 반영하고 tag 생성 단계를 준비한다.

## 현재 우선순위

1. v0.2.0 release metadata commit 원격 반영 여부와 tag 생성을 결정한다.

## In Progress

현재 active 작업 없음

## Pending

### v0.2.0 release metadata 원격 반영 및 tag 준비

- Status: `Pending`
- Goal: v0.2.0 release metadata commit을 GitHub main에 반영하고 `v0.2.0` tag 생성 조건을 확인한다.
- Scope: commit 원격 반영, local/remote tag 상태 확인, `v0.2.0` annotated tag 후보 정리.
- Non-goals: 사용자가 명시하지 않은 tag push, GitHub release publish, PyPI 배포.
- Acceptance criteria:
  - release metadata commit이 원격에 필요한지 상태가 확인된다.
  - `v0.2.0` tag 생성 대상 commit과 기존 `v0.1.0` tag와의 관계가 명확하다.
- Verification commands:
  - `git status --short --branch`
  - `git tag --list --sort=version:refname`
  - `git ls-remote --tags origin`
- Next action: release metadata commit을 push할지 확인하고 `v0.2.0` tag 생성 전 상태를 점검한다.

## 다음 실행 순서

1. `v0.2.0 release metadata 원격 반영 및 tag 준비`를 `In Progress`로 승격한다.
2. 원격 push와 tag push는 사용자가 명시적으로 요청할 때만 실행한다.
