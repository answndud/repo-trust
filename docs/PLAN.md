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

1. Remote GitHub scan MVP story 4: Remote scoring/report integration을 구현한다.
2. Remote GitHub scan MVP를 작은 작업 단위로 반복 구현한다.

## In Progress

### 1. Remote GitHub scan MVP story 4: Remote scoring/report integration

- 작업: remote detected data를 기존 rule/scoring/report contract에 연결한다.
- 배경: Remote scan이 `DetectedFiles`를 만들 수 있으므로 report와 score가 local scan처럼 신뢰 신호를 설명해야 한다.
- 완료 기준:
  - remote scan JSON/Markdown report가 기존 schema와 호환된다.
  - remote detected files가 README/security/hygiene/security posture rule에 반영된다.
  - remote-specific finding이 evidence와 recommendation을 포함한다.
  - fixture/fake remote smoke tests가 통과한다.
- 영향 범위: `src/repotrust/remote.py`, tests, docs.
- 검증: `.venv/bin/python -m pytest -q`, fake remote report tests

## Pending

### 2. Post-v1 loop completion review

- 작업: Remote GitHub scan MVP 전체 검증과 자체 리뷰를 수행한다.
- 완료 기준:
  - pytest, CLI smoke, self scan, fake remote scan이 통과한다.
  - docs/README가 remote scan 사용법과 제한을 설명한다.
  - active 문서가 정리되고 완료 archive가 남는다.

## 다음 실행 순서

1. `Remote GitHub scan MVP story 4`를 구현한다.
2. 완료 시 다음 story를 `In Progress`로 승격한다.
3. 각 story마다 구현, 테스트, 자체 diff 리뷰, local commit을 반복한다.
