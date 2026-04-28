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

오픈소스 공개 준비를 마친 뒤 GitHub에 push하고, post-v1 작업을 Ralph-style 반복 루프로 진행한다.

## 현재 우선순위

1. Post-v1 loop completion review를 수행한다.

## In Progress

### 1. Post-v1 loop completion review

- 작업: Remote GitHub scan MVP 전체 검증과 자체 리뷰를 수행한다.
- 배경: Remote scan CLI, client, metadata detection, scoring/report integration story가 끝났으므로 MVP 완성 여부를 판정한다.
- 완료 기준:
  - pytest, CLI smoke, self scan, fake remote scan이 통과한다.
  - 실제 GitHub remote scan smoke check를 가능한 범위에서 실행한다.
  - docs/README가 remote scan 사용법과 제한을 설명한다.
  - active 문서가 정리되고 완료 archive가 남는다.
- 영향 범위: docs, 필요 시 README 또는 tests.
- 검증: `.venv/bin/python -m pytest -q`, CLI smoke checks, remote smoke check

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. Remote GitHub scan MVP 전체 검증을 실행한다.
2. 자체 diff 리뷰를 수행한다.
3. 완료 판정 후 active 문서를 정리한다.
