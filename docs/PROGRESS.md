# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

README Quality rule 고도화

## 개발 상태 요약

작업 시작. 현재 README rule은 파일 존재, 최소 길이, install section, usage section, maintenance signal 중심이다. 이번 작업에서는 README가 프로젝트의 목적/가치/무엇을 하는지 설명하는지 확인하는 목적 설명 신호를 추가하고, 좋은/부족한 README 테스트와 도메인 문서를 함께 보강한다.

## Blocker

없음

## 최근 검증

작업 시작 전 기존 테스트는 직전 세션에서 `.venv/bin/python -m pytest -q` 기준 `17 passed` 상태였다.

## 다음 액션

1. README 목적 설명 신호를 rule로 추가한다.
2. 좋은 README와 목적 설명이 부족한 README 테스트를 보강한다.
3. `docs/domain-context.md`에 README Quality finding 기준을 문서화한다.
4. 전체 테스트를 실행하고 결과를 기록한다.
