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

Console Mode와 Command Mode를 분리해 유명 CLI/TUI 도구처럼 더 명확한 제품형 터미널 경험으로 개선한다.

## 현재 우선순위

1. Command Mode assessment renderer

## In Progress

### Command Mode assessment renderer

- status: in_progress
- goal: `repo-trust html/json/check` 직접 명령의 결과 화면을 보안/OSINT 도구처럼 판단, 근거, finding, 다음 조치 중심으로 재설계한다.
- scope:
  - Command Mode dashboard 코드를 별도 renderer 모듈로 분리한다.
  - verdict, score, risk, finding distribution, category score bars, evidence snapshot, top findings, next actions를 구분된 섹션으로 출력한다.
  - HTML/JSON 명령은 stdout을 비우고 stderr dashboard만 출력하는 contract를 유지한다.
  - README와 testing docs를 새 화면 구조에 맞춘다.
- non-goals:
  - 점수 산식이나 finding ID를 변경하지 않는다.
  - HTML report renderer에 scan/scoring logic을 넣지 않는다.
- acceptance criteria:
  - direct command dashboard에 `Trust Assessment`, `Risk Breakdown`, `Evidence`, `Top Findings`, `Next Actions`가 표시된다.
  - JSON/HTML 명령은 stdout을 오염시키지 않는다.
  - 기존 legacy `repotrust scan`은 호환된다.
- verification commands:
  - `.venv/bin/python -m pytest -q`
  - `.venv/bin/repo-trust html . --output /tmp/repotrust-command-dashboard.html`
- next action: Command Mode dashboard renderer를 별도 모듈로 분리 구현한다.

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. Command Mode assessment renderer
