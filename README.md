# RepoTrust

RepoTrust는 오픈소스 저장소를 설치하거나 dependency로 넣기 전에, 그 저장소를 믿고 써도 되는지 빠르게 점검하는 Python CLI 도구입니다.

다음 같은 질문에 답하기 위해 만듭니다.

- README에 있는 설치 명령을 그대로 실행해도 되는가?
- 이 저장소를 회사/개인 프로젝트 dependency로 넣어도 되는가?
- AI coding agent에게 이 repo 설치와 실행을 맡겨도 되는가?
- 문서, 보안 정책, CI, lockfile 같은 기본 신뢰 신호가 있는가?

RepoTrust는 최종 결정을 대신하지 않습니다. 대신 점수, finding, evidence, recommendation을 함께 보여줘서 사람이 판단하기 쉽게 만듭니다.

## 빠른 시작

개발 환경에서 바로 사용하려면 저장소 루트에서 아래 명령을 실행합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/repotrust --version
```

현재 저장소를 스캔합니다.

```bash
.venv/bin/repotrust scan .
```

JSON 리포트를 파일로 저장합니다.

```bash
.venv/bin/repotrust scan . --format json --output report.json
```

HTML 리포트를 파일로 저장합니다.

```bash
.venv/bin/repotrust scan . --format html --output report.html
```

## 설치

RepoTrust는 아직 로컬 개발용 editable install을 기준으로 사용합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

설치가 끝나면 아래 명령이 동작해야 합니다.

```bash
.venv/bin/repotrust --version
```

예상 출력:

```text
repotrust 0.1.0
```

## 로컬 저장소 스캔

가장 기본 사용법은 로컬 checkout을 스캔하는 것입니다. 이 모드는 네트워크를 사용하지 않습니다.

```bash
.venv/bin/repotrust scan .
```

RepoTrust는 로컬 파일을 보고 다음 항목을 확인합니다.

- README 존재와 기본 품질
- README의 설치 명령 위험 패턴
- `SECURITY.md`
- GitHub Actions workflow
- Dependabot 설정
- dependency manifest
- lockfile
- LICENSE

## 리포트 형식

기본 출력은 Markdown입니다.

```bash
.venv/bin/repotrust scan . --format markdown
```

JSON은 CI나 다른 도구에서 읽기 좋습니다.

```bash
.venv/bin/repotrust scan . --format json --output report.json
.venv/bin/python -m json.tool report.json
```

HTML은 브라우저에서 보기 좋습니다.

```bash
.venv/bin/repotrust scan . --format html --output report.html
```

`--output`을 쓰면 리포트 본문은 파일에 저장되고, 터미널에는 요약 상태만 표시됩니다.

## GitHub URL 스캔

기본 GitHub URL 스캔은 안전하게 URL만 파싱합니다. clone도 하지 않고 GitHub API도 호출하지 않습니다.

```bash
.venv/bin/repotrust scan https://github.com/openai/codex --format json
```

이 경우 `target.github_not_fetched` finding이 나옵니다. 의미는 "GitHub URL은 인식했지만 원격 저장소 내용은 가져오지 않았다"입니다.

## 원격 GitHub 스캔

원격 저장소 metadata까지 보고 싶을 때만 `--remote`를 명시합니다.

```bash
.venv/bin/repotrust scan https://github.com/openai/codex --remote --format json
```

`--remote`는 GitHub REST API의 read-only metadata를 조회합니다. repository를 clone하지 않습니다.

현재 remote scan이 확인하는 항목:

- repository metadata
- root contents
- README content
- Dependabot config
- GitHub Actions workflow metadata

Remote scan에서 점수에 반영하는 metadata는 보수적으로 제한합니다.

- `archived=true`: `remote.github_archived`
- `has_issues=false`: `remote.github_issues_disabled`

아래 항목은 아직 점수화하지 않습니다.

- star/watch/fork count
- fork/private 여부
- default branch 이름
- language, size, created date
- release/tag freshness
- contributor profile

## Private repository와 GITHUB_TOKEN

private repository를 스캔하거나 rate limit을 줄이고 싶으면 `GITHUB_TOKEN`을 설정합니다.

```bash
GITHUB_TOKEN=ghp_example .venv/bin/repotrust scan https://github.com/owner/private-repo --remote
```

RepoTrust는 token을 GitHub API Authorization header에만 사용합니다. token 값은 finding, report, terminal summary에 출력하지 않습니다.

## 점수와 finding 읽는 법

RepoTrust score는 네 개 category를 합쳐 계산합니다.

- README Quality: README의 존재와 설명 품질
- Install Safety: 설치 명령의 안전성
- Security Posture: 보안 정책, CI, Dependabot, lockfile
- Project Hygiene: LICENSE, dependency manifest, maintenance signal

각 finding은 아래 정보를 포함합니다.

- `id`: 안정적인 finding 식별자
- `category`: 점수 category
- `severity`: `info`, `low`, `medium`, `high`
- `message`: 무엇이 문제인지
- `evidence`: 어떤 근거로 판단했는지
- `recommendation`: 무엇을 고치면 좋은지

예를 들어 `install.risky.shell_pipe_install`은 README에 `curl ... | sh` 같은 위험한 설치 패턴이 있다는 뜻입니다.

## CI에서 실패 기준 걸기

`--fail-under`를 사용하면 점수가 기준보다 낮을 때 exit code `1`로 종료합니다.

```bash
.venv/bin/repotrust scan . --fail-under 80
```

예시:

- score가 80 이상이면 exit code `0`
- score가 80 미만이면 exit code `1`
- 사용법 오류나 잘못된 config는 exit code `2`

리포트는 실패 기준에 걸려도 먼저 출력됩니다. CI에서 결과 파일을 artifact로 남기기 좋습니다.

```bash
.venv/bin/repotrust scan . --format json --output report.json --fail-under 80
```

## 설정 파일 사용

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
.venv/bin/repotrust scan . --config /path/to/repotrust.toml
.venv/bin/repotrust scan https://github.com/owner/repo --remote --config /path/to/repotrust.toml
```

CLI flag가 config보다 우선합니다. 예를 들어 `--fail-under`는 `policy.fail_under`보다 우선합니다.

```bash
.venv/bin/repotrust scan . --config /path/to/repotrust.toml --fail-under 90
```

현재 config가 지원하는 항목:

- `policy.fail_under`
- `weights.readme_quality`
- `weights.install_safety`
- `weights.security_posture`
- `weights.project_hygiene`

아직 지원하지 않는 항목:

- rule enable/disable
- finding별 severity override
- config 자동 탐지
- remote credential 설정

## 예제 fixture로 연습하기

좋은 예시 저장소 fixture:

```bash
.venv/bin/repotrust scan tests/fixtures/repos/good-python --format markdown
.venv/bin/repotrust scan tests/fixtures/repos/good-python --format json --output /tmp/repotrust-good.json
.venv/bin/python -m json.tool /tmp/repotrust-good.json
```

위험한 설치 명령이 들어 있는 fixture:

```bash
.venv/bin/repotrust scan tests/fixtures/repos/risky-install --format html --output /tmp/repotrust-risky.html
```

## 자주 쓰는 명령 모음

```bash
# 현재 저장소 Markdown 리포트
.venv/bin/repotrust scan .

# JSON 파일 생성
.venv/bin/repotrust scan . --format json --output report.json

# HTML 파일 생성
.venv/bin/repotrust scan . --format html --output report.html

# CI threshold 적용
.venv/bin/repotrust scan . --fail-under 80

# GitHub URL parse-only 스캔
.venv/bin/repotrust scan https://github.com/openai/codex --format json

# 명시적 remote scan
.venv/bin/repotrust scan https://github.com/openai/codex --remote --format json

# config 적용
.venv/bin/repotrust scan . --config /path/to/repotrust.toml
```

## 개발자 검증

변경 후 기본 테스트를 실행합니다.

```bash
.venv/bin/python -m pytest -q
```

dependency를 바꾼 경우 lockfile을 갱신합니다.

```bash
.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml
```

clean install 검증이 필요하면 임시 venv에서 확인합니다.

```bash
python3 -m venv /tmp/repotrust-clean/.venv
/tmp/repotrust-clean/.venv/bin/python -m pip install -e '.[dev]'
/tmp/repotrust-clean/.venv/bin/repotrust --version
/tmp/repotrust-clean/.venv/bin/python -m pytest -q
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

## 문서

- `docs/prd.md`: 제품 요구사항과 현재 구현 상태
- `docs/trd.md`: 기술 설계와 JSON/remote/config contract
- `docs/adr.md`: 주요 결정 기록
- `docs/testing-and-validation.md`: 검증 명령과 테스트 기준
- `docs/domain-context.md`: finding과 점수 해석
- `CHANGELOG.md`: 릴리스 변경 기록

## 라이선스

RepoTrust는 MIT License로 배포됩니다. 자세한 내용은 `LICENSE`를 확인하세요.
