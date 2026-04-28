# RepoTrust

RepoTrust는 GitHub 저장소나 로컬 프로젝트를 쓰기 전에 기본 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 안내, 라이선스, 보안 정책, CI, lockfile, Dependabot, GitHub metadata처럼 확인 가능한 근거를 모아 “지금 설치해도 되는지”, “dependency로 넣어도 되는지”, “AI agent에게 맡겨도 되는지”를 리포트로 정리합니다. 취약점 스캐너나 안전 보증 도구가 아니라, 사람이 먼저 확인해야 할 신뢰 신호와 불확실성을 빠르게 보여주는 도구입니다.

## Installation Quickstart / 설치 빠른 시작

처음 쓰는 사람은 한국어 콘솔 모드인 `repo-trust-kr`로 시작하면 됩니다.

**입력할 명령**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
repo-trust-kr
```

터미널을 새로 열었다면 실행 전에 `source .venv/bin/activate`로 가상환경을 다시 활성화하세요.

## Usage / 사용 방식

RepoTrust는 같은 검사 기능을 두 가지 방식으로 제공합니다.

| 방식 | 명령 | 추천 상황 | 결과 |
| --- | --- | --- | --- |
| Console Mode | `repo-trust-kr` 또는 `repo-trust` | 메뉴에서 고르고 싶을 때 | 터미널 workflow 선택 |
| Command Mode | `repo-trust html/json/check <대상>` | 반복 실행, 자동화, 문서화할 때 | HTML/JSON 파일 또는 터미널 대시보드 |

`repo-trust-kr`은 메뉴, 프롬프트, 저장 안내, 검사 결과 대시보드, 다음에 할 일을 한국어로 보여줍니다. `repo-trust`는 같은 기능을 영어 화면으로 보여줍니다.

## Console Mode

명령어 옵션을 외우지 않아도 되는 메뉴 방식입니다.

**입력할 명령**

```bash
repo-trust-kr
```

**화면 예시**

```text
RepoTrust 한국어 콘솔
dependency, agent, audit를 위한 저장소 신뢰도 점검 도구

워크플로우
1  로컬 저장소 검사      이미 clone한 폴더가 있을 때
2  GitHub URL 검사       브라우저용 원격 리포트가 필요할 때
3  GitHub URL 내보내기   자동화용 데이터가 필요할 때
4  빠른 점검             터미널에서 바로 판단할 때
5  최근 리포트 목록      이전 결과 파일을 찾을 때
6  명령어 도움말         직접 명령과 옵션을 확인할 때
q  종료
```

5번 workflow는 파일을 직접 열지 않고 `result/` 폴더에 있는 최근 HTML/JSON 리포트 목록만 보여줍니다.

영어 화면이 필요하면 `repo-trust`를 입력하면 됩니다.

## Command Mode

Command Mode는 명령을 한 줄로 직접 입력하는 방식입니다. 자동화하거나 같은 검사를 반복할 때 적합합니다.

### GitHub URL을 HTML로 저장

브라우저에서 읽을 리포트를 만들 때 사용합니다. GitHub URL은 기본적으로 GitHub REST API의 read-only metadata를 조회합니다. 저장소를 clone하지 않습니다.

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

JSON 파일은 `schema_version`, `target`, `detected_files`, `findings`, `score`, `assessment`, `generated_at`을 포함합니다. 터미널 대시보드는 stderr로만 출력되므로 JSON 파일 내용과 섞이지 않습니다.

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

```text
RepoTrust 한국어 모드
검사 대상 https://github.com/openai/codex
검사 방식 GitHub 원격 검사  리포트 형식 터미널

신뢰도 검사 결과
결론 현재 검사 기준으로 사용 가능
확실도 높음  검사 범위 충분히 확인
점수 92/100  등급 A  위험도 위험 낮음
발견 항목 높음:0  보통:0  낮음:0  정보:1

다음에 할 일
1. 점수와 근거가 기대와 맞는지 확인하세요.
2. 중요한 프로젝트에 쓰기 전에는 HTML 리포트를 저장해 보관하세요.
```

위 출력은 화면 구조 예시입니다. GitHub URL 검사는 GitHub API 응답, rate limit, 인증 상태, 저장소 변경에 따라 점수, confidence, coverage, finding이 달라질 수 있습니다.

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
Help language / 도움말 언어
1. English
2. 한국어
Select [1]:
```

`1`을 입력하면 영어 도움말이 나오고, `2`를 입력하면 한국어 도움말이 나옵니다. `repo-trust-kr --help`, `repo-trust html --help`, `repo-trust json --help`, `repo-trust check --help`도 같은 방식으로 동작합니다.

## 네트워크 없이 GitHub URL만 확인

GitHub API를 호출하지 않고 URL 형식만 확인하고 싶으면 `--parse-only`를 사용합니다.

**입력할 명령**

```bash
repo-trust-kr check https://github.com/openai/codex --parse-only
```

이 경우 README, LICENSE, CI 같은 원격 파일은 확인하지 않습니다. 결과에는 `근거 부족`, `기본 정보만 확인`, `확인 못함` 같은 표시가 나올 수 있습니다.

Private repository를 검사하거나 GitHub rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 환경 변수로 설정한 뒤 실행합니다.

**입력할 명령**

```bash
GITHUB_TOKEN=ghp_example repo-trust html https://github.com/owner/private-repo
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 리포트 읽는 법

처음에는 아래 항목만 보면 됩니다.

| 위치 | 확인할 내용 |
| --- | --- |
| Assessment | 최종 verdict, 점수, confidence, coverage |
| Evidence Matrix | README, LICENSE, SECURITY.md, CI, lockfile 같은 근거가 확인됐는지 |
| Why This Score | finding과 scan completeness가 점수에 준 영향 |
| Prioritized Findings | 실제 문제, 근거, 추천 조치 |
| Next Actions | 지금 바로 할 후속 조치 |

심각도는 이렇게 해석하면 됩니다.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 확인하면 좋은 낮은 위험 |
| `medium` | dependency로 쓰기 전에 검토할 항목 |
| `high` | 설치 전에 반드시 확인할 항목 |

`high`나 `medium` finding이 있거나 confidence가 `low`이면 README의 설치 명령을 바로 실행하지 말고, 리포트의 근거와 추천 조치를 먼저 확인하세요. `unknown` evidence는 파일이 없다는 뜻이 아니라 이번 실행에서 확인하지 못했다는 뜻입니다.

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

## 설정 파일

정책 점수 기준과 category weight를 TOML 파일로 지정할 수 있습니다.

**설정 파일 예시**

```toml
[policy]
fail_under = 80

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

CLI 옵션이 config보다 우선합니다. 현재 지원하는 config는 `policy.fail_under`와 네 category weight입니다. rule enable/disable, finding별 severity override, config 자동 탐지는 아직 지원하지 않습니다.

## RepoTrust가 보는 신뢰 신호

| 영역 | 보는 것 |
| --- | --- |
| README Quality | README가 목적, 설치, 사용법을 충분히 설명하는지 |
| Install Safety | 설치 명령이 위험한 원격 스크립트 실행을 유도하지 않는지 |
| Security Posture | SECURITY.md, CI, Dependabot, lockfile이 있는지 |
| Project Hygiene | LICENSE, dependency manifest 같은 기본 관리 신호가 있는지 |

아직 아래 항목은 점수화하지 않습니다.

- 취약점 DB 조회
- contributor 신뢰도
- release/tag freshness
- star, fork, watcher 수
- GitHub App 상태

## 기존 호환 명령

기존 개발용 명령인 `repotrust scan`도 계속 동작합니다. 새 사용자 문서와 공식 예시는 `repo-trust`와 `repo-trust-kr` 기준으로 설명합니다.

## 개발자 검증

변경 후 기본 테스트를 실행합니다.

**입력할 명령**

```bash
python -m pytest -q
```

dependency를 바꾼 경우에만 lockfile을 갱신합니다.

**입력할 명령**

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```
