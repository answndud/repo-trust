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

GitHub main에 반영된 RepoTrust release candidate의 tag/release 배포 범위를 결정한다.

## 현재 우선순위

1. Release tag 생성 여부를 결정한다.

## In Progress

현재 active 작업 없음

## Pending

### Release tag 생성 여부 결정

- Status: `Pending`
- Goal: 원격 main에 반영된 release candidate에 version tag와 GitHub release를 만들지 결정한다.
- Scope: 현재 package version, existing tag, changelog 상태, release note 필요 여부 확인.
- Non-goals: 사용자가 명시하지 않은 tag push, GitHub release publish, PyPI 배포, 새 기능 추가.
- Acceptance criteria:
  - 현재 version과 existing tag 상태가 확인된다.
  - tag/release를 진행할지 또는 version bump가 먼저 필요한지 다음 액션이 명확해진다.
- Verification commands:
  - `git status --short --branch`
  - `git tag --list`
  - `git log --oneline -3`
- Next action: tag/release 후보와 blocker를 확인한다.

## 다음 실행 순서

1. `Release tag 생성 여부 결정`을 `In Progress`로 승격한다.
2. tag push나 release publish는 사용자가 명시적으로 요청할 때만 실행한다.
