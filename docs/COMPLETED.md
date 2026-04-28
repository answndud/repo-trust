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

## 009: PLAN 자동 보충 규칙과 개발 roadmap 정리

- 완료일: 2026-04-28
- 배경: 사용자가 `PLAN.md`의 active 작업이 모두 끝나면 프로젝트 완성 전까지 다음 개발 계획을 계속 순서대로 추가해 달라고 요청했다. 기존 운영 규칙은 active 작업이 끝나면 `현재 active 작업 없음`으로 두는 데 초점이 있었고, 프로젝트가 아직 미완성일 때 다음 backlog를 자동으로 채우는 규칙은 없었다.
- 변경 내용: `AGENTS.md`에 active 작업이 모두 끝났고 프로젝트가 아직 완성 전이면 `docs/PLAN.md`에 다음 개발 계획을 우선순위 순서로 추가한다는 규칙을 추가했다. `docs/PLAN.md`에는 PRD/TRD 기준의 다음 roadmap을 작성했다: Finding/score 정책 문서화, CLI UX 정리, 설정 파일 v1 설계, Remote GitHub scan 설계, Remote GitHub scan MVP 구현.
- 코드/문서: 코드 변경은 없었다. `AGENTS.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`만 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `23 passed`를 확인했다.
- 결과: 다음 작업이 비어 있는 상태가 되면 프로젝트 완성까지 이어질 개발 계획을 `PLAN.md`에 다시 채우는 운영 방식이 명확해졌다. 다음 작업은 `Finding/score 정책 문서화`다.

## 010: Finding/score 정책 문서화

- 완료일: 2026-04-28
- 배경: rule이 늘어날수록 severity, 감점, finding ID 기준이 흔들리면 RepoTrust 자체 신뢰도가 떨어진다. 현재 정책은 `src/repotrust/scoring.py`와 `src/repotrust/models.py`에 구현되어 있었지만, 문서로 충분히 설명되어 있지 않았다.
- 변경 내용: `docs/domain-context.md`에 severity별 의미와 감점, grade threshold, finding ID 정책, severity 선택 기준, score 변경 원칙을 추가했다. `docs/trd.md`에는 현재 severity deduction, grade threshold, finding ID stability contract를 기술 설계 관점에서 보강했다. `docs/adr.md`에는 `ADR-007: Finding ID는 public-ish contract로 취급한다`를 추가했다.
- 코드/문서: 코드 변경은 없었다. 문서 변경은 `docs/domain-context.md`, `docs/trd.md`, `docs/adr.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`에 적용했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `23 passed`를 확인했다.
- 결과: 새 rule을 추가할 때 severity와 finding ID를 어떤 기준으로 정해야 하는지 명확해졌다. 다음 작업은 `CLI UX 정리`다.

## 011: CLI UX 정리

- 완료일: 2026-04-28
- 배경: 사용자가 처음 실행했을 때 help, format 선택지, target 누락, JSON stdout/stderr 분리를 명확히 이해할 수 있어야 했다. 기존 `--format`은 자유 텍스트로 보였고, root command를 인자 없이 실행하면 아무 출력 없이 종료됐다.
- 변경 내용: `ReportFormat` enum을 도입해 `--format` help에 `[markdown|json|html]` 선택지가 표시되도록 했다. root command를 인자 없이 실행하면 help를 출력하도록 했다. invalid format, missing target, root help, scan help, JSON stdout/stderr 분리를 테스트로 고정했다.
- 코드/문서: `src/repotrust/cli.py`, `tests/test_cli.py`, `AGENTS.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `27 passed`를 확인했다. 추가로 `repotrust --help`, `repotrust scan --help`, invalid format, JSON redirect smoke check를 실행했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 CLI UX와 문서에 한정됨을 확인했다.
- 결과: CLI help와 오류 UX가 더 명확해졌고, JSON report stdout이 stderr summary와 분리되는 동작이 테스트로 보호된다. 다음 작업은 `설정 파일 v1 설계`다.

## 012: 설정 파일 v1 설계

- 완료일: 2026-04-28
- 배경: 회사/개인 프로젝트마다 허용 가능한 risk 기준이 다를 수 있어, 구현 전 설정 파일 이름과 최소 설정 범위를 결정해야 했다. 초기부터 rule override까지 열면 scoring contract와 finding 안정성이 복잡해질 수 있었다.
- 변경 내용: 설정 파일 v1은 repository root의 `repotrust.toml`로 설계했다. 구현은 명시적 `--config <path>`를 먼저 지원하고, 자동 탐지는 이후 단계로 미룬다. v1 설정 항목은 `policy.fail_under`와 네 개 category weight로 제한한다. CLI flag는 config 값보다 우선한다. rule enable/disable, severity override, remote credential 설정은 v1 config에서 제외한다.
- 코드/문서: 코드 변경은 없었다. `docs/trd.md`에 Config File v1 Design 섹션을 추가했고, `docs/adr.md`에 `ADR-008: 설정 파일 v1은 repotrust.toml로 설계한다`를 추가했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `27 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 설정 설계 문서에 한정됨을 확인했다.
- 결과: 설정 파일 구현 범위가 결정됐다. 다음 작업은 `설정 파일 v1 구현`이다.

## 013: 설정 파일 v1 구현

- 완료일: 2026-04-28
- 배경: 설정 파일 설계에서 `repotrust.toml`의 최소 범위를 `policy.fail_under`와 category weights로 제한하기로 결정했다. CI/조직 정책에서 threshold와 가중치를 조정할 수 있도록 구현이 필요했다.
- 변경 내용: `src/repotrust/config.py`를 추가해 명시적 TOML config를 읽고 검증한다. CLI에 `--config <path>` 옵션을 추가했다. `policy.fail_under`는 `--fail-under` 기본값으로 동작하며 CLI flag가 우선한다. `[weights]`는 score 계산에 반영된다. Python 3.10 호환을 위해 `tomli` 조건부 dependency를 추가했다. invalid config와 missing config는 usage error로 실패한다.
- 코드/문서: `pyproject.toml`, `src/repotrust/config.py`, `src/repotrust/cli.py`, `src/repotrust/scanner.py`, `src/repotrust/scoring.py`, `tests/test_config.py`, `tests/test_cli.py`, `README.md`, `docs/trd.md`, `docs/testing-and-validation.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `37 passed`를 확인했다. valid config JSON smoke check, invalid config smoke check를 실행했다. `git diff --stat`과 주요 diff를 검토해 config 구현, 테스트, 문서 변경이 함께 반영됐음을 확인했다.
- 결과: RepoTrust CLI가 명시적 `repotrust.toml` 정책 파일을 읽어 fail threshold와 score weights를 적용할 수 있게 됐다. 다음 작업은 `Remote GitHub scan 설계`다.

## 014: Remote GitHub scan 설계

- 완료일: 2026-04-28
- 배경: GitHub URL은 v1에서 parse-only로 처리하지만, 이후 확장에서는 clone 없이 GitHub API 기반으로 remote metadata를 확인할 필요가 있다. 사용자가 지정한 CLI v1 범위에서는 구현하지 않고 설계까지만 완료하기로 했다.
- 변경 내용: remote scan은 기본 scan 동작이 아니라 `--remote` 명시 옵션으로만 실행하도록 결정했다. local path scan은 네트워크를 사용하지 않고, GitHub URL 기본 동작은 계속 parse-only로 유지한다. 인증은 선택적 `GITHUB_TOKEN` 사용으로 설계하고, token 출력 금지 원칙을 기록했다. repository metadata, contents/README, workflow 목록을 read-only API 범위로 정리했고, 인증 실패, repository not found, rate limit, API error, partial scan을 finding으로 표현하도록 설계했다.
- 코드/문서: `docs/trd.md`에 remote scan interface, API 범위, failure finding, 테스트 접근을 추가했다. `docs/adr.md`에 `ADR-009: Remote GitHub scan은 명시적 --remote로만 설계한다`를 추가했다. `docs/prd.md`의 향후 확장 아이디어를 parse-only 기본 동작과 명시적 remote scan으로 정리했다. `docs/trd.md`의 현재 CLI 옵션 목록에는 이미 구현된 `--config <path>`도 반영했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `37 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote scan 설계 문서와 하네스 상태 문서에 한정됨을 확인했다.
- 결과: Remote GitHub scan은 CLI v1 밖의 post-v1 확장으로 명확히 분리됐고, CLI v1 완성 판정 전에 필요한 설계 문서가 정리됐다. 다음 작업은 `릴리스 전 품질 점검`이다.

## 015: CLI v1 완성 판정

- 완료일: 2026-04-28
- 배경: local repository scan, GitHub URL parse-only 처리, Markdown/JSON/HTML report, 설정 파일, CLI UX, 하네스 문서가 CLI v1 범위대로 안정화됐는지 확인해야 했다. Remote GitHub scan은 설계까지만 완료하고 구현은 post-v1으로 분리했다.
- 변경 내용: 릴리스 전 품질 점검을 수행하며 README의 config 예시를 명시적 path 기준으로 보정했다. `docs/trd.md`의 config 설명을 구현 완료 상태에 맞게 수정했고, `docs/architecture.md`에 `config.py` 책임과 data flow를 추가했다. `docs/testing-and-validation.md`에는 명시적 임시 config를 사용하는 smoke check 절차를 추가했다. active 작업이 모두 끝났으므로 `docs/PLAN.md`와 `docs/PROGRESS.md`는 `현재 active 작업 없음` 상태로 정리했다.
- 코드/문서: 기능 코드 변경은 없었다. `README.md`, `docs/trd.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`에서 `37 passed`를 확인했다. `good-python` fixture Markdown/JSON report를 생성하고 JSON을 `json.tool`로 검증했다. `risky-install` fixture HTML report를 `/tmp/repotrust-risky.html`로 생성했다. 자체 `repotrust scan . --format json`은 92/100, A, Low risk였고 남은 finding은 `security.no_lockfile`, `hygiene.no_license`였다. 두 finding은 LICENSE와 lockfile 정책 선택 전까지 보류하기로 이미 결정한 항목이다. 임시 config smoke check, GitHub URL parse-only JSON check, `--help`, `scan --help`, `--version`, `--fail-under 95` exit code 1도 확인했다. `git diff --stat`과 주요 diff를 검토해 문서 보정 외 회귀 위험이 없음을 확인했다.
- 결과: RepoTrust CLI v1은 사용 가능한 MVP 기준으로 완성됐다. 현재 active 작업은 없다. 다음 작업은 사용자가 post-v1 범위를 지정하면 `PLAN.md`에 새로 추가한다.

## 016: 오픈소스 공개 준비

- 완료일: 2026-04-28
- 배경: 사용자가 RepoTrust를 오픈소스 repo로 공개하기로 결정했고, 자체 scan의 남은 finding은 `hygiene.no_license`, `security.no_lockfile`이었다. 공개 저장소로서 재사용 조건과 dependency 재현성을 명확히 해야 했다.
- 변경 내용: MIT `LICENSE`를 추가했다. pip 26의 `pip lock`으로 `pylock.toml`을 생성해 별도 도구 설치 없이 pip-compatible lockfile을 커밋하도록 했다. RepoTrust lockfile detection에 `pylock.toml`을 추가했다. README와 개발/검증 문서에는 lockfile 재생성 명령과 MIT license 정보를 반영했다.
- 코드/문서: `LICENSE`, `pylock.toml`, `src/repotrust/detection.py`, `tests/test_scanner.py`, `README.md`, `docs/development-workflow.md`, `docs/testing-and-validation.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `37 passed`를 확인했다. 자체 `repotrust scan . --format json`은 100/100, A, Low risk, finding 0개였고 detected files에 `LICENSE`와 `pylock.toml`이 포함됨을 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 공개 준비와 lockfile detection에 한정됨을 확인했다.
- 결과: RepoTrust 저장소는 오픈소스 공개를 위한 license와 lockfile 신호를 갖췄고 자체 RepoTrust Score가 100점이 됐다. 다음 작업은 `GitHub main push`다.

## 017: GitHub main push

- 완료일: 2026-04-28
- 배경: 사용자가 오픈소스 공개 준비 후 GitHub repo에 push까지 진행하라고 요청했다. 이전까지 local commits가 원격보다 앞서 있었다.
- 변경 내용: `main` branch를 그대로 유지하고 별도 branch를 만들지 않았다. `git push origin main`을 실행했다.
- 코드/문서: push 자체에는 파일 변경이 없었다.
- 검증: `git push origin main`이 성공했고 원격 `main`이 `0ea0bc4`에서 `f5852d0`까지 업데이트됐다.
- 결과: 공개 준비가 반영된 RepoTrust CLI v1 상태가 GitHub `answndud/repo-trust`의 `main`에 올라갔다. 다음 작업은 `Ralph-style post-v1 loop 세팅`이다.

## 018: Ralph-style post-v1 loop 세팅

- 완료일: 2026-04-28
- 배경: 사용자가 Ralph 아이디어처럼 완성될 때까지 작은 작업을 재귀적으로 계획, 구현, 테스트, 리뷰하는 루프를 원했다. 외부 Ralph 구현은 Amp/Claude 중심 스크립트와 skill 구조를 포함하므로 그대로 복사하지 않고 현재 Codex 하네스에 맞게 문서 규칙으로 흡수하기로 했다.
- 변경 내용: `AGENTS.md`에 post-v1 반복 작업은 작은 story 하나를 `In Progress`로 승격하고 구현, 검증, 리뷰, 커밋, archive 후 다음 story로 넘어간다는 compact rule을 추가했다. `docs/development-workflow.md`에 lightweight Ralph-style loop 절차를 추가했다. `docs/PLAN.md`에는 Remote GitHub scan MVP를 CLI/API boundary, client/failure findings, metadata detection, scoring/report integration, completion review story로 분할했다.
- 코드/문서: `AGENTS.md`, `docs/development-workflow.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `37 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 하네스/문서에 한정됨을 확인했다.
- 결과: RepoTrust는 post-v1 작업을 작은 story 단위로 반복 진행할 준비가 됐다. 다음 작업은 `Remote GitHub scan MVP story 1: CLI/API boundary`다.

## 019: Remote GitHub scan MVP story 1 - CLI/API boundary

- 완료일: 2026-04-28
- 배경: Remote GitHub scan 구현 전에 CLI contract와 네트워크 없는 기본 동작을 먼저 고정해야 했다. v1의 GitHub URL parse-only 동작은 유지하면서, 명시적 `--remote`만 별도 remote scanner boundary로 보내야 했다.
- 변경 내용: `repotrust scan <target> --remote` 옵션을 추가했다. local path에서 `--remote`를 사용하면 usage error로 실패한다. GitHub URL without `--remote`는 기존 `target.github_not_fetched` parse-only finding을 유지한다. GitHub URL with `--remote`는 새 `remote.py` boundary로 들어가며 현재는 네트워크 없이 `remote.github_not_implemented` finding을 반환한다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/scanner.py`, `src/repotrust/remote.py`, `tests/test_cli.py`, `README.md`, `docs/trd.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `40 passed`를 확인했다. GitHub URL parse-only JSON smoke check는 `target.github_not_fetched`를 반환했다. GitHub URL + `--remote` JSON smoke check는 `remote.github_not_implemented`를 반환했다. local path + `--remote`는 exit code 2와 `--remote can only be used with GitHub URL targets` usage error를 반환했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 CLI/API boundary와 문서에 한정됨을 확인했다.
- 결과: Remote scan의 명시적 opt-in 경계가 생겼고, 다음 story에서 GitHub client와 실패 finding 변환을 구현할 수 있게 됐다. 다음 작업은 `Remote GitHub scan MVP story 2: GitHub client and failure findings`다.

## 020: Remote GitHub scan MVP story 2 - GitHub client and failure findings

- 완료일: 2026-04-28
- 배경: `--remote` CLI boundary가 생겼으므로 GitHub REST 요청 경계와 실패 모드를 먼저 안정화해야 했다. 실제 repository contents/workflow detection은 다음 story로 분리했다.
- 변경 내용: `GitHubClient`, `GitHubResponse`, fake 교체 가능한 `GitHubTransport`, 기본 `UrllibGitHubTransport`를 추가했다. `GITHUB_TOKEN`을 읽어 Authorization header에 사용하되 finding/report에는 token 값을 넣지 않도록 했다. repository metadata endpoint의 success, unauthorized, not found, rate limited, generic API error를 stable finding으로 변환했다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `tests/test_cli.py`, `README.md`, `docs/trd.md`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `45 passed`를 확인했다. fake transport tests로 200 success, 401 unauthorized, 404 not found, 403 rate limit, 500 API error를 확인했다. token non-leak test에서 Authorization header에는 token이 들어가지만 finding message/evidence에는 token이 포함되지 않음을 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote client/failure mapping과 문서에 한정됨을 확인했다.
- 결과: Remote scan은 repository metadata API 실패를 설명 가능한 finding으로 표현할 수 있게 됐다. 다음 작업은 `Remote GitHub scan MVP story 3: Remote metadata detection`이다.

## 021: Remote GitHub scan MVP story 3 - Remote metadata detection

- 완료일: 2026-04-28
- 배경: GitHub client와 실패 finding이 준비됐으므로 repository metadata, root contents, workflow response를 기존 `DetectedFiles` 모델로 변환해야 했다. API 실패를 파일 부재로 오해하지 않도록 partial failure도 finding으로 표현해야 했다.
- 변경 내용: GitHub client에 root contents와 Actions workflows endpoint 호출을 추가했다. Root contents response에서 README, LICENSE, SECURITY, dependency manifest, lockfile을 탐지한다. Workflows response에서 workflow path를 `ci_workflows`로 변환한다. Contents 또는 workflows endpoint가 실패하면 `remote.github_partial_scan` finding을 추가하고, 성공한 endpoint의 metadata는 유지한다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `README.md`, `docs/trd.md`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `48 passed`를 확인했다. Fake transport tests로 remote detected files 변환, contents partial failure, workflows partial failure를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote metadata detection과 문서에 한정됨을 확인했다.
- 결과: Remote scan이 GitHub root contents와 workflows metadata를 `DetectedFiles`로 변환할 수 있게 됐다. 다음 작업은 `Remote GitHub scan MVP story 4: Remote scoring/report integration`이다.

## 022: Remote GitHub scan MVP story 4 - Remote scoring/report integration

- 완료일: 2026-04-28
- 배경: Remote scan이 `DetectedFiles`를 만들 수 있게 됐으므로 기존 rule/scoring/report contract에 연결해야 했다. README와 install safety rule을 remote에서도 사용하려면 README 본문 fetch가 필요했다.
- 변경 내용: Remote scan에서 README content endpoint와 Dependabot config contents endpoint를 추가로 조회한다. README content를 base64 decode해 기존 README Quality와 Install Safety rules에 연결했다. Remote detected files는 Security Posture와 Project Hygiene rules에 연결했다. README content를 가져오지 못하면 `remote.readme_content_unavailable` finding으로 표현하고 false README deductions를 피한다. Remote JSON/Markdown report가 기존 schema와 renderer를 그대로 사용하도록 테스트했다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `README.md`, `docs/trd.md`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `50 passed`를 확인했다. Fake remote success case는 100점과 detected README/LICENSE/SECURITY/manifest/lockfile/workflow/Dependabot을 확인했다. Risky remote README는 `install.risky.shell_pipe_install` finding을 생성했다. Remote report rendering test는 JSON schema version과 Markdown report section을 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote scoring/report integration과 문서에 한정됨을 확인했다.
- 결과: Remote GitHub scan MVP의 기능 구현 story들이 완료됐다. 다음 작업은 `Post-v1 loop completion review`다.

## 023: Remote GitHub scan MVP completion review

- 완료일: 2026-04-28
- 배경: Remote GitHub scan MVP의 CLI boundary, GitHub client/failure findings, metadata detection, scoring/report integration story가 끝났으므로 전체 기능 완성 여부를 확인해야 했다.
- 변경 내용: 전체 검증과 smoke check를 수행했다. `docs/trd.md`와 `docs/architecture.md`에서 remote scan 구현 상태 표현을 현재 동작에 맞게 보정했다. active 작업이 모두 끝났으므로 `docs/PLAN.md`와 `docs/PROGRESS.md`는 `현재 active 작업 없음` 상태로 정리했다.
- 코드/문서: `docs/trd.md`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `50 passed`였다. 자체 local scan은 100/100, A, Low risk, finding 0개였다. `good-python` fixture JSON과 `risky-install` fixture HTML smoke check가 통과했다. 실제 GitHub remote scan `repotrust scan https://github.com/answndud/repo-trust --remote --format json`은 100/100, A, Low risk, finding 1개(`remote.github_metadata_collected`)였고 README, LICENSE, SECURITY, pyproject.toml, pylock.toml, Dependabot, workflows를 탐지했다. 기본 GitHub URL scan은 여전히 parse-only finding `target.github_not_fetched`를 반환했다. `git diff --stat`과 주요 diff를 검토해 남은 변경이 completion 문서 정리에 한정됨을 확인했다.
- 결과: Remote GitHub scan MVP가 완료됐다. 현재 active 작업은 없다. 다음 작업은 사용자가 post-v1 범위를 지정하면 `PLAN.md`에 새로 추가한다.

## 024: Remote scan UX 문서화

- 완료일: 2026-04-28
- 배경: Remote scan MVP가 구현됐으므로 사용자가 local scan, parse-only GitHub scan, explicit remote scan의 차이를 이해하고 `GITHUB_TOKEN`, rate limit, partial scan finding을 안전하게 해석할 수 있어야 했다.
- 변경 내용: README에 local checkout scan은 네트워크를 사용하지 않는다는 점, GitHub URL은 기본 parse-only라는 점, `--remote`가 명시적 GitHub API scan이라는 점을 정리했다. `GITHUB_TOKEN` 사용 예시와 token 값이 findings/report/terminal summary에 출력되지 않는 원칙을 추가했다. `docs/domain-context.md`에 remote finding ID별 해석을 추가했다. `docs/testing-and-validation.md`의 remote smoke command와 expected behavior를 현재 동작에 맞게 보정했다.
- 코드/문서: `README.md`, `docs/domain-context.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `50 passed`를 확인했다. 실제 remote smoke `repotrust scan https://github.com/answndud/repo-trust --remote --format json`은 100/100, A, finding 1개(`remote.github_metadata_collected`)를 반환했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote scan UX 문서와 하네스 상태 문서에 한정됨을 확인했다.
- 결과: Remote scan 사용법과 failure finding 해석이 문서화됐다. 다음 작업은 `v0.1.0 릴리스 준비`다.

## 025: v0.1.0 릴리스 준비

- 완료일: 2026-04-28
- 배경: CLI v1과 Remote scan MVP가 구현됐고 remote scan UX 문서도 정리됐으므로 첫 release를 위한 변경 요약, 알려진 제한, tag 전 checklist가 필요했다.
- 변경 내용: `CHANGELOG.md`를 추가해 v0.1.0 주요 기능, 알려진 제한, 검증 결과, pre-tag checklist를 정리했다. README에 release notes 위치를 추가했다.
- 코드/문서: `CHANGELOG.md`, `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `50 passed`였다. Local self-scan은 100/100, A, finding 0개였고 remote self-scan은 100/100, A, finding 1개(`remote.github_metadata_collected`)였다. `pyproject.toml` version은 `0.1.0`이다.
- 결과: v0.1.0 tag를 만들 수 있는 release notes와 checklist가 준비됐다. 다음 작업은 `v0.1.0 tag 생성`이다.

## 026: v0.1.0 tag 생성

- 완료일: 2026-04-28
- 배경: v0.1.0 release notes와 pre-tag checklist가 준비됐으므로 첫 release tag를 만들 수 있는 상태인지 검증하고 tag를 생성해야 했다.
- 변경 내용: tag 전 remote smoke 중 Dependabot metadata endpoint가 unknown일 때 `security.no_dependabot`까지 감점되는 false deduction을 발견했다. Remote partial scan에서는 실패한 endpoint의 파일 부재를 단정하지 않도록 unknown metadata 기반 local-style deductions를 필터링했다. 이후 `v0.1.0` annotated tag를 생성했다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다. Git tag `v0.1.0`을 생성했다.
- 검증: `.venv/bin/python -m pytest -q`는 `51 passed`였다. Local self-scan은 100/100, A, finding 0개였다. `git tag --list 'v0.1.0' -n`에서 `RepoTrust v0.1.0` tag를 확인했다.
- 결과: v0.1.0 tag가 로컬에 생성됐다. tag와 이후 커밋 push는 사용자가 요청할 때 진행하면 된다. 다음 작업은 `Remote scan 품질 개선 계획`이다.

## 027: Remote scan 품질 개선 계획

- 완료일: 2026-04-28
- 배경: Remote scan MVP는 동작하지만 repository metadata 중 어떤 항목을 score-deducting finding으로 삼고 어떤 항목을 evidence-only context로 둘지 결정이 필요했다.
- 변경 내용: `docs/domain-context.md`에 Remote Metadata Quality Policy를 추가했다. archived 상태처럼 명확한 maintenance risk는 점수화 가능하고, fork/private/default branch/stars/language/size/created date는 evidence-only로 시작하기로 했다. release/tag freshness는 project type과 release practice를 구분할 수 있을 때 낮은 severity부터 도입하기로 했다. `docs/adr.md`에 ADR-010으로 score와 evidence 분리 결정을 기록했다.
- 코드/문서: `docs/domain-context.md`, `docs/trd.md`, `docs/adr.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `51 passed`를 확인했다. 변경 범위가 remote metadata policy 문서와 하네스 상태 문서에 한정됨을 확인했다.
- 결과: Remote scan 품질 개선의 다음 방향이 정리됐다. 현재 active 작업은 없다.

## 028: Remote scan report output contract 보강

- 완료일: 2026-04-28
- 배경: Remote scan MVP 이후 JSON/static HTML report가 remote metadata와 partial finding을 안정적으로 노출하는지 테스트 contract를 더 명확히 해야 했다.
- 변경 내용: remote success report test를 문자열 포함 검사에서 JSON parsing 기반 contract 검사로 강화했다. GitHub target metadata, detected README/workflow, stable finding ID, severity가 JSON report에 유지되는지 확인한다. Remote partial scan finding과 evidence, workflow metadata가 static HTML report에 렌더링되는지도 새 테스트로 추가했다.
- 코드/문서: `tests/test_remote.py`, `docs/PLAN.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `52 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote report output test와 하네스 상태 문서에 한정됨을 확인했다.
- 결과: Remote scan JSON/HTML output contract 회귀 테스트가 보강됐다. 현재 active 작업은 없다.

## 029: Remote archived repository finding 구현

- 완료일: 2026-04-28
- 배경: Remote Metadata Quality Policy에서 archived repository는 명확한 maintenance risk로 score-deducting finding을 허용하기로 했지만, 구현은 아직 `remote.github_metadata_collected` info finding만 내고 있었다.
- 변경 내용: GitHub repository metadata가 `archived=true`일 때 `remote.github_archived` finding을 추가한다. 이 finding은 `project_hygiene` category와 `medium` severity를 사용해 점수에 반영된다. `archived=false` 또는 repository metadata API 실패는 archived deduction을 만들지 않는다. Remote finding 해석 문서와 TRD finding catalog도 새 ID에 맞게 갱신했다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `docs/domain-context.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `54 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote archived metadata handling, 테스트, 문서에 한정됨을 확인했다.
- 결과: Remote scan이 archived repository를 score-deducting maintenance risk로 보고한다. 현재 active 작업은 없다.

## 030: Dev-loop roadmap 시작 및 미커밋 변경 검증

- 완료일: 2026-04-28
- 배경: 사용자가 `PLAN.md`의 모든 작업을 dev-loop로 진행하도록 요청했으므로, 전체 backlog를 status/goal/scope/non-goals/acceptance/verification/next action 형식으로 정리하고 기존 미커밋 변경을 검증해야 했다.
- 변경 내용: `docs/PLAN.md`에 RepoTrust post-v1 완성품 로드맵 task contract와 1-10번 순차 story를 명시했다. 1번 story로 기존 remote report output contract 보강, archived finding 구현, 관련 문서 변경이 하나의 일관된 diff인지 검토했다.
- 코드/문서: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다. 기존 미커밋 변경인 `src/repotrust/remote.py`, `tests/test_remote.py`, `docs/domain-context.md`, `docs/trd.md`도 함께 검토했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `54 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote report output contract, archived metadata finding, dev-loop roadmap 문서에 한정됨을 확인했다.
- 결과: 현재 변경 세트는 커밋 가능한 상태다. push, tag, release publish는 사용자가 요청할 때만 진행한다. 다음 작업은 `Remote metadata quality implementation`이다.

## 031: Remote metadata quality implementation

- 완료일: 2026-04-28
- 배경: Remote Metadata Quality Policy가 score와 evidence-only metadata를 분리하기로 했으므로, `archived` 외에 명확한 repository metadata signal을 구현하고 나머지 metadata는 과잉 점수화하지 않도록 정리해야 했다.
- 변경 내용: GitHub repository metadata의 `has_issues=false`를 `remote.github_issues_disabled` finding으로 추가했다. 이 finding은 public support path가 덜 명확하다는 낮은 project hygiene signal로만 반영된다. fork/private/default branch/stars/language/size/created date와 `security_and_analysis` 세부 값은 JSON evidence-only 표현이 설계될 때까지 점수화하지 않도록 TRD와 domain context에 명시했다.
- 코드/문서: `src/repotrust/remote.py`, `tests/test_remote.py`, `docs/domain-context.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `56 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 remote repository metadata quality classification과 테스트/문서에 한정됨을 확인했다.
- 결과: Remote metadata quality signal은 archived와 disabled issues만 점수에 반영하고, 나머지 context metadata는 보수적으로 deferred/evidence-only로 유지한다. 다음 작업은 `Remote release/tag freshness 설계`다.

## 032: Remote release/tag freshness 설계

- 완료일: 2026-04-28
- 배경: release/tag freshness는 useful signal이지만, GitHub Releases가 없다는 사실만으로 maintenance risk를 단정하면 false positive가 크다. 프로젝트가 release-managed인지, installable package인지, no-release practice가 정상인지 구분하는 기준이 먼저 필요했다.
- 변경 내용: TRD에 future candidate endpoint로 `GET /repos/{owner}/{repo}/releases/latest`와 `GET /repos/{owner}/{repo}/tags?per_page=1`를 정리했다. `404` latest release, tags-only repository, API failure/rate limit/permission failure를 stale-release deduction으로 처리하지 않는 failure policy를 문서화했다. 현재 구현에서는 release/tag freshness를 점수화하지 않고, future stale finding은 installable/package signal과 release/tag date evidence가 있을 때 low/medium severity부터 시작하도록 domain context에 명시했다.
- 코드/문서: `docs/trd.md`, `docs/domain-context.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `56 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 release/tag freshness 설계 문서와 active state 문서에 한정됨을 확인했다.
- 결과: Release/tag freshness는 현재 score에서 제외하고, 향후 구현 기준과 endpoint/failure mode를 문서화했다. 다음 작업은 `Report UX와 static HTML 개선`이다.

## 033: Report UX와 static HTML 개선

- 완료일: 2026-04-28
- 배경: 기존 HTML renderer는 Markdown 출력 문자열을 단순 변환해 만들었으므로 score, detected files, finding category/severity를 구조적으로 스캔하기 어려웠다.
- 변경 내용: `render_html()`이 `ScanResult`를 직접 렌더링하도록 바꿨다. Score summary, category scores, detected files, findings 섹션을 구조화했고 finding article에 severity class를 추가했다. HTML renderer에서 scanning/scoring logic은 추가하지 않았고, 더 이상 사용하지 않는 Markdown-ish HTML 변환 helper를 제거했다. HTML renderer test는 score, detected files, category/severity metadata가 출력되는지 확인한다.
- 코드/문서: `src/repotrust/reports.py`, `tests/test_scanner.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `57 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 static HTML renderer와 renderer test에 한정됨을 확인했다.
- 결과: Static HTML report가 Markdown/JSON과 같은 `ScanResult` 정보를 더 스캔 가능한 구조로 보여준다. 다음 작업은 `JSON contract hardening`이다.

## 034: JSON contract hardening

- 완료일: 2026-04-28
- 배경: JSON report는 CI와 외부 도구가 읽는 interface이므로 대표 scan 결과의 shape와 stable finding ID를 더 직접적으로 고정해야 했다.
- 변경 내용: GitHub parse-only JSON contract test를 추가해 `target.github_not_fetched`와 empty detected files shape를 고정했다. Remote partial scan JSON test는 `remote.github_metadata_collected`, `remote.github_partial_scan`, partial evidence, workflow metadata를 고정한다. Remote archived JSON test는 `remote.github_archived` category/severity와 score impact를 고정한다. TRD에는 `schema_version`이 top-level key 변경 없이 stable finding ID만 추가되는 동안 `"1.0"`으로 유지된다는 정책을 추가했다.
- 코드/문서: `tests/test_scanner.py`, `tests/test_remote.py`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `60 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 JSON contract tests와 schema policy 문서에 한정됨을 확인했다.
- 결과: 대표 local/parse-only/remote success/remote partial/remote archived JSON contract가 focused assertions로 보강됐다. 다음 작업은 `Policy config usability 보강`이다.

## 035: Policy config usability 보강

- 완료일: 2026-04-28
- 배경: config validation과 policy 적용은 이미 있었지만, explicit remote scan에서도 custom weights와 `fail_under`가 동일하게 적용되는지 회귀 테스트가 부족했다.
- 변경 내용: CLI remote scan fake boundary 테스트를 추가해 `--config` weights가 `scan_target(..., weights=..., remote=True)`로 전달되는지 확인했다. Remote scan 결과에도 config `policy.fail_under`가 적용되어 exit code 1을 반환하는 테스트를 추가했다. TRD와 testing guide에서 config를 local-only가 아니라 explicit file-based policy layer로 표현하고, local/remote scan 모두에 적용된다고 정리했다.
- 코드/문서: `tests/test_cli.py`, `docs/trd.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `62 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 config policy CLI coverage와 문서 정합성에 한정됨을 확인했다.
- 결과: Config policy가 local/remote scan 모두에서 일관되게 적용됨을 테스트와 문서로 고정했다. 다음 작업은 `CLI smoke and exit-code matrix`다.

## 036: CLI smoke and exit-code matrix

- 완료일: 2026-04-28
- 배경: CLI는 CI와 agent workflows에서 쓰이므로 핵심 조합의 exit code, stdout report, stderr status 정책이 문서와 테스트로 고정돼야 했다.
- 변경 내용: Remote failure finding이 JSON stdout과 stderr summary를 분리해 유지하는 CLI test를 추가했다. HTML `--output`은 stdout을 비우고 파일과 stderr status만 남기는지 확인했다. Missing local path는 usage error가 아니라 `target.local_path_missing` finding report로 exit 0을 반환한다는 test를 추가했다. Testing guide에는 local/missing/remote/fail-under/output/config error 조합의 exit-code matrix를 추가했다.
- 코드/문서: `tests/test_cli.py`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `64 passed`를 확인했다. `git diff --stat`과 주요 diff를 검토해 변경 범위가 CLI behavior coverage와 testing guide matrix에 한정됨을 확인했다.
- 결과: CLI exit-code와 stdout/stderr 정책이 주요 조합에서 회귀 테스트와 문서로 고정됐다. 다음 작업은 `Documentation alignment pass`다.

## 037: Documentation alignment pass

- 완료일: 2026-04-28
- 배경: v0.1.0 baseline 이후 explicit remote scan과 post-v1 quality work가 구현됐으므로, PRD와 README가 현재 구현 상태를 혼동 없이 설명해야 했다.
- 변경 내용: PRD의 기존 v1 범위를 `v1 baseline`으로 명확히 하고, 현재 구현 상태 섹션을 추가해 기본 GitHub URL scan은 parse-only이고 `--remote`만 GitHub REST API read-only metadata를 조회한다고 정리했다. Remote scan은 clone하지 않으며 archived/disabled issue tracking만 보수적으로 점수화하고 context metadata와 release/tag freshness는 점수화하지 않는다고 명시했다. README config 예시에 remote scan에서도 `--config`를 사용할 수 있음을 추가했다.
- 코드/문서: `README.md`, `docs/prd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `64 passed`를 확인했다. 구현 drift 검색과 `git diff --stat`/주요 diff 검토를 수행해 현재 active 문서 외에는 의도된 v1 baseline 설명만 남아 있음을 확인했다.
- 결과: 사용자 문서와 설계 문서가 v0.1.0 baseline 및 현재 post-v1 remote implementation을 구분해 설명한다. 다음 작업은 `Packaging and install verification`이다.

## 038: Packaging and install verification

- 완료일: 2026-04-28
- 배경: release readiness 전에 clean environment에서 package metadata, editable install, CLI entry point, fixture report, test suite가 실제로 동작하는지 확인해야 했다.
- 변경 내용: 임시 clean venv `/tmp/repotrust-clean-venv.Hrmz4G/.venv`에서 `pip install -e '.[dev]'`를 실행해 `repotrust==0.1.0` editable wheel이 설치되는지 확인했다. `repotrust --version`은 `repotrust 0.1.0`을 출력했다. `good-python` fixture JSON report를 생성하고 `json.tool`로 검증했다. Clean venv에서 pytest도 통과했다. Testing guide에 clean venv packaging verification 절차를 추가했다.
- 코드/문서: `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다. `pyproject.toml`과 `pylock.toml`은 dependency 변경이 없어 수정하지 않았다.
- 검증: clean venv에서 `pip install -e '.[dev]'`, `repotrust --version`, fixture JSON report generation, `python -m json.tool`, `python -m pytest -q`를 실행했고 `64 passed`를 확인했다. 기존 `.venv/bin/python -m pytest -q`도 `64 passed`였다.
- 결과: Packaging과 CLI entry point는 release readiness review에 들어갈 수 있는 상태다. 다음 작업은 `Release readiness review`다.

## 039: Release readiness review

- 완료일: 2026-04-28
- 배경: dev-loop `PLAN.md`의 모든 post-v1 hardening story가 끝났으므로 전체 변경이 release 가능한 상태인지 검증하고 active 문서를 정리해야 했다.
- 변경 내용: `CHANGELOG.md`에 Unreleased 섹션을 추가해 remote metadata quality findings, JSON contract tests, structured HTML renderer, CLI exit-code matrix, clean packaging verification, deferred freshness policy를 정리했다. 대표 smoke checks로 local self JSON report, risky fixture HTML report, GitHub URL parse-only JSON report를 생성하고 JSON reports를 `json.tool`로 검증했다. 모든 active backlog가 완료됐으므로 `docs/PLAN.md`와 `docs/PROGRESS.md`를 `현재 active 작업 없음` 상태로 정리했다.
- 코드/문서: `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다. 전체 dev-loop 변경 세트는 remote metadata handling, report rendering, CLI tests, JSON contract tests, config/exit-code coverage, README/PRD/TRD/domain/testing docs를 포함한다.
- 검증: `.venv/bin/repotrust scan . --format json --output /tmp/repotrust-self.json`, `.venv/bin/python -m json.tool /tmp/repotrust-self.json`, `.venv/bin/repotrust scan tests/fixtures/repos/risky-install --format html --output /tmp/repotrust-risky.html`, `.venv/bin/repotrust scan https://github.com/openai/codex --format json --output /tmp/repotrust-parse-only.json`, `.venv/bin/python -m json.tool /tmp/repotrust-parse-only.json`, `.venv/bin/python -m pytest -q`를 실행했고 `64 passed`를 확인했다.
- 결과: RepoTrust post-v1 완성품 로드맵의 모든 `PLAN.md` story가 완료됐다. commit, push, tag, release publish는 사용자가 요청할 때만 진행한다.

## 040: README 한국어 사용자 가이드 정리

- 완료일: 2026-04-28
- 배경: 초보자도 README만 읽고 RepoTrust의 주요 기능을 설치부터 실행, 해석, 설정까지 사용할 수 있도록 한국어 중심 문서가 필요했다.
- 변경 내용: `README.md`를 한국어 사용자 가이드로 전면 재작성했다. 빠른 시작, 설치, 로컬 스캔, JSON/HTML 리포트, GitHub URL parse-only 스캔, explicit remote scan, `GITHUB_TOKEN`, score/finding 해석, `--fail-under`, TOML config, fixture 연습, 자주 쓰는 명령, 개발자 검증, 현재 하지 않는 일을 순서대로 정리했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `64 passed`를 확인했다. `git diff --stat`과 README diff를 검토해 변경 범위가 한국어 사용자 가이드와 active state 문서에 한정됨을 확인했다.
- 결과: README만 보고도 주요 RepoTrust 기능을 따라 사용할 수 있는 한국어 안내가 준비됐다. 현재 active 작업은 없다.

## 041: `repo-trust TARGET` 기본 CLI 흐름 추가

- 완료일: 2026-04-28
- 배경: README와 실제 사용 경험이 `.venv/bin/repotrust scan .`처럼 개발 환경 내부 명령에 묶여 보여서, 상용 CLI처럼 `repo-trust "url"` 형태로 사용할 수 있는 기본 진입점이 필요했다.
- 변경 내용: `pyproject.toml`에 `repo-trust` console script를 추가했다. `src/repotrust/cli.py`에 scan subcommand 없이 target을 받는 direct app을 추가하고, 기존 `repotrust scan TARGET`과 같은 실행 로직을 공유하도록 정리했다. README는 venv 활성화 후 `repo-trust TARGET`을 쓰는 흐름으로 갱신했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pip install -e '.[dev]'`, `.venv/bin/repo-trust --version`, `.venv/bin/repo-trust https://github.com/openai/codex --format json --output /tmp/repotrust-direct.json`, `.venv/bin/python -m json.tool /tmp/repotrust-direct.json`, `.venv/bin/repotrust scan . --format json --output /tmp/repotrust-legacy.json`, `.venv/bin/python -m json.tool /tmp/repotrust-legacy.json`, `.venv/bin/repo-trust --help`, `.venv/bin/python -m pytest tests/test_cli.py -q`, `.venv/bin/python -m pytest -q`를 실행했고 전체 테스트 `68 passed`를 확인했다.
- 결과: 새 기본 사용법은 `repo-trust .` 또는 `repo-trust "https://github.com/owner/repo"`이고, 기존 `repotrust scan TARGET`도 호환된다. 현재 active 작업은 없다.

## 042: GitHub Actions CI help-output assertion 실패 수정

- 완료일: 2026-04-28
- 배경: `main` push 후 자동 실행된 GitHub Actions `ci` workflow가 실패했다. workflow는 deploy/publish가 아니라 `push`와 `pull_request`에서 pytest만 실행하는 CI였고, 실패 원인은 CI 환경의 Typer/Rich help 출력에 ANSI color/style code가 포함되면서 raw 문자열 assertion이 깨진 것이었다.
- 변경 내용: `tests/test_cli.py`에 ANSI escape 제거 helper를 추가했다. CLI help/error 출력 테스트는 렌더링 포맷 전체가 아니라 `Usage`, command name, option name, error message 같은 의미 텍스트를 검증하도록 안정화했다.
- 코드/문서: `tests/test_cli.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run view 25032794188 --repo answndud/repo-trust --log-failed`로 실패 원인을 확인했다. `CI=true .venv/bin/python -m pytest tests/test_cli.py -q`는 `25 passed`, `.venv/bin/python -m pytest -q`는 `68 passed`였다.
- 결과: 다음 push에서 GitHub Actions `ci` workflow가 동일한 help-output assertion 문제로 실패하지 않도록 수정됐다. 현재 active 작업은 없다.

## 043: 한국어 상세 HTML 리포트 개선

- 완료일: 2026-04-28
- 배경: `repo-trust . --format html --output report.html` 결과가 영어 중심의 컴팩트한 원자료 나열이라 초보자가 점수, 파일, finding의 의미와 다음 조치를 이해하기 어려웠다.
- 변경 내용: `render_html()`을 한국어 `lang="ko"` 정적 리포트로 확장했다. 전체 판단, 리포트 읽는 법, 검사 영역별 점수 설명, 발견된 파일과 의미, finding별 쉬운 설명/원문 메시지/근거/추천 조치, 다음에 할 일을 추가했다. JSON schema, scanner, scoring logic은 변경하지 않았다.
- 코드/문서: `src/repotrust/reports.py`, `tests/test_scanner.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py tests/test_remote.py tests/test_cli.py -q`는 `58 passed`, `.venv/bin/repo-trust . --format html --output /tmp/repotrust-ko.html`은 HTML 파일을 생성했고 한국어 주요 섹션과 finding 설명을 확인했다. `.venv/bin/python -m pytest -q`는 `68 passed`였다.
- 결과: HTML 리포트가 초보자도 읽고 다음 조치를 이해할 수 있는 한국어 설명형 리포트로 개선됐다. 현재 active 작업은 없다.

## 044: 날짜가 붙은 `result/` 출력 경로 추가

- 완료일: 2026-04-28
- 배경: 리포트 파일을 프로젝트 내부에서 날짜별로 쉽게 찾을 수 있도록 `result/` 폴더에 저장하고 파일명에 실행 날짜를 붙이는 흐름이 필요했다.
- 변경 내용: `--output report.html`처럼 파일명만 넘기면 CLI가 `result/report-YYYY-MM-DD.html`로 저장하도록 output path 정규화 helper를 추가했다. 절대 경로나 `reports/report.html`처럼 디렉터리를 포함한 경로는 사용자가 지정한 위치를 그대로 사용한다. 생성 리포트가 git에 올라가지 않도록 `result/`를 `.gitignore`에 추가했다. README 예시도 새 저장 위치 기준으로 갱신했다.
- 코드/문서: `.gitignore`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `28 passed`, `.venv/bin/repo-trust . --format html --output report.html`은 `result/report-2026-04-28.html`을 생성했다. `.venv/bin/python -m pytest -q`는 `71 passed`였고 `git diff --check`도 통과했다.
- 결과: `repo-trust . --format html --output report.html`의 기본 파일명-only 출력은 날짜가 붙은 `result/` 하위 리포트로 저장된다. 현재 active 작업은 없다.

## 045: README 사용 가이드 중복 제거와 구조 개선

- 완료일: 2026-04-28
- 배경: README의 빠른 시작과 설치 섹션이 같은 명령을 반복하고, 리포트 형식과 자주 쓰는 명령도 중복되어 읽기 흐름이 장황했다.
- 변경 내용: README를 소개, 빠른 시작, 기본 사용법, 리포트 읽는 법, CI, 설정, 예제, 개발자 메모 순서로 재작성했다. 설치 명령은 빠른 시작에서 한 번만 보여주고, 이후에는 실제 사용 명령 중심으로 정리했다. 날짜가 붙은 `result/` 출력도 중복 설명을 줄여 핵심 규칙만 남겼다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `71 passed`를 확인했다.
- 결과: README가 중복 명령을 줄이고 초보자 사용 흐름에 맞춘 간결한 한국어 가이드로 정리됐다. 현재 active 작업은 없다.

## 046: README 전체 재작성

- 완료일: 2026-04-28
- 배경: 이전 README는 중복은 줄었지만 실제 따라 하기 흐름, 섹션 구분, 명령 예시의 자연스러움이 부족했다.
- 변경 내용: README를 설치, 첫 리포트 만들기, 리포트에서 볼 것, 자주 쓰는 명령, GitHub URL 검사, CI, 설정, fixture, 신뢰 신호, 개발자용 검증 순서로 처음부터 다시 작성했다. 설치부터 HTML 리포트 확인까지의 흐름을 앞쪽에 배치하고, 설명과 명령을 분리해 읽기 쉽게 정리했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `71 passed`를 확인했다.
- 결과: README가 실제 사용자 onboarding 흐름에 맞춘 한국어 가이드로 재작성됐다. 현재 active 작업은 없다.

## 047: README 명령 예시 중복 제거와 흐름 개선

- 완료일: 2026-04-28
- 배경: README에 반복 명령과 `자주 쓰는 명령` 섹션이 남아 있었고, 로컬 검사 다음에 바로 URL 검사가 이어지지 않아 사용 흐름이 어색했다. 입력 명령과 생성 파일 예시도 더 명확히 구분할 필요가 있었다.
- 변경 내용: `자주 쓰는 명령` 섹션을 제거하고, 로컬 저장소 검사 바로 다음에 GitHub URL 검사 섹션을 배치했다. 각 예시는 `입력할 명령`, `생성되는 파일 예시`, `예상 출력` 라벨로 분리했다. 반복 명령 블록을 줄이기 위해 가상환경 재활성화 안내는 문장으로만 남겼다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `71 passed`를 확인했다.
- 결과: README의 실행 흐름이 로컬 검사 → URL 검사 → 리포트 해석으로 이어지고, 입력 명령과 출력 파일 예시가 구분된다. 현재 active 작업은 없다.

## 048: README GitHub URL HTML/JSON 저장 사용법 보강

- 완료일: 2026-04-28
- 배경: README가 로컬 폴더 검사 중심으로 설명되어 GitHub URL 검사 결과를 HTML/JSON 파일로 저장하는 방법이 명확하지 않았다.
- 변경 내용: GitHub URL 검사 섹션을 `HTML로 저장`, `JSON으로 저장` 하위 섹션으로 나눴다. 각 섹션에 URL을 직접 검사하는 입력 명령과 `result/codex-YYYY-MM-DD.html`, `result/codex-YYYY-MM-DD.json` 생성 파일 예시를 분리해 추가했다. `--remote` 없이 실행하면 parse-only라는 설명도 함께 정리했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `71 passed`를 확인했다.
- 결과: README에서 GitHub URL 검사 결과를 HTML/JSON으로 저장하는 사용법을 바로 확인할 수 있다. 현재 active 작업은 없다.

## 049: GitHub Actions CI workflow 제거

- 완료일: 2026-04-28
- 배경: 이 프로젝트에서는 push마다 GitHub Actions에서 pytest를 자동 실행하는 기능이 불필요하다고 판단했다.
- 변경 내용: `.github/workflows/ci.yml`을 삭제해 push/pull_request 자동 CI 실행을 중단했다. `.github/dependabot.yml`은 Actions workflow가 아니므로 유지했다.
- 코드/문서: `.github/workflows/ci.yml`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `71 passed`를 확인했다. `.github`에는 `.github/dependabot.yml`만 남았다.
- 결과: 앞으로 `main`에 push해도 이 저장소의 `ci` GitHub Actions workflow는 실행되지 않는다. 현재 active 작업은 없다.

## 050: CLI UX와 terminal dashboard 재설계

- 완료일: 2026-04-28
- 배경: 공식 사용법이 `repo-trust URL --remote --format html --output codex.html`처럼 긴 옵션 조합에 의존해 상용 CLI처럼 보이지 않았고, README에서도 입력 명령과 생성 파일 흐름이 충분히 직관적이지 않았다.
- 변경 내용: `repo-trust`를 `html`, `json`, `check` command group으로 전환했다. `repo-trust html/json/check <github-url>`은 GitHub remote scan을 기본으로 실행하고, 네트워크 없는 URL 파싱은 `--parse-only`로 선택하게 했다. HTML/JSON 명령은 기본적으로 `result/<target>-YYYY-MM-DD.<ext>`에 저장한다. Rich 기반 브랜드 헤더와 `RepoTrust Dashboard`를 stderr에 출력하도록 추가했고, 기존 `repotrust scan`은 legacy compatibility용으로 유지했다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/rules.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/prd.md`, `docs/trd.md`, `docs/adr.md`, `docs/domain-context.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `74 passed`를 확인했다. `git diff --check`도 통과했다. `.venv/bin/repo-trust --help`, `.venv/bin/repo-trust html . --output /tmp/repotrust-final.html`, `.venv/bin/repo-trust check https://github.com/openai/codex --parse-only` smoke check를 확인했다.
- 결과: 공식 CLI는 `repo-trust html URL`, `repo-trust json URL`, `repo-trust check URL`, `repo-trust html .` 흐름으로 정리됐고, README도 새 명령 기준의 한국어 사용자 가이드로 갱신됐다. 현재 active 작업은 없다.

## 051: Interactive CLI launcher와 richer dashboard

- 완료일: 2026-04-28
- 배경: `repo-trust`를 처음 실행했을 때 help만 출력되는 흐름은 제품 CLI처럼 보이지 않았고, terminal dashboard도 점수와 finding 수 위주라 OSINT 도구 같은 정보 밀도와 시각적 인상이 부족했다.
- 변경 내용: `repo-trust` 무인자 실행 시 Rich 기반 interactive launcher를 열어 로컬 HTML 검사, GitHub URL HTML/JSON 검사, 빠른 terminal check, help, quit을 선택할 수 있게 했다. `repo-trust --help`와 `repo-trust html/json/check`는 기존처럼 직접 실행된다. 대시보드는 점수/risk/findings/output/next action 패널에 category score bar와 detected file evidence snapshot을 추가했다.
- 코드/문서: `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/prd.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `76 passed`를 확인했다. `printf 'q\n' | .venv/bin/repo-trust`로 interactive launcher smoke를 확인했고, `.venv/bin/repo-trust html . --output /tmp/repotrust-richer-dashboard.html`로 richer dashboard smoke를 확인했다.
- 결과: 사용자는 `repo-trust`만 입력해 메뉴에서 검사 흐름을 선택할 수 있고, 직접 명령을 실행해도 더 풍부한 terminal dashboard를 볼 수 있다. 현재 active 작업은 없다.

## 052: Console Mode product shell 분리

- 완료일: 2026-04-28
- 배경: 기존 `repo-trust` 무인자 실행은 `cli.py` 안에 prompt, 화면, workflow routing이 섞여 있어 Console Mode와 Command Mode가 코드와 UX 양쪽에서 분리되지 않았다.
- 변경 내용: `src/repotrust/console.py`를 추가해 Console Mode를 별도 모듈로 분리했다. Console Mode 첫 화면은 제품 헤더, workflow cards, 최근 리포트 요약, command shortcuts를 보여준다. 선택 가능한 workflow는 로컬 HTML, GitHub HTML, GitHub JSON, quick check, recent reports, help, quit으로 확장했다. Help text는 lazy callback으로 처리해 `repo-trust` 실행 시 stdout help가 섞이지 않게 했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/cli.py`, `tests/test_cli.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`를 실행했고 `34 passed`를 확인했다. Console launcher, local HTML workflow, recent reports workflow, `repo-trust --help` 비-launcher 동작을 테스트로 고정했다.
- 결과: Console Mode가 Command Mode와 별도 코드 경계로 분리됐고, `repo-trust` 무인자 실행은 최근 리포트 탐색까지 포함하는 제품형 shell 화면으로 동작한다.

## 053: Command Mode assessment renderer 분리

- 완료일: 2026-04-28
- 배경: 직접 명령(`repo-trust html/json/check`)의 dashboard가 Console Mode와 같은 `cli.py` helper에 섞여 있었고, 화면도 OSINT/보안 도구처럼 판단, 근거, finding, 다음 조치가 분리된 구조가 아니었다.
- 변경 내용: `src/repotrust/dashboard.py`를 추가해 Command Mode terminal assessment renderer를 별도 모듈로 분리했다. 직접 명령 결과는 `COMMAND MODE` header, `Trust Assessment`, `Risk Breakdown`, `Evidence`, `Top Findings`, `Next Actions` 섹션으로 출력된다. Legacy `repotrust scan`은 `RepoTrust Summary` 출력으로 유지했다. README, architecture, testing docs를 Console Mode/Command Mode 분리 구조와 새 dashboard 용어에 맞췄다.
- 코드/문서: `src/repotrust/dashboard.py`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `77 passed`를 확인했다. `git diff --check`도 통과했다. `printf '5\n' | .venv/bin/repo-trust`로 Console Mode recent reports smoke를 확인했고, `.venv/bin/repo-trust html . --output /tmp/repotrust-command-dashboard.html`로 Command Mode assessment dashboard smoke를 확인했다.
- 결과: Console Mode와 Command Mode가 코드와 UX에서 분리됐고, 직접 명령 결과 화면은 판정, 리스크 분해, 근거, 주요 finding, 다음 행동 중심의 제품형 terminal assessment로 정리됐다. 현재 active 작업은 없다.

## 054: Assessment model and report trust upgrade

- 완료일: 2026-04-28
- 배경: `result/` HTML 리포트가 판단 이유와 검사 프로세스를 충분히 설명하지 못했고, GitHub API rate limit처럼 실제 파일을 보지 못한 실행도 높은 점수처럼 보일 수 있었다. 사용자는 missing과 unknown, 전체 검사와 부분/실패 검사가 명확히 구분되기를 원했다.
- 변경 내용: JSON schema를 `1.1`로 올리고 `ScanResult`에 `assessment`를 추가했다. Assessment는 `verdict`, `confidence`, `coverage`, `summary`, `reasons`, `next_actions`를 제공한다. `target.github_not_fetched`, remote failure, partial scan, README content unavailable, missing local path에 total score cap을 적용했다. `src/repotrust/evidence.py`를 추가해 HTML과 terminal dashboard가 같은 found/missing/unknown evidence matrix를 사용하도록 했다. HTML report는 `Assessment`, `Assessment Process`, `Evidence Matrix`, `Risk Breakdown`, `Why This Score`, `Prioritized Findings`, `Next Actions` 중심으로 재구성했고 terminal dashboard에도 confidence/coverage/unknown 상태를 표시했다.
- 코드/문서: `src/repotrust/models.py`, `src/repotrust/scoring.py`, `src/repotrust/evidence.py`, `src/repotrust/reports.py`, `src/repotrust/dashboard.py`, `tests/test_cli.py`, `tests/test_remote.py`, `tests/test_scanner.py`, `README.md`, `CHANGELOG.md`, `docs/trd.md`, `docs/domain-context.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`를 실행했고 `77 passed`를 확인했다. `git diff --check`도 통과했다. `.venv/bin/repo-trust html . --output /tmp/repotrust-local.html` smoke는 local full coverage/high confidence dashboard와 HTML을 생성했다. `.venv/bin/repo-trust html https://github.com/openai/codex --output /tmp/repotrust-codex.html` smoke는 실제 GitHub rate limit 상황에서 score 60, `insufficient_evidence`, low confidence, failed coverage, all unknown evidence로 표시됨을 확인했다.
- 결과: 불완전한 scan이 더 이상 adoption-ready처럼 보이지 않고, 사용자는 점수뿐 아니라 검사 완성도, 판단 신뢰도, unknown evidence, 다음 조치를 함께 볼 수 있다. 현재 active 작업은 없다.

## 055: Korean community launch readiness와 README review fixes

- 완료일: 2026-04-28
- 배경: 한국어 커뮤니티 공개 전에 README만 읽고 Console Mode와 Command Mode를 구분해 사용할 수 있어야 했고, self-scan도 공개 전 신뢰 신호 기준을 만족해야 했다. README review에서 `check` 예시, Console/Command 개념 구분, recent reports 표현, GitHub URL 출력 안정성 설명이 부족하다는 문제가 발견됐다.
- 변경 내용: README에 Console Mode와 Command Mode를 비교하는 표를 추가했다. Console Mode의 5번 workflow와 실제 출력 문구를 `List recent reports`로 수정했다. `repo-trust check` 예시는 파일을 저장하지 않는다고 명시하고, GitHub URL 결과는 API 응답, rate limit, 인증 상태, 저장소 변경에 따라 달라질 수 있다고 설명했다. GitHub Actions pytest CI workflow를 복구해 self-scan에서 CI evidence가 found로 표시되도록 했다. `SECURITY.md`, `CHANGELOG.md`, testing/domain/TRD docs도 schema 1.1 assessment와 public readiness 기준에 맞췄다.
- 코드/문서: `README.md`, `SECURITY.md`, `.github/workflows/ci.yml`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`, `docs/architecture.md`, `docs/domain-context.md`, `docs/testing-and-validation.md`, `docs/trd.md`, `src/repotrust/console.py`, assessment 관련 source/tests를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `80 passed`였다. `git diff --check`도 통과했다. `.venv/bin/repo-trust json . --output /tmp/repotrust-self.json`, `.venv/bin/python -m json.tool /tmp/repotrust-self.json`, `.venv/bin/repo-trust html . --output /tmp/repotrust-self.html`를 실행했고 self-scan은 100/100, A, `usable_by_current_checks`, high confidence, full coverage, finding 0개였다. `.venv/bin/repo-trust check https://github.com/openai/codex --parse-only`는 70/100, `insufficient_evidence`, low confidence, metadata-only coverage로 표시됐다. `printf 'q\n' | .venv/bin/repo-trust`로 Console Mode 문구도 확인했다.
- 결과: README review findings를 반영했고, 자체 self-scan은 한국어 커뮤니티 공개 전 readiness gate를 만족한다. 현재 active 작업은 없다.

## 056: Korean Console Mode entrypoint

- 완료일: 2026-04-28
- 배경: 기본 `repo-trust` Console Mode는 영어 workflow를 유지하되, 한국어 사용자가 같은 기능을 한국어 메뉴와 프롬프트로 사용할 수 있는 별도 진입점이 필요했다.
- 변경 내용: `repo-trust-kr` console script를 추가하고 product CLI command group을 공유하게 했다. `repo-trust-kr` 무인자 실행은 한국어 Console Mode를 보여주며, `html/json/check` 직접 명령은 기존 Command Mode 계약과 같은 동작을 유지한다. Console Mode 문구를 locale-aware table로 분리하고 README에 English Console Mode, Korean Console Mode, Command Mode 차이를 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/cli.py`, `src/repotrust/console.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `39 passed`였다. `.venv/bin/python -m pip install -e '.[dev]'`로 새 script를 설치했다. `.venv/bin/python -m pytest -q`는 `84 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `.venv/bin/repo-trust-kr --version`, `.venv/bin/repo-trust-kr --help`를 smoke check로 확인했다.
- 결과: `repo-trust`는 영어 Console Mode, `repo-trust-kr`은 한국어 Console Mode로 동작하며, 리포트/JSON/stdout contract와 Command Mode 동작은 유지된다. 현재 active 작업은 없다.

## 057: Localized direct command help

- 완료일: 2026-04-28
- 배경: Console Mode는 한국어 진입점이 생겼지만 `repo-trust --help`와 direct command help는 영어만 제공해 한국어 사용자가 옵션 의미를 바로 이해하기 어려웠다.
- 변경 내용: product CLI의 기본 help option을 커스텀 help selector로 바꿔 `--help` 실행 시 `1. English`, `2. 한국어` 중 선택하게 했다. Root help와 `html`, `json`, `check` command help에 영어/한국어 문구를 제공한다. `repo-trust`와 `repo-trust-kr` 모두 같은 help selector를 공유하고, legacy `repotrust scan --help`는 기존 Typer help로 유지했다.
- 코드/문서: `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `42 passed`였다. `.venv/bin/python -m pytest -q`는 `87 passed`였다. `.venv/bin/python -m pip install -e '.[dev]'`도 통과했다. `git diff --check`도 통과했다. `printf '2\n' | .venv/bin/repo-trust --help`, `printf '2\n' | .venv/bin/repo-trust html --help`, `printf '2\n' | .venv/bin/repo-trust-kr --help`, `printf '2\n' | .venv/bin/repo-trust json --help`, `printf '1\n' | .venv/bin/repo-trust-kr check --help`를 smoke check로 확인했다.
- 결과: 사용자는 root와 direct command help에서 영어 또는 한국어 도움말을 선택할 수 있고, 기존 scan/report 동작과 JSON/stdout contract는 유지된다. 현재 active 작업은 없다.
