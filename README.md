# RepoTrust

RepoTrust is a Python CLI that helps you decide whether an open source repository is ready to install, adopt as a dependency, or hand to an AI coding agent.

- Offline-first by default: local scans use no network, and GitHub URL scans only parse the URL unless you explicitly pass `--remote`.
- GitHub Releases are the official distribution channel; PyPI/TestPyPI publishing is intentionally out of scope.
- Reports are available as terminal dashboards, JSON, static HTML, and saved comparison reports.
- RepoTrust is not a vulnerability scanner or safety guarantee. It surfaces trust signals, missing evidence, and risky install patterns so humans can review them before running commands.

RepoTrust는 GitHub 저장소나 로컬 프로젝트를 쓰기 전에 기본 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 안내, 라이선스, 보안 정책, CI, lockfile, Dependabot, 선택적 GitHub metadata처럼 확인 가능한 근거를 모아 “지금 설치해도 되는지”, “dependency로 넣어도 되는지”, “AI agent에게 맡겨도 되는지”를 리포트로 정리합니다. 취약점 스캐너나 안전 보증 도구가 아니라, 사람이 먼저 확인해야 할 신뢰 신호와 불확실성을 빠르게 보여주는 도구입니다.

## Installation Quickstart / 설치 빠른 시작

PyPI는 사용하지 않습니다. 공식 배포 채널은 GitHub Releases이며, 처음 쓰는 사람은 release wheel을 설치한 뒤 한국어 콘솔 모드인 `repo-trust-kr`로 시작하면 됩니다.

**입력할 명령**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.8/repotrust-0.2.8-py3-none-any.whl
repo-trust-kr
```

터미널을 새로 열었다면 실행 전에 `source .venv/bin/activate`로 가상환경을 다시 활성화하세요.

wheel 설치가 맞지 않는 환경에서는 같은 release의 source archive를 설치할 수 있습니다.

```bash
python -m pip install https://github.com/answndud/repo-trust/releases/download/v0.2.8/repotrust-0.2.8.tar.gz
```

## 처음 쓰는 사람은 3단계만

처음에는 명령어 옵션을 외우지 말고 한국어 Console Mode로 시작하세요.

### 1. 메뉴 열기

```bash
repo-trust-kr
```

### 2. 검사 리포트 만들기

- 내 컴퓨터에 있는 프로젝트를 검사하려면 `[L] 로컬 저장소`를 선택하고 경로에 `.`을 입력합니다.
- GitHub URL을 빠르게 확인하려면 `[G] GitHub 저장소`를 선택하고 URL을 붙여 넣습니다.
- 나중에 비교할 JSON을 남기려면 `[J] JSON 내보내기`를 선택합니다.

### 3. 설치 전 안내와 개선 전/후 비교 확인하기

README의 설치 명령을 실행하기 전에는 `[S] 안전 설치`를 선택해 먼저 확인하세요. JSON 리포트를 두 번 저장했다면 `[M] JSON 비교`를 선택하세요. 최근 JSON 목록에서 이전 리포트 번호와 최신 리포트 번호를 고르면 브라우저에서 열 수 있는 비교 HTML이 만들어집니다. 저장한 파일은 나중에 `[R] 리포트`에서 다시 찾을 수 있습니다.

RepoTrust를 수정하거나 테스트하려는 개발자는 저장소를 clone한 뒤 editable install을 사용하세요.

```bash
git clone https://github.com/answndud/repo-trust.git
cd repo-trust
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Usage / 사용 방식

RepoTrust는 같은 검사 기능을 두 가지 방식으로 제공합니다.

| 방식 | 명령 | 추천 상황 | 결과 |
| --- | --- | --- | --- |
| Console Mode | `repo-trust-kr` 또는 `repo-trust` | 메뉴에서 고르고 싶을 때 | 튜토리얼, 샘플 리포트, 검사, 안전 설치 안내, 다음 조치 계획, JSON 저장, JSON 비교 workflow 선택 |
| Command Mode | `repo-trust tutorial/samples/html/json/check/safe-install/next-steps/explain/compare <대상, finding ID, 리포트>` | 반복 실행, 자동화, 문서화할 때 | 튜토리얼, 샘플 리포트, HTML/JSON 파일, 터미널 대시보드, 안전 설치 안내, 다음 조치 계획, finding 설명, 리포트 비교 |

`repo-trust-kr`은 메뉴, 프롬프트, 저장 안내, 검사 결과 대시보드, 다음에 할 일을 한국어로 보여줍니다. `repo-trust`는 같은 기능을 영어 화면으로 보여줍니다.

차이는 진입 방식입니다. Console Mode는 `repo-trust-kr`처럼 명령만 입력한 뒤 `[G]`, `[L]`, `[C]`, `[J]`, `[S]`, `[N]`, `[T]`, `[P]`, `[M]` 단축키로 작업을 고릅니다. 실제 터미널에서는 `git log`처럼 별도 화면에서 열려 이전 터미널 내역을 가리고, 작업을 끝내면 원래 화면으로 돌아갑니다. Command Mode는 `repo-trust html https://github.com/openai/codex`처럼 처음부터 할 일을 한 줄에 적어 실행합니다. 파일 저장 규칙과 검사 기준은 같지만, `check`, `safe-install`, `next-steps`, `tutorial`은 파일을 저장하지 않고 터미널에만 결과를 보여줍니다.

## Console Mode

명령어 옵션을 외우지 않아도 되는 메뉴 방식입니다.
실제 터미널에서는 alternate screen을 사용하므로 이전 터미널 출력이 뒤에 보이지 않습니다. scan이나 recent reports 같은 workflow를 실행한 뒤에는 결과를 읽고 Enter를 누르면 원래 화면으로 돌아갑니다.

**입력할 명령**

```bash
repo-trust-kr
```

**화면 예시**

```text
RepoTrust v0.2.8
설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다.
처음이면: [L] 로컬 검사 -> [S] 안전 설치 -> [J] JSON 저장.
────────────────────────────────────
작업 선택:
G  GitHub 저장소  기본은 API 없이 URL 확인
L  로컬 저장소    파일 근거까지 로컬 검사
C  빠른 점검      즉시 요약 보기
J  JSON 내보내기  기계가 읽는 리포트 저장
S  안전 설치      설치 전 다음 단계 안내
N  다음 조치      검사 후 우선순위별 행동 계획
T  튜토리얼       처음 따라 할 명령 보기
P  샘플           좋은/위험 리포트 예시 생성
M  JSON 비교      개선 전/후 HTML 만들기
────────────────────────────────────
최근 리포트: 3개
[R] 리포트   [?] 도움말   [Q] 종료
→ 키를 누르세요
```

단축키는 대소문자를 구분하지 않습니다. 잘못 선택했다면 입력 단계에서 `[B]`를 눌러 작업 선택 화면으로 돌아갈 수 있습니다. 기존 숫자 입력도 호환되므로 `1` 또는 `01`은 로컬 리포트, `5` 또는 `05`는 최근 리포트 목록으로 동작합니다. `[R]` workflow는 파일을 직접 열거나 브라우저를 실행하지 않습니다. `result/` 폴더에 있는 최근 HTML/JSON/Markdown 리포트 목록과 macOS에서 `open <경로>`로 여는 힌트를 보여줍니다.

영어 화면이 필요하면 `repo-trust`를 입력하면 됩니다.

### Console Mode에서 JSON 비교 HTML 만들기

명령어 옵션을 외우기 어렵다면 `repo-trust-kr`에서 `[M] JSON 비교`를 선택하세요. `result/`에 저장된 최근 JSON 리포트가 있으면 목록이 먼저 보이고, 번호를 입력해 이전/최신 리포트를 고를 수 있습니다. 목록에 없는 파일은 경로를 직접 입력해도 됩니다.

```text
→ 키를 누르세요
m
최근 JSON 리포트
번호  경로                                      수정 시간
1     result/repotrust-after-2026-05-06.json   2026-05-06 13:20
2     result/repotrust-before-2026-05-06.json  2026-05-06 13:10
이전 JSON 리포트 경로 입력:
> 2
최신 JSON 리포트 경로 입력:
> 1
비교 HTML 저장 경로 입력: (기본값 repotrust-compare.html)
>
```

마지막 입력에서 Enter만 누르면 `result/repotrust-compare-YYYY-MM-DD.html` 형태로 저장됩니다. 저장 후에는 `[R] 리포트`에서 `비교 HTML` 항목으로 다시 찾을 수 있습니다.

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

JSON 파일은 `schema_version`, `target`, `detected_files`, `findings`, `score`, `assessment`, `generated_at`을 포함합니다. `assessment.profiles`에는 설치, dependency 채택, AI agent 위임 목적별 판단이 들어갑니다. 터미널 대시보드는 stderr로만 출력되므로 JSON 파일 내용과 섞이지 않습니다. 자동화에서 파싱할 key와 compatibility 기준은 [docs/json-report-reference.md](docs/json-report-reference.md)에 정리되어 있습니다.

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
repo-trust safe-install tests/fixtures/repos/risky-install
repo-trust-kr safe-install tests/fixtures/repos/good-python
repo-trust safe-install https://github.com/openai/codex
```

`safe-install`은 README에서 발견한 실제 설치 명령을 먼저 보여줍니다. high-risk install finding이 있으면 README 설치 명령을 아직 실행하지 말라고 안내하고, 실행 전 체크리스트와 안전한 다음 단계를 보여줍니다. Python이나 Node manifest가 보이면 가상환경, `pip install -e .`, `npm ci --ignore-scripts`처럼 더 격리된 설치 패턴을 예시로 보여줍니다. GitHub URL을 기본값으로 검사하면 API 없이 URL만 확인하므로 설치 근거가 부족하다고 설명합니다. HTML 리포트의 `Safe Install` 섹션은 `Next safest command`를 맨 위에 따로 보여주므로, 설치 명령을 실행하기 전에 먼저 할 일을 빠르게 확인할 수 있습니다.

### 위험 리포트를 받은 뒤 다음 조치 보기

리포트의 finding을 하나씩 해석하기 어렵다면 `next-steps`를 실행하세요. RepoTrust가 저장소를 다시 검사한 뒤, 초보자가 바로 따라 할 수 있는 순서로 조치 계획을 보여줍니다. 고위험 설치 finding이 있으면 README 설치 명령을 먼저 멈추게 하고, 그 다음 license, CI, security policy 같은 adoption risk를 순서대로 정리합니다.

**입력할 명령**

```bash
repo-trust next-steps tests/fixtures/repos/risky-install
repo-trust-kr next-steps tests/fixtures/repos/good-python
```

좋은 저장소에서는 짧은 확인 checklist와 `safe-install`, `html` 명령을 보여줍니다. 위험 저장소에서는 `repo-trust explain <finding-id>` 명령도 함께 보여주므로, HTML 리포트에서 본 finding을 터미널에서 바로 풀어 읽을 수 있습니다. 이 기능은 자동 수정을 하지 않고, 외부 API나 secret key 없이 로컬 검사 결과만 사용합니다.

### JSON 리포트 비교

개선 전/후 JSON 리포트를 비교해 점수와 finding 변화를 확인할 수 있습니다.

**입력할 명령**

```bash
repo-trust compare /tmp/repotrust-before.json /tmp/repotrust-after.json
repo-trust-kr compare /tmp/repotrust-before.json /tmp/repotrust-after.json
```

`compare`는 저장소를 다시 검사하지 않습니다. 이미 저장된 두 JSON 리포트를 읽어 score delta, grade/verdict 변화, 새 finding, 해결된 finding, severity 변경 finding을 보여줍니다.

비교 결과를 파일로 보관하거나 다른 사람에게 공유하려면 Markdown 또는 HTML로 저장합니다.

```bash
repo-trust compare /tmp/repotrust-before.json /tmp/repotrust-after.json --format markdown --output /tmp/repotrust-compare.md
repo-trust compare /tmp/repotrust-before.json /tmp/repotrust-after.json --format html --output /tmp/repotrust-compare.html
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
| `tests/fixtures/repos/good-python` | `result/good-python-YYYY-MM-DD.html` | `result/good-python-YYYY-MM-DD.json` |

저장 위치를 직접 정해야 할 때만 `--output`을 사용합니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex --output reports/codex.html
```

디렉터리를 포함한 경로는 그대로 사용합니다. 파일명만 넣으면 기존 호환 규칙에 따라 `result/<파일명>-YYYY-MM-DD.<확장자>`로 저장됩니다.

## 도움말

`--help`를 붙이면 먼저 도움말 언어를 고릅니다.

**입력할 명령**

```bash
repo-trust --help
```

**화면 예시**

```text
┌──(repotrust㉿help)-[language]
│ 01 english
│ 02 한국어
└─$ help language [1]:
```

`1`을 입력하면 영어 도움말이 나오고, `2`를 입력하면 한국어 도움말이 나옵니다. `repo-trust-kr --help`, `repo-trust html --help`, `repo-trust json --help`, `repo-trust check --help`도 같은 방식으로 동작합니다.

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
GITHUB_TOKEN=ghp_example repo-trust html https://github.com/owner/private-repo --remote
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 리포트 읽는 법

처음에는 아래 항목만 보면 됩니다.

| 위치 | 확인할 내용 |
| --- | --- |
| RESULT | 최종 판단, 위험도, 점수, confidence |
| 이유 | 판단에 영향을 준 주요 finding 또는 통과 이유 |
| 목적별 판단 | 설치, dependency 채택, AI agent 위임 관점의 별도 verdict |
| 다음 행동 | 지금 바로 실행할 후속 조치 |
| 리포트 | 저장된 HTML/JSON 리포트 위치 |
| DETAILS | 분석이 충분할 때만 보여주는 세부 점수와 근거 |

터미널의 `이유`/`WHY` 영역은 빠르게 읽을 수 있도록 심각도 기준 상위 3개 finding만 요약합니다. 전체 finding은 저장된 HTML 리포트의 `Prioritized Findings` 섹션이나 JSON의 `findings` 배열에서 확인하세요. HTML 리포트의 `Safe Install` 섹션은 `Next safest command`, 실행 전 체크리스트, README에서 발견한 설치 명령, 더 안전한 설치 패턴을 함께 보여줍니다. HTML finding card는 `터미널 없이 읽는 설명과 근거`를 포함하므로 CLI를 다시 열지 않아도 finding의 의미, 실제 근거, 추천 조치를 바로 읽을 수 있습니다. 각 finding card의 `ID 복사`와 `explain 명령 복사` 버튼으로 터미널 설명 명령을 바로 이어서 실행할 수 있습니다. HTML/JSON 리포트를 저장한 뒤 터미널의 `Open with: open <path>` 또는 `열기 명령: open <경로>` 안내를 복사하면 macOS에서 바로 파일을 열 수 있습니다.

심각도는 이렇게 해석하면 됩니다.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 확인하면 좋은 낮은 위험 |
| `medium` | dependency로 쓰기 전에 검토할 항목 |
| `high` | 설치 전에 반드시 확인할 항목 |

`high`나 `medium` finding이 있거나 confidence가 `low`이면 README의 설치 명령을 바로 실행하지 말고, 리포트의 근거와 추천 조치를 먼저 확인하세요. `unknown` evidence는 파일이 없다는 뜻이 아니라 이번 실행에서 확인하지 못했다는 뜻입니다.

## 샘플 리포트로 연습

저장소를 직접 판단하기 전에 fixture로 좋은 결과와 위험 결과를 비교해 볼 수 있습니다.

```bash
repo-trust json tests/fixtures/repos/good-python --output /tmp/repotrust-good.json
repo-trust html tests/fixtures/repos/good-python --output /tmp/repotrust-good.html
repo-trust safe-install tests/fixtures/repos/good-python
repo-trust check tests/fixtures/repos/risky-install
repo-trust safe-install tests/fixtures/repos/risky-install
repo-trust json tests/fixtures/repos/risky-install --output /tmp/repotrust-risky.json
repo-trust html tests/fixtures/repos/risky-install --output /tmp/repotrust-risky.html
repo-trust compare /tmp/repotrust-risky.json /tmp/repotrust-good.json
repo-trust compare /tmp/repotrust-risky.json /tmp/repotrust-good.json --format html --output /tmp/repotrust-compare.html
repo-trust compare /tmp/repotrust-risky.json /tmp/repotrust-good.json --format markdown --output /tmp/repotrust-compare.md
python -m json.tool /tmp/repotrust-good.json
python -m json.tool /tmp/repotrust-risky.json
```

| Fixture | 기대 결과 | 먼저 볼 항목 |
| --- | --- | --- |
| `good-python` | `100/100`, grade `A`, high confidence | 모든 신호가 found이고 finding이 없어야 합니다. |
| `risky-install` | `51/100`, grade `F`, high confidence | 터미널은 전체 12개 finding 중 상위 3개를 먼저 보여주고, HTML/JSON은 전체 finding을 보여줍니다. Install Safety가 `0/100`인지 확인합니다. |

`risky-install`은 일부러 위험한 설치 명령을 담은 연습용 fixture입니다. 실제 저장소에서 비슷한 high finding이 나오면 명령을 바로 실행하지 말고, terminal `WHY`의 상위 항목과 HTML `Prioritized Findings`의 전체 evidence/recommendation을 함께 확인하세요.

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

이 저장소의 예시는 그대로 복사해 시작할 수 있습니다.

1. `examples/repotrust.toml`을 프로젝트의 정책에 맞게 검토합니다.
2. GitHub Actions를 쓴다면 `examples/github-actions-repotrust-gate.yml` 내용을 `.github/workflows/repotrust.yml`로 복사합니다.
3. CI 또는 로컬에서 gate를 실행합니다.

```bash
repo-trust gate . --config examples/repotrust.toml --output repotrust-report.json
```

정책 실패를 확인하려면 risky fixture로 실행해 볼 수 있습니다. 이 명령은 exit code `1`을 반환하지만 JSON report는 먼저 저장합니다.

```bash
repo-trust gate tests/fixtures/repos/risky-install --config examples/repotrust.toml --output /tmp/repotrust-fail.json
python -m json.tool /tmp/repotrust-fail.json
```

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

정책에서 사용할 finding ID와 예외 처리 기준은 [docs/finding-reference.md](docs/finding-reference.md)에 정리되어 있습니다. JSON report를 직접 파싱하는 도구는 [docs/json-report-reference.md](docs/json-report-reference.md)를 기준으로 구현하세요.

## RepoTrust가 보는 신뢰 신호

| 영역 | 보는 것 |
| --- | --- |
| README Quality | README가 목적, 설치, 사용법을 충분히 설명하는지 |
| Install Safety | 설치 명령이 위험한 원격 스크립트 실행을 유도하지 않는지 |
| Security Posture | SECURITY.md, CI, Dependabot, lockfile, dependency pinning 신호가 있는지 |
| Project Hygiene | LICENSE, dependency manifest 같은 기본 관리 신호가 있는지 |

`package.json`의 install lifecycle script와 exact version이 아닌 Node/Python direct dependency도 보수적인 finding으로 표시합니다. `--remote`를 명시한 GitHub 원격 검사에서는 package manifest가 있는 저장소에 한해 오래된 최신 release/tag도 낮은 심각도로 알려줍니다. 이 검사는 취약점 여부를 판단하지 않고, 설치 중 자동 실행되거나 시간이 지나며 다른 dependency가 설치될 수 있는 신호를 알려줍니다.

아직 아래 항목은 점수화하지 않습니다.

- 취약점 DB 조회
- contributor 신뢰도
- star, fork, watcher 수
- GitHub App 상태

## 기존 호환 명령

기존 개발용 명령인 `repotrust scan`도 계속 동작합니다. 새 사용자 문서와 공식 예시는 `repo-trust`와 `repo-trust-kr` 기준으로 설명합니다.

## 릴리즈 노트

현재 변경 사항과 공개 전 검증 목록은 `CHANGELOG.md`에 정리합니다. 배포 전에 JSON schema, `repo-trust gate`, offline-first GitHub URL 동작, sample report 생성 절차가 README와 changelog에서 같은 의미로 설명되는지 확인하세요.

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
