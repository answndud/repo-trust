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

1. v0.1.0 릴리스 준비
2. Remote scan 품질 개선 계획 수립

## In Progress

### 1. v0.1.0 릴리스 준비

- 작업: `CHANGELOG.md`를 추가하고 v0.1.0 release notes 초안을 작성한다.
- 배경: CLI v1과 Remote scan MVP가 구현됐으므로 첫 release를 위한 변경 요약과 제한 사항을 정리해야 한다.
- 완료 기준:
  - v0.1.0의 주요 기능, 검증 결과, 알려진 제한이 정리된다.
  - release/tag 생성 전 확인 checklist가 문서화된다.
  - package metadata와 README가 릴리스 기준으로 어긋나지 않는다.
- 영향 범위: `CHANGELOG.md`, `README.md`, docs.
- 검증: `.venv/bin/python -m pytest -q`, package metadata/docs review

## Pending

### 2. v0.1.0 tag 생성

- 작업: 검증 통과 후 `v0.1.0` git tag를 생성한다.
- 완료 기준:
  - 테스트와 smoke checks가 통과한다.
  - `git tag v0.1.0`이 생성된다.
  - 사용자가 원하면 tag push까지 진행할 수 있는 상태다.

### 3. Remote scan 품질 개선 계획

- 작업: release/tag freshness, archived/fork/private 상태, metadata evidence 정책을 다음 backlog로 설계한다.
- 완료 기준:
  - 점수화할 항목과 evidence-only 항목이 분리된다.
  - 다음 recursive loop story가 작게 쪼개진다.

## 다음 실행 순서

1. `v0.1.0 릴리스 준비`를 진행한다.
3. 검증 후 tag 생성 여부를 결정한다.
