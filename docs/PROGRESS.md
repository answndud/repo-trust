# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

Post-v1 loop completion review

## 개발 상태 요약

Remote scoring/report integration story를 완료했다. 이제 Remote GitHub scan MVP 전체 검증, smoke check, 문서 정합성, diff 리뷰를 수행하고 완료 여부를 판정한다.

## Blocker

없음

## 최근 검증

Remote scoring/report integration story 검증: `.venv/bin/python -m pytest -q`는 `50 passed`. Fake remote report test에서 JSON schema version, github target, detected README, Markdown report section을 확인했다. Risky README fixture는 remote README content 기반으로 `install.risky.shell_pipe_install` finding을 만든다.

## 다음 액션

1. 전체 pytest와 CLI smoke checks를 실행한다.
2. 실제 GitHub remote scan smoke check를 실행한다.
3. README/docs 정합성과 git diff를 리뷰한다.
4. 완료 archive를 남기고 active 문서를 정리한다.
