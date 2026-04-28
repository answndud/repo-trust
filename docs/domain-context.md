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

- High severity: shell-piped remote scripts such as `curl ... | sh`, process substitution such as `bash <(curl ...)`, Python inline execution with `python -c`, and `sudo`.
- Medium severity: global package installs, direct VCS installs such as `pip install git+https://...`, and commands that mark downloaded code executable.
- Low severity: README exists but no recognizable install command is exposed.

These checks are conservative local heuristics. They flag commands that deserve review before a user or AI agent runs them, but they do not prove malicious intent.

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

## Finding Policy

Finding IDs are treated as a public-ish contract because users may grep reports, compare JSON outputs, or build CI policy around them.

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

## Current Scope

Supported:

- Local repository path scanning.
- GitHub URL parsing.
- Markdown, JSON, and static HTML reports.
- Offline file and README checks.

Deferred:

- GitHub API calls.
- Remote cloning.
- Contributor profile analysis.
- Real vulnerability lookup.
- Release and tag freshness analysis from remote metadata.
- GitHub App or dashboard features.

## Risk Language

Use cautious wording. Prefer "missing signal", "cannot verify", or "risky pattern detected" over claims that a repository is malicious or safe.

## Future Expansion Points

- Remote GitHub metadata scanning behind an explicit option.
- Dependency vulnerability lookups with source attribution.
- Release freshness and maintainer activity scoring.
- Configurable organization policies for CI use.
- A web dashboard after the CLI/report schema stabilizes.
