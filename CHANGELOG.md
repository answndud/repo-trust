# Changelog

All notable changes to RepoTrust are documented here.

## Unreleased

### Added

- `repo-trust next-steps <target>` / `repo-trust-kr next-steps <target>` now print a beginner action plan from scan findings.
- `repo-trust next-steps --from-json <report.json>` now reads saved RepoTrust JSON reports without rescanning.
- Console Mode now includes `[N] Next Steps` / `[N] 다음 조치` for the same prioritized action plan.
- Static HTML reports now include a `Next Steps` section with the same action order.

## v0.2.8 - 2026-05-07

### Added

- Static HTML Safe Install sections now highlight a `Next safest command` before the longer checklist.
- Saved report dashboards now show an `open <path>` helper under the report path.
- `repo-trust tutorial` / `repo-trust-kr tutorial` now print copyable first-run commands.
- Console Mode now includes `[T] Tutorial` / `[T] 튜토리얼`.
- `repo-trust samples` / `repo-trust-kr samples` now generate built-in good/risky sample HTML and JSON reports.
- Console Mode now includes `[P] Samples` / `[P] 샘플`.

### Validation

- `.venv/bin/python -m pytest -q` passed with 157 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.8/dist` built `repotrust-0.2.8.tar.gz` and `repotrust-0.2.8-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.8`.
- Clean wheel smoke verified `tutorial`, built-in `samples`, Console Mode `[P] Samples`, `safe-install`, fixture JSON generation, and JSON `json.tool`.
- Local self-scan returned grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.7 - 2026-05-07

### Added

- `safe-install` now lists README install commands found during local scans before showing install advice.
- Static HTML reports now include a `Safe Install` section with a pre-run checklist, README install commands, and safer install patterns.
- Console Mode now shows a first-run path from local scan to safe install advice to JSON export.
- Console Mode recent reports now include a path-copy/open helper for saved report files.

### Changed

- Static HTML finding cards now include terminal-free Korean explanations, evidence, and recommendations directly in the report.

### Validation

- `.venv/bin/python -m pytest -q` passed with 150 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.7/dist` built `repotrust-0.2.7.tar.gz` and `repotrust-0.2.7-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.7`.
- Clean wheel smoke verified README install command display in `safe-install`, Console Mode `[S] 안전 설치`, fixture JSON generation, JSON `json.tool`, and HTML Safe Install rendering.
- Local self-scan returned grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.6 - 2026-05-07

### Changed

- `safe-install` output now includes a short pre-run checklist before any install advice.
- README and testing guidance now describe the safe-install pre-run checklist.

### Validation

- `.venv/bin/python -m pytest -q` passed with 149 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.6/dist` built `repotrust-0.2.6.tar.gz` and `repotrust-0.2.6-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.6`.
- Clean wheel smoke verified `safe-install` pre-run checklist, Console Mode `[S] 안전 설치`, fixture JSON generation, and JSON `json.tool`.
- Local self-scan returned grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.5 - 2026-05-07

### Added

- `repo-trust safe-install <target>` and `repo-trust-kr safe-install <target>` now print install advice without executing repository install commands.
- Console Mode now includes `[S] Safe Install` / `[S] 안전 설치` for the same install advice workflow.

### Changed

- README, testing guide, and architecture docs now describe the safe install workflow for beginner users.

### Validation

- `.venv/bin/python -m pytest -q` passed with 149 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.5/dist` built `repotrust-0.2.5.tar.gz` and `repotrust-0.2.5-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.5`.
- Clean wheel smoke verified `safe-install`, Console Mode `[S] 안전 설치`, fixture JSON generation, and JSON `json.tool`.
- Local self-scan returned grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.4 - 2026-05-06

### Added

- `repo-trust compare` and `repo-trust-kr compare` can now write comparison reports with `--format markdown --output <path>` or `--format html --output <path>`.
- HTML comparison reports now include an outcome summary, `Improvements`, `New issues`, `Severity changes`, and `Still remaining` sections.
- HTML comparison findings now include copy buttons for finding ID and `repo-trust explain <finding-id>`.
- Console Mode now includes `[M] Compare JSON` / `[M] JSON 비교` to create a before/after HTML comparison report without memorizing command options.
- Console Mode JSON comparison can list recent JSON reports from `result/` and accept list numbers or direct paths for older/newer report selection.

### Changed

- Console Mode recent reports now label files by purpose, including `compare html`, `html report`, `json report`, and `markdown report`.
- Console Mode compare completion now reminds users that `[R] Reports` can find the saved comparison file later.
- README now includes beginner-friendly Console Mode and Command Mode guides for creating and reading compare reports.
- Testing guidance now covers compare report export, Console Mode compare workflow, recent JSON number selection, and recent report labels.

### Validation

- `.venv/bin/python -m pytest -q` passed with 143 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.4/dist` built `repotrust-0.2.4.tar.gz` and `repotrust-0.2.4-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.4`.
- Clean wheel smoke verified compare text, Markdown export, HTML export, Console Mode compare workflow with recent JSON number selection, and JSON `json.tool`.
- Local self-scan returned grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.3 - 2026-05-06

### Added

- `repo-trust explain <finding-id>` and `repo-trust-kr explain <finding-id>` commands to explain a finding's category, default severity, meaning, and recommended action without rescanning a repository.
- Static HTML finding filters for severity and category, plus expand/collapse controls for finding detail sections.
- Static HTML copy actions for each finding card: copy the finding ID or copy `repo-trust explain <finding-id>`.
- `repo-trust compare <old.json> <new.json>` and `repo-trust-kr compare <old.json> <new.json>` commands to compare saved JSON reports by score, grade, verdict, added findings, resolved findings, severity changes, and persisting findings.

### Changed

- Risky install fixture coverage now includes positive cases for sudo, global package install, and executable permission changes.
- HTML and Markdown reports now clarify that summary priority IDs show only the top findings while the full finding list remains available in report output.
- Console Mode JSON export now prompts for a generic repository target so local paths and GitHub URLs are both discoverable.
- README and validation docs now describe sample report comparison, finding explanation, HTML filtering, and copy workflows.

### Fixed

- HTML finding titles and explanations now cover all risky install pattern IDs.
- Markdown findings are sorted by severity to match the report text.

### Validation

- `.venv/bin/python -m pytest -q` passed with 139 tests.
- `.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.3/dist` built `repotrust-0.2.3.tar.gz` and `repotrust-0.2.3-py3-none-any.whl`.
- Clean wheel install smoke verified `repo-trust`, `repo-trust-kr`, and `repotrust` version `0.2.3`.
- Clean wheel smoke verified `explain`, fixture JSON generation, risky-to-good `compare`, HTML finding copy actions, and JSON `json.tool`.
- Fixture smoke verified risky-to-good JSON comparison with score `51 -> 100 (+49)` and 12 resolved findings.
- Local self-scan returned score `98`, grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.2.2 - 2026-04-30

### Changed

- GitHub Release install guidance now points at `v0.2.2` wheel and source archive assets.
- Console Mode first screen now says GitHub URL checks are API-free by default and local scans provide file-level evidence.
- CI workflow uses Node 24-compatible `actions/checkout@v6` and `actions/setup-python@v6`.

### Fixed

- README smoke found that `v0.2.1` assets did not include the newer first-run console copy shown on `main`; `v0.2.2` aligns the README quickstart, release asset version, and installed CLI output.
- `remote.github_metadata_collected` explanation now states that remote metadata collection only runs when `--remote` is explicit.

## v0.2.1 - 2026-04-30

### Changed

- Product GitHub URL commands now default to parse-only, API-free scans. Use `--remote` on `repo-trust html/json/check/gate <github-url>` to opt into GitHub REST read-only metadata.
- PyPI/TestPyPI publishing was removed from the active project scope; GitHub Releases remain the release channel.
- Dev packaging validation now uses local `python -m build` artifacts without `twine` or upload credentials.

### Fixed

- `target.github_not_fetched` guidance now recommends explicit `--remote` or local checkout scanning instead of implying API access is the default.

## v0.2.0 - 2026-04-29

Post-v1 public readiness hardening for product CLI, remote scan, assessment profiles, and CI policy gates.

### Added

- Product CLI commands `repo-trust html`, `repo-trust json`, `repo-trust check`, and `repo-trust gate`.
- Korean product entrypoint `repo-trust-kr` with localized Console Mode, command help, dashboard labels, finding messages, and next actions.
- JSON report contract `schema_version: "1.2"` with top-level `assessment.profiles` for install, dependency adoption, and AI agent delegation decisions.
- Config v2 policy support for `[rules] disabled`, `[severity_overrides]`, `[policy.profiles]`, `policy.fail_under`, and category `weights`.
- `repo-trust gate` for CI usage: it preserves JSON output and exits `1` when score or profile policy requirements fail.
- Copyable CI policy examples in `examples/repotrust.toml` and `examples/github-actions-repotrust-gate.yml`.
- Finding ID reference documentation for CI policy exceptions and severity overrides.
- JSON report schema reference documentation for schema `1.2` parsers.
- Package and dependency risk findings for npm install lifecycle scripts and unpinned direct Node/Python dependencies.
- Remote `.github/SECURITY.md` parity with local scanning.
- GitHub tree/blob subpath limitation finding and score cap so monorepo subdirectory URLs are not mistaken for subdirectory-only assessments.
- Remote release/tag freshness finding for package-managed repositories when the latest release or tag date is known and stale.
- Scan completeness score caps for parse-only, remote failure, partial scan, README content unavailable, unsupported GitHub subpaths, and missing local path results.
- Shared evidence matrix status mapping for `found`, `missing`, and `unknown` signals in reports.
- GitHub Actions `ci` workflow that installs the package and runs pytest.
- Remote repository metadata quality findings:
  - `remote.github_archived` for `archived=true` as a medium Project Hygiene deduction.
  - `remote.github_issues_disabled` for `has_issues=false` as a low Project Hygiene deduction.
- Stronger JSON contract tests for GitHub parse-only, remote partial scan, and remote archived scan results.
- Structured static HTML report rendering with score, detected files, category, and severity metadata.
- CLI exit-code matrix documentation and regression tests for stdout/stderr separation.
- Clean environment packaging verification routine.

### Changed

- Product GitHub URL commands use GitHub API read-only remote scans by default, while legacy `repotrust scan <github-url>` remains parse-only unless `--remote` is provided.
- README risky install matching now uses command-like evidence from Installation/Setup sections instead of scanning arbitrary prose.
- Remote metadata policy keeps fork/private/default branch/stars/language/size/security analysis fields deferred or evidence-only until JSON evidence metadata is designed.
- Release/tag freshness is conservative: absence of GitHub Releases, empty tags, or release/tag API failure is not treated as stale maintenance.
- README is now a Korean-first user guide with Console Mode, Command Mode, config v2, gate, and current remote scan behavior.
- Package metadata now includes license, author, keywords, classifiers, and project URLs for wheel metadata.

### Validation

- `.venv/bin/python -m pip install -e '.[dev]'` passed.
- `.venv/bin/python -m pytest -q` passed with 120 tests.
- Finding and JSON report reference coverage tests passed.
- Clean wheel install smoke passed for `repo-trust`, `repo-trust-kr`, and legacy `repotrust` entrypoints.
- Clean wheel smoke generated product JSON, product gate JSON, product HTML, and legacy JSON sample reports; all JSON reports passed `json.tool`.
- Example policy gate smoke passed for `good-python` and failed with preserved JSON for `risky-install`.
- Local self-scan JSON passed `json.tool` with `schema_version: "1.2"`, grade `A`, high confidence, full coverage, and no medium/high findings.

## v0.1.0 - 2026-04-28

Initial public release candidate.

### Added

- `repotrust scan <target>` CLI for local repository paths and GitHub URLs.
- Markdown, JSON, and static HTML reports.
- JSON report contract with `schema_version: "1.0"`.
- Explainable findings with stable IDs, severity, evidence, and recommendations.
- README Quality, Install Safety, Security Posture, and Project Hygiene scoring.
- Risky install command detection for shell-piped scripts, `sudo`, process substitution, Python inline execution, direct VCS installs, global package installs, and executable permission changes.
- Explicit config loading with `--config <path>` for `policy.fail_under` and category weights.
- CI-friendly `--fail-under <score>` exit behavior.
- `repotrust --version`.
- GitHub URL parse-only default behavior.
- Explicit `--remote` GitHub API scan for repository metadata, root contents, README content, Dependabot config, and workflow metadata.
- Remote API failure findings for unauthorized, not found, rate-limited, generic API error, and partial scan states.
- MIT license and committed `pylock.toml`.
- Project harness docs: `AGENTS.md`, PRD/TRD/ADR, workflow, validation, active plan/progress, and completed archive.

### Known Limitations

- Remote scan does not clone repositories.
- Remote scan does not perform real dependency vulnerability lookup.
- Contributor profile analysis is not implemented.
- Release/tag freshness scoring is not implemented.
- GitHub App and web dashboard are out of scope.
- README parsing and install command detection are heuristic and intentionally conservative.

### Validation

- `.venv/bin/python -m pytest -q` passed with 50 tests.
- Local self-scan returned 100/100, A, Low risk, finding 0.
- Remote self-scan for `https://github.com/answndud/repo-trust --remote` returned 100/100, A, Low risk.

### Pre-Tag Checklist

- Run `.venv/bin/python -m pytest -q`.
- Run local self-scan: `.venv/bin/repotrust scan . --format json`.
- Run remote self-scan: `.venv/bin/repotrust scan https://github.com/answndud/repo-trust --remote --format json`.
- Confirm `pyproject.toml` version is `0.1.0`.
- Confirm `README.md` usage examples match current CLI behavior.
- Confirm `docs/PLAN.md` and `docs/PROGRESS.md` are clear before tagging.
