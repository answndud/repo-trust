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

RepoTrust v0.2.0 이후 PyPI 배포 여부와 post-release 검증 범위를 결정한다.

## 현재 우선순위

1. PyPI 배포 여부와 필요한 사전 조건을 판단한다.

## In Progress

현재 active 작업 없음

## Pending

### PyPI 배포 여부와 post-release 검증 결정

- Status: `Pending`
- Goal: GitHub release 이후 PyPI 배포를 진행할지, 아니면 GitHub release만으로 v0.2.0을 마무리할지 결정한다.
- Scope: package name availability/credentials 확인 가능성, build artifact smoke, post-release install path, README 배포 문구 drift 점검.
- Non-goals: 사용자가 명시하지 않은 PyPI publish, 새 기능 추가.
- Acceptance criteria:
  - PyPI 배포 진행/보류 판단이 문서화된다.
  - GitHub release URL과 tag 상태가 확인된다.
  - post-release smoke가 필요한 경우 다음 backlog로 분리된다.
- Verification commands:
  - `git status --short --branch`
  - `gh release view v0.2.0 --repo answndud/repo-trust`
  - `.venv/bin/python -m pip wheel --no-deps . --wheel-dir <tmp>`
- Next action: PyPI 배포 조건과 post-release smoke 범위를 확인한다.

## 다음 실행 순서

1. `PyPI 배포 여부와 post-release 검증 결정`을 `In Progress`로 승격한다.
2. PyPI publish는 credential과 배포 의사가 명확할 때만 실행한다.
