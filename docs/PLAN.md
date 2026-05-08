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

v0.2.9 publish

## 현재 우선순위

1. Local `main`의 v0.2.9 commits를 origin에 push한다.
2. GitHub Actions `ci` 통과를 확인한다.
3. Annotated tag `v0.2.9`와 GitHub Release를 만들고 wheel/sdist asset을 업로드한다.
4. Release URL clean install smoke를 수행한다.

## In Progress

- status: in_progress
- goal: v0.2.9 publish
- scope:
  - local `main`의 v0.2.9 commits를 origin에 push한다.
  - GitHub Actions `ci` 통과를 확인한다.
  - annotated tag `v0.2.9`와 GitHub Release를 만들고 wheel/sdist asset을 업로드한다.
  - GitHub Release wheel URL clean install smoke를 수행한다.
- non-goals:
  - PyPI/TestPyPI 배포는 하지 않는다.
  - v0.2.9 기능 변경은 하지 않는다.
- acceptance criteria:
  - origin/main이 local main commit을 포함한다.
  - GitHub Actions `ci`가 성공한다.
  - `gh release view v0.2.9`에서 draft false, prerelease false, wheel/sdist asset을 확인한다.
  - GitHub Release wheel URL로 clean install한 `repo-trust`, `repo-trust-kr`, `repotrust`가 version `0.2.9`를 출력한다.
- verification commands:
  - `git push origin main`
  - `gh run watch <run-id> --repo answndud/repo-trust --exit-status`
  - `gh release view v0.2.9 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`
- next action: `main` push 후 GitHub Actions `ci` run을 확인한다.

## Pending

현재 pending 작업 없음.

## 다음 실행 순서

1. `main` push와 GitHub Actions 확인.
2. Tag/release/asset upload.
3. Release URL clean install smoke.
4. Archive와 publish 기록 commit/push.
