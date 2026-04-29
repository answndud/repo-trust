# PLAN

앞으로 할 active 작업과 완성품까지의 순차 backlog를 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- `Pending`은 완성품까지의 순차 backlog로 유지한다. 새 작업을 시작할 때 맨 위 항목 하나만 `In Progress`로 승격한다.
- 각 작업에는 status, goal, scope, non-goals, acceptance criteria, verification commands, next action을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 목표

RepoTrust v0.2.0 PyPI publish를 안전하게 준비한다.

## 현재 우선순위

1. PyPI publish setup과 TestPyPI dry-run을 준비한다.

## In Progress

현재 active 작업 없음

## Pending

### PyPI publish setup과 TestPyPI dry-run

- Status: `Pending`
- Goal: PyPI upload 전에 build/publish toolchain과 credential path를 안전하게 준비하고 TestPyPI dry-run으로 검증한다.
- Scope: `build`/`twine` 사용 방식 결정, TestPyPI token 또는 trusted publishing 가능성 확인, `python -m build` artifact 생성, `twine check`, TestPyPI upload/install smoke 절차 문서화.
- Non-goals: 실제 PyPI production publish, 새 기능 추가.
- Acceptance criteria:
  - production PyPI publish 전에 필요한 credential/toolchain blocker가 문서화된다.
  - TestPyPI 또는 trusted publishing 중 하나의 검증 경로가 정해진다.
  - build artifacts와 metadata check가 통과한다.
- Verification commands:
  - `.venv/bin/python -m pip wheel --no-deps . --wheel-dir <tmp>`
  - `.venv/bin/python -m pip show repotrust`
  - `git status --short --branch`
- Next action: publish toolchain과 credential strategy를 정한다.

## 다음 실행 순서

1. `PyPI publish setup과 TestPyPI dry-run`을 `In Progress`로 승격한다.
2. production publish는 credential과 TestPyPI/trusted publishing 검증이 끝난 뒤 진행한다.
