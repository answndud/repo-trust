# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

Remote GitHub scan MVP story 3: Remote metadata detection

## 개발 상태 요약

GitHub client와 실패 finding story를 완료했다. 이제 repository metadata, contents, workflow response를 `DetectedFiles`로 변환한다. partial failure는 file absence와 구분하는 finding으로 표현한다.

## Blocker

없음

## 최근 검증

Remote client/failure story 검증: `.venv/bin/python -m pytest -q`는 `45 passed`. Fake transport tests로 repository success, unauthorized, not found, rate limited, API error, token non-leak를 확인했다.

## 다음 액션

1. contents API response fixture를 fake transport에 추가한다.
2. README/LICENSE/SECURITY/manifests/lockfiles를 remote root contents에서 탐지한다.
3. workflows API response를 `ci_workflows`로 변환한다.
4. partial failure finding을 추가한다.
