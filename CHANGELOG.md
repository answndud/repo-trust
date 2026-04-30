# Changelog

All notable changes to RepoTrust are documented here.

## Unreleased

No changes yet.

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
