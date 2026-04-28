# RepoTrust 에이전트 가이드

RepoTrust는 오픈소스 저장소를 설치해도 되는지, AI agent에게 맡겨도 되는지, 회사/개인 프로젝트의 dependency로 넣어도 되는지 판단하기 위한 Python CLI 리포트 도구다. v1은 작게 유지한다: 로컬 저장소 스캔, GitHub URL 파싱, Markdown/JSON/static HTML 리포트.

## 문서 맵

- `docs/prd.md`: 제품 목적, 사용자, v1 범위, 성공 기준.
- `docs/trd.md`: 기술 구조, 데이터 흐름, 확장 경계, 구현 원칙.
- `docs/adr.md`: 지금까지의 주요 결정과 보류한 선택지.
- `docs/PLAN.md`: 앞으로 할 active 작업과 우선순위.
- `docs/PROGRESS.md`: 현재 진행 상태, blocker, 최근 검증, 다음 액션.
- `docs/COMPLETED.md`: 완료된 작업 archive. 기본 필수 읽기 문서는 아니다.
- `docs/architecture.md`: 현재 패키지 구조와 모듈 책임.
- `docs/development-workflow.md`: 개발 환경, 작업 순서, 코딩 규칙.
- `docs/testing-and-validation.md`: 검증 명령과 테스트 기준.
- `docs/domain-context.md`: 신뢰 평가 도메인과 점수 해석.

## 작업 상태 문서

- 새 세션이나 새 에이전트는 작업 전 `docs/PLAN.md`, `docs/PROGRESS.md`를 먼저 확인한다.
- `docs/COMPLETED.md`는 archive이며 세션 시작 필수 읽기 문서가 아니다.
- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 `docs/PLAN.md`에 반영한다.
- 의미 있는 구현, 수정, 검증을 진행하며 동시에 `docs/PROGRESS.md`에 현재 상태, blocker, 검증 결과, 다음 액션을 갱신한다.
- 작업 완료 시 `docs/PROGRESS.md` 내용을 정리해 `docs/COMPLETED.md`에 append하고, active 문서에서는 완료된 내용을 제거한다.
- `docs/COMPLETED.md`는 append-only, 시간 오름차순, 연속 번호 규칙을 유지한다.
- 모든 active 작업이 끝나면 `docs/PLAN.md`, `docs/PROGRESS.md`의 상태는 `현재 active 작업 없음`으로 둔다.
- 작업을 마친 최종 응답에는 다음에 진행할 작업을 짧게 명시한다.
- 사용자가 요청하지 않으면 매 작업마다 원격 push하지 않는다.
- 코드와 문서가 어긋나면 같은 작업 안에서 함께 수정한다.

## 작업 원칙

- 이 파일은 진입점이다. 긴 설명과 배경은 `docs/`에 둔다.
- v1은 네트워크 없이 결정적인 offline check를 우선한다.
- 모든 주요 감점은 stable finding ID, evidence, recommendation으로 설명 가능해야 한다.
- JSON 출력은 기계가 읽는 인터페이스로 취급하고, 깨뜨릴 때는 의도적으로 변경한다.
- 리포트 본문 stdout과 터미널 상태 stderr를 분리한다.
- 동작을 바꾸면 테스트를 추가하거나 수정한다.

## 검증 원칙

작업을 넘기기 전 기본 검증:

```bash
.venv/bin/python -m pytest -q
```

환경이 없다면:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

## 금지사항

- v1에서 GitHub URL을 clone하거나 GitHub API를 호출하지 않는다.
- 반복 작업이나 외부 도구 필요가 명확하지 않으면 skills, MCP, subagents, hooks, Codex rules를 추가하지 않는다.
- 로컬에서 확인할 수 없는 취약점, contributor 신뢰도, release 상태를 사실처럼 점수화하지 않는다.
- report renderer 안에 scanning/scoring 로직을 넣지 않는다. renderer는 `ScanResult`만 렌더링한다.
