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

post-v0.2.5 safe-install polish 안정화

## 현재 우선순위

1. v0.2.6 GitHub Release publish는 명시 승인 대기 상태다.

## In Progress

- status: blocked
- goal: v0.2.6 GitHub Release publish
- scope: release prep commit push, CI 확인, annotated tag push, GitHub Release 생성과 wheel/sdist asset 업로드.
- non-goals: PyPI/TestPyPI 배포는 하지 않는다.
- blocker: dev-loop safety상 push/tag/release는 live external write이므로 명시 승인이 필요하다.
- acceptance criteria:
  - GitHub Release `v0.2.6` published.
  - release URL clean install smoke 통과.
  - publish 기록 archive.
- verification commands:
  - `gh run watch <run-id> --repo answndud/repo-trust --exit-status`
  - release URL clean install smoke commands
- next action: 사용자가 push/tag/release publish를 명시 승인하면 진행한다.

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. 사용자가 publish를 명시 승인하면 v0.2.6 GitHub Release publish를 진행한다.
