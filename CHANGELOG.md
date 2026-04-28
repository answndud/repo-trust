# Changelog

All notable changes to RepoTrust are documented here.

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
