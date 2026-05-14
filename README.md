# RepoTrust

RepoTrust는 GitHub 저장소나 로컬 프로젝트를 쓰기 전에 기본 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 안내, 라이선스, 보안 정책, CI, lockfile, Dependabot, 선택적 GitHub metadata처럼 확인 가능한 근거를 모아 “지금 설치해도 되는지”, “dependency로 넣어도 되는지”, “AI agent에게 맡겨도 되는지”를 리포트로 정리합니다. 취약점 스캐너나 안전 보증 도구가 아니라, 사람이 먼저 확인해야 할 신뢰 신호와 불확실성을 빠르게 보여주는 도구입니다.

- 기본은 offline-first입니다. 로컬 검사는 네트워크를 쓰지 않고, GitHub URL 검사는 `--remote`를 명시하기 전까지 URL 형식만 확인합니다.
- PyPI/TestPyPI 배포는 하지 않습니다. 공식 배포 채널은 GitHub Releases입니다.
- 결과는 터미널 대시보드, JSON, static HTML로 볼 수 있습니다.
- secret key나 API 연결 없이 시작할 수 있습니다. GitHub API metadata가 필요할 때만 선택적으로 `--remote`와 token을 사용합니다.

English summary: RepoTrust is a Python CLI that helps you review observable trust signals before installing an open source repository, adopting it as a dependency, or handing it to an AI coding agent.

## 먼저 읽을 곳

처음 사용하는 사람은 아래 순서만 보면 됩니다.

1. [설치 빠른 시작](#installation-quickstart--설치-빠른-시작)에서 `repo-trust-kr`을 설치합니다.
2. [5분 시작 가이드](#5분-시작-가이드)에서 샘플 리포트와 실제 저장소 검사를 실행합니다.
3. 명령어가 낯설다면 [Command Mode 초보자 가이드](guides/command-mode-guide.md)를 따라 합니다.
4. [리포트 읽는 법](#리포트-읽는-법)에서 결과를 어떻게 판단할지 확인합니다.

CI, config, fixture, 개발자 검증은 RepoTrust를 프로젝트에 붙이거나 직접 개발할 때만 읽어도 됩니다.

## Installation Quickstart / 설치 빠른 시작

PyPI는 사용하지 않습니다. 공식 배포 채널은 GitHub Releases이며, 처음 쓰는 사람은 release wheel을 설치한 뒤 한국어 command mode인 `repo-trust-kr <명령>`으로 시작하면 됩니다.

RepoTrust는 Python 3.10 이상이 필요합니다. macOS 기본 `/usr/bin/python3`가 3.9.x라면 Homebrew, pyenv, uv 등으로 Python 3.10+ 환경을 먼저 준비하세요.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.3.0/repotrust-0.3.0-py3-none-any.whl
repo-trust-kr --help
```

위의 `python3`는 Python 3.10 이상이어야 합니다. `python3 --version`이 3.9.x라면 Python 3.10+ 실행 파일로 바꿔 실행하세요.

터미널을 새로 열었다면 실행 전에 `source .venv/bin/activate`로 가상환경을 다시 활성화하세요.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.3.0/repotrust-0.3.0-py3-none-any.whl
repo-trust-kr --help
```

PowerShell에서 가상환경 활성화가 막히면 아래처럼 가상환경 안의 실행 파일을 직접 호출해도 됩니다.

```powershell
.\.venv\Scripts\python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.3.0/repotrust-0.3.0-py3-none-any.whl
.\.venv\Scripts\repo-trust-kr.exe --help
```

wheel 설치가 맞지 않는 환경에서는 같은 release의 source archive를 설치할 수 있습니다.

```bash
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.3.0/repotrust-0.3.0.tar.gz
```

## 5분 시작 가이드

설치가 끝났다면 실제 저장소를 바로 검사하기 전에 샘플 리포트부터 만들어 보세요.

```bash
repo-trust-kr samples
```

샘플은 좋은 예시와 위험 예시 HTML/JSON을 `result/` 폴더에 만듭니다. 좋은 리포트는 어떤 항목이 통과된 상태인지 보여주고, 위험 리포트는 설치 명령을 멈춰야 하는 상황을 보여줍니다.

내가 보고 있는 저장소를 검사할 때는 아래 순서로 진행하면 됩니다.

```bash
repo-trust-kr check .
repo-trust-kr safe-install .
repo-trust-kr next-steps .
repo-trust-kr html .
```

1. `check .`로 현재 폴더의 신뢰 판단을 터미널에서 봅니다.
2. README 설치 명령을 실행하기 전에는 `safe-install .`을 봅니다.
3. 위험 finding이 있거나 무엇부터 해야 할지 모르겠다면 `next-steps .`를 실행합니다.
4. 나중에 다시 보거나 공유하려면 `html .` 또는 `json .`으로 리포트를 저장합니다.

GitHub URL만 빠르게 확인할 때는 `repo-trust-kr check https://github.com/owner/repo`를 실행하면 됩니다. 기본 GitHub URL 검사는 API나 token 없이 URL만 확인하므로 파일 수준 근거가 부족할 수 있습니다. 중요한 dependency 후보라면 로컬로 checkout한 뒤 `repo-trust-kr check .`로 검사하는 편이 더 정확합니다.

명령어가 낯설다면 [Command Mode 초보자 가이드](guides/command-mode-guide.md)에 처음 실행 순서, 명령별 판단 기준, 자주 헷갈리는 경로/옵션 설명을 자세히 정리해 두었습니다.

## Usage / 사용 방식

RepoTrust의 공식 사용 방식은 Command Mode입니다. 즉 `repo-trust-kr check .`처럼 할 일을 명령어 한 줄로 직접 지정합니다.

명령 없이 `repo-trust` 또는 `repo-trust-kr`만 실행하면 메뉴 화면을 열지 않고 사용 가능한 명령과 초보자 가이드 위치를 보여줍니다. 예전 Console Mode는 제거됐습니다.

Command Mode는 명령마다 받는 인자가 다릅니다.

| 하고 싶은 일 | 명령 형식 |
| --- | --- |
| 처음 따라 할 명령 보기 | `repo-trust tutorial` |
| 좋은/위험 샘플 리포트 만들기 | `repo-trust samples` |
| HTML 리포트 저장 | `repo-trust html <대상>` |
| JSON 리포트 저장 | `repo-trust json <대상>` |
| 터미널에서 즉시 확인 | `repo-trust check <대상>` |
| 설치 전 안내 보기 | `repo-trust safe-install <대상>` |
| 설치 전 안내와 실행 표면 함께 보기 | `repo-trust safe-install --audit <대상>` |
| 검사 후 다음 조치 보기 | `repo-trust next-steps <대상>` |
| 저장된 JSON에서 다음 조치 보기 | `repo-trust next-steps --from-json <report.json>` |
| finding ID 설명 보기 | `repo-trust explain <finding-id>` |

파일 저장 규칙과 검사 기준은 모든 command에서 공유합니다. `check`, `safe-install`, `next-steps`, `tutorial`은 파일을 저장하지 않고 터미널에만 결과를 보여줍니다.

Monorepo에서 특정 package만 검사하려면 로컬 checkout을 대상으로 `--subdir <상대경로>`를 사용할 수 있습니다.

```bash
repo-trust check . --subdir packages/api
repo-trust json . --subdir services/worker --output worker-repotrust.json
repo-trust safe-install --audit . --subdir packages/cli
```

`--subdir`은 로컬 대상에서만 동작합니다. GitHub `tree`/`blob` URL은 clone이나 API 호출 없이 URL 형식만 확인하므로, 하위 폴더 단위 신뢰 평가는 해당 저장소를 로컬로 checkout한 뒤 `--subdir`로 실행하세요.

## Command Mode

Command Mode는 명령을 한 줄로 직접 입력하는 방식입니다. 자동화하거나 같은 검사를 반복할 때 적합합니다.

### 처음 따라 할 명령 보기

설치 직후 무엇부터 실행해야 할지 모르겠다면 tutorial을 먼저 보세요. 실제 검사를 실행하지 않고, 로컬 검사, 안전 설치 안내, JSON 저장, GitHub URL quick check 순서의 copyable command만 보여줍니다.

**입력할 명령**

```bash
repo-trust-kr tutorial
repo-trust tutorial
```

### 샘플 리포트 갤러리 만들기

자기 저장소를 검사하기 전에 좋은 리포트와 위험 리포트가 어떻게 보이는지 먼저 보고 싶다면 sample gallery를 만드세요. 실제 저장소를 검사하지 않고 내장 예시 데이터로 HTML/JSON 샘플 리포트를 생성합니다.

**입력할 명령**

```bash
repo-trust-kr samples
repo-trust samples
```

**생성되는 파일 예시**

```text
result/sample-good-YYYY-MM-DD.html
result/sample-good-YYYY-MM-DD.json
result/sample-risky-YYYY-MM-DD.html
result/sample-risky-YYYY-MM-DD.json
```

### GitHub URL을 HTML로 저장

브라우저에서 읽을 리포트를 만들 때 사용합니다. GitHub URL은 기본적으로 API를 호출하지 않고 URL 형식만 확인합니다. 저장소 파일까지 검사하려면 로컬로 checkout한 폴더를 검사하고, 제한된 GitHub read-only metadata가 필요할 때만 `--remote`를 명시합니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.html
```

2026년 4월 28일에 실행하면 `result/codex-2026-04-28.html`처럼 날짜가 붙은 파일이 생깁니다.

### GitHub URL을 JSON으로 저장

자동화나 다른 도구에서 읽을 결과가 필요할 때 사용합니다.

**입력할 명령**

```bash
repo-trust json https://github.com/openai/codex
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.json
```

JSON 파일은 `schema_version`, `target`, `detected_files`, `findings`, `score`, `assessment`, `generated_at`을 포함합니다. `assessment.profiles`에는 설치, dependency 채택, AI agent 위임 목적별 판단이 들어갑니다. 터미널 대시보드는 stderr로만 출력되므로 JSON 파일 내용과 섞이지 않습니다.

### Finding ID 설명 보기

리포트에서 본 finding ID가 무엇을 뜻하는지 바로 확인할 수 있습니다.

**입력할 명령**

```bash
repo-trust explain install.risky.uses_sudo
repo-trust-kr explain security.no_policy
```

`explain`은 저장소를 다시 검사하지 않고 finding ID의 영역, 기본 심각도, 의미, 추천 조치를 보여줍니다. HTML 리포트에서 ID를 발견한 뒤 터미널에서 자세히 확인할 때 유용합니다.

### 설치 명령 실행 전 안전 안내

README의 설치 명령을 복사하기 전에, 초보자도 바로 읽을 수 있는 설치 조언만 따로 볼 수 있습니다. 이 명령은 저장소의 설치 명령을 실행하지 않고 RepoTrust 검사 결과만 읽어 안내합니다.

**입력할 명령**

```bash
repo-trust safe-install .
repo-trust-kr safe-install .
repo-trust safe-install --audit .
repo-trust safe-install https://github.com/openai/codex
```

`safe-install`은 README에서 발견한 실제 설치 명령을 먼저 보여줍니다. high-risk install finding이 있으면 README 설치 명령을 아직 실행하지 말라고 안내하고, 실행 전 체크리스트와 안전한 다음 단계를 보여줍니다. Python이나 Node manifest가 보이면 source install도 코드 실행으로 보고, 가상환경, `pip install -e .`, `npm ci --ignore-scripts`처럼 격리된 검토/설치 패턴을 예시로 보여줍니다. GitHub URL을 기본값으로 검사하면 API 없이 URL만 확인하므로 설치 근거가 부족하다고 설명합니다. 안전 설치 안내는 터미널 전용 명령으로 유지하고, HTML 리포트는 점수와 근거를 보관하는 정적 리포트로 둡니다.

`--audit`을 붙이면 안전 설치 안내 뒤에 로컬 설치 시점 실행 표면을 점검합니다. README 설치 명령과 위험 README 패턴은 앞의 Safe Install Advice에서 다루고, audit 출력은 `pyproject.toml` build backend, `setup.py`, `package.json` install lifecycle script, root `Makefile`/`Dockerfile`/shell script, VCS dependency 신호에 집중합니다. GitHub URL은 clone/API 호출 없이 로컬 checkout이 필요하다고 안내합니다.

### 위험 리포트를 받은 뒤 다음 조치 보기

리포트의 finding을 하나씩 해석하기 어렵다면 `next-steps`를 실행하세요. RepoTrust가 저장소를 검사한 뒤, 초보자가 바로 따라 할 수 있는 순서로 조치 계획을 보여줍니다. 고위험 설치 finding이 있으면 README 설치 명령을 먼저 멈추게 하고, 그 다음 license, CI, security policy 같은 adoption risk를 순서대로 정리합니다. 실행 순서 안내는 터미널 전용 명령으로 유지하고, HTML 리포트에는 검사 결과와 전체 finding 근거만 남깁니다.

**입력할 명령**

```bash
repo-trust next-steps .
repo-trust-kr next-steps .
repo-trust next-steps https://github.com/openai/codex
```

좋은 저장소에서는 짧은 확인 checklist와 `safe-install`, `html` 명령을 보여줍니다. 위험 저장소에서는 `repo-trust explain <finding-id>` 명령도 함께 보여주므로, HTML 리포트에서 본 finding을 터미널에서 바로 풀어 읽을 수 있습니다.

이미 저장한 JSON 리포트에서 이어서 보고 싶다면 `--from-json`을 사용하세요. 이 방식은 저장소를 다시 검사하지 않고 JSON 파일만 읽습니다.

```bash
repo-trust json . --output reports/current.json
repo-trust next-steps --from-json reports/current.json
```

이 기능은 자동 수정을 하지 않고, 외부 API나 secret key 없이 리포트 근거만 사용합니다.

### 로컬 폴더를 HTML로 저장

이미 clone한 저장소나 현재 작업 중인 폴더를 검사할 때 사용합니다. 로컬 검사는 네트워크를 사용하지 않습니다.

**입력할 명령**

```bash
repo-trust html .
```

**생성되는 파일 예시**

```text
result/<현재폴더>-YYYY-MM-DD.html
```

`.` 대신 다른 폴더 경로를 넣으면 해당 폴더를 검사합니다.

### 터미널에서 바로 확인

파일을 만들지 않고 터미널에서 바로 판단할 때 사용합니다.

**입력할 명령**

```bash
repo-trust-kr check https://github.com/openai/codex
```

**화면 예시**

아래는 출력 형태를 보여주는 예시입니다. 기본 GitHub URL 검사는 API를 호출하지 않으므로 파일 수준 근거가 부족하다는 판단이 나올 수 있습니다.

```text
────────────────────────────────────
RESULT: 판단 근거 부족
────────────────────────────────────
Risk: 주의 필요
Score: 70/100  Grade: C
Confidence: 낮음 (분석이 완전하지 않음)
Target: https://github.com/openai/codex
Mode: GitHub URL만 확인

────────────────────────────────────
이유
- GitHub URL 형식만 확인했고 원격 정보는 가져오지 않았습니다.
  → --remote로 원격 조회를 명시하거나 로컬 checkout을 검사해 파일 수준 근거를 확인하세요.

────────────────────────────────────
목적별 판단
설치: 근거 부족
의존성: 근거 부족
agent 위임: 근거 부족

────────────────────────────────────
다음 행동
1. 근거가 부족하므로 HTML 리포트를 저장해 빠진 항목을 확인하세요.
2. 중요한 프로젝트에 쓰기 전에는 로컬 checkout을 검사하세요.
```

`check` 명령은 HTML/JSON 파일을 저장하지 않습니다. 공유하거나 나중에 다시 볼 리포트가 필요하면 `html` 또는 `json` 명령을 사용하세요.

## 결과 파일 규칙

`html`과 `json` 명령은 기본적으로 `result/` 폴더에 날짜가 붙은 파일을 만듭니다.

| 입력 대상 | HTML 결과 예시 | JSON 결과 예시 |
| --- | --- | --- |
| `https://github.com/openai/codex` | `result/codex-YYYY-MM-DD.html` | `result/codex-YYYY-MM-DD.json` |
| `.` | `result/<현재폴더>-YYYY-MM-DD.html` | `result/<현재폴더>-YYYY-MM-DD.json` |
| `repo-trust samples` | `result/sample-good-YYYY-MM-DD.html` | `result/sample-good-YYYY-MM-DD.json` |

저장 위치를 직접 정해야 할 때만 `--output`을 사용합니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex --output reports/codex.html
```

디렉터리를 포함한 경로는 그대로 사용합니다. 파일명만 넣으면 기존 호환 규칙에 따라 `result/<파일명>-YYYY-MM-DD.<확장자>`로 저장됩니다.

## 도움말

`--help`를 붙이면 entrypoint 언어에 맞는 도움말을 바로 출력합니다. `repo-trust`는 영어, `repo-trust-kr`은 한국어 도움말을 보여줍니다.

**입력할 명령**

```bash
repo-trust --help
repo-trust-kr --help
```

**화면 예시**

```text
Usage: repo-trust [OPTIONS] COMMAND [ARGS]...

Inspect repository trust signals and write clear local reports.
```

subcommand도 같은 규칙을 따릅니다. 예를 들어 `repo-trust html --help`는 영어, `repo-trust-kr html --help`는 한국어 도움말을 바로 출력합니다.

## GitHub 원격 검사

GitHub URL은 기본적으로 GitHub API를 호출하지 않고 URL 형식만 확인합니다. 이 기본 실행은 secret key, API token, 네트워크 metadata 조회가 필요 없습니다.

**입력할 명령**

```bash
repo-trust-kr check https://github.com/openai/codex
```

이 경우 README, LICENSE, CI 같은 원격 파일은 확인하지 않습니다. 결과에는 `근거 부족`, `기본 정보만 확인`, `확인 못함` 같은 표시가 나올 수 있습니다.

GitHub API read-only metadata까지 확인하고 싶을 때만 `--remote`를 명시합니다. 현재 remote scan은 고정된 제한 범위로 유지합니다: repository metadata, root contents, README content만 확인합니다. GitHub Actions workflow, Dependabot 설정, release/tag freshness, commit activity, `.github/SECURITY.md` 같은 중첩 GitHub 설정은 remote scan에 추가하지 않습니다. 이런 신호까지 판단해야 하면 로컬로 checkout한 뒤 검사하세요. Public repository는 token 없이 시도할 수 있지만 rate limit이나 private repository 접근이 필요하면 `GITHUB_TOKEN`을 환경 변수로 설정합니다.

이 경계는 1인 운영용 v1을 작게 유지하기 위한 의도적인 제한입니다. `--remote`는 GitHub의 모든 신뢰 신호를 대신 판단하는 기능이 아니라, URL parse-only보다 조금 더 많은 read-only 근거를 가져오는 보조 경로입니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex --remote
GITHUB_TOKEN=<your-token> repo-trust html https://github.com/owner/private-repo --remote
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다. 실제 token은 공유 PC, 녹화 중인 화면, 공개 문서, shell history에 남지 않게 주의하세요.

## 리포트 읽는 법

처음에는 아래 항목만 보면 됩니다.

| 위치 | 확인할 내용 |
| --- | --- |
| RESULT | 최종 판단, 위험도, 점수, confidence |
| 이유 | 판단에 영향을 준 주요 finding 또는 통과 이유 |
| 목적별 판단 | 터미널 dashboard와 JSON `assessment.profiles`에서 설치, dependency 채택, AI agent 위임 관점의 별도 verdict 확인 |
| 다음 행동 | 지금 바로 실행할 후속 조치 |
| HTML `Assessment` | 저장해 둘 최종 판단, 점수, confidence, coverage |
| HTML `Evidence Matrix` | 실제로 확인한 근거와 확인하지 못한 근거 |
| HTML `Prioritized Findings` | 각 finding의 설명, 원문 메시지, 실제 근거, 추천 조치 |
| 리포트 | 저장된 HTML/JSON 리포트 위치 |
| DETAILS | 분석이 충분할 때만 보여주는 세부 점수와 근거 |

처음에는 아래 순서로 읽으면 됩니다.

1. 터미널의 `RESULT`와 `이유`/`WHY`에서 최종 판단과 상위 위험을 확인합니다.
2. HTML 리포트를 만들었다면 `Evidence Matrix`에서 이번 실행이 실제 파일 근거를 충분히 봤는지 확인합니다.
3. 더 자세한 근거가 필요하면 `Prioritized Findings`에서 설명, 원문 메시지, 실제 근거, 추천 조치를 확인합니다.
4. 설치 명령 실행 여부가 고민되면 `repo-trust safe-install <대상>`을 실행합니다.
5. 위험 finding 처리 순서가 필요하면 `repo-trust next-steps <대상>` 또는 `repo-trust next-steps --from-json <report.json>`을 실행합니다.

HTML/JSON 리포트를 저장한 뒤 터미널의 `Open with: open <path>` 또는 `열기 명령: open <경로>` 안내를 복사하면 macOS에서 바로 파일을 열 수 있습니다. Windows에서는 파일 탐색기에서 `result` 폴더를 열거나 PowerShell에서 `ii .\result\<파일명>.html`을 실행할 수 있습니다.

심각도는 이렇게 해석하면 됩니다.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 확인하면 좋은 낮은 위험 |
| `medium` | dependency로 쓰기 전에 검토할 항목 |
| `high` | 설치 전에 반드시 확인할 항목 |

`high`나 `medium` finding이 있거나 confidence가 `low`이면 README의 설치 명령을 바로 실행하지 말고, 리포트의 근거와 추천 조치를 먼저 확인하세요. `unknown` evidence는 파일이 없다는 뜻이 아니라 이번 실행에서 확인하지 못했다는 뜻입니다.

## 샘플 리포트로 연습

저장소를 직접 판단하기 전에 내장 샘플로 좋은 결과와 위험 결과를 나란히 확인할 수 있습니다. 이 방식은 설치한 wheel만으로 동작하며, RepoTrust 저장소를 clone하지 않아도 됩니다.

```bash
repo-trust-kr samples --output-dir repotrust-samples
repo-trust-kr next-steps --from-json repotrust-samples/sample-risky-YYYY-MM-DD.json
python -m json.tool repotrust-samples/sample-good-YYYY-MM-DD.json
```

`YYYY-MM-DD`는 파일이 만들어진 날짜입니다. 정확한 파일명은 `samples` 명령이 출력하는 저장 경로를 그대로 복사하면 됩니다.

| 샘플 | 기대 결과 | 먼저 볼 항목 |
| --- | --- | --- |
| `sample-good` | `100/100`, grade `A`, high confidence | 모든 신호가 found이고 finding이 없어야 합니다. |
| `sample-risky` | `57/100`, grade `F`, high confidence | HTML/JSON의 전체 finding과 Install Safety가 `30/100`인지 확인합니다. |

`sample-risky`는 일부러 위험한 설치 명령을 담은 연습용 리포트입니다. 실제 저장소에서 비슷한 high finding이 나오면 명령을 바로 실행하지 말고, terminal `WHY`, `repo-trust safe-install`, `repo-trust next-steps`, HTML `Prioritized Findings`의 evidence/recommendation을 함께 확인하세요.

특정 finding을 더 자세히 보고 싶으면 HTML 리포트의 finding ID를 보고 `repo-trust explain <finding-id>`를 실행하세요.

## 실패 기준 설정

점수가 기준보다 낮을 때 명령을 실패시키려면 `--fail-under`를 사용합니다.

**입력할 명령**

```bash
repo-trust json https://github.com/openai/codex --fail-under 80
```

| 상황 | Exit code |
| --- | ---: |
| 점수가 기준 이상 | `0` |
| 점수가 기준 미만 | `1` |
| 잘못된 인자 또는 config 오류 | `2` |

점수가 낮아도 리포트 파일은 먼저 저장됩니다.

CI에서 JSON을 stdout으로 남기면서 정책 실패만 exit code로 표현하려면 `gate`를 사용합니다.

```bash
repo-trust gate . --config /path/to/repotrust.toml
```

`gate`는 기본적으로 JSON을 stdout에 출력합니다. `--output`을 주면 JSON 파일을 먼저 저장한 뒤 정책 실패 여부를 exit code로 반환합니다.

### CI gate 빠른 시작

복사 가능한 시작점은 `examples/repotrust.toml`과 `examples/github-actions-repotrust-gate.yml`에 있습니다.

1. `examples/repotrust.toml`을 프로젝트의 `repotrust.toml`로 복사한 뒤 정책에 맞게 검토합니다.
2. GitHub Actions를 쓸 경우 `examples/github-actions-repotrust-gate.yml`을 `.github/workflows/repotrust.yml`로 복사할지 결정합니다.
3. CI 또는 로컬에서 gate를 실행합니다.

GitHub Actions 예시는 `gh release download`로 최신 RepoTrust GitHub Release wheel을 받아 설치합니다. 특정 버전에 고정해야 하는 조직 정책이 있으면 workflow의 install step에 tag를 명시하세요.

```bash
repo-trust gate . --config repotrust.toml --output repotrust-report.json
```

RepoTrust 저장소를 clone한 개발자는 risky fixture로 정책 실패를 확인할 수 있습니다. 이 명령은 exit code `1`을 반환하지만 JSON report는 먼저 저장합니다.

```bash
repo-trust gate tests/fixtures/repos/risky-install --config examples/repotrust.toml --output /tmp/repotrust-fail.json
python -m json.tool /tmp/repotrust-fail.json
```

## 설정 파일

정책 점수 기준을 TOML 파일로 지정할 수 있습니다. 1인 운영용 v1 범위에서는 `policy.fail_under`만 지원합니다.

복사 가능한 시작점은 `examples/repotrust.toml`에 있습니다.

**설정 파일 예시**

```toml
[policy]
fail_under = 80
```

**입력할 명령**

```bash
repo-trust html . --config /path/to/repotrust.toml
```

CLI 옵션이 config보다 우선합니다. config 자동 탐지, category weight 조정, finding disable, severity override, 목적별 profile gate, 중앙 조직 policy server는 지원하지 않습니다.

정책에서 사용할 finding ID는 리포트와 `repo-trust explain <finding-id>` 출력의 설명을 기준으로 검토하세요. JSON report를 직접 파싱하는 도구는 `schema_version`을 먼저 확인하고 필요한 key만 보수적으로 읽는 방식으로 구현하세요.

## RepoTrust가 보는 신뢰 신호

| 영역 | 보는 것 |
| --- | --- |
| README Quality | README가 목적, 설치, 사용법을 충분히 설명하는지 |
| Install Safety | 설치 명령이 위험한 원격 스크립트 실행을 유도하지 않는지 |
| Security Posture | SECURITY.md, CI, Dependabot, lockfile, dependency pinning 신호가 있는지 |
| Project Hygiene | LICENSE, dependency manifest 같은 기본 관리 신호가 있는지 |

`package.json`의 install lifecycle script와 exact version이 아닌 Node/Python direct dependency도 보수적인 finding으로 표시합니다. 이 검사는 취약점 여부를 판단하지 않고, 설치 중 자동 실행되거나 시간이 지나며 다른 dependency가 설치될 수 있는 신호를 알려줍니다.

아직 아래 항목은 점수화하지 않습니다.

- 취약점 DB 조회
- contributor 신뢰도
- star, fork, watcher 수
- GitHub App 상태

## 제거된 legacy 명령

`repotrust scan` legacy command는 제거됐습니다. 새 사용 경로는 `repo-trust`와 `repo-trust-kr`입니다.

| 제거된 명령 | 현재 명령 |
| --- | --- |
| `repotrust scan . --format html --output report.html` | `repo-trust html . --output report.html` |
| `repotrust scan . --format json --output report.json` | `repo-trust json . --output report.json` |
| `repotrust scan .` | `repo-trust check .` |

## 릴리즈 노트

현재 변경 사항과 공개 전 검증 목록은 `CHANGELOG.md`에 정리합니다. 배포 전에 JSON schema, `repo-trust gate`, offline-first GitHub URL 동작, sample report 생성 절차가 README와 changelog에서 같은 의미로 설명되는지 확인하세요.

## 개발자용 설치

RepoTrust를 수정하거나 테스트하려는 개발자는 저장소를 clone한 뒤 editable install을 사용하세요. 일반 사용자는 이 섹션을 건너뛰어도 됩니다.

```bash
git clone https://github.com/answndud/repo-trust.git
cd repo-trust
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## 개발자 검증

변경 후 기본 테스트를 실행합니다.

**입력할 명령**

```bash
python -m pytest -q
```

패키징이나 CLI entrypoint를 바꿨다면 clean venv에서 wheel install smoke도 확인합니다.

**입력할 명령**

```bash
python -m pip wheel --no-deps . --wheel-dir /tmp/repotrust-wheelhouse
python -m pip install /tmp/repotrust-wheelhouse/repotrust-*.whl
repo-trust --version
repo-trust-kr --version
```

dependency를 바꾼 경우에만 lockfile을 갱신합니다.

**입력할 명령**

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```
