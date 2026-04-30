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

README만 따라 하는 신규 사용자 경로가 GitHub-only 배포와 현재 CLI 동작에 맞도록 `v0.2.2` patch release를 준비한다.

## 현재 우선순위

1. README smoke에서 발견한 `v0.2.1` 배포본과 main 문구 불일치를 해소한다.
2. `v0.2.2` version metadata, README, changelog를 준비한다.
3. 새 release asset 설치 smoke로 README 경로를 재검증한다.

## In Progress

### v0.2.2 README smoke release 정합화

- Status: `In Progress`
- Goal: README가 안내하는 GitHub Release 설치 경로와 실제 설치되는 CLI 첫 화면/명령 동작을 일치시킨다.
- Scope: `0.2.2` version bump, changelog, README install URLs/version 예시, build artifact 검증, GitHub-only release publish, clean venv install smoke.
- Non-goals: PyPI/TestPyPI publish, 기능 변경, remote API 기본값 변경.
- Acceptance criteria:
  - README quickstart가 `v0.2.2` GitHub Release asset URL을 안내한다.
  - `repo-trust`, `repo-trust-kr`, `repotrust` version command가 `0.2.2`를 출력한다.
  - Clean venv에 `v0.2.2` wheel을 설치했을 때 `repo-trust-kr` 첫 화면이 README 예시와 핵심 문구가 일치한다.
  - README의 `check`, `html`, `json` 예시가 `v0.2.2` 설치 환경에서 성공한다.
  - JSON output은 `json.tool`로 검증된다.
  - GitHub Release `v0.2.2`가 wheel/source archive asset을 포함한다.
- Verification commands:
  - `.venv/bin/python -m pytest -q`
  - `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.2/dist`
  - `gh release view v0.2.2 --repo answndud/repo-trust --json name,tagName,body,url,assets`
  - `printf 'q\n' | <tmp>/.venv/bin/repo-trust-kr`
  - `<tmp>/.venv/bin/repo-trust-kr check https://github.com/openai/codex`
  - `<tmp>/.venv/bin/repo-trust html https://github.com/openai/codex --output <tmp>/codex.html`
  - `<tmp>/.venv/bin/repo-trust json https://github.com/openai/codex --output <tmp>/codex.json`
  - `<tmp>/.venv/bin/python -m json.tool <tmp>/codex.json`
- Next action: version metadata와 README/CHANGELOG를 `v0.2.2`로 갱신한다.

## Pending

현재 active 작업 없음

## 다음 실행 순서

1. v0.2.2 README smoke release 정합화를 완료한다.
