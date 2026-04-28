# RepoTrust

RepoTrust는 오픈소스 저장소를 설치하거나 dependency로 추가하기 전에, 그 저장소를 믿고 써도 되는지 빠르게 점검하는 Python CLI 도구입니다.

RepoTrust가 확인하는 질문은 단순합니다.

- README의 설치 명령을 그대로 실행해도 되는가?
- 회사나 개인 프로젝트의 dependency로 넣어도 되는가?
- AI coding agent에게 설치와 실행을 맡겨도 되는가?
- README, LICENSE, SECURITY.md, CI, lockfile 같은 기본 신뢰 신호가 있는가?

RepoTrust는 최종 결정을 대신하지 않습니다. 대신 점수, 발견 항목, 근거, 추천 조치를 함께 보여줘서 사람이 판단하기 쉽게 만듭니다.

## 빠른 시작

처음 한 번만 설치합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
repo-trust --version
```

설치 후에는 아래 명령만 기억하면 됩니다.

```bash
# 현재 저장소를 한국어 HTML 리포트로 저장
repo-trust . --format html --output report.html

# GitHub URL을 안전하게 parse-only 점검
repo-trust "https://github.com/openai/codex"

# JSON 리포트 생성
repo-trust . --format json --output report.json
```

파일명만 지정하면 결과는 자동으로 `result/` 폴더에 날짜가 붙어 저장됩니다.

```text
result/report-YYYY-MM-DD.html
result/report-YYYY-MM-DD.json
```

## 기본 사용법

### 로컬 저장소 점검

현재 디렉터리를 점검합니다. 이 모드는 네트워크를 사용하지 않습니다.

```bash
repo-trust .
```

HTML 리포트를 만들려면:

```bash
repo-trust . --format html --output report.html
```

JSON 리포트를 만들려면:

```bash
repo-trust . --format json --output report.json
```

`--output`에 파일명만 쓰면 `result/파일명-YYYY-MM-DD.확장자`로 저장됩니다. 위치를 직접 정하고 싶으면 경로를 포함해서 쓰면 됩니다.

```bash
repo-trust . --format html --output reports/my-report.html
repo-trust . --format html --output /tmp/repotrust.html
```

### GitHub URL 점검

기본 GitHub URL 점검은 URL만 파싱합니다. clone도 하지 않고 GitHub API도 호출하지 않습니다.

```bash
repo-trust "https://github.com/openai/codex"
```

이 경우 `target.github_not_fetched` finding이 나옵니다. 의미는 “GitHub URL은 인식했지만 저장소 파일은 가져오지 않았다”입니다.

원격 metadata까지 확인하려면 명시적으로 `--remote`를 붙입니다.

```bash
repo-trust "https://github.com/openai/codex" --remote --format html --output codex.html
```

`--remote`는 GitHub REST API의 read-only metadata를 조회합니다. repository를 clone하지 않습니다.

Private repository를 보거나 rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 설정합니다.

```bash
GITHUB_TOKEN=ghp_example repo-trust "https://github.com/owner/private-repo" --remote
```

Token 값은 리포트나 터미널 출력에 남기지 않습니다.

## 리포트 읽는 법

HTML 리포트는 초보자가 읽기 쉽게 한국어로 작성됩니다.

- **전체 판단**: 지금 바로 설치해도 될지 빠르게 보는 요약입니다.
- **검사 영역별 점수**: README, 설치 안전성, 보안 태세, 프로젝트 관리 상태 중 약한 부분을 보여줍니다.
- **발견된 파일과 의미**: README, LICENSE, SECURITY.md, workflow, lockfile 같은 근거 파일을 설명합니다.
- **발견 항목과 추천 조치**: 무엇이 문제인지, 어떤 근거가 있는지, 다음에 무엇을 해야 하는지 알려줍니다.

점수 category는 네 가지입니다.

| Category | 의미 |
| --- | --- |
| README Quality | README가 목적, 설치, 사용법을 충분히 설명하는지 |
| Install Safety | 설치 명령이 위험한 원격 스크립트 실행을 유도하지 않는지 |
| Security Posture | SECURITY.md, CI, Dependabot, lockfile 같은 보안/재현성 신호가 있는지 |
| Project Hygiene | LICENSE, dependency manifest 같은 기본 관리 신호가 있는지 |

Finding의 `severity`는 이렇게 보면 됩니다.

| Severity | 의미 |
| --- | --- |
| `info` | 참고 정보 |
| `low` | 당장 위험하진 않지만 확인하면 좋은 항목 |
| `medium` | dependency 채택 전에 검토해야 하는 항목 |
| `high` | 설치 전 반드시 확인해야 하는 항목 |

## CI에서 사용하기

점수가 기준보다 낮을 때 실패시키려면 `--fail-under`를 사용합니다.

```bash
repo-trust . --format json --output report.json --fail-under 80
```

동작은 다음과 같습니다.

- score가 80 이상이면 exit code `0`
- score가 80 미만이면 exit code `1`
- 잘못된 인자나 config 오류는 exit code `2`

리포트는 실패 기준에 걸려도 먼저 저장됩니다. CI artifact로 `result/report-YYYY-MM-DD.json`을 남기기 좋습니다.

## 설정 파일

명시적으로 TOML config를 넘길 수 있습니다.

```toml
[policy]
fail_under = 80

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
```

사용 예시:

```bash
repo-trust . --config /path/to/repotrust.toml
repo-trust "https://github.com/owner/repo" --remote --config /path/to/repotrust.toml
```

CLI flag가 config보다 우선합니다. 예를 들어 `--fail-under`는 `policy.fail_under`보다 우선합니다.

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

## 예제로 연습하기

좋은 예시 저장소 fixture:

```bash
repo-trust tests/fixtures/repos/good-python --format html --output good-python.html
```

위험한 설치 명령이 들어 있는 fixture:

```bash
repo-trust tests/fixtures/repos/risky-install --format html --output risky-install.html
```

JSON을 확인하려면:

```bash
repo-trust tests/fixtures/repos/good-python --format json --output good-python.json
python -m json.tool result/good-python-*.json
```

## 현재 하지 않는 일

RepoTrust는 아직 아래 기능을 제공하지 않습니다.

- GitHub App
- 웹 대시보드
- remote clone
- dependency vulnerability DB 조회
- contributor profile 분석
- release/tag freshness 점수화
- config 자동 탐지

## 개발자 메모

기본 검증:

```bash
python -m pytest -q
```

dependency를 바꾼 경우 lockfile 갱신:

```bash
python -m pip lock -e '.[dev]' -o pylock.toml
```

기존 개발용 명령인 `repotrust scan TARGET`도 계속 동작합니다. 사용자 문서에서는 더 짧은 `repo-trust TARGET` 형태를 기본으로 설명합니다.

## 문서

- `docs/prd.md`: 제품 요구사항과 현재 구현 상태
- `docs/trd.md`: 기술 설계와 JSON/remote/config contract
- `docs/adr.md`: 주요 결정 기록
- `docs/testing-and-validation.md`: 검증 명령과 테스트 기준
- `docs/domain-context.md`: finding과 점수 해석
- `CHANGELOG.md`: 릴리스 변경 기록

## 라이선스

RepoTrust는 MIT License로 배포됩니다. 자세한 내용은 `LICENSE`를 확인하세요.
