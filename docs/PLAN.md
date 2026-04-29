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

RepoTrust post-v1 release candidate를 원격 반영할지 결정하고 배포 전 마지막 단계를 준비한다.

## 현재 우선순위

1. GitHub push 여부와 release tag 생성 여부를 결정한다.

## In Progress

현재 active 작업 없음

## Pending

### Release candidate 원격 반영 여부 결정

- Status: `Pending`
- Goal: 생성된 release candidate commit을 GitHub 원격에 push할지, release tag를 만들지 결정한다.
- Scope: commit hash/status 확인, push 필요 여부 확인, tag/release note 필요 여부 정리.
- Non-goals: 사용자가 명시하지 않은 원격 push, PyPI 배포, 새 기능 추가.
- Acceptance criteria:
  - 로컬 commit 상태와 원격 대비 ahead/behind 상태가 확인된다.
  - push 또는 tag를 진행할지 다음 액션이 명확해진다.
- Verification commands:
  - `git status --short --branch`
  - `git log --oneline -3`
- Next action: 사용자가 push를 원하면 `git push origin main`을 실행한다.

## 다음 실행 순서

1. `Release candidate 원격 반영 여부 결정`을 `In Progress`로 승격한다.
2. 원격 push는 사용자가 명시적으로 요청할 때만 실행한다.
