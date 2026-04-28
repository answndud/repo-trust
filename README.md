# RepoTrust

RepoTrust는 오픈소스 저장소를 설치하거나 프로젝트 dependency로 추가하기 전에, 기본적인 신뢰 신호를 점검하는 Python CLI 도구입니다.

README, 설치 명령, 보안 정책, CI, lockfile, 라이선스 같은 파일을 보고 “이 저장소를 지금 믿고 써도 되는지” 판단할 수 있는 리포트를 만듭니다.

## 1. 설치

저장소 루트에서 한 번만 실행합니다.

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

터미널을 새로 열었다면 작업 전에 가상환경을 다시 활성화해야 합니다.

## 2. 로컬 저장소 검사

현재 디렉터리를 검사하고 한국어 HTML 리포트를 만듭니다. 이 모드는 네트워크를 사용하지 않습니다.

**입력할 명령**

```bash
repo-trust . --format html --output report.html
```

**생성되는 파일 예시**

```text
result/report-YYYY-MM-DD.html
```

파일명만 지정하면 RepoTrust가 `result/` 폴더를 만들고 날짜를 붙입니다. 예를 들어 2026년 4월 28일에 실행하면 `result/report-2026-04-28.html`이 생깁니다.

브라우저에서 생성된 HTML 파일을 열어 결과를 확인하세요.

## 3. GitHub URL 검사

GitHub URL을 직접 넣어 검사 결과를 HTML이나 JSON 파일로 저장할 수 있습니다. 원격 저장소 내용을 보려면 `--remote`를 명시해야 합니다.

`--remote`는 GitHub REST API의 read-only metadata를 조회합니다. repository를 clone하지 않습니다.

### HTML로 저장

**입력할 명령**

```bash
repo-trust "https://github.com/openai/codex" --remote --format html --output codex.html
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.html
```

HTML 리포트는 브라우저에서 읽기 좋습니다. 저장소를 dependency로 넣기 전에 사람이 직접 확인할 때 이 형식을 쓰면 됩니다.

### JSON으로 저장

**입력할 명령**

```bash
repo-trust "https://github.com/openai/codex" --remote --format json --output codex.json
```

**생성되는 파일 예시**

```text
result/codex-YYYY-MM-DD.json
```

JSON 리포트는 CI, 자동화, 다른 도구 연동에 적합합니다.

`--remote`를 빼면 RepoTrust는 URL만 파싱하고 원격 파일을 가져오지 않습니다. 이 경우 `target.github_not_fetched` finding이 나올 수 있습니다.

Private repository를 검사하거나 rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 사용합니다.

**입력할 명령**

```bash
GITHUB_TOKEN=ghp_example repo-trust "https://github.com/owner/private-repo" --remote
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 4. 리포트 읽는 법

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

`high`가 있으면 README의 설치 명령을 바로 실행하지 말고, 리포트의 “실제 근거”와 “추천 조치”를 먼저 확인하세요.

## 5. CI에서 실패 기준 걸기

점수가 기준보다 낮을 때 CI를 실패시키려면 `--fail-under`를 사용합니다.

**입력할 명령**

```bash
repo-trust . --format json --output report.json --fail-under 80
```

**생성되는 파일 예시**

```text
result/report-YYYY-MM-DD.json
```

동작은 다음과 같습니다.

- 점수가 80 이상이면 exit code `0`
- 점수가 80 미만이면 exit code `1`
- 잘못된 인자나 config 오류는 exit code `2`

점수가 낮아도 리포트 파일은 먼저 저장됩니다.

## 6. 설정 파일

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
repo-trust . --config /path/to/repotrust.toml
```

CLI 옵션이 config보다 우선합니다. 예를 들어 `--fail-under`를 명령에 직접 쓰면 config의 `policy.fail_under`보다 우선합니다.

현재 지원하는 config:

- `policy.fail_under`
- `weights.readme_quality`
- `weights.install_safety`
- `weights.security_posture`
- `weights.project_hygiene`

아직 지원하지 않는 config:

- rule enable/disable
- finding별 severity override
- config 자동 탐지
- remote credential 설정

## 7. 연습용 fixture

좋은 예시 저장소를 검사합니다.

**입력할 명령**

```bash
repo-trust tests/fixtures/repos/good-python --format html --output good-python.html
```

**생성되는 파일 예시**

```text
result/good-python-YYYY-MM-DD.html
```

위험한 설치 명령이 들어 있는 저장소를 검사합니다.

**입력할 명령**

```bash
repo-trust tests/fixtures/repos/risky-install --format html --output risky-install.html
```

**생성되는 파일 예시**

```text
result/risky-install-YYYY-MM-DD.html
```

## 8. RepoTrust가 보는 신뢰 신호

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

## 9. 개발자용 검증

변경 후 테스트를 실행합니다.

**입력할 명령**

```bash
python -m pytest -q
```

dependency를 바꾼 경우 lockfile을 갱신합니다.

**입력할 명령**

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```

기존 개발용 명령도 계속 동작합니다.

**입력할 명령**

```bash
repotrust scan .
```

사용자 문서에서는 더 짧은 `repo-trust TARGET` 형태를 기본으로 설명합니다.

## 문서

- `docs/prd.md`: 제품 요구사항과 현재 구현 상태
- `docs/trd.md`: 기술 설계와 JSON/remote/config contract
- `docs/adr.md`: 주요 결정 기록
- `docs/testing-and-validation.md`: 검증 명령과 테스트 기준
- `docs/domain-context.md`: finding과 점수 해석
- `CHANGELOG.md`: 릴리스 변경 기록

## 라이선스

RepoTrust는 MIT License로 배포됩니다. 자세한 내용은 `LICENSE`를 확인하세요.
