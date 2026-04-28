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
