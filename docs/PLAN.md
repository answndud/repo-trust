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

RepoTrust v1 CLI를 실제 사용 가능한 로컬 신뢰 리포트 도구로 다듬고, 이후 remote scan과 정책 설정으로 확장할 기반을 만든다.

## 현재 우선순위

1. 릴리스 전 품질 점검으로 CLI v1 완성 여부를 판정한다.

## In Progress

### 1. 릴리스 전 품질 점검

- 작업: CLI v1 완성 판정 전 테스트, fixture smoke check, 자체 스캔, 문서 정합성, git 상태를 점검한다.
- 배경: v1 완성 선언 전 자동화/문서/리포트 계약이 맞는지 확인해야 한다.
- 완료 기준:
  - pytest가 통과한다.
  - fixture Markdown/JSON/HTML smoke check가 통과한다.
  - 자체 `repotrust scan .` 결과와 남은 정책성 finding이 기록된다.
  - `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`가 운영 규칙과 맞다.
- 영향 범위: `docs/`, 필요 시 `README.md`.
- 검증: `.venv/bin/python -m pytest -q`, fixture smoke checks, 자체 scan.

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. `릴리스 전 품질 점검`부터 시작한다.
2. 작업 시작 시 `docs/PROGRESS.md`에 현재 작업, 목표, 예상 영향 범위를 기록한다.
3. 구현과 테스트가 끝나면 검증 결과를 `docs/PROGRESS.md`에 남긴다.
4. 완료 시 `docs/COMPLETED.md`에 다음 번호로 archive하고 active 문서에서 완료 항목을 제거한다.
