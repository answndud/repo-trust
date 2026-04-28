# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

Remote GitHub scan MVP story 2: GitHub client and failure findings

## 개발 상태 요약

Remote CLI/API boundary story를 완료했다. 이제 GitHub REST client abstraction과 실패 응답을 finding으로 변환하는 동작을 구현한다. 실제 metadata detection은 다음 story로 분리하고, 이번 story는 fake transport 기반 실패 모드 테스트에 집중한다.

## Blocker

없음

## 최근 검증

Remote boundary story 검증: `.venv/bin/python -m pytest -q`는 `40 passed`; GitHub URL parse-only JSON smoke check는 `target.github_not_fetched`; GitHub URL + `--remote` smoke check는 `remote.github_not_implemented`; local path + `--remote`는 exit code 2로 실패했다.

## 다음 액션

1. fake transport가 가능한 GitHub client 경계를 설계한다.
2. repository metadata 요청 실패를 finding으로 변환한다.
3. unauthorized/not-found/rate-limited/api-error 테스트를 추가한다.
4. token 값이 report/finding에 노출되지 않는 테스트를 추가한다.
