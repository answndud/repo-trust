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
- `Assessment`: machine-readable verdict, confidence, coverage, 판단 이유, 다음 조치.
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

Scan completeness cap:

- `remote.github_rate_limited`, `remote.github_unauthorized`, `remote.github_not_found`, `remote.github_api_error`: score cap 60.
- `target.local_path_missing`: score cap 0.
- `target.github_not_fetched`: score cap 70.
- `target.github_subpath_unsupported`: score cap 85.
- `remote.github_partial_scan`, `remote.readme_content_unavailable`: score cap 85.

이 cap은 category score를 바꾸지 않고 total score에만 적용한다. category별 감점은 여전히 finding severity와 category weight로 설명하고, scan completeness로 인한 불확실성은 `assessment`와 total cap으로 설명한다.

## 출력 정책

- report 본문은 stdout 또는 `--output` 파일로 나간다.
- Rich summary와 상태 메시지는 stderr로 나간다.
- JSON 출력은 pipe 가능한 valid JSON이어야 한다.
- HTML은 단일 static file이며 서버가 필요 없어야 한다.

## JSON Report Contract

JSON report는 외부 도구와 CI에서 사용할 수 있는 안정적인 contract로 취급한다. 현재 contract는 `schema_version: "1.2"`를 최상위에 포함한다.
상세 field reference와 parsing examples는 `docs/json-report-reference.md`에 둔다.

최상위 key:

- `schema_version`: JSON report contract version.
- `target`: 입력 target과 파싱 결과.
- `detected_files`: repository file detection 결과.
- `findings`: finding 객체 배열.
- `score`: category score와 total score.
- `assessment`: verdict, confidence, coverage, summary, reasons, next_actions, profiles.
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

Assessment key:

- `verdict`: `usable_by_current_checks`, `usable_after_review`, `insufficient_evidence`, `do_not_install_before_review`.
- `confidence`: `high`, `medium`, `low`.
- `coverage`: `full`, `partial`, `metadata_only`, `failed`.
- `summary`
- `reasons`
- `next_actions`
- `profiles`: `install`, `dependency`, `agent_delegate` 목적별 판단 map.

Assessment profile key:

- `verdict`: profile-specific verdict using the same verdict IDs as the top-level assessment.
- `summary`
- `reasons`
- `next_actions`
- `priority_finding_ids`: up to three finding IDs most relevant to this profile.

JSON report를 stdout으로 출력할 때는 summary/table이 섞이면 안 된다. 상태 출력은 stderr에만 기록한다.

Schema version policy:

- `schema_version` changed from `"1.0"` to `"1.1"` because `assessment` was added as a top-level JSON key.
- `schema_version` changed from `"1.1"` to `"1.2"` because `assessment.profiles` was added to the machine-readable assessment shape.
- `schema_version` remains `"1.2"` while changes only add new stable finding IDs or renderer behavior without changing JSON shape.
- Adding top-level JSON keys, renaming existing keys, changing finding key names, or changing score key names requires an intentional schema review before release.
- Stable finding IDs are part of the JSON contract; changing an existing ID's meaning should create a new ID instead of reusing the old one.

## Config File v2 Design

Config file support is implemented as an explicit file-based policy layer. The conventional file name is `repotrust.toml`, but RepoTrust only loads a config when `--config <path>` is provided.

CLI behavior:

- Default scan remains config-free.
- `--config <path>` loads an explicit TOML config file.
- Loaded policy applies consistently to local scans, product parse-only/remote scans, and explicit legacy remote scans.
- `repo-trust gate` always renders JSON first, then exits `1` when a configured score/profile policy fails.
- Auto-discovery may later look for `repotrust.toml` at the scanned repository root, but current versions do not auto-load it.
- CLI flags override config values when both are provided.

Supported config shape:

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

Validation rules:

- `policy.fail_under` must be an integer from 0 to 100.
- `[policy.profiles]` may only contain `install`, `dependency`, and `agent_delegate`.
- Profile verdict values must be one of `do_not_install_before_review`, `insufficient_evidence`, `usable_after_review`, or `usable_by_current_checks`.
- `rules.disabled` must be a list of finding ID strings.
- `[severity_overrides]` maps finding IDs to one of `info`, `low`, `medium`, or `high`.
- All configured weights must be numeric and non-negative.
- If any weight is configured, all four category weights must be present.
- Weight totals must sum to `1.0`; small floating point tolerance is accepted.
- Unknown top-level sections produce a config error instead of being ignored silently.

Policy application order:

1. Scanner emits normal findings and computes an initial score using configured weights.
2. Config policy filters disabled finding IDs and applies severity overrides.
3. Score and assessment are recalculated from the adjusted finding set.
4. Gate policy compares score and configured profile minimums against the adjusted result.

Out of scope for config v2:

- Remote GitHub credentials.
- Organization-wide inherited config.

Implementation note: Python 3.11+ includes `tomllib`; Python 3.10 uses the conditional `tomli` dependency declared in `pyproject.toml`.

## v1 기술 제약

- Legacy `repotrust scan <github-url>`는 기본적으로 파싱만 한다.
- Product CLI와 legacy CLI의 GitHub URL 기본 scan은 네트워크 없이 URL만 파싱한다.
- Product CLI `--remote`와 legacy `--remote`는 GitHub API read-only metadata를 조회하지만 clone/fetch는 하지 않는다.
- dependency manifest는 package-level local signal만 읽으며 실제 vulnerability lookup은 하지 않는다.
- README command parsing은 Installation/Setup 섹션의 command-like line을 대상으로 하는 regex heuristic이다.
- Python dependency lockfile은 `pylock.toml`을 사용한다. dependency 변경 시 `pip lock -e '.[dev]' -o pylock.toml`로 갱신한다.

## Remote GitHub Scan Design

Remote GitHub scan은 product CLI와 legacy `repotrust scan` 모두에서 명시적 `--remote` opt-in으로 유지한다. 기본 GitHub URL scan은 secret key나 API 연결 없이 URL parse-only로 실행한다.

Current implementation boundary:

- Legacy `--remote` CLI option exists on `repotrust scan`.
- Legacy `--remote` is rejected for local path targets.
- Legacy GitHub URL without `--remote` remains parse-only.
- Product `repo-trust html/json/check/gate <github-url>` defaults to parse-only.
- Product `--remote` is rejected for local path targets.
- Product `repo-trust` without a subcommand opens an interactive launcher that routes to the same `html/json/check` execution path.
- Product `--parse-only` keeps URL-only behavior without GitHub API access and is equivalent to the default for GitHub URLs.
- GitHub URL remote scans enter `remote.py`, request repository metadata, and convert repository metadata API failures into findings.
- Remote root contents and workflow metadata are converted into `DetectedFiles`.
- README content and Dependabot config are fetched through read-only contents endpoints.
- Remote detected files and README content are scored with the existing rule/scoring/report contract.

Interface:

- `repo-trust html/json/check/gate <github-url>` 기본 동작은 URL parse-only scan이다.
- `repo-trust` 무인자 실행은 interactive launcher를 열고 선택한 workflow를 같은 scan/report path로 전달한다.
- `repo-trust html/json/check/gate <github-url> --remote`는 GitHub API remote scan을 실행한다.
- `repo-trust html/json/check/gate <github-url> --parse-only`는 URL parse-only로 유지한다.
- GitHub `tree`/`blob` subpath URL은 repository root 기준 scan에 `target.github_subpath_unsupported` finding을 추가한다. 하위 폴더 단위 신뢰 평가는 local checkout scan으로 안내한다.
- `repotrust scan <github-url>` 기본 동작은 legacy compatibility를 위해 URL parse-only로 유지한다.
- `repotrust scan <github-url> --remote`는 legacy path에서 GitHub API remote scan을 실행한다.
- `--remote`와 `--parse-only`는 각각의 command surface에서 GitHub URL target에만 유효하다.
- local path scan은 네트워크를 절대 사용하지 않는다.

Authentication:

- public repository 기본 metadata는 인증 없이도 scan할 수 있게 설계한다.
- `GITHUB_TOKEN`이 있으면 더 높은 rate limit 또는 private repository 접근에 사용한다.
- token 값은 finding, report, log에 절대 출력하지 않는다.

Read-only API scope:

- Repository metadata: `GET /repos/{owner}/{repo}`.
- README/content metadata: repository contents API. README, root file인 LICENSE/SECURITY/manifest/lockfile, 그리고 root `SECURITY.md`가 없을 때 `.github/SECURITY.md`를 확인한다.
- CI signal: GitHub Actions workflows API, 특히 repository workflow 목록을 확인한다.
- Release freshness signal: package manifest가 있는 저장소에 한해 `GET /repos/{owner}/{repo}/releases/latest`를 확인한다. latest release가 404이면 `GET /repos/{owner}/{repo}/tags?per_page=1`와 해당 tag commit endpoint로 tag commit date를 확인한다.

Remote release/tag freshness design:

- Candidate condition: root dependency manifest가 확인된 remote repository.
- Candidate endpoints:
  - Latest release metadata: `GET /repos/{owner}/{repo}/releases/latest`.
  - Tags list fallback: `GET /repos/{owner}/{repo}/tags?per_page=1`.
  - Tag commit date fallback: `GET /repos/{owner}/{repo}/commits/{sha}` for the latest tag commit SHA.
- Finding:
  - `remote.release_or_tag_stale`: low `project_hygiene`, emitted only when a latest release/tag date is known and older than the freshness threshold.
- Failure modes:
  - `404` from latest release can mean no GitHub Release practice, not necessarily stale maintenance.
  - Tags without releases can be valid for small libraries or tools.
  - Release/tag API errors are treated as unknown freshness evidence, not as stale maintenance.
  - API errors, rate limits, and permission failures must remain remote failure/partial metadata, not stale-release deductions.
- Scoring policy:
  - Release freshness starts as `low` severity only.
  - The freshness finding includes release/tag date evidence and explains why the project appears package-managed.
  - A stale finding should require an installable/package signal such as dependency manifest plus release/tag metadata, not repository age or popularity alone.

Failure modes as findings:

- `remote.github_unauthorized`: authentication required or token lacks access.
- `remote.github_not_found`: repository does not exist or is not visible.
- `remote.github_rate_limited`: primary or secondary rate limit prevents scan completion.
- `remote.github_api_error`: other non-success API response.
- `remote.github_partial_scan`: some endpoints failed but enough data was collected to score partially.
- `remote.github_archived`: repository metadata has `archived=true`; this is a project hygiene deduction.
- `remote.github_issues_disabled`: repository metadata has `has_issues=false`; this is a low project hygiene deduction.

Scoring behavior:

- Remote scan은 기존 `ScanResult`, `Finding`, scoring model을 재사용한다.
- 알 수 없는 remote 상태는 신뢰 판단 영향도에 따라 `info` 또는 `medium` finding으로 표현한다.
- `archived=true`처럼 명확한 maintenance risk metadata는 `PROJECT_HYGIENE` finding으로 점수에 반영한다.
- `has_issues=false`는 public support path가 덜 명확하다는 낮은 project hygiene signal로만 반영한다.
- fork/private/default branch/stars/language/size/created date와 `security_and_analysis` 세부 값은 JSON contract에서 evidence-only metadata 표현이 설계될 때까지 점수화하지 않는다.
- release/tag freshness는 package manifest와 release/tag date evidence가 있을 때만 low project hygiene signal로 반영한다.
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
- Remote metadata quality signals should separate score deductions from evidence-only context before implementation.
