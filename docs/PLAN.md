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
- goal: HTML 리포트와 저장된 JSON 리포트에서도 `next-steps` 흐름을 이어갈 수 있게 한다.
- scope:
  - HTML 리포트에 `Next Steps` 섹션 또는 action block을 추가한다.
  - 저장된 JSON 리포트를 다시 스캔하지 않고 읽어 `next-steps`를 출력하는 command option 또는 별도 command를 검토한다.
  - README에 "저장된 리포트에서 다음 조치 이어가기" 가이드를 추가한다.
- non-goals:
  - 자동 수정 적용은 하지 않는다.
  - 외부 API, secret key, vulnerability DB 조회는 하지 않는다.
- acceptance criteria:
  - HTML 리포트에서 high severity install finding 다음에 license/CI/security policy 순서의 action이 보인다.
  - 저장된 JSON report workflow가 재스캔 없이 동작하거나, 미지원이면 의도적으로 문서화된다.
  - tests와 README가 함께 갱신된다.
- verification commands:
  - `.venv/bin/python -m pytest -q`

## 다음 실행 순서

1. 다음 작업을 시작하면 pending의 HTML/JSON next-steps integration을 In Progress로 승격한다.
2. HTML report renderer와 JSON report reuse 가능성을 먼저 확인한다.
3. 구현 후 fixture 기반 테스트와 전체 테스트를 실행한다.
