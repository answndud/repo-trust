# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.2.8 publish.

## 개발 상태 요약

v0.2.8 release candidate commit `b100aa3`를 origin/main에 push했다. GitHub Actions run `25477613123`이 `tests/test_cli.py::test_direct_cli_samples_writes_good_and_risky_gallery`에서 실패했으며, 원인은 Rich가 긴 sample report 경로를 터미널 폭에 맞춰 줄바꿈하면서 파일명 substring assertion이 깨진 것이다. 출력 의미와 파일 생성 검증은 유지하고, 줄바꿈에 흔들리지 않도록 assertion을 안정화했다.

## Blocker

현재 blocker 없음.

## 최근 검증

- 시작 전 확인: local `main` ahead 4, `v0.2.8` local tag 없음, GitHub Release `v0.2.8` 없음.
- `git push origin main`: succeeded, `0cedcaa..b100aa3 main -> main`.
- `gh run watch 25477613123 --repo answndud/repo-trust --exit-status`: failed in sample gallery output assertion.
- `.venv/bin/python -m pytest tests/test_cli.py::test_direct_cli_samples_writes_good_and_risky_gallery -q`: passed, 1 test.

## 다음 액션

전체 테스트를 다시 실행한 뒤 CI 안정화 commit을 push하고 GitHub Actions `ci`를 재확인한다.
