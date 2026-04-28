# PLAN

앞으로 할 active 작업만 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- 각 작업에는 완료 기준을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.
- 프로젝트가 아직 완성 전이면 다음 개발 계획을 우선순위 순서로 다시 채운다.

## 현재 목표

Remote scan UX를 문서화하고 v0.1.0 릴리스 준비를 완료한다.

## 현재 우선순위

1. v0.1.0 tag 생성
2. Remote scan 품질 개선 계획 수립

## In Progress

### 1. v0.1.0 tag 생성

- 작업: 검증 통과 후 `v0.1.0` git tag를 생성한다.
- 배경: release notes와 pre-tag checklist가 준비됐으므로 실제 tag를 만들 수 있는 상태인지 확인한다.
- 완료 기준:
  - 테스트와 smoke checks가 통과한다.
  - `git tag v0.1.0`이 생성된다.
  - 사용자가 원하면 tag push까지 진행할 수 있는 상태다.
- 영향 범위: git tag, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`.
- 검증: `.venv/bin/python -m pytest -q`, local/remote smoke checks

## Pending

### 2. Remote scan 품질 개선 계획

- 작업: release/tag freshness, archived/fork/private 상태, metadata evidence 정책을 다음 backlog로 설계한다.
- 완료 기준:
  - 점수화할 항목과 evidence-only 항목이 분리된다.
  - 다음 recursive loop story가 작게 쪼개진다.

## 다음 실행 순서

1. `v0.1.0 tag 생성`을 진행한다.
2. tag 생성 후 Remote scan 품질 개선 계획을 수립한다.
