# TRD: RepoTrust 기술 설계

## 기술 선택

- 언어: Python.
- CLI: Typer.
- 터미널 출력: Rich.
- 모델: dataclasses.
- 테스트: pytest.
- 패키징: `pyproject.toml` 기반 pip-compatible 구조.

이 선택은 v1에서 빠른 구현, 낮은 진입 장벽, 단순한 배포를 우선한 결과다.

## 현재 명령

```bash
repotrust scan <target>
```

옵션:

- `--format markdown|json|html`
- `--output <path>`
- `--fail-under <score>`
- `--config <path>`
- `--remote`
- `--verbose`

## 데이터 흐름

1. `cli.py`가 인자와 옵션을 받는다.
2. `scanner.py`가 target을 분석하고 scan 흐름을 결정한다.
3. `targets.py`가 local path와 GitHub URL을 구분한다.
4. local path이면 `detection.py`가 파일 존재 여부를 찾는다.
5. `rules.py`가 finding을 만든다.
6. `scoring.py`가 finding을 category score와 total score로 변환한다.
7. `reports.py`가 `ScanResult`를 Markdown/JSON/HTML로 렌더링한다.

## 핵심 모델

- `Target`: 입력 target의 종류와 파싱 결과.
- `DetectedFiles`: README, LICENSE, SECURITY, workflow, manifest, lockfile 등 탐지 결과.
- `Finding`: `id`, `category`, `severity`, `message`, `evidence`, `recommendation`.
- `Score`: category별 점수, total, grade, risk label.
- `ScanResult`: target, detected files, findings, score, generated timestamp.

## 모듈 책임

- `cli.py`: CLI UX, stdout/stderr 분리, exit code.
- `scanner.py`: scan orchestration. 세부 rule을 직접 구현하지 않는다.
- `targets.py`: target parsing. 네트워크 접근 금지.
- `detection.py`: 파일 시스템 탐지. scoring 판단 금지.
- `rules.py`: finding 생성. report rendering 금지.
- `scoring.py`: 감점/가중치 계산. 파일 시스템 접근 금지.
- `reports.py`: `ScanResult` 렌더링만 담당. scan logic 금지.

## 스코어링

현재 weight:

- README Quality: 25%
- Install Safety: 30%
- Security Posture: 25%
- Project Hygiene: 20%

severity별 감점은 `scoring.py`에만 둔다. rule은 severity를 결정하고, 점수 계산은 scoring layer가 담당한다.

현재 severity 감점:

- `info`: 0
- `low`: 8
- `medium`: 18
- `high`: 35

현재 grade threshold:

- `A`: 90 이상
- `B`: 80 이상
- `C`: 70 이상
- `D`: 60 이상
- `F`: 60 미만

Finding ID는 JSON report 사용자에게 노출되는 안정적인 식별자다. 새 rule을 추가할 때 기존 ID의 의미를 바꾸지 말고, 의미가 달라지면 새 ID를 만든다.

## 출력 정책

- report 본문은 stdout 또는 `--output` 파일로 나간다.
- Rich summary와 상태 메시지는 stderr로 나간다.
- JSON 출력은 pipe 가능한 valid JSON이어야 한다.
- HTML은 단일 static file이며 서버가 필요 없어야 한다.

## JSON Report Contract

JSON report는 외부 도구와 CI에서 사용할 수 있는 안정적인 contract로 취급한다. v1 contract는 `schema_version: "1.0"`을 최상위에 포함한다.

최상위 key:

- `schema_version`: JSON report contract version.
- `target`: 입력 target과 파싱 결과.
- `detected_files`: repository file detection 결과.
- `findings`: finding 객체 배열.
- `score`: category score와 total score.
- `generated_at`: UTC ISO timestamp.

Finding key:

- `id`
- `category`
- `severity`
- `message`
- `evidence`
- `recommendation`

Score key:

- `categories`
- `total`
- `max_score`
- `grade`
- `risk_label`

JSON report를 stdout으로 출력할 때는 summary/table이 섞이면 안 된다. 상태 출력은 stderr에만 기록한다.

## Config File v1 Design

Config file support is implemented as an explicit local-only policy layer. The conventional file name is `repotrust.toml`, but v1 only loads a config when `--config <path>` is provided.

CLI behavior:

- Default scan remains config-free.
- `--config <path>` loads an explicit TOML config file.
- Auto-discovery may later look for `repotrust.toml` at the scanned repository root, but v1 does not auto-load it.
- CLI flags override config values when both are provided.

Minimum v1 config shape:

```toml
[policy]
fail_under = 80

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
```

Validation rules:

- `policy.fail_under` must be an integer from 0 to 100.
- All configured weights must be numeric and non-negative.
- If any weight is configured, all four category weights must be present.
- Weight totals must sum to `1.0`; small floating point tolerance is accepted.
- Unknown top-level sections produce a config error instead of being ignored silently.

Out of scope for config v1:

- Rule enable/disable.
- Finding-specific severity overrides.
- Remote GitHub credentials.
- Organization-wide inherited config.

Implementation note: Python 3.11+ includes `tomllib`; Python 3.10 uses the conditional `tomli` dependency declared in `pyproject.toml`.

## v1 기술 제약

- GitHub URL은 파싱만 한다.
- clone, fetch, GitHub API call은 하지 않는다.
- dependency manifest를 읽더라도 실제 vulnerability lookup은 하지 않는다.
- README command parsing은 skeleton 수준의 regex heuristic이다.
- Python dependency lockfile은 `pylock.toml`을 사용한다. dependency 변경 시 `pip lock -e '.[dev]' -o pylock.toml`로 갱신한다.

## Remote GitHub Scan Design

Remote GitHub scan은 v1 이후의 명시적 opt-in 확장으로 설계한다. GitHub URL을 입력했다는 이유만으로 네트워크 scan을 암묵적으로 실행하지 않는다.

Current implementation boundary:

- `--remote` CLI option exists.
- `--remote` is rejected for local path targets.
- GitHub URL without `--remote` remains parse-only.
- GitHub URL with `--remote` enters `remote.py`, requests repository metadata, and converts repository metadata API failures into findings.
- Remote root contents and workflow metadata are converted into `DetectedFiles`.
- README content and Dependabot config are fetched through read-only contents endpoints.
- Remote detected files and README content are scored with the existing rule/scoring/report contract.

Interface:

- `repotrust scan <github-url>` 기본 동작은 URL parse-only로 유지한다.
- remote 구현을 시작할 때 `repotrust scan <github-url> --remote`를 추가한다.
- `--remote`는 GitHub URL target에서만 유효하다.
- local path scan은 네트워크를 절대 사용하지 않는다.

Authentication:

- public repository 기본 metadata는 인증 없이도 scan할 수 있게 설계한다.
- `GITHUB_TOKEN`이 있으면 더 높은 rate limit 또는 private repository 접근에 사용한다.
- token 값은 finding, report, log에 절대 출력하지 않는다.

Read-only API scope:

- Repository metadata: `GET /repos/{owner}/{repo}`.
- README/content metadata: repository contents API. README와 root file인 LICENSE, SECURITY, manifest, lockfile을 확인한다.
- CI signal: GitHub Actions workflows API, 특히 repository workflow 목록을 확인한다.
- Release signal은 나중에 releases endpoint로 추가할 수 있지만 첫 remote MVP 필수 범위는 아니다.

Failure modes as findings:

- `remote.github_unauthorized`: authentication required or token lacks access.
- `remote.github_not_found`: repository does not exist or is not visible.
- `remote.github_rate_limited`: primary or secondary rate limit prevents scan completion.
- `remote.github_api_error`: other non-success API response.
- `remote.github_partial_scan`: some endpoints failed but enough data was collected to score partially.

Scoring behavior:

- Remote scan은 기존 `ScanResult`, `Finding`, scoring model을 재사용한다.
- 알 수 없는 remote 상태는 신뢰 판단 영향도에 따라 `info` 또는 `medium` finding으로 표현한다.
- API 실패를 repository file 부재로 조용히 해석하지 않는다.

Testing approach:

- unit test는 mocked HTTP response 또는 local fake transport를 사용한다.
- test는 실제 네트워크 접근이나 실제 GitHub credential을 요구하지 않는다.

Reference basis:

- GitHub REST repository contents docs: `https://docs.github.com/en/rest/repos/contents`
- GitHub REST workflows docs: `https://docs.github.com/en/rest/actions/workflows`
- GitHub REST rate limit docs: `https://docs.github.com/rest/using-the-rest-api/rate-limits-for-the-rest-api`

## 확장 포인트

- remote scan을 추가할 때는 기본 동작으로 켜지 말고 explicit option으로 시작한다.
- 외부 API가 들어오면 source attribution과 failure mode를 finding으로 표현한다.
- policy config가 생기면 scoring과 rule enable/disable을 분리한다.
- HTML dashboard가 생겨도 CLI JSON schema를 먼저 안정화한다.
