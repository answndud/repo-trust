# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

Remote GitHub scan MVP story 1: CLI/API boundary

## 개발 상태 요약

Ralph-style loop 규칙을 하네스에 반영했다. 다음 story는 remote scan의 CLI/API boundary다. 먼저 `--remote` 옵션과 validation/no-network 기본 동작을 고정하고, 실제 GitHub HTTP client 구현은 다음 story로 분리한다.

## Blocker

없음

## 최근 검증

`git push origin main` 성공: `0ea0bc4..f5852d0 main -> main`. Ralph 참고 자료에서는 PRD item을 작은 story로 쪼개고, 각 반복에서 하나의 story를 구현, 검사, 커밋, 진행 기록 갱신한 뒤 다음 story로 넘어가는 방식을 확인했다. Loop 문서 변경 후 `.venv/bin/python -m pytest -q`는 `37 passed`다.

## 다음 액션

1. `cli.py`에 `--remote` 옵션을 추가한다.
2. local path + `--remote` usage error를 구현한다.
3. GitHub URL parse-only 기본 동작을 유지하는 테스트를 보강한다.
4. GitHub URL + `--remote`가 remote scanner boundary로 들어가는 최소 구조를 추가한다.
