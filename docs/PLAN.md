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

1. 리포트 결과를 CI/자동화에서 쓰기 좋게 만든다.
2. remote GitHub scan은 명시적 옵션으로 설계한 뒤 구현한다.

## In Progress

현재 active 작업 없음

## Pending

### 1. 설정 파일 v1 설계

- 작업: 사용자/조직이 threshold나 category weight를 조정할 수 있는 config 파일을 설계한다.
- 배경: 회사/개인 프로젝트마다 허용 가능한 risk 기준이 다를 수 있다.
- 완료 기준:
  - config 파일명과 위치 후보가 결정된다.
  - v1에서 지원할 최소 설정 항목이 문서화된다.
  - 구현 전 ADR 또는 TRD에 설계가 남는다.
- 영향 범위: `docs/trd.md`, `docs/adr.md`, 필요 시 `docs/prd.md`.
- 검증: 문서 변경 후 `.venv/bin/python -m pytest -q`

### 2. Remote GitHub scan 설계

- 작업: `--remote` 또는 별도 command로 GitHub API 기반 scan을 추가할지 설계한다.
- 배경: PRD의 향후 확장 아이디어이며, clone 없이 URL만 파싱하는 현재 v1 이후의 자연스러운 확장이다.
- 완료 기준:
  - clone 금지 원칙과 API 사용 범위가 정리된다.
  - auth/rate limit/private repo 실패 모드가 finding으로 표현되는 설계가 나온다.
  - 구현 여부와 command/interface가 ADR에 기록된다.
- 영향 범위: `docs/prd.md`, `docs/trd.md`, `docs/adr.md`.
- 검증: 문서 변경 후 `.venv/bin/python -m pytest -q`

### 3. Remote GitHub scan MVP 구현

- 작업: 설계가 확정된 뒤 GitHub API 기반 remote metadata scan을 구현한다.
- 배경: 사용자가 local checkout 없이 GitHub URL만으로 기본 신뢰 신호를 확인할 수 있어야 한다.
- 완료 기준:
  - 명시적 opt-in으로만 네트워크를 사용한다.
  - README/LICENSE/SECURITY/CI/release metadata를 API로 확인한다.
  - API 실패와 미지원 상태가 finding으로 표현된다.
  - remote scan 테스트는 네트워크 없이 fixture/mocking으로 검증된다.
- 영향 범위: `src/repotrust/`, `tests/`, `docs/trd.md`, `docs/testing-and-validation.md`.
- 검증: `.venv/bin/python -m pytest -q`

## 다음 실행 순서

1. `설정 파일 v1 설계`부터 시작한다.
2. 작업 시작 시 `docs/PROGRESS.md`에 현재 작업, 목표, 예상 영향 범위를 기록한다.
3. 구현과 테스트가 끝나면 검증 결과를 `docs/PROGRESS.md`에 남긴다.
4. 완료 시 `docs/COMPLETED.md`에 다음 번호로 archive하고 active 문서에서 완료 항목을 제거한다.

