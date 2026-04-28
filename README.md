# RepoTrust

RepoTrust is a Python CLI that scans a local repository and produces an explainable trust report for installation safety, documentation quality, security posture, and basic project hygiene.

## Installation

For local development, install the package in editable mode:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

The package exposes the `repotrust` CLI after installation.

## Usage

Local checkout scans inspect files directly and never use the network:

```bash
repotrust scan .
repotrust scan . --format json --output report.json
repotrust scan . --format html --output report.html
repotrust scan . --fail-under 80
repotrust scan . --config /path/to/repotrust.toml
repotrust --version
```

GitHub URLs are parsed by default, but repositories are not cloned or fetched unless `--remote` is explicit:

```bash
repotrust scan https://github.com/openai/codex --format json
```

Remote GitHub scanning is available behind explicit opt-in. It requests repository metadata, root contents, README content, Dependabot config, and workflow metadata, then applies the existing report and scoring contract:

```bash
repotrust scan https://github.com/openai/codex --remote --format json
```

Set `GITHUB_TOKEN` to scan private repositories or reduce rate-limit failures:

```bash
GITHUB_TOKEN=ghp_example repotrust scan https://github.com/owner/private-repo --remote
```

RepoTrust uses the token only for GitHub API authorization. Token values are not written to findings, reports, or terminal summaries.

## Development

Run the test suite before handing off changes:

```bash
.venv/bin/python -m pytest -q
```

Refresh the lockfile after dependency changes:

```bash
.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml
```

## Configuration

RepoTrust can load an explicit TOML config file:

```toml
[policy]
fail_under = 80

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
```

Use it with:

```bash
repotrust scan . --config /path/to/repotrust.toml
```

CLI flags override config values. For example, `--fail-under` takes precedence over `policy.fail_under`.

## Fixture Reports

Development fixtures are available under `tests/fixtures/repos/`.

```bash
.venv/bin/repotrust scan tests/fixtures/repos/good-python --format markdown
.venv/bin/repotrust scan tests/fixtures/repos/risky-install --format html --output /tmp/repotrust-risky.html
```

## Contributing

Keep changes small and explainable. Rule changes should include tests, and report contract changes should update the relevant documentation under `docs/`.

See `AGENTS.md` and `docs/` for the current project workflow, active plan, validation routine, and decision records.

## Release Notes

See `CHANGELOG.md` for release history and the v0.1.0 pre-tag checklist.

## License

RepoTrust is released under the MIT License. See `LICENSE`.
