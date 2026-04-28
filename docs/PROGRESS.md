# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

Remote GitHub scan MVP story 4: Remote scoring/report integration

## 개발 상태 요약

Remote metadata detection story를 완료했다. 이제 remote detected files를 기존 rule/scoring/report contract에 연결해 remote scan 결과가 local scan처럼 trust score와 findings를 설명하도록 만든다.

## Blocker

없음

## 최근 검증

Remote metadata detection story 검증: `.venv/bin/python -m pytest -q`는 `48 passed`. Fake transport tests로 root contents에서 README/LICENSE/SECURITY/manifest/lockfile을 탐지하고 workflows response에서 CI workflow를 탐지함을 확인했다. contents/workflows partial failure는 `remote.github_partial_scan` finding으로 표현된다.

## 다음 액션

1. remote detected files를 local-like rules에 연결할 범위를 정한다.
2. remote README content 없이 수행 가능한 security/project hygiene scoring을 먼저 연결한다.
3. remote report JSON/Markdown tests를 추가한다.
4. remote-specific finding과 local finding이 함께 렌더링되는지 확인한다.
