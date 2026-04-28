# PLAN

앞으로 할 active 작업만 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- 각 작업에는 완료 기준을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

RepoTrust 자체 스캔에서 남은 정책성 finding을 줄일지 결정한다.

## 현재 우선순위

1. LICENSE와 lockfile 도입 여부를 결정한다.

## In Progress

현재 active 작업 없음

## Pending

### 1. LICENSE와 lockfile 정책 결정

- 작업: RepoTrust 저장소에 LICENSE와 lockfile을 추가할지 결정한다.
- 배경: 자체 스캔은 92점이며 남은 finding은 `hygiene.no_license`, `security.no_lockfile`이다.
- 완료 기준:
  - LICENSE를 추가할 경우 라이선스 종류와 copyright holder가 명확하다.
  - lockfile을 추가할 경우 사용할 도구(`uv`, `pip-tools`, Poetry 등)가 명확하다.
  - 결정 결과가 README 또는 docs에 필요한 만큼 반영된다.
- 영향 범위: `LICENSE` 또는 lockfile, 필요 시 `README.md`, `docs/PLAN.md`, `docs/COMPLETED.md`.
- 검증: `.venv/bin/python -m pytest -q`, `.venv/bin/repotrust scan . --format json`

## 다음 실행 순서

1. LICENSE와 lockfile 도입 여부를 결정한다.
2. 결정된 범위만 구현한다.
3. 테스트와 자체 스캔을 실행한다.
4. 완료 시 `docs/COMPLETED.md`에 archive하고 active 문서를 정리한다.

