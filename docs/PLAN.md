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

RepoTrust v0.2.0 GitHub release publish 여부와 배포 후 검증 범위를 결정한다.

## 현재 우선순위

1. v0.2.0 GitHub release publish를 준비한다.

## In Progress

현재 active 작업 없음

## Pending

### v0.2.0 GitHub release publish 준비

- Status: `Pending`
- Goal: pushed `v0.2.0` tag를 기준으로 GitHub release를 만들 수 있는지 확인하고 release note를 준비한다.
- Scope: `CHANGELOG.md`의 `v0.2.0` section 추출, GitHub release 생성 가능 여부 확인, release publish command 정리.
- Non-goals: PyPI 배포, 새 기능 추가.
- Acceptance criteria:
  - GitHub release note에 들어갈 `v0.2.0` 변경 내용이 확인된다.
  - GitHub release publish를 진행할 command와 검증 방법이 명확하다.
- Verification commands:
  - `git status --short --branch`
  - `git tag --list 'v0.2.0' -n`
  - `git ls-remote --tags origin 'refs/tags/v0.2.0*'`
- Next action: `CHANGELOG.md`의 `v0.2.0` section을 release note 후보로 추출한다.

## 다음 실행 순서

1. `v0.2.0 GitHub release publish 준비`를 `In Progress`로 승격한다.
2. release note와 publish command를 준비한다.
