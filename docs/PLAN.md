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
- goal: 초보 사용자가 scan 결과를 본 뒤 바로 실행할 수 있는 `fix-plan` 또는 `next-steps` 기능을 추가한다.
- scope:
  - JSON/HTML/terminal report의 findings를 기반으로 우선순위별 조치 목록을 생성한다.
  - `repo-trust next-steps <target>` 또는 기존 `explain`/`safe-install`과 연결되는 copyable 명령을 제공한다.
  - README에 "위험 리포트를 받았을 때 무엇을 해야 하나" 초보자 가이드를 추가한다.
- non-goals:
  - 자동 수정 적용은 하지 않는다.
  - 외부 API나 vulnerability DB 조회는 하지 않는다.
- acceptance criteria:
  - 좋은 fixture는 짧은 확인 checklist를 보여준다.
  - risky fixture는 high severity install finding을 먼저 멈추게 하고, 그 다음 license/CI/security policy 순서로 설명한다.
  - 영어/한국어 CLI와 README 가이드가 모두 갱신된다.
- verification commands:
  - `.venv/bin/python -m pytest -q`

## 다음 실행 순서

1. 다음 작업을 시작하면 pending의 `next-steps` 기능을 In Progress로 승격한다.
2. CLI 출력과 README 초보자 가이드를 함께 구현한다.
3. fixture 기반 테스트와 smoke를 추가한다.
