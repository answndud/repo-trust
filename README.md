# RepoTrust

RepoTrust는 오픈소스 저장소를 설치하거나 프로젝트 dependency로 추가하기 전에 기본 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 명령, 보안 정책, CI, lockfile, 라이선스 같은 파일과 GitHub metadata를 보고 “이 저장소를 지금 믿고 써도 되는지” 판단할 수 있는 HTML/JSON 리포트를 만듭니다.

## 1. 설치

저장소 루트에서 한 번만 설치합니다.

**입력할 명령**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
repo-trust --version
```

**예상 출력**

```text
repo-trust 0.1.0
```

터미널을 새로 열었다면 실행 전에 `source .venv/bin/activate`로 가상환경을 다시 활성화하세요.

## 2. GitHub URL을 HTML로 저장

브라우저에서 읽을 리포트가 필요하면 `html` 명령을 사용합니다. GitHub URL을 넣으면 RepoTrust가 GitHub REST API의 read-only metadata를 조회합니다. repository를 clone하지 않습니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.html
```

예를 들어 2026년 4월 28일에 실행하면 `result/codex-2026-04-28.html` 파일이 생깁니다. 이 파일을 브라우저에서 열어 점수, 발견 항목, 추천 조치를 확인하세요.

## 3. GitHub URL을 JSON으로 저장

자동화나 다른 도구에서 읽을 결과가 필요하면 `json` 명령을 사용합니다.

**입력할 명령**

```bash
repo-trust json https://github.com/openai/codex
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.json
```

JSON은 `schema_version`, `target`, `detected_files`, `findings`, `score`, `generated_at`을 포함합니다. 터미널의 요약 대시보드는 stderr로만 출력되므로 JSON 파일 내용과 섞이지 않습니다.

## 4. 로컬 폴더를 HTML로 저장

이미 clone한 저장소나 현재 작업 중인 프로젝트를 검사하려면 로컬 경로를 넣습니다. 로컬 검사는 네트워크를 사용하지 않습니다.

**입력할 명령**

```bash
repo-trust html .
```

**생성되는 파일 예시**

```text
result/repo-trust-YYYY-MM-DD.html
```

다른 폴더를 검사할 때는 `.` 대신 해당 경로를 넣으면 됩니다.

## 5. 터미널에서 바로 확인

파일을 만들지 않고 터미널에서 빠르게 점검하려면 `check` 명령을 사용합니다.

**입력할 명령**

```bash
repo-trust check https://github.com/openai/codex
```

**예상 출력**

```text
RepoTrust
target https://github.com/openai/codex
mode GitHub remote  format markdown

RepoTrust Dashboard
Score  92/100
Grade  A
Risk   LOW RISK
```

실제 출력에는 finding 목록과 다음 조치가 함께 표시될 수 있습니다.

## 6. 결과 파일 규칙

`html`과 `json` 명령은 기본적으로 `result/` 폴더에 날짜가 붙은 파일을 만듭니다.

| 입력 대상 | HTML 결과 예시 | JSON 결과 예시 |
| --- | --- | --- |
| `https://github.com/openai/codex` | `result/codex-YYYY-MM-DD.html` | `result/codex-YYYY-MM-DD.json` |
| `.` | `result/<현재폴더>-YYYY-MM-DD.html` | `result/<현재폴더>-YYYY-MM-DD.json` |
| `tests/fixtures/repos/good-python` | `result/good-python-YYYY-MM-DD.html` | `result/good-python-YYYY-MM-DD.json` |

원하는 위치에 직접 저장해야 할 때만 `--output`을 사용합니다.

**입력할 명령**

```bash
repo-trust html https://github.com/openai/codex --output reports/codex.html
```

디렉터리를 포함한 경로는 그대로 사용합니다. 파일명만 넣는 경우에는 기존 호환 규칙에 따라 `result/<파일명>-YYYY-MM-DD.<확장자>`로 저장됩니다.

## 7. GitHub URL을 네트워크 없이 파싱

GitHub API를 호출하지 않고 URL 형식만 확인하고 싶으면 `--parse-only`를 사용합니다.

**입력할 명령**

```bash
repo-trust check https://github.com/openai/codex --parse-only
```

이 경우 remote metadata, README 내용, LICENSE, CI 같은 원격 파일 기반 판단은 하지 않습니다. 리포트에는 `target.github_not_fetched` finding이 나올 수 있습니다.

Private repository를 검사하거나 GitHub rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 환경 변수로 설정한 뒤 실행합니다.

**입력할 명령**

```bash
GITHUB_TOKEN=ghp_example repo-trust html https://github.com/owner/private-repo
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 8. 리포트 읽는 법

HTML 리포트는 한국어로 작성됩니다. 처음에는 아래 네 부분만 보면 됩니다.

| 위치 | 확인할 내용 |
| --- | --- |
| 전체 판단 | 지금 바로 설치해도 되는지에 대한 요약 |
| 검사 영역별 점수 | README, 설치 안전성, 보안, 프로젝트 관리 중 약한 영역 |
| 발견된 파일과 의미 | README, LICENSE, SECURITY.md, CI, lockfile 같은 근거 파일 |
| 발견 항목과 추천 조치 | 실제 문제, 근거, 다음에 해야 할 일 |

심각도는 이렇게 해석합니다.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 확인하면 좋은 낮은 위험 |
| `medium` | dependency로 쓰기 전에 검토할 항목 |
| `high` | 설치 전에 반드시 확인할 항목 |

`high`나 `medium` finding이 있으면 README의 설치 명령을 바로 실행하지 말고, 리포트의 근거와 추천 조치를 먼저 확인하세요.

## 9. 실패 기준 설정

점수가 기준보다 낮을 때 명령을 실패시키려면 `--fail-under`를 사용합니다.

**입력할 명령**

```bash
repo-trust json https://github.com/openai/codex --fail-under 80
```

동작은 다음과 같습니다.

| 상황 | Exit code |
| --- | --- |
| 점수가 기준 이상 | `0` |
| 점수가 기준 미만 | `1` |
| 잘못된 인자 또는 config 오류 | `2` |

점수가 낮아도 리포트 파일은 먼저 저장됩니다.

## 10. 설정 파일

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

CLI 옵션이 config보다 우선합니다. 예를 들어 `--fail-under`를 명령에 직접 쓰면 config의 `policy.fail_under`보다 우선합니다.

현재 지원하는 config는 `policy.fail_under`와 네 category weight입니다. rule enable/disable, finding별 severity override, config 자동 탐지는 아직 지원하지 않습니다.

## 11. Help 확인

명령어 구조와 옵션은 CLI에서 바로 확인할 수 있습니다.

**입력할 명령**

```bash
repo-trust --help
repo-trust html --help
repo-trust json --help
repo-trust check --help
```

기존 개발용 명령인 `repotrust scan`도 호환용으로 계속 동작합니다. 새 사용자 문서와 예시는 `repo-trust html/json/check`를 기준으로 설명합니다.

## 12. RepoTrust가 보는 신뢰 신호

RepoTrust는 현재 네 영역을 점수화합니다.

| 영역 | 보는 것 |
| --- | --- |
| README Quality | README가 목적, 설치, 사용법을 충분히 설명하는지 |
| Install Safety | 설치 명령이 위험한 원격 스크립트 실행을 유도하지 않는지 |
| Security Posture | SECURITY.md, CI, Dependabot, lockfile이 있는지 |
| Project Hygiene | LICENSE, dependency manifest 같은 기본 관리 신호가 있는지 |

RepoTrust는 아직 아래 항목을 점수화하지 않습니다.

- 취약점 DB 조회
- contributor 신뢰도
- release/tag freshness
- star, fork, watcher 수
- GitHub App 상태

## 13. 개발자 검증

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
