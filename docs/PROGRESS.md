# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.1.0 릴리스 준비

## 개발 상태 요약

Remote scan UX 문서화를 완료했다. 이제 v0.1.0 release notes, 변경 요약, 알려진 제한, tag 전 checklist를 추가한다.

## Blocker

없음

## 최근 검증

Remote scan UX 문서화 검증: `.venv/bin/python -m pytest -q`는 `50 passed`; 실제 remote smoke `https://github.com/answndud/repo-trust --remote`는 100/100, A, `remote.github_metadata_collected` finding을 반환했다.

## 다음 액션

1. `CHANGELOG.md`를 추가한다.
2. v0.1.0 release notes 초안을 작성한다.
3. known limitations와 pre-tag checklist를 문서화한다.
4. 테스트와 diff 리뷰를 실행한다.
