# Domain Context

RepoTrust helps users decide whether a repository is safe enough to install, delegate to an AI agent, or add as a dependency. It does not prove that a repository is safe. It reports local, inspectable trust signals and explains uncertainty.

## Current Trust Categories

- README Quality: whether the repository explains purpose, installation, usage, and maintenance expectations.
- Install Safety: whether README install commands include risky patterns such as shell-piped installs or `sudo`.
- Security Posture: whether security policy, CI, Dependabot config, lockfiles, and dependency manifests are present.
- Project Hygiene: whether license and standard project metadata are present.

## README Quality Signals

README Quality currently checks for these local signals:

- README presence: a root README must exist.
- Minimum substance: very short README files are not enough to establish usage confidence.
- Project purpose: the README should include a short prose overview near the top that explains what the project does and why a user would use it.
- Installation guidance: the README should expose an obvious Installation or Setup section.
- Usage guidance: the README should expose an obvious Usage, Quickstart, or Examples section.
- Maintenance signal: the README should mention contribution, support, changelog, release, or maintenance expectations.

These checks are heuristics. They should identify missing trust signals without claiming that a repository is safe or unsafe by themselves.

## Install Safety Signals

Install Safety currently checks README install instructions for risky execution patterns:

- Risky pattern matching is limited to command-like evidence in Installation or Setup sections, rather than arbitrary prose anywhere in the README.
- High severity: shell-piped remote scripts such as `curl ... | sh`, process substitution such as `bash <(curl ...)`, Python inline execution with `python -c`, and `sudo`.
- Medium severity: global package installs, direct VCS installs such as `pip install git+https://...`, and commands that mark downloaded code executable.
- Low severity: README exists but no recognizable install command is exposed.

These checks are conservative local heuristics. They flag commands that deserve review before a user or AI agent runs them, but they do not prove malicious intent.

## Package And Dependency Signals

Local manifest parsing currently adds conservative package-level signals:

- Medium severity install safety: `package.json` install lifecycle scripts such as `preinstall`, `install`, `postinstall`, and `prepare`.
- Low severity security posture: direct Node dependencies that are not exact semver versions.
- Low severity security posture: Python dependencies in `pyproject.toml` or `requirements*.txt` that are not exact pins or direct references.

These findings do not replace lockfile checks. Missing lockfiles remain covered by `security.no_lockfile`; unpinned direct dependencies are weaker signals that should be interpreted with lockfile and update policy evidence.

Remote package repositories with dependency manifests also get a conservative freshness signal:

- Low severity project hygiene: latest GitHub Release or latest tag commit date is older than the freshness threshold.
- No GitHub Release practice, empty tags, or release/tag endpoint failures are not converted into stale findings.
- The finding evidence includes the source (`latest release` or `latest tag`), version/tag label, source date, age, and threshold.

## Scoring

Current weights:

- README Quality: 25%
- Install Safety: 30%
- Security Posture: 25%
- Project Hygiene: 20%

Severity deductions:

- `info`: 0 points. Use for state or limitation notices that should not lower trust by themselves.
- `low`: 8 points. Use for missing convenience or maturity signals that are worth improving but not immediately risky.
- `medium`: 18 points. Use for missing trust signals that materially reduce confidence or reproducibility.
- `high`: 35 points. Use for risky install behavior, missing core documentation, or patterns that could lead users or agents into unsafe execution.

Grade thresholds:

- `A`: 90-100, Low risk.
- `B`: 80-89, Moderate-low risk.
- `C`: 70-79, Moderate risk.
- `D`: 60-69, Elevated risk.
- `F`: below 60, High risk.

Scores are explainable heuristics, not guarantees. Every major deduction should have a corresponding finding.

Scan completeness can cap the total score without changing category scores:

- Remote scan failed before file evidence was collected: cap total score at 60 and mark coverage `failed`, confidence `low`.
- Missing local target path: cap total score at 0 because no repository was scanned.
- GitHub URL parse-only scan: cap total score at 70 and mark coverage `metadata_only`, confidence `low`.
- Partial remote scan or unavailable README content: cap total score at 85 and mark coverage `partial`, confidence `medium`.
- GitHub tree/blob subpath URL scan: cap total score at 85 because RepoTrust reports repository-root signals plus an explicit subpath limitation, not a subdirectory-only assessment.

This prevents incomplete scans from looking adoption-ready while preserving category scores as the explanation of actual observed findings.

## Assessment Policy

Every `ScanResult` includes a machine-readable assessment:

- `verdict`: final decision language for humans and automation.
- `confidence`: how much evidence was collected for this target.
- `coverage`: whether the scan was full, partial, metadata-only, or failed.
- `summary`, `reasons`, `next_actions`: concise explanation and follow-up steps.
- `profiles`: purpose-specific verdicts for `install`, `dependency`, and `agent_delegate`.

Verdict priority:

- `do_not_install_before_review` when any high severity finding exists.
- `insufficient_evidence` when coverage is `failed` or `metadata_only`.
- `usable_after_review` when medium severity findings remain.
- `usable_by_current_checks` when current checks completed without blocking findings.

Profile policy:

- `install`: focuses on install-safety findings from README commands and package install behavior.
- `dependency`: focuses on security posture, project hygiene, reproducibility, and package dependency findings.
- `agent_delegate`: is stricter than normal adoption because an agent may run setup commands; any high finding or medium install-safety finding blocks delegation until reviewed.
- Failed, metadata-only, and partial scans lower profile confidence in the same way as the top-level assessment.

Evidence status in reports:

- `found`: the scanner verified the signal.
- `missing`: the scanner had enough evidence to check the signal and did not find it.
- `unknown`: the scanner could not verify the signal because of parse-only mode or a remote endpoint failure.

## Finding Policy

Finding IDs are treated as a public-ish contract because users may grep reports, compare JSON outputs, or build CI policy around them.

Config policy may disable specific finding IDs or override severity for a local organization, but the underlying rule still emits the original finding before policy adjustment. Reports and scores use the adjusted finding set so CI behavior matches the configured exception.

Finding ID rules:

- Use lowercase dotted IDs shaped like `<area>.<specific_check>`.
- Keep existing IDs stable unless the old meaning was clearly wrong.
- If a rule changes severity but keeps the same meaning, keep the ID and update tests/docs.
- If a rule meaning changes materially, add a new ID instead of silently reusing the old one.
- Finding evidence should point to a local file, command line, missing file pattern, or API state that explains the finding.
- Recommendations should be actionable and avoid vague advice.

Severity selection rules:

- Prefer `info` when the scanner is reporting a limitation, such as a GitHub URL that was parsed but not fetched.
- Prefer `low` for optional hygiene improvements or missing clarity that does not block safe use.
- Prefer `medium` for missing license/security/CI/lockfile/documentation signals that a prudent user should review before depending on the repo.
- Prefer `high` for install instructions or repository states that could cause unsafe execution or seriously mislead a user.

Score change rules:

- Category weights should change rarely and only with documentation updates.
- New rules should start with the smallest severity that honestly communicates the risk.
- Do not use score deductions for facts the scanner cannot verify locally.
- For remote/API-derived signals added later, represent API failure and unknown state as findings rather than silently lowering unrelated categories.
- Use score caps for scan completeness gaps instead of pretending unknown files are missing.

## Remote GitHub Scan Findings

Product CLI GitHub URL scans use GitHub REST API read-only metadata by default and keep clone-free behavior. `--parse-only` keeps a URL-only scan. Legacy `repotrust scan` remains parse-only unless `--remote` is provided.

Remote finding interpretation:

- `target.github_not_fetched`: a GitHub URL was parsed without network access; no remote metadata scan happened.
- `target.github_subpath_unsupported`: a GitHub tree/blob subpath URL was parsed, but RepoTrust does not scan only that subdirectory; use a local checkout for subpath-level assessment.
- `remote.github_metadata_collected`: repository metadata was fetched successfully. This is informational and does not lower score.
- `remote.github_archived`: GitHub repository metadata has `archived=true`. This lowers project hygiene because archived repositories are read-only maintenance risk signals.
- `remote.github_issues_disabled`: GitHub repository metadata has `has_issues=false`. This lightly lowers project hygiene because the public support and bug-reporting path is less obvious.
- `remote.release_or_tag_stale`: package metadata exists and the latest release or latest tag commit date is older than the freshness threshold. This is low severity and does not fire when release/tag evidence is absent or unavailable.
- `remote.github_unauthorized`: GitHub returned 401 or 403 for repository metadata. The repository may be private, the token may be missing, or the token may not have access.
- `remote.github_not_found`: GitHub returned 404. The owner/repo may be wrong, private, or not visible to the current token.
- `remote.github_rate_limited`: GitHub rate limits prevented completion. Retrying later or setting `GITHUB_TOKEN` may help.
- `remote.github_api_error`: GitHub returned an unexpected non-success response.
- `remote.github_partial_scan`: some remote endpoints failed, but enough metadata was collected to report partial results. Missing files from failed endpoints should be treated as unknown, not definitely absent.
- `remote.readme_content_unavailable`: README metadata exists, but content could not be fetched or decoded. Local checkout scanning can provide fuller README and install safety analysis.

Remote scans may use `GITHUB_TOKEN` for authorization and higher rate limits. Token values must never appear in findings, reports, logs, or terminal summaries.

## Remote Metadata Quality Policy

Remote repository metadata should be handled conservatively:

- Score-deducting findings: archived repositories and disabled issue tracking when the API field clearly indicates a reduced maintenance or support signal.
- Deferred security metadata: repository `security_and_analysis` fields are not scored yet because availability and meaning vary by repository visibility, plan, and permissions. They should become findings only after RepoTrust can distinguish unavailable metadata from explicitly disabled security features.
- Evidence-only findings: fork status, private visibility, star/watch/fork counts, default branch name, repository size, language, and creation date. These can help a human reviewer but should not lower score by themselves.
- Freshness findings: releases/tags start as `low` only and require package manifest evidence plus release or tag date evidence.
- Absence of GitHub Releases, empty tags, or release/tag API failure is not a trust failure by itself.
- Unknown metadata: API failures, rate limits, and permission failures must remain remote failure/partial findings. They must not be converted into missing-file or missing-maintenance deductions.
- Contributor and profile signals: keep deferred until source attribution and privacy implications are designed.

## Current Scope

Supported:

- Local repository path scanning.
- GitHub URL parsing.
- Product GitHub API remote scanning with `repo-trust html/json/check <github-url>`.
- Legacy explicit GitHub API remote scanning with `repotrust scan <github-url> --remote`.
- Markdown, JSON, and static HTML reports.
- Offline file and README checks.

Deferred:

- Remote cloning.
- Contributor profile analysis.
- Real vulnerability lookup.
- GitHub App or dashboard features.

## Risk Language

Use cautious wording. Prefer "missing signal", "cannot verify", or "risky pattern detected" over claims that a repository is malicious or safe.

## Future Expansion Points

- Remote GitHub metadata scanning behind an explicit option.
- Dependency vulnerability lookups with source attribution.
- Maintainer activity scoring.
- Configurable organization policies for CI use.
- A web dashboard after the CLI/report schema stabilizes.
