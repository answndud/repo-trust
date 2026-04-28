# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.1.0 tag 생성

## 개발 상태 요약

v0.1.0 release notes와 pre-tag checklist를 추가했다. 이제 변경 사항을 커밋한 뒤 tag 생성 전 검증을 실행하고 `v0.1.0` tag를 만든다.

## Blocker

없음

## 최근 검증

v0.1.0 릴리스 준비 검증: `.venv/bin/python -m pytest -q`는 `50 passed`; local self-scan은 100/100, A, finding 0; remote self-scan은 100/100, A, finding 1(`remote.github_metadata_collected`)이었다.

## 다음 액션

1. `CHANGELOG.md`, README, 하네스 문서를 커밋한다.
2. tag 전 검증을 다시 실행한다.
3. `v0.1.0` tag를 생성한다.
4. tag 상태를 확인한다.
