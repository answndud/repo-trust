# PLAN

앞으로 할 active 작업과 완성품까지의 순차 backlog를 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- credential, production publish, 보안/권한 결정처럼 진행 불가한 항목은 `In Progress` 아래에 두고 status를 `Blocked`로 표시한다.
- `Pending`은 완성품까지의 순차 backlog로 유지한다. 새 작업을 시작할 때 맨 위 항목 하나만 `In Progress`로 승격한다.
- 각 작업에는 status, goal, scope, non-goals, acceptance criteria, verification commands, next action을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

RepoTrust runtime은 secret key나 API 연결 없이 기본 동작한다. PyPI production publish는 credential/trusted publishing 설정 전까지 보류한다.

## 현재 우선순위

1. PyPI/TestPyPI credential 또는 trusted publishing 설정 후 remote upload를 수행한다.

## In Progress

현재 active 작업 없음

## Pending

### PyPI production publish

- Status: `Blocked`
- Goal: TestPyPI 검증 후 RepoTrust v0.2.0 artifact를 production PyPI에 publish한다.
- Scope: TestPyPI 또는 trusted publishing credential 설정 확인, release artifact 재생성, `twine check`, TestPyPI upload/install smoke, production PyPI upload, post-publish install smoke.
- Non-goals: 새 기능 추가, version bump, release note 재작성.
- Acceptance criteria:
  - TestPyPI 또는 trusted publishing 기반 remote upload가 성공한다.
  - TestPyPI 설치 smoke가 통과한다.
  - Production PyPI upload 후 isolated install smoke가 통과한다.
- Verification commands:
  - `.venv/bin/python -m build --outdir <tmp>/dist`
  - `.venv/bin/python -m twine check <tmp>/dist/*`
  - `.venv/bin/python -m twine upload --repository testpypi <tmp>/dist/*`
  - `python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ repotrust==0.2.0`
  - `.venv/bin/python -m twine upload <tmp>/dist/*`
  - `python -m pip install repotrust==0.2.0`
  - `git status --short --branch`
- Next action: TestPyPI/PyPI API token을 제공하거나 GitHub trusted publishing을 설정한다.

## 다음 실행 순서

1. TestPyPI/PyPI credential 또는 trusted publishing 설정을 완료한다.
2. local artifact validation을 다시 실행한다.
3. TestPyPI upload/install smoke 후 production PyPI upload를 진행한다.
