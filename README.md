# RepoTrust

RepoTrust는 GitHub 저장소나 로컬 프로젝트를 쓰기 전에 기본 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 안내, 라이선스, 보안 정책, CI, lockfile, Dependabot, 선택적 GitHub metadata처럼 확인 가능한 근거를 모아 “지금 설치해도 되는지”, “dependency로 넣어도 되는지”, “AI agent에게 맡겨도 되는지”를 리포트로 정리합니다. 취약점 스캐너나 안전 보증 도구가 아니라, 사람이 먼저 확인해야 할 신뢰 신호와 불확실성을 빠르게 보여주는 도구입니다.

- 기본은 offline-first입니다. 로컬 검사는 네트워크를 쓰지 않고, GitHub URL 검사는 `--remote`를 명시하기 전까지 URL 형식만 확인합니다.
- PyPI/TestPyPI 배포는 하지 않습니다. 공식 배포 채널은 GitHub Releases입니다.
- 결과는 터미널 대시보드, JSON, static HTML, 비교 리포트로 볼 수 있습니다.
- secret key나 API 연결 없이 시작할 수 있습니다. GitHub API metadata가 필요할 때만 선택적으로 `--remote`와 token을 사용합니다.

English summary: RepoTrust is a Python CLI that helps you review observable trust signals before installing an open source repository, adopting it as a dependency, or handing it to an AI coding agent.

## 먼저 읽을 곳

처음 사용하는 사람은 아래 순서만 보면 됩니다.

1. [설치 빠른 시작](#installation-quickstart--설치-빠른-시작)에서 `repo-trust-kr`을 설치합니다.
2. [5분 시작 가이드](#5분-시작-가이드)에서 샘플 리포트와 실제 저장소 검사를 실행합니다.
3. [리포트 읽는 법](#리포트-읽는-법)에서 결과를 어떻게 판단할지 확인합니다.

CI, config, fixture, 개발자 검증은 RepoTrust를 프로젝트에 붙이거나 직접 개발할 때만 읽어도 됩니다.

## Installation Quickstart / 설치 빠른 시작

PyPI는 사용하지 않습니다. 공식 배포 채널은 GitHub Releases이며, 처음 쓰는 사람은 release wheel을 설치한 뒤 한국어 콘솔 모드인 `repo-trust-kr`로 시작하면 됩니다.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.10/repotrust-0.2.10-py3-none-any.whl
repo-trust-kr
```

터미널을 새로 열었다면 실행 전에 `source .venv/bin/activate`로 가상환경을 다시 활성화하세요.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.10/repotrust-0.2.10-py3-none-any.whl
repo-trust-kr
```

PowerShell에서 가상환경 활성화가 막히면 아래처럼 가상환경 안의 실행 파일을 직접 호출해도 됩니다.

```powershell
.\.venv\Scripts\python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.10/repotrust-0.2.10-py3-none-any.whl
.\.venv\Scripts\repo-trust-kr.exe
```

wheel 설치가 맞지 않는 환경에서는 같은 release의 source archive를 설치할 수 있습니다.

```bash
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.10/repotrust-0.2.10.tar.gz
```

## 5분 시작 가이드

설치가 끝났다면 실제 저장소를 바로 검사하기 전에 샘플 리포트부터 만들어 보세요.

```bash
repo-trust-kr samples
```

샘플은 좋은 예시와 위험 예시 HTML/JSON을 `result/` 폴더에 만듭니다. 좋은 리포트는 어떤 항목이 통과된 상태인지 보여주고, 위험 리포트는 설치 명령을 멈춰야 하는 상황을 보여줍니다.

내가 보고 있는 저장소를 검사할 때는 아래 순서로 진행하면 됩니다.

```bash
repo-trust-kr
```

1. `[L] 로컬 저장소`를 선택하고 경로에 `.`을 입력합니다.
2. README 설치 명령을 실행하기 전에는 `[S] 안전 설치`를 선택합니다.
3. 위험 finding이 있거나 무엇부터 해야 할지 모르겠다면 `[N] 다음 조치`를 선택합니다.
4. 나중에 다시 보거나 비교하려면 `[J] JSON 내보내기` 또는 `html` 명령으로 리포트를 저장합니다.

GitHub URL만 빠르게 확인할 때는 `[G] GitHub 저장소`를 선택하면 됩니다. 기본 GitHub URL 검사는 API나 token 없이 URL만 확인하므로 파일 수준 근거가 부족할 수 있습니다. 중요한 dependency 후보라면 로컬로 checkout한 뒤 `[L] 로컬 저장소`로 검사하는 편이 더 정확합니다.

## Usage / 사용 방식

RepoTrust는 같은 검사 기능을 두 가지 방식으로 제공합니다.

| 방식 | 명령 | 추천 상황 | 결과 |
| --- | --- | --- | --- |
| Console Mode | `repo-trust-kr` 또는 `repo-trust` | 메뉴에서 고르고 싶을 때 | 튜토리얼, 샘플 리포트, 검사, 안전 설치 안내, 다음 조치 계획, JSON 저장 |
| Command Mode | 아래 명령별 형식을 직접 입력 | 반복 실행, 자동화, 문서화할 때 | 튜토리얼, 샘플 리포트, HTML/JSON 파일, 터미널 대시보드, 안전 설치 안내, 다음 조치 계획, finding 설명, 리포트 비교 |

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
| CI policy 시작 파일 만들기 | `repo-trust init-policy` |
| finding ID 설명 보기 | `repo-trust explain <finding-id>` |
| JSON 리포트 2개 비교 | `repo-trust compare <old.json> <new.json>` |

`repo-trust-kr`은 메뉴, 프롬프트, 저장 안내, 검사 결과 대시보드, 다음에 할 일을 한국어로 보여줍니다. `repo-trust`는 같은 기능을 영어 화면으로 보여줍니다.

차이는 진입 방식입니다. Console Mode는 `repo-trust-kr`처럼 명령만 입력한 뒤 `[G]`, `[L]`, `[C]`, `[J]`, `[S]`, `[N]` 단축키로 작업을 고릅니다. Command Mode는 `repo-trust html https://github.com/openai/codex`처럼 처음부터 할 일을 한 줄에 적어 실행합니다. 파일 저장 규칙과 검사 기준은 같지만, `check`, `safe-install`, `next-steps`, `tutorial`은 파일을 저장하지 않고 터미널에만 결과를 보여줍니다.

Monorepo에서 특정 package만 검사하려면 로컬 checkout을 대상으로 `--subdir <상대경로>`를 사용할 수 있습니다.

```bash
repo-trust check . --subdir packages/api
repo-trust json . --subdir services/worker --output worker-repotrust.json
repo-trust safe-install --audit . --subdir packages/cli
```

`--subdir`은 로컬 대상에서만 동작합니다. GitHub `tree`/`blob` URL은 clone이나 API 호출 없이 URL 형식만 확인하므로, 하위 폴더 단위 신뢰 평가는 해당 저장소를 로컬로 checkout한 뒤 `--subdir`로 실행하세요.

## Console Mode

명령어 옵션을 외우지 않아도 되는 메뉴 방식입니다.
선택한 workflow의 결과는 같은 터미널에 바로 출력됩니다.

**입력할 명령**

```bash
repo-trust-kr
```

**화면 예시**

```text
RepoTrust v0.2.10
설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다.
처음이면: [L] 로컬 검사 -> [S] 안전 설치 -> [N] 다음 조치.
────────────────────────────────────
작업 선택:
G  GitHub 저장소  기본은 API 없이 URL 확인
L  로컬 저장소    파일 근거까지 로컬 검사
C  빠른 점검      즉시 요약 보기
J  JSON 내보내기  기계가 읽는 리포트 저장
S  안전 설치      설치 전 다음 단계 안내
N  다음 조치      검사 후 우선순위별 행동 계획
────────────────────────────────────
[?] 도움말   [Q] 종료
→ 키를 누르세요
```

단축키는 대소문자를 구분하지 않습니다. 잘못 선택했다면 입력 단계에서 `[B]`를 눌러 작업 선택 화면으로 돌아갈 수 있습니다. 기존 숫자 입력도 일부 호환되므로 `1` 또는 `01`은 로컬 리포트로 동작합니다. 튜토리얼과 샘플 리포트 생성은 `repo-trust tutorial`, `repo-trust samples` command mode로 실행하세요.

영어 화면이 필요하면 `repo-trust`를 입력하면 됩니다.

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

브라우저에서 읽을 리포트를 만들 때 사용합니다. GitHub URL은 기본적으로 API를 호출하지 않고 URL 형식만 확인합니다. 저장소 파일까지 검사하려면 로컬로 checkout한 폴더를 검사하고, GitHub read-only metadata가 필요할 때만 `--remote`를 명시합니다.

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

`safe-install`은 README에서 발견한 실제 설치 명령을 먼저 보여줍니다. high-risk install finding이 있으면 README 설치 명령을 아직 실행하지 말라고 안내하고, 실행 전 체크리스트와 안전한 다음 단계를 보여줍니다. Python이나 Node manifest가 보이면 source install도 코드 실행으로 보고, 가상환경, `pip install -e .`, `npm ci --ignore-scripts`처럼 격리된 검토/설치 패턴을 예시로 보여줍니다. GitHub URL을 기본값으로 검사하면 API 없이 URL만 확인하므로 설치 근거가 부족하다고 설명합니다. HTML 리포트의 `Safe Install` 섹션은 `Next isolated step`을 맨 위에 따로 보여주므로, 설치 명령을 실행하기 전에 먼저 할 일을 빠르게 확인할 수 있습니다.

`--audit`을 붙이면 README 설치 명령 외에도 설치 시점에 실행될 수 있는 표면을 한 번 더 점검합니다. 로컬 checkout을 대상으로 `pyproject.toml` build backend, `setup.py`, `package.json` install lifecycle script, root `Makefile`/`Dockerfile`/shell script, VCS dependency 신호를 보여줍니다. GitHub URL은 clone/API 호출 없이 로컬 checkout이 필요하다고 안내합니다. 기존 `audit-install` 명령은 호환용으로 남아 있지만 새 사용법은 `safe-install --audit`입니다.

### 위험 리포트를 받은 뒤 다음 조치 보기

리포트의 finding을 하나씩 해석하기 어렵다면 `next-steps`를 실행하세요. RepoTrust가 저장소를 검사한 뒤, 초보자가 바로 따라 할 수 있는 순서로 조치 계획을 보여줍니다. 고위험 설치 finding이 있으면 README 설치 명령을 먼저 멈추게 하고, 그 다음 license, CI, security policy 같은 adoption risk를 순서대로 정리합니다. HTML 리포트에도 같은 `Next Steps` 섹션이 들어갑니다.

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

### JSON 리포트 비교

개선 전/후 JSON 리포트를 비교해 점수와 finding 변화를 확인할 수 있습니다.

**입력할 명령**

```bash
repo-trust compare reports/repotrust-before.json reports/repotrust-after.json
repo-trust-kr compare reports/repotrust-before.json reports/repotrust-after.json
```

`compare`는 저장소를 다시 검사하지 않습니다. 이미 저장된 두 JSON 리포트를 읽어 score delta, grade/verdict 변화, 새 finding, 해결된 finding, severity 변경 finding을 보여줍니다.

비교 결과를 파일로 보관하거나 다른 사람에게 공유하려면 Markdown 또는 HTML로 저장합니다.

```bash
repo-trust compare reports/repotrust-before.json reports/repotrust-after.json --format markdown --output reports/repotrust-compare.md
repo-trust compare reports/repotrust-before.json reports/repotrust-after.json --format html --output reports/repotrust-compare.html
```

HTML 파일은 브라우저에서 열어 읽을 수 있고, Markdown 파일은 GitHub issue, PR 설명, 문서에 붙여 넣기 쉽습니다.

**비교 결과를 읽는 법**

- `Score`가 올라가면 전반적인 신뢰 신호가 개선된 것입니다.
- HTML 비교 리포트의 `Improvements`는 사라진 문제입니다. 숫자가 많을수록 개선된 항목이 많습니다.
- HTML 비교 리포트의 `New issues`는 새로 생긴 문제입니다. 0이어야 가장 좋습니다.
- `Severity changes`는 같은 finding의 심각도가 바뀐 경우입니다.
- `Still remaining`은 아직 남아 있는 문제입니다. HTML/JSON 리포트에서 해당 finding ID를 다시 확인하세요.
- HTML 비교 리포트에서 `Copy ID`는 finding ID만 복사하고, `Copy explain`은 `repo-trust explain <finding-id>` 명령을 복사합니다.

처음 연습할 때는 아래의 [샘플 리포트로 연습](#샘플-리포트로-연습) 섹션을 그대로 실행하면 됩니다.

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

GitHub API read-only metadata까지 확인하고 싶을 때만 `--remote`를 명시합니다. Public repository는 token 없이 시도할 수 있지만 rate limit이나 private repository 접근이 필요하면 `GITHUB_TOKEN`을 환경 변수로 설정합니다.

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
| 목적별 판단 | 설치, dependency 채택, AI agent 위임 관점의 별도 verdict |
| 다음 행동 | 지금 바로 실행할 후속 조치 |
| HTML `Next Steps` | 위험 finding을 어떤 순서로 확인하고 멈출지 |
| HTML `Safe Install` | README 설치 명령을 실행해도 되는지와 격리된 검토/설치 대안 |
| HTML `Prioritized Findings` | 각 finding의 위험 이유, 지금 할 일, 수용 가능한 조건, 실제 근거 |
| 리포트 | 저장된 HTML/JSON 리포트 위치 |
| DETAILS | 분석이 충분할 때만 보여주는 세부 점수와 근거 |

처음에는 아래 순서로 읽으면 됩니다.

1. 터미널의 `RESULT`와 `이유`/`WHY`에서 최종 판단과 상위 위험을 확인합니다.
2. HTML 리포트를 만들었다면 `Next Steps`를 먼저 보고, 설치를 멈춰야 하는지 판단합니다.
3. README의 설치 명령을 복사하기 전에는 `Safe Install`의 `Next isolated step`과 체크리스트를 확인합니다.
4. 더 자세한 근거가 필요하면 `Prioritized Findings`에서 `왜 위험한가요?`, `지금 할 일`, `언제 수용할 수 있나요?`, `실제 근거`를 확인합니다.
5. finding card의 `ID 복사`와 `explain 명령 복사` 버튼으로 `repo-trust explain <finding-id>` 설명을 이어서 봅니다.

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

저장소를 직접 판단하기 전에 내장 샘플로 좋은 결과와 위험 결과를 비교해 볼 수 있습니다. 이 방식은 설치한 wheel만으로 동작하며, RepoTrust 저장소를 clone하지 않아도 됩니다.

```bash
repo-trust-kr samples --output-dir repotrust-samples
repo-trust-kr next-steps --from-json repotrust-samples/sample-risky-YYYY-MM-DD.json
repo-trust-kr compare repotrust-samples/sample-risky-YYYY-MM-DD.json repotrust-samples/sample-good-YYYY-MM-DD.json
repo-trust-kr compare repotrust-samples/sample-risky-YYYY-MM-DD.json repotrust-samples/sample-good-YYYY-MM-DD.json --format html --output repotrust-samples/compare.html
python -m json.tool repotrust-samples/sample-good-YYYY-MM-DD.json
```

`YYYY-MM-DD`는 파일이 만들어진 날짜입니다. 정확한 파일명은 `samples` 명령이 출력하는 저장 경로를 그대로 복사하면 됩니다.

| 샘플 | 기대 결과 | 먼저 볼 항목 |
| --- | --- | --- |
| `sample-good` | `100/100`, grade `A`, high confidence | 모든 신호가 found이고 finding이 없어야 합니다. |
| `sample-risky` | `57/100`, grade `F`, high confidence | HTML/JSON의 전체 finding과 Install Safety가 `30/100`인지 확인합니다. |

`sample-risky`는 일부러 위험한 설치 명령을 담은 연습용 리포트입니다. 실제 저장소에서 비슷한 high finding이 나오면 명령을 바로 실행하지 말고, terminal `WHY`의 상위 항목과 HTML `Next Steps`, `Safe Install`, `Prioritized Findings`의 evidence/recommendation을 함께 확인하세요.

특정 finding을 더 자세히 보고 싶으면 `repo-trust explain <finding-id>`를 실행하세요. HTML 리포트에서는 finding card에서 해당 명령을 바로 복사할 수 있습니다.

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

`repo-trust init-policy`를 쓰면 현재 디렉터리에 `repotrust.toml`과 `.github/workflows/repotrust.yml` 시작 파일을 만듭니다. 기존 파일은 기본적으로 덮어쓰지 않습니다.

```bash
repo-trust init-policy
```

1. 생성된 `repotrust.toml`을 프로젝트의 정책에 맞게 검토합니다.
2. 생성된 `.github/workflows/repotrust.yml`을 pull request gate로 쓸지 결정합니다.
3. CI 또는 로컬에서 gate를 실행합니다.

```bash
repo-trust gate . --config repotrust.toml --output repotrust-report.json
```

RepoTrust 저장소를 clone한 개발자는 risky fixture로 정책 실패를 확인할 수 있습니다. 이 명령은 exit code `1`을 반환하지만 JSON report는 먼저 저장합니다.

```bash
repo-trust gate tests/fixtures/repos/risky-install --config examples/repotrust.toml --output /tmp/repotrust-fail.json
python -m json.tool /tmp/repotrust-fail.json
```

복사 가능한 템플릿은 `examples/repotrust.toml`과 `examples/github-actions-repotrust-gate.yml`에도 남겨 둡니다.

## 설정 파일

정책 점수 기준, 목적별 profile gate, category weight, finding 예외를 TOML 파일로 지정할 수 있습니다.

복사 가능한 시작점은 `examples/repotrust.toml`에 있습니다.

**설정 파일 예시**

```toml
[policy]
fail_under = 80

[policy.profiles]
install = "usable_after_review"
dependency = "usable_after_review"
agent_delegate = "usable_by_current_checks"

[rules]
disabled = ["remote.github_issues_disabled"]

[severity_overrides]
"security.no_policy" = "low"

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
```

**입력할 명령**

```bash
repo-trust html . --config /path/to/repotrust.toml
```

CLI 옵션이 config보다 우선합니다. `policy.profiles`는 `install`, `dependency`, `agent_delegate`에 대해 최소 허용 verdict를 지정합니다. verdict는 낮은 순서대로 `do_not_install_before_review`, `insufficient_evidence`, `usable_after_review`, `usable_by_current_checks`입니다.

`rules.disabled`는 지정한 finding ID를 리포트와 점수 계산에서 제외합니다. `severity_overrides`는 finding ID별 severity를 `info`, `low`, `medium`, `high` 중 하나로 바꾼 뒤 점수와 assessment를 다시 계산합니다. config 자동 탐지와 중앙 조직 policy server는 아직 지원하지 않습니다.

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

## 기존 호환 명령

기존 개발용 명령인 `repotrust scan`도 계속 동작합니다. 새 사용자 문서와 공식 예시는 `repo-trust`와 `repo-trust-kr` 기준으로 설명합니다.
`audit-install`도 기존 사용자를 위해 남아 있지만 실행 시 호환 명령 안내를 출력합니다. 새 사용법은 `repo-trust safe-install --audit <대상>`입니다.

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
repotrust --version
```

dependency를 바꾼 경우에만 lockfile을 갱신합니다.

**입력할 명령**

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```
