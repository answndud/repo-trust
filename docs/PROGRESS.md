# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.2.9 publish.

## 개발 상태 요약

v0.2.9 release candidate commit `36b2c97`까지 local `main`에 준비되어 있고, `main...origin/main [ahead 3]` 상태다. v0.2.9 local tag와 GitHub Release는 아직 없다.

## Blocker

현재 blocker 없음.

## 최근 검증

시작 전 확인: local `main` ahead 3, `v0.2.9` local tag 없음, GitHub Release `v0.2.9` 없음.

## 다음 액션

`main`을 origin에 push하고 GitHub Actions `ci` run을 확인한다.
