# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.2.1 release commit/tag/publish

## 개발 상태 요약

v0.2.1 release metadata 준비가 완료됐다. `pyproject.toml`, `src/repotrust/__init__.py`, version tests는 `0.2.1`로 일치하고, `CHANGELOG.md`는 `v0.2.1 - 2026-04-30` heading을 갖는다. README는 GitHub Release source archive 기반 설치와 PyPI 제외 방향을 설명한다.

## Blocker

현재 blocker 없음. PyPI/TestPyPI publish는 명시적 non-goal이다.

## 최근 검증

- `.venv/bin/python -m pytest tests/test_cli.py -q`: `59 passed`.
- `.venv/bin/python -m pytest -q`: `124 passed`.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release/dist`: `repotrust-0.2.1.tar.gz`, `repotrust-0.2.1-py3-none-any.whl` 생성.
- `.venv/bin/repo-trust --version`: `repo-trust 0.2.1`.
- `.venv/bin/repo-trust-kr --version`: `repo-trust-kr 0.2.1`.
- `.venv/bin/repotrust --version`: `repotrust 0.2.1`.
- `.venv/bin/repo-trust json . --output /tmp/repotrust-self-021.json`: score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음.
- `git diff --check`: 통과.

## 다음 액션

1. release metadata 변경과 archive 상태 문서를 commit한다.
2. `main`을 원격에 push한다.
3. `v0.2.1` annotated tag와 GitHub Release를 생성한다.
