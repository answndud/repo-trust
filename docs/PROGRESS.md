# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

PyPI production publish

## 개발 상태 요약

PyPI publish setup story는 완료됐다. `build`/`twine`을 dev release toolchain에 추가했고, lockfile과 release validation docs를 갱신했으며 local build, `twine check`, clean wheel install smoke, pytest가 통과했다.

## Blocker

TestPyPI/PyPI upload는 remote write이며 credential 또는 GitHub trusted publishing 설정이 필요하다. 현재 환경에는 token/trusted publishing 설정이 확인되지 않아 실제 upload를 실행하지 않는다.

## 최근 검증

- `.venv/bin/python -m pip install -e '.[dev]'`: 통과, `build==1.4.4`, `twine==6.2.0` 설치.
- `.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml`: 통과.
- `.venv/bin/python -m build --outdir <tmp>/dist`: 통과, `repotrust-0.2.0.tar.gz`, `repotrust-0.2.0-py3-none-any.whl` 생성.
- `.venv/bin/python -m twine check <tmp>/dist/*`: 통과, wheel과 sdist 모두 `PASSED`.
- clean venv wheel install smoke: 통과, `repo-trust`, `repo-trust-kr`, `repotrust` 모두 `0.2.0` 출력, fixture JSON `json.tool` 통과.
- `.venv/bin/python -m pytest -q`: `120 passed`.
- `git diff --check`: 통과.
- `git diff --stat`: release tooling/docs/lockfile 변경 범위 확인.

## 다음 액션

1. TestPyPI/PyPI API token을 환경 변수나 `.pypirc`에 설정하거나 GitHub trusted publishing을 구성한다.
2. 설정 후 `docs/testing-and-validation.md`의 PyPI/TestPyPI Release Validation 절차를 실행한다.
3. TestPyPI install smoke가 통과하면 production PyPI upload를 진행한다.
