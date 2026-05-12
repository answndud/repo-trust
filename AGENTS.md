# RepoTrust 에이전트 가이드

RepoTrust는 오픈소스 저장소를 설치해도 되는지, AI agent에게 맡겨도 되는지, 회사/개인 프로젝트의 dependency로 넣어도 되는지 판단하기 위한 Python CLI 리포트 도구다. v1은 작게 유지한다: 로컬 저장소 스캔, GitHub URL 파싱, Markdown/JSON/static HTML 리포트.

## 문서 맵

`docs/`는 로컬 작업 상태와 상세 설계 메모를 두는 ignored 폴더다. 로컬에 있을 때만 참고하고, clean checkout에는 없을 수 있다.

- `docs/PLAN.md`: active roadmap과 다음 작업 후보.
- `docs/PROGRESS.md`: 현재 resumable state. active 작업이 없으면 짧게 비워둔다.
- `docs/COMPLETED.md`: 완료된 작업 archive. 기본 필수 읽기 문서는 아니다.

## 작업 상태 문서

- 새 세션은 로컬에 있을 때만 `docs/PLAN.md`와 `docs/PROGRESS.md`를 읽는다.
- `docs/COMPLETED.md`는 완료 archive이며, 로컬에 있고 과거 맥락이 필요할 때만 읽는다.
- 범위, 우선순위, 신규 작업은 `docs/PLAN.md`에 기록한다.
- 진행 상태, 변경 파일, 검증 결과, blocker, 다음 액션은 `docs/PROGRESS.md`에 기록한다.
- 완료된 작업은 `docs/COMPLETED.md`에 append한 뒤 active 문서에서 제거한다.
- active 작업이 없으면 `PLAN.md`와 `PROGRESS.md`는 `현재 active 작업 없음`만 명확히 표시한다.
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
