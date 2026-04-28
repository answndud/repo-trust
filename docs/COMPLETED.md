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

## 003: Install Safety 위험 패턴 확장

- 완료일: 2026-04-28
- 배경: 기존 Install Safety rule은 shell pipe install, `sudo`, global install, `chmod +x`를 탐지했지만, AI agent에게 설치를 맡길 때 문제가 될 수 있는 다른 실행 패턴을 충분히 다루지 못했다.
- 변경 내용: 위험 패턴 정의를 stable id, regex pattern, label, severity를 가진 구조로 바꿨다. 기존 `install.risky.shell_pipe_install` ID는 유지했고, `bash <(curl ...)` 형태의 process substitution shell execution, `python -c` inline execution, `pip install git+https://...` 직접 VCS install 탐지를 추가했다. 고위험 원격 실행은 high severity, 직접 VCS install과 global/chmod 계열은 medium severity로 정리했다.
- 코드/문서: `src/repotrust/rules.py`의 `RISKY_INSTALL_PATTERNS`를 구조화하고 새 패턴을 추가했다. `tests/test_scanner.py`에는 process substitution, Python inline execution, direct VCS install 테스트를 추가해 severity와 evidence line을 고정했다. `docs/domain-context.md`에는 Install Safety signal과 severity 기준을 문서화했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `21 passed`를 확인했다.
- 결과: README install instruction에서 agent가 실행하기 전에 검토해야 할 원격 실행/직접 설치 패턴을 더 잘 포착하게 됐다. 현재 active 작업은 없으며, 다음 작업은 `JSON report contract 정리`다.

## 004: JSON report contract 정리

- 완료일: 2026-04-28
- 배경: JSON report는 이후 CI나 외부 도구가 사용할 가능성이 높지만, 기존 테스트는 최상위 key 일부만 확인했고 schema version이 없었다. 또한 CLI JSON stdout이 Rich Console wrapping에 의해 깨질 수 있는 위험이 있었다.
- 변경 내용: JSON 최상위 contract에 `schema_version: "1.0"`을 추가했다. JSON shape 테스트를 강화해 최상위 key, target key, detected_files key, score key, finding key를 고정했다. CLI JSON 테스트는 stdout을 실제 JSON으로 파싱하도록 바꿨다. 이 과정에서 Rich Console이 긴 JSON string을 줄바꿈해 stdout JSON을 깨뜨리는 문제를 발견했고, report 본문 출력은 `sys.stdout.write()`를 사용하도록 수정했다.
- 코드/문서: `src/repotrust/models.py`에 `JSON_SCHEMA_VERSION`을 추가하고 `ScanResult.to_dict()`에 포함했다. `src/repotrust/cli.py`는 report stdout을 plain write로 출력하도록 수정했다. `tests/test_scanner.py`와 `tests/test_cli.py`는 JSON contract와 stdout valid JSON을 검증하도록 보강했다. `docs/trd.md`에는 JSON Report Contract 섹션을 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `21 passed`를 확인했다. 추가로 `.venv/bin/repotrust scan . --format json > /tmp/repotrust.json` 후 `.venv/bin/python -m json.tool /tmp/repotrust.json`로 실제 redirect된 JSON이 valid임을 확인했다.
- 결과: JSON report contract가 `schema_version` 기준으로 명시됐고, CLI stdout은 CI와 shell pipe에서 바로 파싱 가능한 JSON을 유지하게 됐다. 현재 active 작업은 없으며, 다음 작업은 `샘플 fixture와 예시 리포트 추가`다.

## 005: 샘플 fixture와 예시 리포트 추가

- 완료일: 2026-04-28
- 배경: 기존 테스트는 README 문자열을 테스트 파일에 직접 작성했기 때문에 실제 저장소 구조를 한눈에 보기 어렵고, 개발을 오래 쉬었다가 돌아왔을 때 rule 의도를 복기하기 어려웠다. 좋은 저장소와 위험 설치 저장소의 작은 fixture가 필요했다.
- 변경 내용: `tests/fixtures/repos/good-python`과 `tests/fixtures/repos/risky-install` fixture repo를 추가했다. `good-python`은 README, LICENSE, SECURITY, CI, Dependabot, dependency manifest, lockfile을 갖춘 100점 예시다. `risky-install`은 shell pipe, process substitution, Python inline execution, direct VCS install을 포함해 Install Safety finding을 확인하는 예시다. scanner 테스트는 fixture repo를 임시 디렉터리로 복사해 scan하도록 바꿨다.
- 코드/문서: `tests/test_scanner.py`에 fixture copy helper를 추가하고 good/risky 사례 테스트를 fixture 기반으로 전환했다. `docs/testing-and-validation.md`에는 fixture 설명과 Markdown/JSON/HTML sample report 생성 명령을 추가했다. `README.md`에도 fixture report 실행 예시를 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `21 passed`를 확인했다. 추가로 `good-python` fixture JSON report를 생성해 `json.tool`로 검증했고, `risky-install` fixture HTML report가 생성되는지 확인했다.
- 결과: 테스트가 실제 작은 repo 구조를 사용하게 되어 rule 의도를 더 쉽게 이해할 수 있다. 현재 active 작업은 없다.

## 006: RepoTrust 자체 신뢰 신호 보강

- 완료일: 2026-04-28
- 배경: `repotrust scan .` 기준 자체 저장소 점수가 68점(D)였고, README install/usage/maintenance 섹션, SECURITY.md, CI, Dependabot 등 기본 신뢰 신호가 부족했다. LICENSE와 lockfile은 정책/도구 선택이 필요하므로 이번 작업에서는 임의로 추가하지 않기로 했다.
- 변경 내용: README에 Installation, Usage, Development, Fixture Reports, Contributing 섹션을 추가했다. `SECURITY.md`를 추가해 v1의 보안 범위와 취약점 보고 정보를 적었다. `.github/workflows/ci.yml`을 추가해 push/PR에서 pytest를 실행하도록 했다. `.github/dependabot.yml`을 추가해 pip ecosystem weekly update 설정을 넣었다. 실제 README 설치 명령인 `.venv/bin/python -m pip install -e '.[dev]'`가 install command로 인식되도록 rule regex도 보강했다.
- 코드/문서: `README.md`, `SECURITY.md`, `.github/workflows/ci.yml`, `.github/dependabot.yml`을 추가/수정했다. `src/repotrust/rules.py`는 `python -m pip` 형태를 install command로 인식하도록 수정했다. `tests/test_scanner.py`에는 해당 형태가 `install.no_commands`를 만들지 않는 테스트를 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `22 passed`를 확인했다. 자체 스캔은 68점(D)에서 92점(A)으로 개선됐다. 남은 finding은 `hygiene.no_license`, `security.no_lockfile` 두 개다.
- 결과: RepoTrust 저장소 자체가 README/보안/CI/Dependabot 신호를 갖추게 됐다. 다음 작업은 LICENSE와 lockfile 도입 여부를 결정하는 것이다.

## 007: LICENSE와 lockfile 정책 결정

- 완료일: 2026-04-28
- 배경: 자체 스캔 기준 남은 finding은 `hygiene.no_license`, `security.no_lockfile` 두 개였다. 다만 LICENSE는 법적/소유자 선택이 필요하고, lockfile은 프로젝트 표준 도구 선택이 필요하다.
- 변경 내용: LICENSE는 임의로 MIT 등으로 추가하지 않기로 결정했다. lockfile도 현재 `uv`나 `pip-tools`가 설치되어 있지 않고 프로젝트 표준 도구가 정해져 있지 않으므로 임의 생성하지 않기로 결정했다. 사용자가 요청하지 않으면 매 작업마다 원격 push하지 않는 운영 규칙을 `AGENTS.md`에 추가했다.
- 코드/문서: 코드 변경은 없었다. `AGENTS.md`에 push 운영 규칙을 추가했고, active 작업 문서를 작업 시작/완료 상태에 맞게 갱신했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `22 passed`를 확인했다. 자체 스캔은 92/100, A 상태를 유지했고 남은 finding은 `security.no_lockfile`, `hygiene.no_license`이다.
- 결과: 정책 선택이 필요한 항목을 임의로 처리하지 않고 보류했다. 현재 active 작업은 없다.

## 008: CLI version 옵션 추가

- 완료일: 2026-04-28
- 배경: CLI 도구는 설치/디버깅/리포트 공유 시 실행 중인 버전을 확인할 수 있어야 한다. 패키지에는 이미 `__version__ = "0.1.0"`이 있었지만 CLI에서 확인하는 옵션은 없었다.
- 변경 내용: `repotrust --version` 옵션을 추가해 `repotrust 0.1.0` 형식으로 출력하도록 했다. Typer 앱은 subcommand 없이 version callback을 실행할 수 있도록 `invoke_without_command=True`를 설정했다.
- 코드/문서: `src/repotrust/cli.py`에 version option을 추가했다. `tests/test_cli.py`에 version 테스트를 추가했다. `README.md`의 usage 예시에 `repotrust --version`을 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `23 passed`를 확인했다.
- 결과: 사용자가 설치된 RepoTrust CLI 버전을 바로 확인할 수 있게 됐다. 현재 active 작업은 없다.
