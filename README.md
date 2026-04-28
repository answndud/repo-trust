# RepoTrust

RepoTrust는 오픈소스 저장소를 설치하거나 프로젝트 dependency로 추가하기 전에, 기본적인 신뢰 신호를 빠르게 점검하는 Python CLI 도구입니다.

README, 설치 명령, 보안 정책, CI, lockfile, 라이선스 같은 파일을 보고 “이 저장소를 지금 믿고 써도 되는지” 판단할 수 있는 리포트를 만듭니다.

## 1. 설치

현재는 로컬 개발용 설치를 기준으로 사용합니다. 저장소 루트에서 한 번만 실행하세요.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

설치가 끝났는지 확인합니다.

```bash
repo-trust --version
```

예상 출력:

```text
repo-trust 0.1.0
```

터미널을 새로 열었다면 다시 가상환경을 켜야 합니다.

```bash
source .venv/bin/activate
```

## 2. 첫 리포트 만들기

현재 저장소를 HTML 리포트로 저장합니다.

```bash
repo-trust . --format html --output report.html
```

파일명만 지정하면 RepoTrust가 `result/` 폴더를 만들고 날짜를 붙여 저장합니다.

```text
result/report-YYYY-MM-DD.html
```

예를 들어 2026년 4월 28일에 실행하면 아래 파일이 생깁니다.

```text
result/report-2026-04-28.html
```

브라우저에서 이 HTML 파일을 열어 결과를 확인하면 됩니다.

## 3. 리포트에서 볼 것

HTML 리포트는 한국어로 작성됩니다. 처음에는 아래 네 부분만 보면 됩니다.

| 위치 | 확인할 내용 |
| --- | --- |
| 전체 판단 | 지금 바로 설치해도 되는지에 대한 요약 |
| 검사 영역별 점수 | README, 설치 안전성, 보안, 프로젝트 관리 중 약한 영역 |
| 발견된 파일과 의미 | README, LICENSE, SECURITY.md, CI, lockfile 같은 근거 파일 |
| 발견 항목과 추천 조치 | 실제 문제, 근거, 다음에 해야 할 일 |

심각도는 이렇게 해석하세요.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 확인하면 좋은 낮은 위험 |
| `medium` | dependency로 쓰기 전에 검토할 항목 |
| `high` | 설치 전에 반드시 확인할 항목 |

`high`가 있으면 README의 설치 명령을 바로 실행하지 말고, 리포트의 “실제 근거”와 “추천 조치”를 먼저 확인하세요.

## 4. 자주 쓰는 명령

현재 저장소를 터미널에 Markdown으로 출력:

```bash
repo-trust .
```

현재 저장소를 HTML 리포트로 저장:

```bash
repo-trust . --format html --output report.html
```

현재 저장소를 JSON 리포트로 저장:

```bash
repo-trust . --format json --output report.json
```

저장 위치를 직접 정하고 싶으면 경로를 포함하세요.

```bash
repo-trust . --format html --output reports/my-report.html
repo-trust . --format html --output /tmp/repotrust.html
```

파일명만 쓰면 `result/파일명-YYYY-MM-DD.확장자`로 저장되고, 경로를 쓰면 지정한 위치에 그대로 저장됩니다.

## 5. GitHub URL 검사

GitHub URL도 입력할 수 있습니다.

```bash
repo-trust "https://github.com/openai/codex"
```

기본 GitHub URL 검사는 안전하게 URL만 파싱합니다. clone하지 않고 GitHub API도 호출하지 않습니다. 이때는 `target.github_not_fetched` finding이 나올 수 있습니다.

원격 저장소 metadata까지 확인하려면 `--remote`를 명시하세요.

```bash
repo-trust "https://github.com/openai/codex" --remote --format html --output codex.html
```

`--remote`는 GitHub REST API의 read-only metadata를 조회합니다. repository를 clone하지 않습니다.

Private repository를 검사하거나 rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 사용합니다.

```bash
GITHUB_TOKEN=ghp_example repo-trust "https://github.com/owner/private-repo" --remote
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 6. CI에서 실패 기준 걸기

점수가 기준보다 낮을 때 CI를 실패시키려면 `--fail-under`를 사용합니다.

```bash
repo-trust . --format json --output report.json --fail-under 80
```

동작:

- 점수가 80 이상이면 exit code `0`
- 점수가 80 미만이면 exit code `1`
- 잘못된 인자나 config 오류는 exit code `2`

점수가 낮아도 리포트 파일은 먼저 저장됩니다. CI artifact로 `result/report-YYYY-MM-DD.json`을 남길 수 있습니다.

## 7. 설정 파일

정책 점수 기준과 category weight를 TOML 파일로 지정할 수 있습니다.

```toml
[policy]
fail_under = 80

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
```

사용:

```bash
repo-trust . --config /path/to/repotrust.toml
```

CLI 옵션이 config보다 우선합니다. 예를 들어 아래 명령의 `--fail-under 90`은 config의 `policy.fail_under`보다 우선합니다.

```bash
repo-trust . --config /path/to/repotrust.toml --fail-under 90
```

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

## 8. 연습용 fixture

좋은 예시 저장소:

```bash
repo-trust tests/fixtures/repos/good-python --format html --output good-python.html
```

위험한 설치 명령이 들어 있는 저장소:

```bash
repo-trust tests/fixtures/repos/risky-install --format html --output risky-install.html
```

JSON 구조를 보고 싶으면:

```bash
repo-trust tests/fixtures/repos/good-python --format json --output good-python.json
python -m json.tool result/good-python-*.json
```

## 9. RepoTrust가 보는 신뢰 신호

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

## 10. 개발자용 검증

테스트 실행:

```bash
python -m pytest -q
```

dependency를 바꾼 경우 lockfile 갱신:

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```

기존 개발용 명령도 계속 동작합니다.

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
