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

RepoTrust v0.2.1 GitHub-only release를 준비하고 publish한다.

## 현재 우선순위

1. 검증된 v0.2.1 release metadata를 commit하고 원격에 반영한다.
2. v0.2.1 annotated tag와 GitHub Release를 생성한다.

## In Progress

### v0.2.1 release commit/tag/publish

- Status: `In Progress`
- Goal: 검증된 `v0.2.1` GitHub-only release를 commit, tag, GitHub Release로 publish한다.
- Scope: release metadata commit, `main` push, annotated tag 생성/push, GitHub Release publish, post-release 상태 문서 정리.
- Non-goals: PyPI/TestPyPI publish, 새 기능 추가.
- Acceptance criteria:
  - `main`과 `origin/main`이 release metadata commit으로 동기화된다.
  - `v0.2.1` annotated tag가 local과 remote에 존재한다.
  - GitHub Release `v0.2.1`이 publish된다.
- Verification commands:
  - `git status --short --branch`
  - `git ls-remote --tags origin 'refs/tags/v0.2.1*'`
  - `gh release view v0.2.1 --repo answndud/repo-trust`
- Next action: release metadata 검증 후 commit/tag/release를 진행한다.

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. release metadata commit을 생성하고 원격에 반영한다.
2. `v0.2.1` annotated tag를 생성하고 push한다.
3. `v0.2.1` GitHub Release를 publish한다.
