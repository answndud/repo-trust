# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.2.2 README smoke release 정합화

## 개발 상태 요약

README만 따라 하는 신규 사용자 흐름을 검증하던 중, README/main은 개선된 첫 화면 문구를 보여주지만 README가 설치시키는 `v0.2.1` wheel은 이전 첫 화면 문구를 출력하는 불일치를 발견했다. README를 과거 문구로 되돌리기보다 이미 main에 반영된 설치 UX/CI 개선을 포함한 `v0.2.2` GitHub-only patch release로 정합성을 맞춘다.

## Blocker

현재 blocker 없음.

## 최근 검증

- `git status --short --branch`: `main...origin/main`, clean.
- Clean venv `v0.2.1` wheel README smoke: 설치, check, html/json 생성, `json.tool`, 세 entrypoint version은 성공했다.
- Smoke mismatch: 설치된 `v0.2.1` `repo-trust-kr` 첫 화면은 `사용 전 저장소 신뢰도를 분석합니다.`, README/main 예시는 `설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다.`로 다르다.

## 다음 액션

1. `pyproject.toml`, `src/repotrust/__init__.py`, tests, README, CHANGELOG를 `0.2.2`로 갱신한다.
2. 로컬 pytest/build/self-scan 검증을 실행한다.
3. commit/tag/release 후 clean venv `v0.2.2` README smoke를 재실행한다.
