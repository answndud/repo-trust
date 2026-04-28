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

```bash
repotrust scan .
repotrust scan . --format json --output report.json
repotrust scan . --format html --output report.html
```

GitHub URLs are parsed in v1, but repositories are not cloned or fetched yet.

```bash
repotrust scan https://github.com/openai/codex --format json
```

## Development

Run the test suite before handing off changes:

```bash
.venv/bin/python -m pytest -q
```

## Fixture Reports

Development fixtures are available under `tests/fixtures/repos/`.

```bash
.venv/bin/repotrust scan tests/fixtures/repos/good-python --format markdown
.venv/bin/repotrust scan tests/fixtures/repos/risky-install --format html --output /tmp/repotrust-risky.html
```

## Contributing

Keep changes small and explainable. Rule changes should include tests, and report contract changes should update the relevant documentation under `docs/`.

See `AGENTS.md` and `docs/` for the current project workflow, active plan, validation routine, and decision records.
