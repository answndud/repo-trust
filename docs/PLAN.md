# PLAN

앞으로 할 active 작업만 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- 각 작업에는 완료 기준을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

RepoTrust v1 CLI를 "로컬 저장소 신뢰 리포트 도구"로 안정화한다. 다음 개발은 리포트 신뢰성과 CLI 사용성을 순서대로 개선한다.

## 현재 우선순위

1. JSON report를 이후 CI/외부 도구가 사용할 수 있도록 안정적인 contract로 다듬는다.
2. 샘플 저장소 fixture와 리포트 예시를 추가해 회귀 테스트와 문서 이해도를 높인다.

## In Progress

현재 active 작업 없음

## Pending

### 1. JSON report contract 정리

- 작업: JSON report를 CI와 외부 도구가 안정적으로 사용할 수 있는 형태로 문서화한다.
- 배경: RepoTrust Score와 finding은 이후 자동화에서 사용할 가능성이 높다.
- 완료 기준:
  - JSON 최상위 key와 finding/score 구조가 문서화된다.
  - snapshot 성격의 테스트가 강화된다.
  - stdout에 valid JSON만 출력되는 CLI 테스트가 보강된다.
- 영향 범위: `src/repotrust/reports.py`, `tests/test_cli.py`, `tests/test_scanner.py`, 필요 시 `docs/trd.md`.
- 검증: `.venv/bin/python -m pytest -q`

### 2. 샘플 fixture와 예시 리포트 추가

- 작업: small fixture repo를 만들어 좋은/나쁜 신뢰 신호를 빠르게 확인할 수 있게 한다.
- 배경: 개발을 오래 쉬었다가 돌아왔을 때 rule 의도를 샘플로 확인하기 쉽다.
- 완료 기준:
  - fixture 또는 테스트 helper로 good/bad repo 사례가 정리된다.
  - Markdown/JSON report 예시 생성 방법이 문서화된다.
  - fixture가 실제 테스트에 사용된다.
- 영향 범위: `tests/`, `docs/testing-and-validation.md`, 필요 시 `README.md`.
- 검증: `.venv/bin/python -m pytest -q`

## 다음 실행 순서

1. `JSON report contract 정리`부터 시작한다.
2. 작업 시작 시 `docs/PROGRESS.md`에 현재 작업, 목표, 예상 영향 범위를 기록한다.
3. 구현과 테스트가 끝나면 검증 결과를 `docs/PROGRESS.md`에 남긴다.
4. 완료 시 `docs/COMPLETED.md`에 다음 번호로 archive하고 active 문서에서 완료 항목을 제거한다.
