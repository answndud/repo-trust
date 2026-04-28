# COMPLETED

완료된 작업을 시간 오름차순으로 축적하는 append-only archive다. 새 세션 시작 시 필수로 읽지 않는다.

## 운영 규칙

- 완료 항목은 문서 맨 아래에 append한다.
- 번호는 `001`, `002`, `003`처럼 연속 번호를 사용하고 재사용하지 않는다.
- 오래된 작업이 위, 최신 작업이 아래에 오도록 유지한다.
- `docs/PLAN.md`, `docs/PROGRESS.md`에서 제거한 완료 기록을 복기 가능한 수준으로 정리한다.
- 명백한 오타 수정 외에는 기존 완료 항목의 의미를 바꾸지 않는다.

## 항목 포맷

```md
## 001: 작업 제목

- 완료일: YYYY-MM-DD
- 배경:
- 변경 내용:
- 코드/문서:
- 검증:
- 결과:
```

## Archive

## 001: Codex 작업 상태 하네스 추가

- 완료일: 2026-04-28
- 배경: 프로젝트를 오래 쉬었다가 다시 시작하거나 Codex 세션이 중간에 끊겨도, 다음 세션이 바로 이어서 개발할 수 있는 active/archive 문서 체계가 필요했다. 기존 PRD/TRD/ADR은 제품과 기술 맥락을 설명하지만, 현재 진행 중인 작업 상태와 완료 archive를 분리해서 운영하는 문서는 없었다.
- 변경 내용: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 추가했다. `PLAN.md`는 앞으로 할 active 작업과 우선순위, `PROGRESS.md`는 현재 진행 상태와 blocker/검증/다음 액션, `COMPLETED.md`는 완료된 작업의 append-only archive로 역할을 분리했다. `AGENTS.md`에는 새 세션이 `PLAN.md`와 `PROGRESS.md`를 먼저 확인하고, 완료 작업은 `COMPLETED.md`로 옮기는 운영 규칙을 추가했다.
- 코드/문서: 코드 변경은 없었다. 문서 변경은 `AGENTS.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`에 적용했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `17 passed`를 확인했다. 추가로 새 문서 파일 목록과 line count를 확인해 `AGENTS.md`가 짧은 진입점 역할을 유지하는지 점검했다.
- 결과: Codex가 작업 전 active plan과 progress를 확인하고, 완료된 작업은 archive로 분리할 수 있는 최소 하네스가 생겼다. `COMPLETED.md`는 세션 시작 필수 읽기 문서가 아니므로 archive가 커져도 기본 context 부담을 줄일 수 있다.

## 002: README Quality rule 고도화

- 완료일: 2026-04-28
- 배경: 기존 README Quality rule은 README 존재, 최소 길이, 설치 섹션, 사용 섹션, 유지보수 신호를 중심으로 평가했다. 하지만 README가 프로젝트의 목적과 사용 맥락을 설명하지 않아도 섹션만 있으면 품질이 높게 평가될 수 있었다.
- 변경 내용: README 본문에 프로젝트 목적을 설명하는 실질적인 prose 문단이 있는지 확인하는 `readme.no_project_purpose` finding을 추가했다. 코드 블록, 헤더, 목록, admonition, table line은 목적 설명 후보에서 제외하고, 충분한 길이와 단어 수를 가진 일반 문장을 신호로 본다. 좋은 README fixture는 readme finding 없이 통과하고, 목적 설명이 부족한 README fixture는 새 finding을 내도록 테스트를 보강했다.
- 코드/문서: `src/repotrust/rules.py`에 목적 설명 heuristic과 finding을 추가했다. `tests/test_scanner.py`에 `GOOD_README` fixture와 `_write_trusted_repo` helper를 추가하고 목적 설명 누락 테스트를 추가했다. `docs/domain-context.md`에는 README Quality가 보는 신호 목록을 문서화했다. `AGENTS.md`에는 작업 완료 후 다음 진행 작업을 최종 응답에 짧게 알리는 규칙을 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `18 passed`를 확인했다.
- 결과: README Quality가 섹션 존재뿐 아니라 프로젝트가 무엇을 하는지 설명하는 기본 신뢰 신호까지 확인하게 됐다. 현재 active 작업은 없으며, 다음 작업은 `Install Safety 위험 패턴 확장`이다.
