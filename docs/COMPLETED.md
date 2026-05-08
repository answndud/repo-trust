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

## 058: Korean product execution UX

- 완료일: 2026-04-28
- 배경: `repo-trust-kr`은 콘솔과 도움말은 한국어였지만 실제 검사 실행 후 command header, dashboard, 저장 안내, next action 일부가 영어라 초보 사용자가 결과를 바로 이해하기 어려웠다.
- 변경 내용: `repo-trust-kr html/json/check` 실행 경로에 locale을 전달하고, command header, write notice, trust assessment, risk breakdown, evidence, top findings, verbose findings, next actions를 한국어로 렌더링하게 했다. 한국어 check 모드에서는 영어 Markdown report block을 숨기고 한국어 대시보드만 보여준다. 고정 finding message와 recommendation, evidence label, severity, category label도 한국어 매핑을 추가했다. `repo-trust` 영어 UX와 JSON schema 1.1 contract는 유지했다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/console.py`, `src/repotrust/dashboard.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `44 passed`였다. `.venv/bin/python -m pytest -q`는 `89 passed`였다. `.venv/bin/python -m pip install -e '.[dev]'`도 통과했다. `git diff --check`도 통과했다. `.venv/bin/repo-trust-kr check .`, `.venv/bin/repo-trust-kr html . --output /tmp/repotrust-kr.html`, `.venv/bin/repo-trust-kr check tests/fixtures/repos/risky-install`를 smoke check로 확인했다.
- 결과: `repo-trust-kr`은 메뉴, 도움말, 실행 상태, 대시보드, finding 설명, 다음 행동 안내까지 한국어 중심으로 동작한다. 현재 active 작업은 없다.

## 059: README latest UX refresh

- 완료일: 2026-04-28
- 배경: 최신 CLI는 `repo-trust-kr` 한국어 콘솔/대시보드, 선택형 help, Command Mode 자동 저장 규칙을 갖췄지만 README가 기능 누적 방식으로 길어져 초보자가 읽는 흐름이 다소 복잡했다.
- 변경 내용: README를 설치 빠른 시작, 사용 방식, Console Mode, Command Mode, 결과 파일 규칙, 도움말, parse-only, 리포트 해석, 실패 기준, config, 신뢰 신호 순서로 전면 재구성했다. 입력 명령과 생성 파일 예시를 분리하고, `repo-trust-kr` 한국어 UX를 기본 진입점으로 설명했다. README self-scan rule이 인식하도록 Installation/Usage heading도 유지했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `89 passed`였다. `git diff --check`도 통과했다. README diff를 검토해 `check`가 파일을 저장하지 않는 점, Console/Command Mode 구분, 최근 리포트 목록 동작, GitHub URL 예시의 변동 가능성 안내가 유지됨을 확인했다.
- 결과: README가 최신 개발 상태와 맞고, 초보자가 한국어 콘솔에서 시작해 HTML/JSON 저장과 터미널 점검까지 따라갈 수 있는 구조가 됐다. 현재 active 작업은 없다.

## 060: Dashboard i18n table extraction

- 완료일: 2026-04-28
- 배경: 한국어 대시보드 UX가 확장되면서 `dashboard.py`에 Rich 렌더링 함수와 번역 table, finding message/recommendation mapping이 함께 쌓여 유지보수 경계가 흐려졌다.
- 변경 내용: `src/repotrust/dashboard_i18n.py`를 추가해 dashboard label, evidence/status label, beginner summary, next action, finding message, recommendation 번역을 분리했다. `dashboard.py`는 새 i18n helper를 import해 panel/table 렌더링과 score/risk badge 조립에 집중하도록 정리했다.
- 코드/문서: `src/repotrust/dashboard.py`, `src/repotrust/dashboard_i18n.py`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `89 passed`였다. `.venv/bin/repo-trust-kr check tests/fixtures/repos/risky-install`로 한국어 command header, dashboard, finding message, recommendation 번역 smoke를 확인했다. `git diff --check`도 통과했다.
- 결과: Command Mode dashboard 렌더러와 locale 문구 mapping이 분리됐고, 사용자-facing CLI 동작과 JSON/report contract는 변경되지 않았다. 현재 active 작업은 없다.

## 061: Console i18n table extraction

- 완료일: 2026-04-28
- 배경: `console.py`도 Console Mode shell 흐름과 영어/한국어 workflow 문구 table을 한 파일에 함께 갖고 있어, dashboard i18n 분리 후에도 locale data 책임이 일관되지 않았다.
- 변경 내용: `src/repotrust/console_i18n.py`를 추가해 Console Mode title, mission, workflow menu, prompt, recent report 문구를 분리했다. `console.py`는 새 helper를 import해 interactive shell 흐름, workflow routing, recent report listing에 집중하도록 정리했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `89 passed`였다. `printf 'q\n' | .venv/bin/repo-trust`와 `printf 'q\n' | .venv/bin/repo-trust-kr`로 영어/한국어 Console Mode smoke를 확인했다. `git diff --check`도 통과했다.
- 결과: Console Mode shell과 locale 문구 mapping이 분리됐고, `repo-trust`/`repo-trust-kr` 무인자 실행 UX와 Command Mode 동작은 유지된다. 현재 active 작업은 없다.

## 062: README review hardening

- 완료일: 2026-04-28
- 배경: README review findings는 최신 README에 대부분 반영되어 있었지만, 같은 오해가 다시 생기지 않도록 Console Mode/Command Mode 차이, `check` 저장 동작, recent reports 동작, GitHub URL 예시 변동성을 더 직접적으로 설명할 필요가 있었다.
- 변경 내용: Usage 섹션에 Console Mode와 Command Mode의 진입 방식 차이를 문장으로 추가하고, `check`는 두 방식 모두 파일을 저장하지 않는다고 명시했다. Console Mode 5번 workflow는 파일을 열거나 브라우저를 실행하지 않고 목록만 보여준다고 보강했다. GitHub `check` 화면 예시는 고정 예상값이 아니라 출력 형태 예시이며 실제 값이 GitHub API 응답, rate limit, 인증 상태, 저장소 상태에 따라 달라질 수 있다고 예시 앞에 배치했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `89 passed`였다. `git diff --check`도 통과했다.
- 결과: README review findings 4개 항목이 현재 문서 기준에서 명확히 방지되도록 보강됐다. 현재 active 작업은 없다.

## 063: CLI help i18n extraction

- 완료일: 2026-04-28
- 배경: Console Mode와 Command Mode dashboard 문구를 각각 i18n 모듈로 분리했지만, `cli.py`에는 product help text와 help language selector 문구가 남아 있어 command wiring과 locale data가 섞여 있었다.
- 변경 내용: `src/repotrust/help_i18n.py`를 추가해 root/html/json/check product help text, help option label, help language selector, localized help lookup을 분리했다. `cli.py`는 help callback과 Console Mode help에서 새 helper를 호출하도록 정리했다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `docs/architecture.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `89 passed`였다. `printf '2\n' | .venv/bin/repo-trust --help`와 `printf '2\n' | .venv/bin/repo-trust html --help`로 한국어 help selector와 direct command help를 확인했다. `git diff --check`도 통과했다.
- 결과: CLI help 문구 data와 command orchestration이 분리됐고, `repo-trust`/`repo-trust-kr` help 언어 선택 동작은 유지된다. 현재 active 작업은 없다.

## 064: Kali-style terminal UX repair

- 완료일: 2026-04-28
- 배경: 이전 `e882fcc Redesign terminal UX theme`는 `repo-trust // console` 스타일과 green 중심 색상이 실제 Kali-like terminal UX와 맞지 않았다.
- 변경 내용: `git revert --no-commit e882fcc`로 실패한 변경을 되돌린 뒤, `src/repotrust/terminal_theme.py`를 Kali prompt primitive 중심으로 다시 작성했다. Console Mode, Command Mode dashboard, help selector, legacy summary가 `┌──(repotrust㉿...)-[...]`와 `└─$` 구조를 공유한다. Product terminal renderer에서 `cyan`, `magenta`, `pink`, `bright_green`, `green`, 실패 화면 문구가 재도입되지 않도록 CLI test를 추가했다. `repo-trust check`는 Markdown block을 앞에 붙이지 않고 terminal dashboard만 출력한다. JSON/HTML/scoring/assessment contract는 변경하지 않았다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/terminal_theme.py`, `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/dashboard.py`, `src/repotrust/dashboard_i18n.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `90 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `.venv/bin/repo-trust check .`, `.venv/bin/repo-trust-kr check .`, `printf '2\n' | .venv/bin/repo-trust --help`, `.venv/bin/repo-trust html . --output /tmp/repotrust-kali-terminal.html` smoke를 확인했다.
- 결과: 터미널 UX는 Kali prompt/MOTD 스타일로 복구됐고, 이미 push된 실패 커밋은 force push 없이 corrective commit으로 바로잡을 준비가 됐다. 현재 active 작업은 없다.

## 065: Console Mode alternate screen

- 완료일: 2026-04-28
- 배경: Console Mode가 기존 터미널 내역 위에 바로 출력되어 화면이 지저분해 보였고, 사용자는 `git log --oneline`처럼 이전 내역이 보이지 않는 새 화면 느낌을 원했다.
- 변경 내용: `run_console_mode()`가 실제 TTY에서 Rich alternate screen을 사용하도록 바꿨다. `q`로 종료할 때는 바로 원래 화면으로 돌아가고, scan/recent/help workflow를 실행한 뒤에는 결과를 읽을 수 있도록 Enter pause 후 원래 화면으로 복귀한다. non-TTY/test runner에서는 기존 출력 flow를 유지한다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `92 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `.venv/bin/repo-trust check .` smoke를 확인했다.
- 결과: 실제 터미널에서 Console Mode는 pager처럼 별도 화면으로 열리고, 테스트/파이프 환경에서는 기존 CLI contract를 유지한다. 현재 active 작업은 없다.

## 066: Console Mode professional input prompt

- 완료일: 2026-04-28
- 배경: Console Mode의 선택 입력부가 기본 Rich Prompt처럼 보여 전문적인 Kali-style 콘솔 화면과 맞지 않았다.
- 변경 내용: Console Mode menu 입력을 local helper로 렌더링해 `workflow  01-06 | q` / `워크플로우  01-06 | q` 안내와 별도 `└─$` command line으로 분리했다. `1`과 `01`을 모두 같은 workflow로 normalize하고, non-TTY transcript에서는 입력 prompt 뒤 줄바꿈을 보정했다. workflow target prompt도 같은 `└─$` command line을 공유한다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `92 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `printf '05\n' | .venv/bin/repo-trust` smoke를 확인했다.
- 결과: 번호 선택부는 기본 choices suffix 없이 command prompt처럼 보이며, zero-padded workflow 번호도 지원한다. 현재 active 작업은 없다.

## 067: Console Mode ASCII input guide

- 완료일: 2026-04-28
- 배경: `workflow  01-06 | q` 한 줄 안내만으로는 사용자가 번호를 어떻게 입력해야 하는지 직관적으로 이해하기 어려웠다.
- 변경 내용: Console Mode 선택 입력부에 ASCII 안내창을 추가해 선택 방법, 입력 예시, 종료 키를 함께 보여준다. 안내창은 `01-06`, `Enter`, `q`를 명확히 표시하고, 실제 입력은 기존 Kali-style `└─$` command prompt에서 받는다. 한국어 폭 정렬은 Rich `cell_len` 기준으로 보정했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `92 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `printf '05\n' | .venv/bin/repo-trust` smoke를 확인했다.
- 결과: 메뉴 번호 입력부가 설명창과 입력창으로 분리되어, 처음 보는 사용자도 `01` 같은 번호를 입력하고 Enter를 누르면 된다는 흐름을 바로 읽을 수 있다. 현재 active 작업은 없다.

## 068: Console Mode input guide simplification

- 완료일: 2026-04-28
- 배경: 워크플로우 선택 설명창은 화면을 다시 무겁게 만들었고, 사용자는 설명창 자체가 필요 없다고 판단했다.
- 변경 내용: Console Mode의 ASCII 설명 박스와 관련 helper/i18n key를 제거했다. 메뉴 아래에는 `select 01-06, q to quit, then Enter` / `01-06 선택, q 종료, 입력 후 Enter` 한 줄 안내와 `└─$` 입력줄만 남겼다. `1`과 `01` normalize 동작은 유지했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `92 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `printf '05\n' | .venv/bin/repo-trust` smoke를 확인했다.
- 결과: Console Mode 선택부는 설명 박스 없이 간결한 힌트와 Kali-style prompt만 남는다. 현재 active 작업은 없다.

## 069: Console Mode product dashboard redesign

- 완료일: 2026-04-28
- 배경: Console Mode가 여전히 메뉴와 설명을 한 화면에 나열하는 구조라 정보 위계와 interaction focus가 약했다. 사용자는 production-grade CLI UX 기준으로 Home/Input/Processing/Result 흐름과 shortcut 중심 조작을 요구했다.
- 변경 내용: Home 화면을 `tool/signal`, primary actions, recent reports, controls로 분리했다. Primary actions는 `[G] GitHub report`, `[L] Local report`, `[C] Quick check`, `[J] JSON export` 네 개로 제한하고, `[R] recent`, `[?] help`, `[Q] quit`는 보조 controls로 내렸다. 기존 `1`-`6`, `01`-`06` 입력은 shortcut으로 normalize해 호환성을 유지했다. workflow 실행 전 processing feedback을 출력하고, GitHub shortcut 입력 flow를 테스트로 고정했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `93 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `printf 'c\n.\n' | .venv/bin/repo-trust` smoke를 확인했다.
- 결과: Console Mode는 action-driven terminal dashboard 형태가 되었고, input과 processing 단계가 Home 화면과 분리되어 보인다. 현재 active 작업은 없다.

## 070: Console Mode focused interaction redesign

- 완료일: 2026-04-28
- 배경: shortcut 기반 Home으로 바꾼 뒤에도 Home 화면이 여전히 정적이고, `signal`, recent report 목록, 시스템 메시지형 prompt가 남아 있어 시선 흐름과 선택 피드백이 약했다.
- 변경 내용: Console Mode Home을 `RepoTrust vX`, 한 줄 가치 설명, separator, `Select action`, 4개 primary actions, compact recent count, secondary controls만 남긴 구조로 줄였다. recent report 목록은 `[R]` 선택 시에만 열리도록 Home에서는 count로 축약했다. 선택 후 `Selected:` 상태를 출력하고, GitHub URL 입력에는 예시 URL을 보여준다. processing copy는 짧은 `Running analysis...`로 바꿨다. action은 cyan, selected feedback은 green 스타일을 허용하도록 terminal visual contract를 갱신했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `93 passed`였다. `git diff --check`도 통과했다. `printf 'q\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr`, `printf 'g\nhttps://github.com/owner/repo\n' | .venv/bin/repo-trust`, `printf 'c\n.\n' | .venv/bin/repo-trust` smoke를 확인했다.
- 결과: Console Mode는 설명 중심 화면에서 focused terminal dashboard로 바뀌었고, Home/Input/Processing/Result 단계가 눈에 구분된다. 현재 active 작업은 없다.

## 071: Console Mode back navigation polish

- 완료일: 2026-04-28
- 배경: action을 잘못 선택했을 때 입력 단계에서 Home으로 돌아갈 방법이 없었고, action 목록 shortcut 표기가 controls의 `[R]` 형식과 일관되지 않았다.
- 변경 내용: Home action 표기를 `[G]`, `[L]`, `[C]`, `[J]`로 통일했다. target 입력 단계에 `[B] Back` / `[B] 뒤로` 안내를 추가하고, `b` 또는 `B` 입력 시 scan을 실행하지 않고 Home으로 돌아가도록 Console Mode loop를 조정했다. Back 경로는 테스트로 고정했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `94 passed`였다. `git diff --check`도 통과했다. `printf 'l\nb\nq\n' | .venv/bin/repo-trust`, `printf 'g\nhttps://github.com/owner/repo\n' | .venv/bin/repo-trust`, `printf 'q\n' | .venv/bin/repo-trust-kr` smoke를 확인했다.
- 결과: Console Mode는 잘못 선택한 action에서 빠져나올 수 있고, shortcut 표기는 Home과 controls 전체에서 일관된 bracket 형식을 사용한다. 현재 active 작업은 없다.

## 072: Result dashboard interface redesign

- 완료일: 2026-04-28
- 배경: 기능과 구조는 충분해졌지만 결과 화면이 `Wrote...`, `Trust Assessment`, `Risk Breakdown`, `Evidence`를 순서대로 흘리는 로그 출력처럼 보여 핵심 판단이 약했다.
- 변경 내용: terminal dashboard를 `RESULT`, `WHY`, `ACTIONS`, `REPORT`, `DETAILS` 블록으로 재구성했다. 저장 파일 안내는 결과 상단 로그에서 제거하고 `Open full report:` 블록으로 내렸다. failed/incomplete coverage에서는 세부 점수와 evidence table을 숨기고 unavailable 메시지를 보여준다. finding ID 대신 사용자에게 의미 있는 message와 recommendation을 WHY에 먼저 표시한다. missing local path는 전용 next action과 예시 명령을 제공한다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/dashboard.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `94 passed`였다. `git diff --check`도 통과했다. `.venv/bin/repo-trust check /tmp/does-not-exist`, `.venv/bin/repo-trust check .`, `.venv/bin/repo-trust html . --output /tmp/repotrust-result-ui.html` smoke를 확인했다.
- 결과: 결과 화면은 로그 나열이 아니라 판단 중심 인터페이스로 보이며, 실패/불충분 상태에서는 유효하지 않은 세부 표를 보여주지 않는다. 현재 active 작업은 없다.

## 073: Remote SECURITY.md parity 수정

- 완료일: 2026-04-29
- 배경: Local scan은 root `SECURITY.md`와 `.github/SECURITY.md`를 모두 보안 정책 신호로 인정하지만, Remote GitHub scan은 root `SECURITY.md`만 확인해 `.github/SECURITY.md`를 사용하는 저장소를 잘못 감점할 수 있었다.
- 변경 내용: Remote scan이 root contents에서 `SECURITY.md`를 찾지 못하면 `.github/SECURITY.md` contents endpoint를 추가로 조회하도록 했다. 해당 파일이 확인되면 `DetectedFiles.security`에 반영하고, 조회 실패는 `remote.github_partial_scan`과 unknown evidence로 표시해 `security.no_policy` 감점으로 오해하지 않도록 했다.
- 코드/문서: `src/repotrust/remote.py`, `src/repotrust/evidence.py`, `src/repotrust/remote_markers.py`, `tests/test_remote.py`, `docs/trd.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_remote.py -q`에서 `20 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `96 passed`를 확인했다. `.venv/bin/repo-trust check https://github.com/openai/codex --parse-only`는 parse-only capped result를 정상 출력했다.
- 결과: Remote GitHub scan이 `.github/SECURITY.md`를 local scan과 같은 보안 정책 신호로 다룬다. 다음 작업은 `Install command evidence extractor 도입`이다.

## 074: Install command evidence extractor 도입

- 완료일: 2026-04-29
- 배경: Install Safety rule이 README 전체 텍스트에서 위험 패턴을 검색해 `do not use sudo` 같은 경고 문장이나 설치 섹션 밖 anti-pattern 예시를 실제 설치 명령처럼 오판할 수 있었다.
- 변경 내용: README Installation/Setup 섹션 안의 command-like line만 추출하는 helper를 추가하고, risky install pattern matching이 이 evidence 목록만 검사하도록 바꿨다. 설치 섹션의 실제 `curl ... | sh`, `bash <(curl ...)`, `python -c`, direct VCS install은 계속 finding으로 남긴다.
- 코드/문서: `src/repotrust/rules.py`, `tests/test_scanner.py`, `docs/domain-context.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py -q`에서 `19 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `98 passed`를 확인했다. `.venv/bin/repo-trust check tests/fixtures/repos/risky-install`는 기존 risky install finding을 정상 출력했다.
- 결과: Install Safety가 실제 설치 명령 근거 중심으로 동작해 자연어 경고와 설치 섹션 밖 예시에 대한 false positive를 줄인다. 다음 작업은 `GitHub subpath target 처리 명확화`다.

## 075: GitHub subpath target 처리 명확화

- 완료일: 2026-04-29
- 배경: GitHub `tree`/`blob` URL의 `subpath`는 파싱되지만 remote scan은 repository root 기준으로 파일과 README를 평가했다. 이 상태는 monorepo 하위 패키지를 평가한 것처럼 보이는 오해를 만들 수 있었다.
- 변경 내용: `target.github_subpath_unsupported` finding을 추가해 subpath URL이 하위 폴더 단독 평가가 아님을 명시했다. Remote subpath scan은 score cap 85, coverage `partial`, verdict `usable_after_review`로 표시한다. Parse-only subpath scan은 기존 parse-only cap 70을 유지하되 subpath limitation finding과 local checkout next action을 함께 보여준다.
- 코드/문서: `src/repotrust/rules.py`, `src/repotrust/scanner.py`, `src/repotrust/remote.py`, `src/repotrust/models.py`, `src/repotrust/scoring.py`, `src/repotrust/reports.py`, `src/repotrust/dashboard_i18n.py`, `tests/test_scanner.py`, `tests/test_remote.py`, `docs/domain-context.md`, `docs/trd.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py tests/test_remote.py -q`에서 `41 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `100 passed`를 확인했다. `.venv/bin/repo-trust check https://github.com/owner/repo/tree/main/packages/example --parse-only`는 subpath limitation과 parse-only limitation을 함께 출력했다.
- 결과: GitHub subpath URL report가 repository-root scan과 subdirectory-only scan을 혼동하지 않도록 명확한 finding, cap, next action을 제공한다. 리뷰 finding 3개 처리 milestone은 완료됐다.

## 076: Dependency/package risk scanner 추가

- 완료일: 2026-04-29
- 배경: 기존 dependency manifest 검사는 파일 존재 여부와 lockfile 유무만 보았기 때문에, 설치 중 자동 실행되는 npm lifecycle script나 시간이 지나며 다른 dependency를 설치할 수 있는 unpinned direct dependency를 설명하지 못했다.
- 변경 내용: Local rule layer가 `package.json`, `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`를 보수적으로 읽어 package-level finding을 생성하도록 했다. `dependency.npm_lifecycle_script`는 medium install safety finding으로, `dependency.unpinned_node_dependency`와 `dependency.unpinned_python_dependency`는 low security posture finding으로 추가했다. 기존 `security.no_lockfile`은 그대로 유지하고 exact dependency에는 unpinned finding을 내지 않도록 테스트했다.
- 코드/문서: `src/repotrust/rules.py`, `src/repotrust/reports.py`, `src/repotrust/dashboard_i18n.py`, `tests/test_scanner.py`, `README.md`, `docs/domain-context.md`, `docs/trd.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py -q`에서 `25 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `104 passed`를 확인했다. `.venv/bin/repo-trust check tests/fixtures/repos/good-python`은 `100/100` 결과를 유지했다. 자체 JSON report는 `98/100`으로, unpinned Python dependency low finding만 추가됐고 `json.tool` 검증을 통과했다.
- 결과: RepoTrust가 dependency 채택 판단에 필요한 첫 package-level local risk signal을 제공한다. 다음 작업은 `목적별 assessment profile 분리`다.

## 077: 목적별 assessment profile 분리

- 완료일: 2026-04-29
- 배경: 하나의 verdict만으로는 "설치해도 되는가", "dependency로 넣어도 되는가", "AI agent에게 맡겨도 되는가"라는 서로 다른 질문에 직접 답하기 어려웠다.
- 변경 내용: `AssessmentProfile`을 추가하고 `assessment.profiles.install`, `assessment.profiles.dependency`, `assessment.profiles.agent_delegate`를 JSON contract에 포함했다. 기존 `assessment.verdict`, `confidence`, `coverage`, `summary`, `reasons`, `next_actions`는 유지했고, schema version은 `1.2`로 올렸다. Terminal dashboard, Markdown, HTML report에 목적별 판단을 노출했다. Agent delegation profile은 high finding과 medium install-safety finding을 더 엄격하게 차단한다.
- 코드/문서: `src/repotrust/models.py`, `src/repotrust/reports.py`, `src/repotrust/dashboard.py`, `src/repotrust/dashboard_i18n.py`, `tests/test_scanner.py`, `tests/test_remote.py`, `tests/test_cli.py`, `README.md`, `docs/domain-context.md`, `docs/testing-and-validation.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py tests/test_remote.py tests/test_cli.py -q`에서 `97 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `107 passed`를 확인했다. `.venv/bin/repo-trust json tests/fixtures/repos/risky-install --output /tmp/repotrust-risky.json` 실행 후 `json.tool`과 profile verdict를 확인했다. `git diff --check`도 통과했다.
- 결과: RepoTrust 리포트가 전체 verdict와 함께 목적별 verdict를 제공한다. 다음 작업은 `Remote release/tag freshness 구현`이다.

## 078: Remote release/tag freshness 구현

- 완료일: 2026-04-29
- 배경: release/tag freshness는 유용한 maintenance signal이지만, GitHub Release가 없거나 tags-only 관행인 저장소를 stale로 오판하면 false positive가 크다. package manifest가 있는 remote repository에 한해 확인 가능한 release/tag 날짜만 낮은 심각도로 보고하도록 구현했다.
- 변경 내용: Remote GitHub client에 latest release, tags list, tag commit endpoint를 추가했다. root dependency manifest가 있는 remote repository에서 latest release date를 우선 확인하고, release가 404이면 latest tag commit date로 fallback한다. freshness 기준보다 오래된 경우에만 `remote.release_or_tag_stale` low project hygiene finding을 생성하며, no release/tag practice와 release/tag API failure는 stale finding이나 partial scan으로 바꾸지 않는다.
- 코드/문서: `src/repotrust/remote.py`, `src/repotrust/reports.py`, `src/repotrust/dashboard_i18n.py`, `tests/test_remote.py`, `README.md`, `docs/adr.md`, `docs/domain-context.md`, `docs/prd.md`, `docs/testing-and-validation.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_remote.py -q`에서 `25 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `111 passed`를 확인했다. `git diff --check`도 통과했다.
- 결과: Remote scan이 package-managed 저장소의 오래된 release/tag를 보수적인 low finding으로 설명한다. 다음 작업은 `CI/조직 정책 모드 확장`이다.

## 079: CI/조직 정책 모드 확장

- 완료일: 2026-04-29
- 배경: RepoTrust를 CI와 팀 정책에서 쓰려면 단순 score threshold 외에도 finding 예외, severity 조정, 목적별 profile gate를 명시할 수 있어야 했다.
- 변경 내용: `repotrust.toml` v2 policy로 `[rules] disabled`, `[severity_overrides]`, `[policy.profiles]`를 추가했다. Scanner가 낸 finding set에 config policy를 적용한 뒤 score와 assessment를 다시 계산하도록 했다. `repo-trust gate`와 `repo-trust-kr gate` 명령을 추가해 JSON report를 stdout 또는 `--output`에 먼저 보존하고, score/profile policy 실패를 exit code `1`로 반환한다. invalid policy는 usage error로 처리하고 invalid secret-like value를 stderr에 echo하지 않도록 테스트했다.
- 코드/문서: `src/repotrust/config.py`, `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/adr.md`, `docs/architecture.md`, `docs/domain-context.md`, `docs/prd.md`, `docs/testing-and-validation.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`에서 `53 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `115 passed`를 확인했다. 임시 `repotrust.toml`로 `.venv/bin/repo-trust json . --config <tmp> --output /tmp/repotrust-079.json`와 `.venv/bin/repo-trust gate . --config <tmp>`를 실행하고 두 JSON report를 `json.tool`로 검증했다.
- 결과: RepoTrust가 CI에서 JSON contract를 유지하면서 조직별 예외와 목적별 minimum verdict를 적용할 수 있다. 다음 작업은 `릴리즈 준비와 패키징 smoke`다.

## 080: 릴리즈 준비와 패키징 smoke

- 완료일: 2026-04-29
- 배경: 기능이 늘어난 뒤 release note와 packaging metadata가 현재 동작을 따라오지 못했고, public install 관점에서 product entrypoint와 wheel install smoke를 다시 확인해야 했다.
- 변경 내용: `pyproject.toml`에 license, author, keywords, classifiers, project URLs를 추가했다. `CHANGELOG.md`의 Unreleased 항목을 JSON schema `1.2`, 목적별 profile, config v2, `repo-trust gate`, remote freshness, Korean product CLI 기준으로 갱신했다. README에 release note 위치와 wheel install smoke를 추가하고, testing guide의 packaging verification을 clean wheel install, product/legacy entrypoint 확인, product JSON/gate/HTML와 legacy JSON sample report 검증 절차로 확장했다.
- 코드/문서: `pyproject.toml`, `CHANGELOG.md`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pip install -e '.[dev]'`를 실행해 editable install을 확인했다. `.venv/bin/python -m pytest -q`에서 `115 passed`를 확인했다. `.venv/bin/python -m pip wheel --no-deps . --wheel-dir <tmp>`로 `repotrust-0.1.0-py3-none-any.whl` 생성을 확인했다. 별도 clean venv에 wheel을 설치해 `repo-trust`, `repo-trust-kr`, `repotrust` entrypoint가 모두 `0.1.0`을 출력하는지 확인했다. Clean wheel 환경에서 product JSON, gate JSON, product HTML, legacy JSON sample report를 생성하고 JSON reports를 `json.tool`로 검증했다. Self-scan JSON은 schema `1.2`, score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었다.
- 결과: RepoTrust는 현재 변경 세트 기준 release readiness smoke를 통과했다. 다음 작업은 `CI policy 예시와 config template 추가`다.

## 081: CI policy 예시와 config template 추가

- 완료일: 2026-04-29
- 배경: `repo-trust gate`와 config v2가 구현됐지만, 사용자가 CI에 붙일 때 바로 복사할 sample policy와 GitHub Actions 예시가 없었다.
- 변경 내용: `examples/repotrust.toml`에 score threshold, profile gate, finding disable, severity override를 포함한 CI policy template을 추가했다. `examples/github-actions-repotrust-gate.yml`에는 checkout, Python setup, RepoTrust install, gate 실행, report artifact 업로드 흐름을 담았다. README에는 CI gate 빠른 시작과 실패 예시를 추가했고, testing guide는 committed sample config 기준으로 gate pass/fail smoke를 설명하게 바꿨다. `tests/test_config.py`와 `tests/test_cli.py`가 sample config load, good fixture pass, risky fixture fail-with-json 동작을 검증한다.
- 코드/문서: `examples/repotrust.toml`, `examples/github-actions-repotrust-gate.yml`, `tests/test_config.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_config.py tests/test_cli.py -q`에서 `61 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `118 passed`를 확인했다. `examples/repotrust.toml`로 `repo-trust gate tests/fixtures/repos/good-python --output /tmp/repotrust-example-good.json`을 실행해 exit 0과 JSON 검증을 확인했다. 같은 sample config로 `tests/fixtures/repos/risky-install` gate를 실행해 exit 1과 JSON report 보존을 확인했다.
- 결과: 사용자가 CI policy를 복사해 시작할 수 있는 config/workflow 예시와 검증 경로가 생겼다. 다음 작업은 `Finding catalog와 policy reference 추가`다.

## 082: Finding catalog와 policy reference 추가

- 완료일: 2026-04-29
- 배경: config v2에서 `rules.disabled`와 `severity_overrides`가 가능해졌기 때문에, 사용자가 finding ID를 정책 예외로 다룰 때 ID 의미와 profile/score 영향을 확인할 reference가 필요했다.
- 변경 내용: `docs/finding-reference.md`를 추가해 target, README, install safety, security posture, dependency, project hygiene, remote finding ID를 category, 기본 severity, score cap, policy 사용 기준과 함께 정리했다. README와 AGENTS 문서 맵에서 reference로 연결했다. `tests/test_docs.py`는 `src/repotrust`의 finding ID string literal이 reference 문서에 누락되지 않았는지 검증한다. CHANGELOG에도 finding ID reference 추가를 기록했다.
- 코드/문서: `docs/finding-reference.md`, `tests/test_docs.py`, `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_docs.py -q`에서 `1 passed`를 확인했다. `.venv/bin/python -m pytest -q`에서 `119 passed`를 확인했다. `.venv/bin/repo-trust json tests/fixtures/repos/risky-install --output /tmp/repotrust-catalog-check.json`을 실행했고 JSON은 schema `1.2`, score `51`, grade `F`로 `json.tool` 검증을 통과했다.
- 결과: CI policy와 exception review에서 사용할 stable finding ID reference가 생겼다. 다음 작업은 `JSON report schema reference 추가`다.

## 083: JSON report schema reference 추가

- 완료일: 2026-04-29
- 배경: CI와 외부 도구가 RepoTrust JSON report를 안정적으로 파싱하려면 schema `1.2`의 key 구조, compatibility 기준, purpose profile 위치를 한 문서에서 확인할 수 있어야 했다.
- 변경 내용: `docs/json-report-reference.md`를 추가해 top-level object, `target`, `detected_files`, `findings[]`, `score`, `assessment`, `assessment.profiles` 구조와 enum-like 값, schema compatibility policy, jq/Python parsing 예시를 정리했다. README, AGENTS 문서 맵, TRD, CHANGELOG에서 새 reference로 연결했다.
- 코드/문서: `docs/json-report-reference.md`, `tests/test_docs.py`, `README.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/trd.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_docs.py -q`에서 `2 passed`를 확인했다. `.venv/bin/repo-trust json tests/fixtures/repos/good-python --output /tmp/repotrust-schema-good.json`을 실행해 schema `1.2`, top-level keys, profile keys를 확인했고 `json.tool` 검증을 통과했다. `.venv/bin/python -m pytest -q`에서 `120 passed`를 확인했다. `git diff --check`도 통과했다.
- 결과: JSON report schema `1.2`를 파싱하는 CI와 외부 도구가 따라야 할 key contract와 호환성 기준이 문서화됐다. 다음 작업은 `Release candidate final review와 commit 준비`다.

## 084: Release candidate final review와 commit 준비

- 완료일: 2026-04-29
- 배경: 누적된 post-v1 변경 세트가 product CLI, config/gate, remote scan, assessment profile, docs/tests를 넓게 건드렸기 때문에 commit 전에 범위와 검증 결과를 다시 확인해야 했다.
- 변경 내용: `git status`, `git diff --stat`, untracked 파일 목록을 검토해 변경 범위를 product CLI/gate/config v2, remote scan hardening, assessment profiles, package risk rules, reference docs, CI examples, tests로 분류했다. Untracked 파일인 `docs/finding-reference.md`, `docs/json-report-reference.md`, `examples/`, `tests/test_docs.py`는 의도된 새 문서/예시/테스트 파일로 확인했다. README/CHANGELOG/testing guide의 현재 validation 숫자는 120 tests와 schema `1.2` 기준으로 맞는지 확인했다.
- 코드/문서: 기능 코드는 새로 수정하지 않았다. 작업 상태 문서인 `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`만 release candidate review 결과와 다음 commit 작업에 맞게 갱신했다.
- 검증: `.venv/bin/python -m pytest -q`에서 `120 passed`를 확인했다. `examples/repotrust.toml`로 good fixture gate는 exit 0과 valid JSON을, risky fixture gate는 expected exit 1과 valid JSON을 확인했다. wheel build와 clean venv wheel install을 실행해 `repo-trust`, `repo-trust-kr`, `repotrust` entrypoint가 모두 `0.1.0`을 출력하는지 확인했다. self JSON은 schema `1.2`, score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었다. self HTML, product/legacy fixture JSON, parse-only dashboard, version commands, `git diff --check`도 통과했다.
- 결과: commit 전 blocker는 발견되지 않았다. 추천 commit boundary는 현재 modified 파일과 의도된 untracked 파일 전체를 하나의 release candidate hardening commit으로 묶는 것이다. 추천 commit message는 `Prepare post-v1 release candidate`이다. 다음 작업은 `Release candidate commit 생성`이다.

## 085: Release candidate commit 생성

- 완료일: 2026-04-29
- 배경: release candidate final review에서 blocker가 없음을 확인했으므로, 누적 post-v1 변경 세트를 하나의 commit으로 고정해야 했다.
- 변경 내용: 의도된 modified 파일과 untracked 문서/예시/테스트 파일을 stage하고 `Prepare post-v1 release candidate` commit으로 저장했다. 원격 push, release tag, PyPI 배포는 이번 작업 범위에서 제외했다.
- 코드/문서: commit 대상은 product CLI/gate/config v2, remote scan hardening, assessment profiles, package risk rules, reference docs, CI examples, tests, release readiness docs 전체다.
- 검증: commit 직전 `git status --short`로 대상 파일을 확인하고, `git diff --cached --stat`로 staged 범위를 확인했다. 직전 release candidate review에서 `.venv/bin/python -m pytest -q`, gate sample smoke, wheel clean install smoke, self JSON/HTML smoke, `git diff --check`가 모두 통과했다.
- 결과: release candidate 변경 세트가 로컬 commit으로 고정됐다. 다음 작업은 `Release candidate 원격 반영 여부 결정`이다.

## 086: Release candidate 원격 반영

- 완료일: 2026-04-29
- 배경: release candidate commit `e7c52b3 Prepare post-v1 release candidate`가 로컬 `main`에 생성됐고, 사용자가 다음 단계 진행을 요청했다.
- 변경 내용: `main`이 `origin/main`보다 1커밋 앞선 상태임을 확인한 뒤 `git push origin main`으로 release candidate commit을 GitHub 원격에 반영했다.
- 코드/문서: push 자체에는 기능 코드 변경이 없었다. push 완료 후 작업 상태 문서를 tag/release 결정 단계로 갱신했다.
- 검증: `git status --short --branch`에서 push 전 `main...origin/main [ahead 1]` 상태를 확인했다. `git push origin main`은 `b084ae0..e7c52b3 main -> main`으로 성공했다.
- 결과: post-v1 release candidate가 GitHub `main`에 반영됐다. 다음 작업은 `Release tag 생성 여부 결정`이다.

## 087: Release tag 생성 여부 결정

- 완료일: 2026-04-29
- 배경: GitHub main에 post-v1 release candidate가 반영됐지만, tag/release는 package version과 changelog 의미가 맞을 때만 생성해야 한다.
- 변경 내용: 현재 branch 상태, local/remote tag, package version, changelog heading을 확인했다. Local에는 `v0.1.0` tag가 있지만 remote tag 목록은 비어 있었다. Local `v0.1.0` tag는 `f0a3d70 Avoid remote deductions for unknown metadata` 커밋을 가리키며 현재 HEAD가 아니다. 현재 package version은 `pyproject.toml`과 `src/repotrust/__init__.py` 모두 `0.1.0`이고, post-v1 변경 사항은 `CHANGELOG.md`의 `Unreleased` 아래에 있다.
- 코드/문서: 기능 코드는 변경하지 않았다. `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 tag 판단 결과와 다음 release metadata 작업에 맞게 갱신했다.
- 검증: `git status --short --branch`에서 `main...origin/main` 상태를 확인했다. `git tag --list --sort=version:refname`은 local `v0.1.0`을 반환했다. `git ls-remote --tags origin`은 remote tag가 없음을 보여줬다. `pyproject.toml`, `src/repotrust/__init__.py`, `CHANGELOG.md`의 version/release 상태를 확인했다.
- 결과: 지금 current HEAD에 tag/release를 만들지 않는다. post-v1 변경 범위는 patch보다 크고, 기존 `0.1.0`/`v0.1.0` 의미와 맞지 않으므로 먼저 `0.2.0` version bump와 `v0.2.0 - 2026-04-29` changelog 정리가 필요하다. 다음 작업은 `v0.2.0 release metadata 준비`다.

## 088: v0.2.0 release metadata 준비

- 완료일: 2026-04-29
- 배경: post-v1 release candidate는 `0.1.0` patch로 보기에는 변경 범위가 크고, changelog도 `Unreleased` 상태였으므로 `v0.2.0` release metadata가 필요했다.
- 변경 내용: `pyproject.toml`과 `src/repotrust/__init__.py` version을 `0.2.0`으로 올렸다. `CHANGELOG.md`에는 새 empty `Unreleased` 섹션을 만들고 기존 post-v1 release notes를 `v0.2.0 - 2026-04-29` 아래로 이동했다. README Console Mode 예시와 CLI version tests도 `0.2.0`으로 맞췄다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `CHANGELOG.md`, `README.md`, `tests/test_cli.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`에서 `120 passed`를 확인했다. `repo-trust`, `repo-trust-kr`, `repotrust` version command가 모두 `0.2.0`을 출력했다. self JSON은 schema `1.2`, score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었고 `json.tool` 검증을 통과했다. `pip wheel --no-deps .`는 `repotrust-0.2.0-py3-none-any.whl`을 생성했다. editable reinstall 후 `pip show repotrust`도 version `0.2.0`을 보여줬고, clean venv wheel install에서도 세 entrypoint가 모두 `0.2.0`을 출력했다. `git diff --check`도 통과했다.
- 결과: v0.2.0 release metadata는 tag 생성 전 상태로 준비됐다. 다음 작업은 `v0.2.0 release metadata commit 생성`이다.

## 089: v0.2.0 release metadata commit 생성

- 완료일: 2026-04-29
- 배경: v0.2.0 version bump와 changelog release heading이 검증됐으므로, tag 생성 전에 release metadata 변경을 commit으로 고정해야 했다.
- 변경 내용: `CHANGELOG.md`, `README.md`, `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, 작업 상태 문서 변경을 `Prepare v0.2.0 release metadata` commit으로 저장했다.
- 코드/문서: 기능 동작 변경은 없고 release metadata, 사용자 예시, version tests, 작업 상태 문서만 수정했다.
- 검증: commit 직전 `.venv/bin/python -m pytest -q`에서 `120 passed`를 확인했고 `git diff --check`도 통과했다. `git diff --stat`으로 변경 범위가 release metadata와 문서/test에 한정됨을 확인했다.
- 결과: v0.2.0 release metadata가 로컬 commit으로 고정됐다. 다음 작업은 `v0.2.0 release metadata 원격 반영 및 tag 준비`다.

## 090: v0.2.0 release metadata 원격 반영 및 tag 준비

- 완료일: 2026-04-29
- 배경: `77232d7 Prepare v0.2.0 release metadata` commit이 로컬 `main`에 생성됐고, release tag를 만들기 전에 원격 main과 tag 상태를 맞춰야 했다.
- 변경 내용: `git push origin main`으로 release metadata commit을 GitHub `main`에 반영했다. 이후 local tag 목록과 remote tag 목록을 확인했다.
- 코드/문서: push 자체에는 기능 코드 변경이 없었다. 작업 상태 문서를 다음 `v0.2.0` annotated tag 생성 단계로 갱신했다.
- 검증: push 전 `main...origin/main [ahead 1]` 상태를 확인했고, push는 `3d9b3e2..77232d7 main -> main`으로 성공했다. push 후 `git status --short --branch`는 `main...origin/main` 상태였다. local tag는 기존 `v0.1.0`만 있었고, `git ls-remote --tags origin`은 remote tag가 아직 없음을 보여줬다. `git log --oneline --decorate -5`에서 `77232d7 (HEAD -> main, origin/main) Prepare v0.2.0 release metadata`를 확인했다.
- 결과: v0.2.0 release metadata는 GitHub main에 반영됐고, `v0.2.0` remote tag는 아직 없다. 기존 local `v0.1.0` tag는 이동하지 않는다. 다음 작업은 `v0.2.0 annotated tag 생성 및 push`다.

## 091: v0.2.0 annotated tag 생성 및 push

- 완료일: 2026-04-29
- 배경: v0.2.0 release metadata가 GitHub main에 반영됐고 remote에는 아직 release tag가 없었다.
- 변경 내용: 현재 HEAD에 `v0.2.0` annotated tag를 `RepoTrust v0.2.0` 메시지로 생성하고 `git push origin v0.2.0`으로 원격에 반영했다. 기존 local `v0.1.0` tag는 이동하거나 재사용하지 않았다.
- 코드/문서: tag 생성 자체에는 파일 변경이 없었다. 작업 상태 문서를 다음 GitHub release publish 준비 단계로 갱신했다.
- 검증: `git status --short --branch`에서 `main...origin/main` 상태를 확인했다. `git tag --list --sort=version:refname -n`에서 `v0.1.0`과 `v0.2.0`을 확인했다. `git ls-remote --tags origin 'refs/tags/v0.2.0*'`에서 remote `v0.2.0` tag object와 dereferenced commit `0aa555a`를 확인했다. `git show --stat --oneline --decorate v0.2.0`에서 tag message `RepoTrust v0.2.0`과 target commit을 확인했다.
- 결과: v0.2.0 annotated tag가 local과 GitHub remote에 생성됐다. 다음 작업은 `v0.2.0 GitHub release publish 준비`다.

## 092: v0.2.0 GitHub release publish

- 완료일: 2026-04-29
- 배경: `v0.2.0` annotated tag가 GitHub 원격에 반영됐고, 사용자가 간단한 release 단계는 묻지 말고 진행하라고 지시했다.
- 변경 내용: `CHANGELOG.md`의 `v0.2.0` section을 release notes로 추출해 `gh release create v0.2.0 --repo answndud/repo-trust --title "RepoTrust v0.2.0" --notes-file /tmp/repotrust-v0.2.0-notes.md --verify-tag`로 GitHub release를 생성했다.
- 코드/문서: release publish 자체에는 repository 파일 변경이 없었다. 작업 상태 문서를 다음 PyPI 배포 여부와 post-release 검증 결정 단계로 갱신했다.
- 검증: `gh release view v0.2.0 --repo answndud/repo-trust`는 `isDraft=false`, `isPrerelease=false`, `tagName=v0.2.0`, URL `https://github.com/answndud/repo-trust/releases/tag/v0.2.0`을 반환했다. `git ls-remote --tags origin 'refs/tags/v0.2.0*'`도 remote tag object와 dereferenced commit을 반환했다. `git status --short --branch`는 `main...origin/main` 상태였다.
- 결과: RepoTrust v0.2.0 GitHub release가 publish됐다. 다음 작업은 `PyPI 배포 여부와 post-release 검증 결정`이다.

## 093: PyPI 배포 여부와 post-release 검증 결정

- 완료일: 2026-04-29
- 배경: GitHub release `v0.2.0` publish 이후 production PyPI 배포를 바로 진행할 수 있는지 확인해야 했다.
- 변경 내용: GitHub release 상태, PyPI package name availability, local build artifact, publish credential/toolchain 상태를 확인했다. `repotrust` 이름은 PyPI에서 published project/distribution으로 확인되지 않았지만, 현재 환경에는 `twine`/`build`, `.pypirc`, `TWINE_USERNAME`, `TWINE_PASSWORD`, `PYPI_TOKEN`, `PYPI_API_TOKEN`이 준비되어 있지 않았다.
- 코드/문서: 기능 코드는 변경하지 않았다. `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 PyPI publish 보류 판단과 다음 setup/dry-run 작업에 맞게 갱신했다.
- 검증: `gh release view v0.2.0 --repo answndud/repo-trust`로 published GitHub release를 확인했다. `pip wheel --no-deps .`는 `repotrust-0.2.0-py3-none-any.whl`을 생성했다. `pip index versions repotrust`는 matching distribution이 없다고 반환했다. PyPI project page/API도 현재 published project로 확인되지 않았다. publish credential/toolchain 존재 여부는 값 노출 없이 boolean으로만 확인했다.
- 결과: PyPI production publish는 지금 실행하지 않는다. package name은 비어 있는 것으로 보이지만 credential/toolchain이 없으므로, 다음 작업은 `PyPI publish setup과 TestPyPI dry-run`이다.

## 094: PyPI publish setup과 TestPyPI dry-run

- 완료일: 2026-04-29
- 배경: v0.2.0 GitHub release 이후 PyPI production publish를 바로 실행하기에는 build/publish toolchain과 credential path가 준비되지 않았다. 실제 remote upload 전에 local artifact validation과 TestPyPI 절차를 명확히 해야 했다.
- 변경 내용: `pyproject.toml` dev dependencies에 `build`와 `twine`을 추가하고 `pylock.toml`을 갱신했다. Testing guide에 `python -m build`, `twine check`, TestPyPI upload, TestPyPI install smoke, production upload 절차를 추가했다. Development workflow에도 release artifact check와 credential/trusted publishing 주의사항을 추가했다.
- 코드/문서: `pyproject.toml`, `pylock.toml`, `docs/testing-and-validation.md`, `docs/development-workflow.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다. 기능 코드는 변경하지 않았다.
- 검증: `.venv/bin/python -m pip install -e '.[dev]'`로 dev release toolchain 설치를 확인했다. `.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml`로 lockfile을 갱신했다. `.venv/bin/python -m build --outdir <tmp>/dist`는 `repotrust-0.2.0.tar.gz`와 `repotrust-0.2.0-py3-none-any.whl`을 생성했다. `.venv/bin/python -m twine check <tmp>/dist/*`는 wheel과 sdist 모두 `PASSED`였다. Clean venv wheel install smoke에서 `repo-trust`, `repo-trust-kr`, `repotrust`가 모두 `0.2.0`을 출력했고 fixture JSON은 `json.tool`을 통과했다. `.venv/bin/python -m pytest -q`는 `120 passed`였고 `git diff --check`도 통과했다.
- 결과: PyPI/TestPyPI publish 준비용 local toolchain과 검증 절차는 준비됐다. 실제 TestPyPI/PyPI upload는 token 또는 GitHub trusted publishing 설정이 필요한 blocked 작업으로 남긴다.

## 095: Offline-first GitHub URL default

- 완료일: 2026-04-30
- 배경: 사용자는 secret key나 API 연결 없이 RepoTrust가 기본 동작하기를 원했다. Legacy `repotrust scan <github-url>`은 이미 parse-only 기본값이었지만 product CLI와 Console Mode GitHub workflow는 GitHub API remote scan을 기본 사용하고 있었다.
- 변경 내용: `repo-trust html/json/check/gate <github-url>`의 기본 동작을 parse-only로 바꿨고, GitHub API read-only metadata 조회는 `--remote`를 명시했을 때만 실행되도록 했다. `--parse-only`는 URL-only 동작을 강제하는 호환성 옵션으로 유지했다. Local path + `--remote`, `--remote` + `--parse-only` usage error 테스트를 추가했다. `target.github_not_fetched` 추천 조치와 dashboard next action을 explicit `--remote` 또는 local checkout scan 안내로 바꿨다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/console.py`, `src/repotrust/rules.py`, `src/repotrust/models.py`, `src/repotrust/dashboard_i18n.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/adr.md`, `docs/prd.md`, `docs/trd.md`, `docs/architecture.md`, `docs/domain-context.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `59 passed`였다. `.venv/bin/python -m pytest -q`는 `124 passed`였다. `repo-trust html --help` 한국어 도움말에서 `--remote`와 `--parse-only` 설명을 확인했다. `.venv/bin/repo-trust json https://github.com/openai/codex --output /tmp/repotrust-offline.json`는 `target.github_not_fetched`, `coverage=metadata_only`, `confidence=low` JSON을 생성했고 `json.tool` 검증을 통과했다.
- 결과: RepoTrust runtime의 GitHub URL 기본 경로는 secret key나 API 연결 없이 동작한다. 원격 GitHub metadata는 `--remote`를 명시한 사용자만 사용한다. PyPI production publish는 여전히 credential 또는 trusted publishing 설정이 필요한 별도 blocked 작업이다.

## 096: PyPI production publish 제외 결정

- 완료일: 2026-04-30
- 배경: 사용자는 secret key나 API 연결 없이 동작하는 프로젝트 원칙을 유지하고 싶어 했다. PyPI/TestPyPI upload는 remote write이며 token 또는 trusted publishing 설정이 필요하므로 현재 운영 방식과 맞지 않았다.
- 변경 내용: `docs/PLAN.md`에서 PyPI production publish pending 항목을 제거하고 active 상태를 `현재 active 작업 없음`으로 정리했다. Packaging validation 문서는 PyPI/TestPyPI upload 절차 대신 local `python -m build` artifact 검증만 남겼다. `twine` dev dependency를 제거하고 lockfile 갱신 대상으로 돌렸다. Changelog에는 PyPI/TestPyPI publish를 active project scope에서 제외한다고 기록했다.
- 코드/문서: `pyproject.toml`, `pylock.toml`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/development-workflow.md`, `docs/testing-and-validation.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pip install -e '.[dev]'`로 `twine` 없는 dev dependency set을 재설치했다. `.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml`로 lockfile을 갱신했다. `.venv/bin/python -m pytest -q`는 `124 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release/dist`는 `repotrust-0.2.0.tar.gz`와 `repotrust-0.2.0-py3-none-any.whl`을 생성했다. `git diff --check`도 통과했다.
- 결과: RepoTrust의 공식 배포 흐름은 GitHub Releases와 source/local artifact 검증 중심으로 유지한다. PyPI/TestPyPI publish는 현재 프로젝트 범위가 아니다.

## 097: v0.2.1 release metadata 준비

- 완료일: 2026-04-30
- 배경: offline-first GitHub URL default와 PyPI/TestPyPI publish 제외 결정이 `main`에 반영됐지만, 최신 GitHub Release는 아직 `v0.2.0`이었다. GitHub-only 배포 흐름을 공식화하려면 patch release metadata가 필요했다.
- 변경 내용: package version을 `0.2.1`로 올리고 CLI version tests와 README Console Mode 예시를 맞췄다. `CHANGELOG.md`의 Unreleased 내용을 `v0.2.1 - 2026-04-30` 아래로 이동하고 새 empty Unreleased 섹션을 만들었다. README quickstart는 PyPI 대신 GitHub Release source archive 설치를 안내하고, 개발자는 editable dev install을 사용하도록 설명했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `59 passed`였다. `.venv/bin/python -m pytest -q`는 `124 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release/dist`는 `repotrust-0.2.1.tar.gz`와 `repotrust-0.2.1-py3-none-any.whl`을 생성했다. `repo-trust`, `repo-trust-kr`, `repotrust` version command는 모두 `0.2.1`을 출력했다. Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었고 `json.tool` 검증을 통과했다. `git diff --check`도 통과했다.
- 결과: v0.2.1 release metadata는 commit/tag/release 생성 단계로 넘길 수 있는 상태다.

## 098: v0.2.1 GitHub-only release publish

- 완료일: 2026-04-30
- 배경: v0.2.1 release metadata가 검증됐으므로, PyPI 없이 GitHub Releases를 공식 배포 채널로 사용해 patch release를 publish해야 했다.
- 변경 내용: `Prepare v0.2.1 release metadata` commit을 생성하고 `main`에 push했다. `v0.2.1` annotated tag를 만들고 원격에 push했다. `CHANGELOG.md`의 `v0.2.1` section을 release notes로 추출해 GitHub Release `RepoTrust v0.2.1`을 publish했다. Release asset으로 `repotrust-0.2.1-py3-none-any.whl`과 `repotrust-0.2.1.tar.gz`를 업로드했다.
- 코드/문서: release publish 자체에는 기능 코드 변경이 없었다. `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 post-release 상태로 정리했다.
- 검증: `git push origin main`은 `7794d25..63a09e1 main -> main`으로 성공했다. `git push origin v0.2.1`은 새 tag를 원격에 생성했다. `gh release view v0.2.1 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`는 `tagName=v0.2.1`, `isDraft=false`, `isPrerelease=false`, URL `https://github.com/answndud/repo-trust/releases/tag/v0.2.1`, asset 2개 업로드 상태를 반환했다.
- 결과: RepoTrust v0.2.1 GitHub-only release가 publish됐다. PyPI/TestPyPI publish는 프로젝트 범위가 아니며 active 작업은 없다.

## 099: GitHub Release 설치 smoke

- 완료일: 2026-04-30
- 배경: v0.2.1 GitHub-only release가 publish됐으므로, PyPI 없이 GitHub Release asset만으로 사용자가 설치하고 기본 명령을 실행할 수 있는지 clean venv에서 확인해야 했다.
- 변경 내용: GitHub Release의 wheel asset과 source archive asset을 각각 새 venv에 설치해 세 CLI entrypoint와 기본 check/json 동작을 검증했다. README quickstart가 검증한 release asset URL과 어긋나지 않도록 wheel 설치를 기본 경로로 조정하고 source archive 설치를 대안으로 분리했다.
- 코드/문서: 기능 코드는 변경하지 않았다. `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: Clean venv wheel install에서 `repo-trust`, `repo-trust-kr`, `repotrust`가 모두 `0.2.1`을 출력했고, `repo-trust check .`, fixture JSON 생성, `json.tool` 검증이 성공했다. Clean venv source archive install에서도 동일한 entrypoint version, local check, fixture JSON, `json.tool` 검증이 성공했다. `.venv/bin/python -m pytest -q`는 `124 passed`였다.
- 결과: v0.2.1은 PyPI 없이 GitHub Release wheel 또는 source archive로 설치해 바로 사용할 수 있다. 다음 작업은 `설치 UX 보강`이다.

## 100: 설치 UX 보강

- 완료일: 2026-04-30
- 배경: PyPI를 사용하지 않는 배포 정책에서는 사용자가 README에서 사용자 설치, source archive 대안, 개발자 editable install을 혼동하지 않아야 했다.
- 변경 내용: README의 Installation Quickstart를 GitHub Release wheel 설치 중심으로 정리하고, source archive 설치와 clone 후 개발자 설치를 별도 블록으로 분리했다. PyPI를 사용하지 않고 GitHub Releases가 공식 배포 채널이라는 설명을 quickstart 맨 앞에 배치했다. 관련 docs는 PyPI/TestPyPI 제외와 GitHub Releases 중심 배포 설명을 이미 유지하고 있어 의미가 일치함을 확인했다.
- 코드/문서: 기능 코드는 변경하지 않았다. `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/repo-trust json . --output /tmp/repotrust-install-docs.json`은 self-scan JSON을 생성했고 score `98`, grade `A`, high confidence를 반환했다. `.venv/bin/python -m json.tool /tmp/repotrust-install-docs.json`는 통과했다. 첫 병렬 실행의 `json.tool`은 파일 생성 전에 실행되어 `FileNotFoundError`가 났고, JSON 생성 후 순차 재실행으로 통과했다.
- 결과: README는 검증된 GitHub Release asset 설치 경로와 개발자 설치 경로를 구분한다. 다음 작업은 `첫 실행 경험 개선`이다.

## 101: 첫 실행 경험 개선

- 완료일: 2026-04-30
- 배경: GitHub Release로 설치한 사용자가 처음 `repo-trust-kr` 또는 `repo-trust`를 실행했을 때 GitHub URL 기본 검사가 API 없이 parse-only로 동작한다는 점과 로컬 checkout scan의 차이를 바로 이해해야 했다.
- 변경 내용: Console Mode 첫 화면 tagline과 GitHub/Local workflow 설명을 한국어/영어 모두 수정했다. README Console Mode 화면 예시를 실제 문구와 맞췄고, `remote.github_metadata_collected` 상세 설명이 예전 remote-default 동작을 말하지 않도록 `--remote` 명시 실행으로 보정했다. CLI launcher 테스트는 새 문구를 검증하도록 갱신했다.
- 코드/문서: `src/repotrust/console_i18n.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `59 passed`였다. `printf 'q\n' | .venv/bin/repo-trust`와 `printf 'q\n' | .venv/bin/repo-trust-kr`는 새 첫 화면 문구를 출력했다. `.venv/bin/repo-trust check https://github.com/openai/codex`는 `GitHub parse-only`, score `70`, confidence `LOW`, `--remote` 또는 local checkout 안내를 출력했다. `.venv/bin/python -m pytest -q`는 `124 passed`였다. `.venv/bin/repo-trust json . --output /tmp/repotrust-final-plan.json`과 `json.tool` 검증도 통과했다. `git diff --check`와 diff review를 완료했다.
- 결과: v0.2.1 GitHub-only 배포 이후 설치와 첫 실행 경험 정리 작업이 모두 완료됐다. 현재 active 작업은 없다.

## 102: v0.2.1 release notes 보강

- 완료일: 2026-04-30
- 배경: README에는 검증된 GitHub Release wheel/source archive 설치 명령이 반영됐지만, GitHub Release 페이지 본문에는 사용자가 바로 복사할 설치 명령이 없었다.
- 변경 내용: GitHub Release `v0.2.1` 본문 상단에 `Install from GitHub Releases` 섹션을 추가했다. PyPI/TestPyPI는 프로젝트 범위가 아니고 GitHub Releases가 공식 배포 채널이라는 안내, venv 생성 후 wheel URL 설치와 `repo-trust-kr` 실행 명령, source archive 설치 대안을 포함했다.
- 코드/문서: GitHub Release 본문을 원격에서 갱신했다. Repository 문서는 `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh release view v0.2.1 --repo answndud/repo-trust --json name,tagName,body,url,assets`로 release title, tag, 갱신된 설치 섹션, wheel/sdist asset 2개를 확인했다. `git diff --check`도 통과했다.
- 결과: GitHub Release 페이지에서도 README와 같은 GitHub-only 설치 경로를 바로 확인할 수 있다. 현재 active 작업은 없다.

## 103: GitHub Actions Node 24 대응

- 완료일: 2026-04-30
- 배경: main CI는 성공했지만 GitHub Actions가 `actions/checkout@v4`, `actions/setup-python@v5`를 Node.js 20 기반 action으로 경고했다. GitHub hosted runner의 Node 20 action deprecation에 대비해 Node 24 runtime을 사용하는 최신 major로 갱신해야 했다.
- 변경 내용: `.github/workflows/ci.yml`에서 `actions/checkout@v4`를 `actions/checkout@v6`으로, `actions/setup-python@v5`를 `actions/setup-python@v6`으로 갱신했다. 작업 상태 문서에는 Node 24 대응 story를 기록했다.
- 코드/문서: `.github/workflows/ci.yml`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `124 passed`였다. `git diff --check`도 통과했다. 공식 GitHub action release 정보에서 `actions/checkout` v6 계열과 `actions/setup-python` v6 계열이 Node 24 runtime으로 업데이트된 것을 확인했다. Push 후 GitHub Actions run `25152879649`는 success였고 이전 Node.js 20 deprecation annotation은 출력되지 않았다.
- 결과: CI workflow는 Node 24 대응 action major를 사용하며 main CI가 경고 없이 통과했다. 현재 active 작업은 없다.

## 104: v0.2.2 README smoke release 정합화

- 완료일: 2026-04-30
- 배경: README 최종 사용자 smoke 중 README/main의 최신 첫 화면 문구와 README가 설치시키는 `v0.2.1` wheel의 실제 첫 화면 문구가 다르다는 문제가 발견됐다. README를 과거 문구로 되돌리기보다 이미 main에 반영된 설치 UX, release notes, CI Node 24 대응을 포함한 patch release로 정합성을 맞추기로 했다.
- 변경 내용: package version을 `0.2.2`로 올리고 README GitHub Release 설치 URL, README Console Mode 예시, CLI version tests, changelog를 `v0.2.2`에 맞췄다. `Prepare v0.2.2 release` commit을 main에 push하고 CI 통과 후 `v0.2.2` annotated tag와 GitHub Release를 publish했다. Release asset으로 `repotrust-0.2.2-py3-none-any.whl`과 `repotrust-0.2.2.tar.gz`를 업로드했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -q`는 `59 passed`, `.venv/bin/python -m pytest -q`는 `124 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.2/dist`는 wheel과 sdist를 생성했다. Self-scan JSON은 score `98`, grade `A`, high confidence였고 `json.tool`을 통과했다. Local wheel clean venv smoke와 GitHub Release asset URL clean venv smoke 모두 `repo-trust`, `repo-trust-kr`, `repotrust`가 `0.2.2`를 출력했고, `repo-trust-kr` 첫 화면은 README 예시와 일치했다. GitHub URL check/html/json smoke와 JSON `json.tool` 검증도 통과했다. `gh release view v0.2.2`로 release와 asset 2개를 확인했다.
- 결과: README quickstart, GitHub Release asset, 설치된 CLI 첫 화면이 `v0.2.2` 기준으로 일치한다. 현재 active 작업은 없다.

## 105: 샘플 리포트 UX 보강

- 완료일: 2026-04-30
- 배경: 설치와 첫 실행 경로가 정리됐지만, 새 사용자가 좋은 저장소와 위험 설치 저장소의 리포트 차이를 바로 비교해 보는 안내가 부족했다.
- 변경 내용: README에 `good-python`과 `risky-install` fixture로 JSON/HTML sample report를 만드는 연습 섹션을 추가했다. `good-python`은 `100/100`, grade `A`, high confidence, finding 없음으로 기대하고, `risky-install`은 `51/100`, grade `F`, Install Safety `0/100`, high severity risky install finding을 먼저 봐야 한다고 설명했다. Testing guide의 fixture sample report 명령도 good/risky JSON/HTML과 expected behavior를 모두 포함하도록 보강했다.
- 코드/문서: `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/repo-trust json/html tests/fixtures/repos/good-python`과 `.venv/bin/repo-trust json/html tests/fixtures/repos/risky-install` sample report smoke가 모두 성공했다. `/tmp/repotrust-good.json`과 `/tmp/repotrust-risky.json`은 `json.tool` 검증을 통과했다. `.venv/bin/python -m pytest -q`는 `124 passed`였고 `git diff --check`도 통과했다.
- 결과: 사용자가 설치 직후 fixture sample reports로 좋은 결과와 위험 결과를 직접 비교할 수 있다. 현재 active 작업은 없다.

## 106: README 영어 요약 보강

- 완료일: 2026-04-30
- 배경: README는 한국어 중심으로 설치와 사용 흐름을 설명하지만, GitHub에 처음 들어온 비한국어 사용자는 프로젝트 목적, 설치 채널, 기본 네트워크 정책, 한계를 빠르게 파악하기 어려웠다.
- 변경 내용: README 상단에 짧은 English overview를 추가했다. RepoTrust가 설치, dependency 채택, AI coding agent 위임 판단을 돕는 Python CLI라는 점, local/offline-first와 GitHub URL parse-only 기본값, GitHub Releases-only 배포 정책, terminal/JSON/static HTML report, vulnerability scanner나 safety guarantee가 아니라는 한계를 명시했다. 기존 한국어 소개와 quickstart 흐름은 유지했다.
- 코드/문서: `README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `124 passed`였다. `.venv/bin/repo-trust json . --output /tmp/repotrust-readme-english.json`는 score `98`, grade `A`, high confidence self-scan JSON을 생성했고 `json.tool` 검증을 통과했다. `git diff --check`도 통과했다.
- 결과: 비한국어 사용자도 README 첫 화면에서 RepoTrust의 목적과 운영 정책을 빠르게 이해할 수 있다. 현재 active 작업은 없다.

## 107: 리뷰 finding 개선

- 완료일: 2026-05-06
- 배경: 저장소 리뷰에서 risky install positive coverage 공백, HTML finding title/explanation 매핑 누락, Console Mode JSON export prompt 혼선이 발견됐다.
- 변경 내용: `risky-install` fixture에 `sudo`, global npm install, `chmod +x` 설치 명령을 추가하고 해당 finding ID의 severity/evidence positive 테스트를 추가했다. 모든 `RISKY_INSTALL_PATTERNS` ID가 HTML title/explanation 매핑을 갖는지 검증하는 테스트를 추가했다. Console Mode JSON export는 GitHub 전용 prompt 대신 generic repository target prompt와 기본값 `.`을 사용하도록 수정했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `tests/fixtures/repos/risky-install/README.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q tests/test_scanner.py tests/test_cli.py`는 `91 passed`였다. `.venv/bin/python -m pytest -q`는 `129 passed`였다. `.venv/bin/repo-trust json tests/fixtures/repos/risky-install --output /tmp/repotrust-risky-after.json`는 score `51`, grade `F`, Install Safety `0/100`을 유지하며 모든 risky install finding ID를 JSON에 포함했다.
- 결과: 리뷰 finding 3건이 모두 해소됐고 현재 active 작업은 없다.

## 108: Finding summary UX 명확화

- 완료일: 2026-05-06
- 배경: terminal WHY 요약과 assessment/profile priority ID는 상위 3개 finding만 보여주지만, HTML/Markdown/JSON 리포트에는 전체 finding이 들어 있어 사용자가 둘의 관계를 혼동할 수 있었다.
- 변경 내용: terminal dashboard WHY 섹션에 전체 finding 중 상위 3개만 표시한다는 안내를 추가했다. Markdown Findings 섹션과 HTML Prioritized Findings 설명에 전체 finding count와 정렬 기준을 명시했다. 관련 CLI/renderer 회귀 테스트를 추가했다.
- 코드/문서: `src/repotrust/dashboard.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: focused renderer/CLI 테스트 3개는 통과했다. `.venv/bin/repo-trust check tests/fixtures/repos/risky-install` smoke에서 `Showing top 3 of 12 findings` 안내를 확인했다. `.venv/bin/python -m pytest -q`는 `131 passed`였다.
- 결과: summary와 full findings의 관계가 terminal, Markdown, HTML에서 명확해졌다. 현재 active 작업은 없다.

## 109: 샘플 리포트 문서 정합화

- 완료일: 2026-05-06
- 배경: README와 testing guide의 fixture walkthrough도 terminal top-3 summary와 HTML/JSON full findings 동작을 설명해야 사용자 온보딩이 실제 UX와 일치한다.
- 변경 내용: README 리포트 읽는 법과 샘플 리포트 섹션에 terminal `WHY`는 상위 3개 finding만 요약하고 HTML/JSON은 전체 finding을 보여준다는 설명을 추가했다. Testing guide fixture sample behavior에 risky fixture의 현재 score, 12개 finding count, high/medium risky install finding 기대값을 명시했다. Console Mode JSON export가 generic target prompt를 써야 한다는 검증 기대도 추가했다.
- 코드/문서: `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/repo-trust check tests/fixtures/repos/risky-install` smoke에서 score `51/100`, grade `F`, `Showing top 3 of 12 findings` 안내를 확인했다. `.venv/bin/repo-trust json tests/fixtures/repos/risky-install --output /tmp/repotrust-risky-doc.json`과 `json.tool` 검증은 성공했고 JSON은 score `51`, grade `F`, Install Safety `0/100`, finding 12개와 risky install finding 7개를 포함했다. `.venv/bin/python -m pytest -q`는 `131 passed`였다.
- 결과: README, testing guide, CLI/renderer 동작이 sample report walkthrough 기준으로 일치한다. 현재 active 작업은 없다.

## 110: Explain command와 HTML finding filters

- 완료일: 2026-05-06
- 배경: 사용자가 단순 리팩터링보다 직관적인 사용자 기능을 원했고, finding을 바로 이해하는 CLI와 많은 finding을 탐색하기 쉬운 HTML 리포트가 가장 효과적인 다음 기능으로 판단됐다.
- 변경 내용: known finding catalog를 추가하고 `repo-trust explain <finding-id>` / `repo-trust-kr explain <finding-id>` 명령을 구현했다. HTML 리포트의 `Prioritized Findings`에 severity/category 필터, 전체 펼치기/접기 controls, finding별 `details` 접기 UI와 `data-severity`/`data-category` 속성을 추가했다. README, finding reference, testing guide, localized help를 새 기능에 맞게 갱신했다.
- 코드/문서: `src/repotrust/finding_catalog.py`, `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `tests/test_docs.py`, `README.md`, `docs/finding-reference.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `repo-trust explain install.risky.uses_sudo`와 `repo-trust-kr explain security.no_policy` smoke가 title/category/severity/meaning/action을 출력했다. unknown finding ID는 exit code `1`과 대표 ID 예시를 반환했다. HTML fixture smoke에서 filter buttons, expand/collapse controls, `data-severity`, `data-category` 속성을 확인했다. `.venv/bin/python -m pytest -q`는 `136 passed`였다.
- 결과: 사용자가 finding을 CLI에서 바로 해석하고, HTML 리포트에서 finding을 필터링/접기 탐색할 수 있다. 현재 active 작업은 없다.

## 111: JSON report compare command

- 완료일: 2026-05-06
- 배경: RepoTrust가 단발성 검사 도구에서 개선 추적 도구로 확장되려면 사용자가 저장된 JSON 리포트 두 개를 비교해 점수와 finding 변화를 바로 확인할 수 있어야 했다.
- 변경 내용: `repo-trust compare <old.json> <new.json>` / `repo-trust-kr compare <old.json> <new.json>` 명령을 추가했다. 두 RepoTrust JSON 리포트를 읽어 score delta, grade 변화, verdict 변화, added/resolved/severity-changed/persisting finding 요약을 출력한다. invalid JSON이나 RepoTrust JSON shape이 아닌 파일은 exit code `1`과 명확한 오류를 반환한다. README, testing guide, localized help, CLI 테스트를 갱신했다.
- 코드/문서: `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: risky fixture JSON과 good fixture JSON을 생성한 뒤 `repo-trust compare` smoke에서 score `51 -> 100 (+49)`, grade `F -> A`, resolved findings `12`를 확인했다. `repo-trust-kr compare`도 같은 비교를 한국어 label로 출력했다. `.venv/bin/python -m pytest -q`는 `139 passed`였다.
- 결과: 사용자가 개선 전/후 RepoTrust JSON 리포트를 비교해 해결된 finding과 새로 생긴 finding을 바로 파악할 수 있다. 현재 active 작업은 없다.

## 112: HTML finding copy actions

- 완료일: 2026-05-06
- 배경: HTML 리포트에서 finding ID를 확인한 뒤 `repo-trust explain <id>`로 이어가는 workflow가 생겼으므로, 사용자가 ID와 explain 명령을 직접 복사하지 않아도 되게 해야 했다.
- 변경 내용: HTML finding card에 `ID 복사`와 `explain 명령 복사` 버튼을 추가했다. 각 버튼은 `data-copy-value`에 복사 대상을 노출하고, JavaScript는 Clipboard API를 우선 사용하며 실패/미지원 환경에서는 hidden textarea와 `document.execCommand('copy')` fallback을 사용한다. 버튼 클릭 후 짧게 `복사됨` 상태를 표시한다. README와 testing guide에 HTML copy actions 설명을 반영했다.
- 코드/문서: `src/repotrust/reports.py`, `tests/test_scanner.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: focused HTML renderer test는 통과했다. risky fixture HTML smoke에서 `ID 복사`, `explain 명령 복사`, `data-copy-value="repo-trust explain install.risky.uses_sudo"`, Clipboard API, fallback copy script를 확인했다. `.venv/bin/python -m pytest -q`는 `139 passed`였다.
- 결과: HTML 리포트에서 finding ID와 explain 명령을 바로 복사해 CLI 설명 workflow로 이어갈 수 있다. 현재 active 작업은 없다.

## 113: v0.2.3 release preparation

- 완료일: 2026-05-06
- 배경: `explain`, HTML finding filters/copy actions, `compare` 기능이 사용자에게 직접 가치가 있는 기능 묶음이므로 patch release 후보로 준비해야 했다.
- 변경 내용: package version을 `0.2.3`으로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.3`에 맞췄다. CHANGELOG에 v0.2.3 section을 추가해 `explain`, HTML finding UX, `compare`, risky install coverage, Console JSON prompt, Markdown sorting 개선을 정리했다. 작업 상태 문서를 release prep 완료 상태로 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: version focused tests 5개는 통과했고 `repo-trust`, `repo-trust-kr`, `repotrust`는 모두 `0.2.3`을 출력했다. `.venv/bin/python -m pytest -q`는 `139 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.3/dist`는 wheel과 sdist를 생성했다. Clean wheel install smoke에서 세 entrypoint version, `explain`, fixture JSON generation, risky-to-good `compare`, risky fixture HTML, JSON `json.tool` 검증이 성공했다. Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었다.
- 결과: v0.2.3 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. push/tag/GitHub Release publish는 아직 진행하지 않았다. 현재 active 작업은 없다.

## 114: v0.2.3 GitHub Release publish

- 완료일: 2026-05-06
- 배경: v0.2.3 release candidate가 로컬 테스트, build, clean wheel smoke, self-scan을 통과했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: `main`의 release prep commit `e9481b7`을 origin에 push하고 GitHub Actions `ci` run `25416142099` 통과를 확인했다. annotated tag `v0.2.3`를 release commit에 생성해 push했고, GitHub Release `RepoTrust v0.2.3`를 publish했다. Release asset으로 `repotrust-0.2.3-py3-none-any.whl`과 `repotrust-0.2.3.tar.gz`를 업로드했다. 작업 상태 문서를 release publish 완료 상태로 archive했다.
- 코드/문서: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run watch 25416142099 --repo answndud/repo-trust --exit-status`는 성공했다. `gh release view v0.2.3 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.3`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 `repo-trust --version`은 `0.2.3`을 출력했고, `explain`, fixture JSON generation, risky-to-good `compare`, JSON `json.tool` 검증이 성공했다.
- 결과: v0.2.3은 https://github.com/answndud/repo-trust/releases/tag/v0.2.3 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다.

## 115: Compare report export

- 완료일: 2026-05-06
- 배경: `repo-trust compare`는 개선 전/후 JSON 리포트 차이를 터미널에만 보여줬다. 초보 사용자도 결과를 브라우저로 열거나 문서에 붙여 공유할 수 있도록 파일 출력이 필요했다.
- 변경 내용: compare summary 계산과 text/Markdown/HTML 렌더링을 `src/repotrust/compare_reports.py`로 분리했다. `repo-trust compare`와 `repo-trust-kr compare`에 `--format text|markdown|html`과 `--output` 옵션을 추가했고, 기존 terminal text 출력은 기본값으로 유지했다. Markdown/HTML output 테스트를 추가하고 localized help를 갱신했다. README에 초보자용 “JSON 저장 -> 비교 HTML 저장 -> 비교 Markdown 저장 -> 결과 읽는 법” 가이드를 추가했으며 testing guide의 smoke command와 exit-code matrix를 갱신했다.
- 코드/문서: `src/repotrust/compare_reports.py`, `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `tests/test_cli.py -k compare`는 `5 passed`였다. `.venv/bin/python -m pytest -q`는 `141 passed`였다. `repo-trust compare /tmp/repotrust-before.json /tmp/repotrust-after.json --format html --output /tmp/repotrust-compare.html`와 `--format markdown --output /tmp/repotrust-compare.md` smoke가 성공했고, 두 파일 모두 score `51 -> 100 (+49)`와 `install.risky.uses_sudo` resolved finding을 포함했다. `git diff --check`도 통과했다.
- 결과: 사용자는 저장된 두 JSON 리포트의 차이를 터미널, Markdown, HTML 중 원하는 형식으로 확인하고 공유할 수 있다. 현재 active 작업은 없다.

## 116: Compare HTML readability

- 완료일: 2026-05-06
- 배경: compare HTML 파일 출력은 가능해졌지만, 초보 사용자가 브라우저에서 열었을 때 어떤 항목이 좋아졌고 무엇을 먼저 확인해야 하는지 더 직관적으로 보여줄 필요가 있었다.
- 변경 내용: HTML compare report에 score delta 기반 outcome summary를 추가했다. finding 섹션을 `Improvements`, `New issues`, `Severity changes`, `Still remaining`으로 재정리하고 각 섹션에 쉬운 설명을 붙였다. finding ID마다 `Copy ID`와 `Copy explain` 버튼을 추가했으며 Clipboard API와 textarea fallback을 사용하는 copy script를 포함했다. README의 초보자용 compare guide와 testing guide 기대 동작을 새 HTML UI에 맞게 갱신했다.
- 코드/문서: `src/repotrust/compare_reports.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `tests/test_cli.py -k compare`는 `5 passed`였다. `.venv/bin/python -m pytest -q`는 `141 passed`였다. `repo-trust compare /tmp/repotrust-before.json /tmp/repotrust-after.json --format html --output /tmp/repotrust-compare.html` smoke에서 `Improved`, `Improvements: 12`, `New issues: 0`, `Still remaining: 0`, `Copy explain`, `repo-trust explain install.risky.uses_sudo` copy value를 확인했다. `git diff --check`도 통과했다.
- 결과: compare HTML report는 개선 여부, 해결된 문제, 새 문제, 남은 문제와 다음 explain 명령 복사까지 한 화면에서 제공한다. 현재 active 작업은 없다.

## 117: Console compare workflow

- 완료일: 2026-05-06
- 배경: compare HTML report는 Command Mode에서 만들 수 있었지만, 초보 사용자는 `--format html --output` 옵션을 외워야 했다. Console Mode에서 메뉴로 같은 workflow를 실행할 수 있어야 했다.
- 변경 내용: Console Mode home에 `[M] Compare JSON` / `[M] JSON 비교` action을 추가했다. Console workflow model을 scan/compare를 모두 표현하도록 확장했고, compare workflow는 이전 JSON, 최신 JSON, HTML output path를 차례대로 입력받는다. 기존 compare renderer를 재사용해 HTML 파일을 저장하고, 상대 output path는 기존 규칙대로 `result/<name>-YYYY-MM-DD.html`에 저장한다. README에 Console Mode JSON 비교 절차를 추가하고 testing guide 기대 동작을 갱신했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: Console Mode smoke에서 `m`, old/new JSON path, 기본 output 입력으로 `result/repotrust-compare-2026-05-06.html`이 생성됐고 HTML에 `Improved`, `Improvements: 12`, `Copy explain`이 포함됐다. `.venv/bin/python -m pytest -q`는 `142 passed`였다.
- 결과: 사용자는 `repo-trust` 또는 `repo-trust-kr` 메뉴에서 두 JSON 리포트를 입력해 브라우저용 비교 HTML을 만들 수 있다. 현재 active 작업은 없다.

## 118: Console compare recent JSON picker

- 완료일: 2026-05-06
- 배경: Console Mode에서 compare HTML을 만들 수 있게 됐지만, 이전/최신 JSON 경로를 직접 복사해 입력해야 했다. 초보 사용자가 최근 리포트 목록에서 번호로 선택할 수 있게 해야 했다.
- 변경 내용: `[M] Compare JSON` workflow에 최근 JSON 리포트 목록을 추가했다. `result/` 안의 최근 `.json` 파일만 번호, 경로, 수정 시간과 함께 보여주고, 이전/최신 prompt는 목록 번호 또는 직접 경로를 모두 허용한다. JSON 리포트가 없으면 직접 경로 입력 workflow를 그대로 유지한다. README Console compare 예시와 testing guide 기대 동작을 번호 선택 기준으로 갱신했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: Console Mode smoke에서 최근 JSON 목록의 `2`, `1` 번호를 입력해 `result/repotrust-compare-2026-05-06.html`을 생성했고 HTML에 `Improved`, `Improvements: 12`, `security.no_policy`가 포함됐다. `.venv/bin/python -m pytest -q`는 `143 passed`였다. `git diff --check`도 통과했다.
- 결과: Console Mode 사용자는 JSON 파일 경로를 직접 복사하지 않고 최근 리포트 번호만으로 before/after HTML 비교 리포트를 만들 수 있다. 현재 active 작업은 없다.

## 119: Console recent report clarity

- 완료일: 2026-05-06
- 배경: Console Mode에서 compare HTML을 만들 수 있지만, 저장 후 사용자가 `[R] Reports`에서 어떤 파일이 비교 리포트인지 바로 구분하기 어려웠다.
- 변경 내용: Recent Reports의 type label을 파일 확장자 대신 용도 중심으로 표시하도록 개선했다. JSON은 `json report`, 일반 HTML은 `html report`, 파일명에 `compare`가 들어간 HTML은 `compare html`, Markdown은 `markdown report`로 표시한다. compare workflow 완료 후에는 `[R] Reports`에서 저장 파일을 다시 찾을 수 있다는 안내를 출력한다. README와 testing guide도 새 안내와 type label 기대값에 맞게 갱신했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: Console Mode smoke에서 compare HTML 생성 후 `Use [R] Reports from Console Mode to find this file later.` 안내를 확인했다. 이어서 `[R] Reports` smoke에서 `result/repotrust-compare-2026-05-06.html`은 `compare html`, JSON 파일은 `json report`로 표시됐다. `.venv/bin/python -m pytest -q`는 `143 passed`였고 `git diff --check`도 통과했다.
- 결과: 사용자는 compare HTML을 저장한 뒤 최근 리포트 목록에서 비교 리포트를 쉽게 식별하고 다시 찾을 수 있다. 현재 active 작업은 없다.

## 120: v0.2.4 release preparation

- 완료일: 2026-05-06
- 배경: v0.2.3 이후 compare export와 Console Mode compare workflow 개선이 초보 사용자에게 직접 가치가 있는 기능 묶음으로 쌓였으므로 patch release 후보로 정리해야 했다.
- 변경 내용: package version을 `0.2.4`로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.4`에 맞췄다. CHANGELOG에 v0.2.4 section을 추가해 compare Markdown/HTML export, HTML compare readability, Console Mode compare workflow, recent JSON number picker, recent report clarity를 정리했다. 작업 상태 문서를 release prep 완료 상태로 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest -q`는 `143 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.4/dist`는 `repotrust-0.2.4.tar.gz`와 `repotrust-0.2.4-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version, fixture JSON generation, text/Markdown/HTML compare export, Console Mode recent JSON number selection compare workflow, recent reports type label, JSON `json.tool` 검증이 성공했다. Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 없음이었다.
- 결과: v0.2.4 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. push/tag/GitHub Release publish는 아직 진행하지 않았다. 현재 active 작업은 없다.

## 121: v0.2.4 GitHub Release publish

- 완료일: 2026-05-07
- 배경: v0.2.4 release candidate가 로컬 테스트, build, clean wheel smoke, self-scan을 통과했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: `main`의 release prep commit `19753c9`을 origin에 push하고 GitHub Actions `ci` run `25470956575` 통과를 확인했다. annotated tag `v0.2.4`를 release commit에 생성해 push했고, GitHub Release `RepoTrust v0.2.4`를 publish했다. Release asset으로 `repotrust-0.2.4-py3-none-any.whl`과 `repotrust-0.2.4.tar.gz`를 업로드했다. 작업 상태 문서를 release publish 완료 상태로 archive했다.
- 코드/문서: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run watch 25470956575 --repo answndud/repo-trust --exit-status`는 성공했다. `gh release view v0.2.4 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.4`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 세 entrypoint version `0.2.4`, fixture JSON generation, text/HTML compare export, Console Mode recent JSON number selection compare workflow, recent report type label, JSON `json.tool` 검증이 성공했다.
- 결과: v0.2.4는 https://github.com/answndud/repo-trust/releases/tag/v0.2.4 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다.

## 122: README first-use onboarding

- 완료일: 2026-05-07
- 배경: v0.2.4에서 Console Mode와 compare workflow가 늘어나 README 초반부만 보고는 초보 사용자가 “처음에 무엇을 누르면 되는지”를 바로 파악하기 어려울 수 있었다.
- 변경 내용: README 설치 빠른 시작 바로 뒤에 `처음 쓰는 사람은 3단계만` 섹션을 추가했다. `repo-trust-kr`로 메뉴 열기, `[L]`/`[G]`/`[J]`로 첫 검사와 JSON 저장하기, `[M] JSON 비교`로 개선 전/후 HTML을 만들고 `[R] 리포트`에서 다시 찾는 흐름을 짧게 정리했다. Testing guide에 README first-use onboarding 기대값을 추가했다.
- 코드/문서: `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `rg`로 README의 `처음 쓰는 사람은 3단계만`, `repo-trust-kr`, `[M] JSON 비교`, `[R] 리포트` 문구를 확인했다. `.venv/bin/python -m pytest -q`는 `143 passed`였고 `git diff --check`도 통과했다.
- 결과: README 상단에서 설치 후 첫 검사와 compare HTML 생성까지의 최소 경로를 바로 확인할 수 있다. 현재 active 작업은 없다.

## 123: README compare docs dedupe

- 완료일: 2026-05-07
- 배경: README 상단 first-use path가 추가되면서 Command Mode compare 섹션의 초보자용 4단계 절차와 내용이 중복되어 문서가 길어졌다.
- 변경 내용: Command Mode compare 섹션에서 중복된 `초보자용: 개선 전/후 비교 파일 만들기` 절차를 제거하고, compare 결과 읽는 법은 유지했다. 연습용 명령은 기존 `샘플 리포트로 연습` 섹션으로 연결했다. Console Mode 요약 문구에 `[M]` compare action을 추가했고, testing guide에는 first-use onboarding과 상세 Command Mode compare docs의 역할 분리를 기대값으로 추가했다.
- 코드/문서: `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `rg`로 README의 `처음 쓰는 사람은 3단계만`, `비교 결과를 읽는 법`, `샘플 리포트로 연습`, `[M]` 문구와 `초보자용: 개선 전/후` 제거를 확인했다. `.venv/bin/python -m pytest -q`는 `143 passed`였고 `git diff --check`도 통과했다.
- 결과: README 상단은 초보자 first-use path를 담당하고, Command Mode compare 섹션은 옵션 중심의 상세 설명으로 짧아졌다. 현재 active 작업은 없다.

## 124: Safe install advice command

- 완료일: 2026-05-07
- 배경: 초보 사용자는 README 설치 명령을 바로 실행해도 되는지 판단하기 어렵다. 기존 report와 finding은 충분한 근거를 제공하지만, “지금 설치 명령을 실행하지 말아야 하는지”와 “더 안전한 다음 행동은 무엇인지”를 별도 명령으로 바로 보여줄 필요가 있었다.
- 변경 내용: `repo-trust safe-install <target>` / `repo-trust-kr safe-install <target>` 명령을 추가했다. 새 `install_advice` renderer는 기존 scan result, install profile, install safety finding, manifest/lockfile 신호를 재사용해 설치 조언을 출력한다. high-risk install finding이 있으면 README 설치 명령 실행을 막고, good Python fixture에는 virtualenv 기반 설치 패턴을 제안하며, GitHub parse-only 대상은 파일 근거 부족을 설명한다. README, CHANGELOG, localized help, testing guide, PRD/TRD/architecture 문서를 갱신했다.
- 코드/문서: `src/repotrust/install_advice.py`, `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/prd.md`, `docs/trd.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k safe_install -q`는 `4 passed, 71 deselected`였다. `repo-trust safe-install` risky/good fixture smoke와 `repo-trust-kr safe-install` risky fixture smoke, `repo-trust safe-install --help` 한국어 help smoke를 확인했다. `git diff --check && .venv/bin/python -m pytest -q`는 `147 passed`였다.
- 결과: 사용자는 설치 명령을 실행하지 않고도 RepoTrust 검사 결과 기반의 안전 설치 안내를 영어/한국어로 받을 수 있다. 현재 active 작업은 없다.

## 125: Console safe install workflow

- 완료일: 2026-05-07
- 배경: `safe-install` 명령은 추가됐지만, 초보 사용자는 Command Mode 명령을 외우기보다 Console Mode 메뉴에서 기능을 발견하는 편이 자연스럽다.
- 변경 내용: Console Mode Home에 `[S] Safe Install` / `[S] 안전 설치` action을 추가했다. 새 workflow는 generic repository target prompt를 받은 뒤 기존 `render_safe_install_advice`를 재사용해 영어/한국어 안전 설치 안내를 출력한다. README first-use path, Console Mode 예시, testing guide, architecture, CHANGELOG를 새 메뉴에 맞게 갱신했다.
- 코드/문서: `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/cli.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/architecture.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k "interactive_safe_install or root_starts" -q`는 `4 passed, 73 deselected`였다. `git diff --check && .venv/bin/python -m pytest -q`는 `149 passed`였다. `printf 's\ntests/fixtures/repos/risky-install\n' | .venv/bin/repo-trust`와 `repo-trust-kr` smoke에서 `[S]` 메뉴와 safe install advice 출력을 확인했다.
- 결과: 사용자는 `repo-trust` 또는 `repo-trust-kr` 메뉴에서 설치 전 안전 안내를 바로 실행할 수 있다. 현재 active 작업은 없다.

## 126: v0.2.5 release preparation

- 완료일: 2026-05-07
- 배경: safe-install Command Mode와 Console `[S]` workflow가 사용자-facing 기능 묶음으로 main에 반영되고 CI가 통과했으므로 patch release candidate로 정리해야 했다.
- 변경 내용: package version과 runtime version을 `0.2.5`로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.5`에 맞췄다. CHANGELOG에 v0.2.5 section을 추가해 safe-install command, Console `[S]` workflow, beginner docs 갱신과 validation 결과를 정리했다. 작업 상태 문서를 release prep 완료 상태로 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check && .venv/bin/python -m pytest -q`는 `149 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.5/dist`는 `repotrust-0.2.5.tar.gz`와 `repotrust-0.2.5-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version `0.2.5`, `safe-install`, Console `[S] 안전 설치`, risky fixture JSON 생성, `json.tool` 검증이 성공했다. Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 0개였다.
- 결과: v0.2.5 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. push/tag/GitHub Release publish는 아직 진행하지 않았다. 현재 active 작업은 없다.

## 127: v0.2.5 GitHub Release publish

- 완료일: 2026-05-07
- 배경: v0.2.5 release candidate가 전체 테스트, build, clean wheel smoke, self-scan을 통과했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: `main`의 release prep commit `75b4c36`을 origin에 push하고 GitHub Actions `ci` run `25471816207` 통과를 확인했다. annotated tag `v0.2.5`를 release commit에 생성해 push했고, GitHub Release `RepoTrust v0.2.5`를 publish했다. Release asset으로 `repotrust-0.2.5-py3-none-any.whl`과 `repotrust-0.2.5.tar.gz`를 업로드했다.
- 코드/문서: `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run watch 25471816207 --repo answndud/repo-trust --exit-status`는 성공했다. `gh release view v0.2.5 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.5`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 세 entrypoint version `0.2.5`, `safe-install`, Console `[S] 안전 설치`, risky fixture JSON 생성, `json.tool` 검증이 성공했다.
- 결과: v0.2.5는 https://github.com/answndud/repo-trust/releases/tag/v0.2.5 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다.

## 128: Safe install pre-run checklist

- 완료일: 2026-05-07
- 배경: `safe-install`은 위험 판단과 다음 행동을 보여주지만, 초보 사용자가 설치 명령을 복사하기 직전에 확인할 간단한 checklist가 없었다.
- 변경 내용: 영어/한국어 `safe-install` 출력 상단에 3줄 실행 전 체크리스트를 추가했다. 명령 출처 확인, global/sudo/shell-pipe 대신 격리 패턴 우선, high-risk evidence가 있으면 HTML 리포트 먼저 확인하는 흐름을 명시했다. README와 testing guide 기대값, CLI 테스트를 갱신했다.
- 코드/문서: `src/repotrust/install_advice.py`, `tests/test_cli.py`, `README.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k safe_install -q`는 `6 passed, 71 deselected`였다. `git diff --check && .venv/bin/python -m pytest -q`는 `149 passed`였다. 영어/한국어 `safe-install` smoke에서 `Before you run anything:` / `실행 전 체크리스트:` 출력을 확인했다.
- 결과: 사용자는 설치 조언을 읽는 즉시 실행 전 확인해야 할 최소 행동을 볼 수 있다. 현재 active 작업은 없다.

## 129: v0.2.6 release preparation

- 완료일: 2026-05-07
- 배경: `safe-install` pre-run checklist가 v0.2.5 공개 직후 main에 추가됐으므로, 문서와 release artifact가 다시 일치하도록 patch release candidate로 정리해야 했다.
- 변경 내용: package version과 runtime version을 `0.2.6`으로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.6`에 맞췄다. CHANGELOG에 v0.2.6 section을 추가해 safe-install pre-run checklist와 validation 결과를 정리했다. publish 단계는 push/tag/release 생성이 필요한 live external write이므로 명시 승인 전까지 blocked로 남겼다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check && .venv/bin/python -m pytest -q`는 `149 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.6/dist`는 `repotrust-0.2.6.tar.gz`와 `repotrust-0.2.6-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version `0.2.6`, safe-install checklist, Console `[S] 안전 설치`, risky fixture JSON 생성, `json.tool` 검증이 성공했다. Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 0개였다.
- 결과: v0.2.6 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. GitHub Release publish는 명시 승인 대기 상태다.

## 130: v0.2.6 GitHub Release publish

- 완료일: 2026-05-07
- 배경: v0.2.6 release candidate가 전체 테스트, build, clean wheel smoke, self-scan을 통과했고 사용자가 publish 진행을 승인했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: `main`의 release prep commit `e6419c4`을 origin에 push하고 GitHub Actions `ci` run `25472674774` 통과를 확인했다. annotated tag `v0.2.6`을 release commit에 생성해 push했고, GitHub Release `RepoTrust v0.2.6`을 publish했다. Release asset으로 `repotrust-0.2.6-py3-none-any.whl`과 `repotrust-0.2.6.tar.gz`를 업로드했다. 작업 상태 문서를 active 작업 없음으로 정리했다.
- 코드/문서: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run watch 25472674774 --repo answndud/repo-trust --exit-status`는 성공했다. `gh release view v0.2.6 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.6`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 세 entrypoint version `0.2.6`, safe-install checklist, Console `[S] 안전 설치`, risky fixture JSON 생성, `json.tool` 검증이 성공했다.
- 결과: v0.2.6은 https://github.com/answndud/repo-trust/releases/tag/v0.2.6 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다.

## 131: Beginner adoption install/report guidance

- 완료일: 2026-05-07
- 배경: v0.2.6 이후 초보 사용자가 README 설치 명령을 실행하기 전 실제 명령, 안전한 대안, HTML 리포트 설명, 저장된 리포트 위치를 더 직관적으로 확인할 수 있게 해야 했다.
- 변경 내용: 기존 README install section parser를 재사용 가능한 `install_command_lines` helper로 공개하고, `safe-install` 영어/한국어 출력에 로컬 README에서 발견한 설치 명령을 먼저 표시했다. HTML 리포트에는 `Safe Install` 섹션을 추가해 실행 전 체크리스트, README 설치 명령, 더 안전한 설치 패턴을 보여준다. Console Mode 첫 화면에는 `[L] -> [S] -> [J]` first-run flow를 추가했고, recent reports 화면에는 경로 복사와 macOS `open <path>` 안내를 추가했다. HTML finding card의 detail summary는 terminal-free 설명 중심으로 바꾸고 finding 의미, 원문 메시지, 실제 근거, 추천 조치를 한 카드 안에서 읽을 수 있게 했다. README, CHANGELOG, testing guide를 새 기능에 맞춰 갱신했다.
- 코드/문서: `src/repotrust/rules.py`, `src/repotrust/install_advice.py`, `src/repotrust/reports.py`, `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check`는 통과했다. `.venv/bin/python -m pytest -q`는 `150 passed`였다. `repo-trust safe-install` good/risky fixture smoke에서 README install commands와 safe install guidance를 확인했다. `repo-trust html tests/fixtures/repos/risky-install --output /tmp/repotrust-risky-html-safe.html` smoke와 `rg`로 HTML의 `Safe Install`, `README에서 발견한 설치 명령`, `터미널 없이 읽는 설명과 근거`, 위험 설치 명령 렌더링을 확인했다. `printf 'r\n' | .venv/bin/repo-trust` smoke에서 first-run hint와 recent reports open helper를 확인했다.
- 결과: beginner adoption 기능 5개가 모두 구현/문서화/검증됐다. 현재 active 작업은 없다. 다음 추천 작업은 이번 기능 묶음을 GitHub Release asset에 반영하는 v0.2.7 release prep이다.

## 132: v0.2.7 release preparation

- 완료일: 2026-05-07
- 배경: beginner adoption install/report guidance 기능 묶음이 사용자-facing 개선이므로 GitHub Release asset으로 공개할 수 있게 patch release candidate로 정리해야 했다.
- 변경 내용: package version과 runtime version을 `0.2.7`로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.7`에 맞췄다. CHANGELOG에 v0.2.7 section을 추가해 README install command display, HTML Safe Install section, Console first-run hint, recent reports open helper, terminal-free HTML finding explanations와 validation 결과를 정리했다. 작업 상태 문서는 active 작업 없음으로 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check`는 통과했다. `.venv/bin/python -m pytest -q`는 `150 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.7/dist`는 `repotrust-0.2.7.tar.gz`와 `repotrust-0.2.7-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version `0.2.7`, `safe-install` README install commands, Console `[S] 안전 설치`, fixture JSON 생성, `json.tool`, HTML Safe Install section 렌더링을 확인했다. Self-scan JSON은 grade `A`, high confidence, full coverage, medium/high finding 0개였다.
- 결과: v0.2.7 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. GitHub Release publish는 명시 승인 대기 상태다.

## 133: v0.2.7 GitHub Release publish

- 완료일: 2026-05-07
- 배경: v0.2.7 release candidate가 전체 테스트, build, clean wheel smoke, self-scan을 통과했고 사용자가 다음 작업 진행을 요청했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: `main`의 release prep commit `26ee982`까지 origin에 push하고 GitHub Actions `ci` run `25476035889` 통과를 확인했다. annotated tag `v0.2.7`을 release commit에 생성해 push했고, GitHub Release `RepoTrust v0.2.7`을 publish했다. Release asset으로 `repotrust-0.2.7-py3-none-any.whl`과 `repotrust-0.2.7.tar.gz`를 업로드했다. 작업 상태 문서를 active 작업 없음으로 정리했다.
- 코드/문서: `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `gh run watch 25476035889 --repo answndud/repo-trust --exit-status`는 성공했다. `gh release view v0.2.7 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.7`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 세 entrypoint version `0.2.7`, `safe-install` README install commands, Console `[S] 안전 설치`, fixture JSON 생성, `json.tool` 검증이 성공했다.
- 결과: v0.2.7은 https://github.com/answndud/repo-trust/releases/tag/v0.2.7 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다.

## 134: HTML/Console beginner command guidance

- 완료일: 2026-05-07
- 배경: v0.2.7 이후 초보 사용자가 HTML 리포트에서 다음에 무엇을 실행해야 하는지와 저장된 리포트를 어떻게 열어야 하는지 더 빠르게 찾을 수 있게 해야 했다.
- 변경 내용: HTML Safe Install 섹션 상단에 `Next safest command` 강조 블록을 추가했다. 고위험 설치 finding이 있으면 설치 명령 대신 `repo-trust explain <finding-id>` 검토 명령을 보여주고, clean fixture처럼 설치 blocker가 없으면 첫 safe install command를 보여준다. Console/Command dashboard의 저장된 리포트 안내에는 `Open with: open <path>` / `열기 명령: open <경로>` helper를 추가했다. README, CHANGELOG, testing guide, PLAN/PROGRESS/COMPLETED를 갱신했다.
- 코드/문서: `src/repotrust/dashboard.py`, `src/repotrust/reports.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_scanner.py -k html_report -q`는 `3 passed, 32 deselected`였다. `.venv/bin/python -m pytest tests/test_cli.py -k "html_github_url_defaults or json_writes_file_with_korean_status or interactive_local_html or interactive_github_shortcut" -q`는 `5 passed, 72 deselected`였다. `git diff --check`는 통과했고, `.venv/bin/python -m pytest -q`는 `151 passed`였다. CLI smoke에서 저장된 HTML/JSON 리포트의 `Open with: open <path>` / `열기 명령: open <경로>` 안내를 확인했다. HTML smoke에서 `Next safest command`와 `repo-trust explain install.risky.process_substitution_shell` 렌더링을 확인했다.
- 결과: 리포트를 만든 직후 사용자가 다음 안전 행동과 파일 열기 명령을 더 쉽게 찾을 수 있다. 현재 active 작업은 없다. 다음 추천 작업은 sample report gallery 또는 beginner tutorial command다.

## 135: Beginner tutorial command

- 완료일: 2026-05-07
- 배경: 설치 직후 초보 사용자가 어떤 명령부터 실행해야 할지 README 전체를 읽기 전에 바로 확인할 수 있는 copyable tutorial entrypoint가 필요했다.
- 변경 내용: `repo-trust tutorial` / `repo-trust-kr tutorial` 명령을 추가했다. 새 tutorial renderer는 실제 scan이나 파일 write 없이 로컬 HTML 검사, safe-install, JSON 저장, API-free GitHub URL quick check, Console Mode 선택 순서를 영어/한국어로 보여준다. Console Mode에는 `[T] Tutorial` / `[T] 튜토리얼` workflow를 추가했고, localized help, README, CHANGELOG, testing guide를 갱신했다.
- 코드/문서: `src/repotrust/tutorial.py`, `src/repotrust/cli.py`, `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k "tutorial or root_starts" -q`는 `5 passed, 75 deselected`였다. `git diff --check`는 통과했고, `.venv/bin/python -m pytest -q`는 `154 passed`였다. Smoke에서 `repo-trust tutorial`, `repo-trust-kr tutorial`, Console `[T] 튜토리얼` 출력이 copyable first-run commands를 보여주는 것을 확인했다.
- 결과: 사용자는 설치 직후 `tutorial` 명령이나 Console `[T]`로 첫 로컬 검사부터 안전 설치 확인, JSON 저장까지의 최소 경로를 바로 볼 수 있다. 현재 active 작업은 없다. 다음 추천 작업은 sample report gallery다.

## 136: Sample report gallery

- 완료일: 2026-05-07
- 배경: 초보 사용자가 실제 저장소를 검사하기 전에 좋은 리포트와 위험 리포트가 어떻게 보이는지 빠르게 익힐 수 있는 내장 예시가 필요했다.
- 변경 내용: `repo-trust samples` / `repo-trust-kr samples` 명령을 추가했다. 새 sample gallery generator는 tests fixture나 네트워크에 의존하지 않는 in-memory good/risky `ScanResult`를 만들고, `sample-good-YYYY-MM-DD.html/json`과 `sample-risky-YYYY-MM-DD.html/json` 4개 파일을 생성한다. Console Mode에는 `[P] Samples` / `[P] 샘플` workflow를 추가했다. localized help, README, CHANGELOG, testing guide, PLAN/PROGRESS/COMPLETED를 갱신했다.
- 코드/문서: `src/repotrust/sample_gallery.py`, `src/repotrust/cli.py`, `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k "samples or root_starts" -q`는 `5 passed, 78 deselected`였다. `git diff --check`는 통과했고, `.venv/bin/python -m pytest -q`는 `157 passed`였다. Smoke에서 `repo-trust samples`, `repo-trust-kr samples`, Console `[P] Samples`가 good/risky HTML/JSON 4개 파일을 생성하는 것을 확인했다. 생성된 sample JSON은 `json.tool` 검증을 통과했고, risky sample HTML에는 `Next safest command`와 `install.risky.shell_pipe_install`이 렌더링됐다.
- 결과: 사용자는 실제 저장소를 검사하기 전에 built-in sample report gallery로 좋은 결과와 위험 결과의 차이를 학습할 수 있다. 현재 active 작업은 없다. 다음 추천 작업은 v0.2.8 release prep 또는 sample gallery polish다.

## 137: v0.2.8 release preparation

- 완료일: 2026-05-07
- 배경: beginner command guidance, tutorial command, sample gallery가 사용자-facing 기능 묶음으로 쌓였으므로 GitHub Release asset으로 공개할 수 있게 patch release candidate로 정리해야 했다.
- 변경 내용: package version과 runtime version을 `0.2.8`로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.8`에 맞췄다. CHANGELOG에 v0.2.8 section을 추가해 Next safest command, report open helper, tutorial command, sample gallery, Console `[T]`/`[P]` workflow와 validation 결과를 정리했다. 작업 상태 문서는 active 작업 없음으로 정리했다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check`는 통과했다. `.venv/bin/python -m pytest -q`는 `157 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.8/dist`는 `repotrust-0.2.8.tar.gz`와 `repotrust-0.2.8-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version `0.2.8`, `tutorial`, `samples`, Console `[P] Samples`, `safe-install`, fixture JSON 생성, `json.tool`을 확인했다. Self-scan JSON은 grade `A`, high confidence, full coverage, medium/high finding 0개였다.
- 결과: v0.2.8 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. GitHub Release publish는 명시 승인 대기 상태다.

## 138: v0.2.8 GitHub Release publish

- 완료일: 2026-05-07
- 배경: v0.2.8 release candidate가 전체 테스트, build, clean wheel smoke, self-scan을 통과했고 사용자가 다음 작업 진행을 요청했으므로 GitHub Release로 공개해야 했다.
- 변경 내용: release prep commit `b100aa3`까지 origin/main에 push했다. 첫 GitHub Actions `ci` run `25477613123`은 sample gallery stderr의 긴 경로가 Rich 터미널 폭에 따라 줄바꿈되면서 파일명 substring assertion이 깨져 실패했다. 기능 코드는 유지하고 `tests/test_cli.py` assertion을 줄바꿈에 흔들리지 않도록 안정화한 commit `d8d3ad3`를 push했다. GitHub Actions `ci` run `25477688302` 통과를 확인한 뒤 annotated tag `v0.2.8`을 생성/push했고, GitHub Release `RepoTrust v0.2.8`을 publish했다. Release asset으로 `repotrust-0.2.8-py3-none-any.whl`과 `repotrust-0.2.8.tar.gz`를 업로드했다.
- 코드/문서: `tests/test_cli.py`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py::test_direct_cli_samples_writes_good_and_risky_gallery -q`는 `1 passed`였다. `git diff --check && .venv/bin/python -m pytest -q`는 `157 passed`였다. `gh run watch 25477688302 --repo answndud/repo-trust --exit-status`는 성공했다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.8/dist`는 최신 commit 기준 wheel/sdist를 생성했다. `gh release view v0.2.8 --repo answndud/repo-trust --json tagName,isDraft,isPrerelease,url,assets`에서 `v0.2.8`, draft false, prerelease false, wheel/sdist asset uploaded 상태를 확인했다. GitHub Release wheel URL clean install smoke에서 세 entrypoint version `0.2.8`, `tutorial`, `samples`, sample JSON `json.tool`, `safe-install`, fixture JSON `json.tool`, Console `[P] Samples`가 성공했다.
- 결과: v0.2.8은 https://github.com/answndud/repo-trust/releases/tag/v0.2.8 에 공개됐고 release asset URL로 설치 가능하다. 현재 active 작업은 없다. 다음 추천 작업은 `repo-trust next-steps <target>` 또는 `fix-plan` 계열의 초보자용 조치 계획 기능이다.

## 139: Beginner next-steps command

- 완료일: 2026-05-08
- 배경: 초보 사용자가 위험 리포트를 받은 뒤 어떤 finding부터 멈추고 어떤 조치를 이어가야 하는지 터미널에서 바로 확인할 수 있어야 했다.
- 변경 내용: `repo-trust next-steps <target>` / `repo-trust-kr next-steps <target>` 명령을 추가했다. 새 renderer는 high severity install finding이 있으면 README 설치 명령 실행을 먼저 중단시키고, 그 다음 license, CI, security policy, lockfile, medium install finding 순서로 조치 계획을 보여준다. 좋은 fixture는 `safe-install`과 `html`로 이어지는 짧은 checklist를 출력한다. Console Mode에는 `[N] Next Steps` / `[N] 다음 조치` workflow를 추가했다. localized help, README, CHANGELOG, testing guide, PLAN/PROGRESS/COMPLETED를 갱신했다.
- 코드/문서: `src/repotrust/next_steps.py`, `src/repotrust/cli.py`, `src/repotrust/console.py`, `src/repotrust/console_i18n.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k "next_steps or root_starts or help_shows_product" -q`는 `7 passed, 80 deselected`였다. Smoke에서 `repo-trust next-steps` good/risky fixture, `repo-trust-kr next-steps` risky fixture, Console `[N]` workflow를 확인했다. `git diff --check && .venv/bin/python -m pytest -q`는 `161 passed`였다.
- 결과: 초보 사용자는 HTML/JSON 리포트를 따로 열기 전에 `next-steps`로 실행 중단, adoption risk 검토, copyable `safe-install`/`html`/`explain` 명령을 한 화면에서 확인할 수 있다. 현재 active 작업은 없다. 다음 추천 작업은 HTML/JSON next-steps integration이다.

## 140: HTML/JSON next-steps integration

- 완료일: 2026-05-08
- 배경: `next-steps`가 터미널/콘솔에서만 보이면 HTML 리포트를 공유받은 사용자가 같은 조치 순서를 바로 읽기 어렵고, 이미 저장한 JSON 리포트도 다시 스캔해야 했다.
- 변경 내용: static HTML 리포트에 `Next Steps` 섹션을 추가해 터미널 `next-steps`와 같은 action order를 보여준다. `repo-trust next-steps --from-json <report.json>` / `repo-trust-kr next-steps --from-json <report.json>` 옵션을 추가해 저장된 RepoTrust JSON 리포트를 재스캔 없이 읽어 action plan을 출력한다. `--from-json` help, README, CHANGELOG, testing guide, PLAN/PROGRESS/COMPLETED를 갱신했다.
- 코드/문서: `src/repotrust/reports.py`, `src/repotrust/cli.py`, `src/repotrust/help_i18n.py`, `tests/test_cli.py`, `tests/test_scanner.py`, `README.md`, `CHANGELOG.md`, `docs/testing-and-validation.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `.venv/bin/python -m pytest tests/test_cli.py -k "next_steps" tests/test_scanner.py -k "next_steps or safe_install_section" -q`는 `7 passed, 117 deselected`였다. Smoke에서 `repo-trust next-steps --from-json /tmp/repotrust-next-steps-risky.json`, HTML `Next Steps` section grep, `repo-trust next-steps --help` Korean help를 확인했다. `git diff --check && .venv/bin/python -m pytest -q`는 `163 passed`였다.
- 결과: 사용자는 HTML 리포트 안에서 바로 다음 조치 순서를 읽을 수 있고, 저장된 JSON 리포트는 재스캔 없이 `next-steps`로 이어갈 수 있다. 현재 active 작업은 없다. 다음 추천 작업은 v0.2.9 release prep이다.

## 141: v0.2.9 release preparation

- 완료일: 2026-05-08
- 배경: `next-steps` command와 HTML/JSON next-steps integration이 사용자-facing 기능 묶음으로 준비됐으므로 GitHub Release asset으로 공개할 수 있게 patch release candidate로 정리해야 했다.
- 변경 내용: package version과 runtime version을 `0.2.9`로 올리고 README GitHub Release install URL, Console Mode 예시, CLI version tests를 `0.2.9`에 맞췄다. CHANGELOG에 v0.2.9 section을 추가해 `next-steps`, `next-steps --from-json`, Console `[N]`, HTML `Next Steps` section과 validation 결과를 정리했다. 작업 상태 문서는 active 작업 없음으로 정리하고 v0.2.9 publish를 pending으로 남겼다.
- 코드/문서: `pyproject.toml`, `src/repotrust/__init__.py`, `tests/test_cli.py`, `README.md`, `CHANGELOG.md`, `docs/PLAN.md`, `docs/PROGRESS.md`, `docs/COMPLETED.md`를 수정했다.
- 검증: `git diff --check && .venv/bin/python -m pytest -q`는 `163 passed`였다. `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.9/dist`는 `repotrust-0.2.9.tar.gz`와 `repotrust-0.2.9-py3-none-any.whl`을 생성했다. Clean wheel install smoke에서 세 entrypoint version `0.2.9`, `next-steps`, `next-steps --from-json`, HTML `Next Steps`, Console `[N] Next Steps`, `safe-install`, fixture JSON 생성, `json.tool`을 확인했다. Self-scan JSON은 grade `A`, high confidence, full coverage, medium/high finding 0개였다.
- 결과: v0.2.9 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. GitHub Release publish는 명시 승인 대기 상태다.
