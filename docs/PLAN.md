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

1. Remote GitHub scan MVP story 1: CLI/API boundary를 구현한다.
2. Remote GitHub scan MVP를 작은 작업 단위로 반복 구현한다.

## In Progress

### 1. Remote GitHub scan MVP story 1: CLI/API boundary

- 작업: `--remote` CLI option, target validation, scanner boundary를 추가하되 실제 HTTP 구현은 아직 fake client 기반으로 분리한다.
- 배경: Remote scan 전체 구현 전에 CLI contract와 no-network 기본값을 안정적으로 고정한다.
- 완료 기준:
  - local path에서 `--remote` 사용 시 usage error가 난다.
  - GitHub URL without `--remote`는 기존 parse-only 동작을 유지한다.
  - GitHub URL with `--remote`는 remote scanner 진입점으로 분기한다.
  - tests가 CLI 동작과 no-network 기본값을 고정한다.
- 영향 범위: `src/repotrust/cli.py`, `src/repotrust/scanner.py`, `tests/test_cli.py`, docs.
- 검증: `.venv/bin/python -m pytest -q`, GitHub URL parse-only JSON smoke check

## Pending

### 2. Remote GitHub scan MVP story 2: GitHub client and failure findings

- 작업: GitHub REST read-only client와 실패 finding 변환을 구현한다.
- 완료 기준:
  - HTTP transport는 테스트에서 fake로 대체 가능하다.
  - unauthorized/not-found/rate-limited/api-error finding이 생성된다.
  - token 값은 출력되지 않는다.

### 3. Remote GitHub scan MVP story 3: Remote metadata detection

- 작업: repository metadata, root contents, README, workflow 목록을 remote detected files로 변환한다.
- 완료 기준:
  - README/LICENSE/SECURITY/manifests/lockfiles/workflows를 remote response에서 탐지한다.
  - API partial failure는 file absence와 구분된다.
  - tests는 실제 네트워크를 사용하지 않는다.

### 4. Remote GitHub scan MVP story 4: Remote scoring/report integration

- 작업: remote detected data를 기존 rule/scoring/report contract에 연결한다.
- 완료 기준:
  - remote scan JSON/Markdown report가 기존 schema와 호환된다.
  - remote-specific finding이 evidence와 recommendation을 포함한다.
  - fixture/fake remote smoke tests가 통과한다.

### 5. Post-v1 loop completion review

- 작업: Remote GitHub scan MVP 전체 검증과 자체 리뷰를 수행한다.
- 완료 기준:
  - pytest, CLI smoke, self scan, fake remote scan이 통과한다.
  - docs/README가 remote scan 사용법과 제한을 설명한다.
  - active 문서가 정리되고 완료 archive가 남는다.

## 다음 실행 순서

1. `Remote GitHub scan MVP story 1`을 구현한다.
2. 완료 시 다음 story를 `In Progress`로 승격한다.
3. 각 story마다 구현, 테스트, 자체 diff 리뷰, local commit을 반복한다.
