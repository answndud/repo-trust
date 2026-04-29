# Testing and Validation

## Required Command

Run this before handing off changes:

```bash
.venv/bin/python -m pytest -q
```

If the environment is not installed:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

## Test Coverage Expectations

Add or update tests for:

- GitHub URL parsing and invalid target handling.
- Local file detection.
- Rule findings and severity changes.
- Scoring changes.
- JSON shape and Markdown report sections.
- CLI options, output files, stdout/stderr behavior, and exit codes.

## Manual Smoke Checks

Use these when changing CLI or report behavior:

```bash
printf '2\n' | .venv/bin/repo-trust --help
printf '2\n' | .venv/bin/repo-trust html --help
printf 'q\n' | .venv/bin/repo-trust
printf 'q\n' | .venv/bin/repo-trust-kr
.venv/bin/repo-trust check .
.venv/bin/repo-trust-kr check .
.venv/bin/repo-trust html . --output /tmp/repotrust-report.html
.venv/bin/repo-trust-kr html . --output /tmp/repotrust-kr-report.html
.venv/bin/repo-trust json https://github.com/answndud/repo-trust
.venv/bin/repo-trust check https://github.com/openai/codex --parse-only
.venv/bin/repotrust scan https://github.com/openai/codex --format json
```

For config smoke checks, use the committed CI policy template:

```bash
.venv/bin/repo-trust html . --config examples/repotrust.toml
.venv/bin/repo-trust gate tests/fixtures/repos/good-python --config examples/repotrust.toml --output /tmp/repotrust-gate-good.json
.venv/bin/repo-trust gate tests/fixtures/repos/risky-install --config examples/repotrust.toml --output /tmp/repotrust-gate-fail.json || test $? -eq 1
.venv/bin/python -m json.tool /tmp/repotrust-gate-good.json
.venv/bin/python -m json.tool /tmp/repotrust-gate-fail.json
```

Expected behavior:

- Local paths are scanned without network access.
- `repo-trust` without a subcommand opens Console Mode with a Kali-style prompt header, primary shortcut actions, and recent reports.
- In a real TTY, Console Mode uses alternate screen like a pager so previous terminal history is not visible while the menu is open; non-TTY output remains plain for tests and pipes.
- Console Mode Home should show four primary shortcut actions `[G]`, `[L]`, `[C]`, `[J]`, a compact recent report count, and a controls line for `[R]`, `[?]`, `[Q]`; legacy `1` and `01` should still select the local report workflow.
- Console Mode should show `Selected:` feedback, GitHub URL example input, `[B] Back` target-input control, and a processing line before the result dashboard.
- Command Mode/help terminal UI should include `repotrust㉿` and `└─$`, and product terminal sources should not reintroduce pink/magenta/bright-green theme strings.
- `repo-trust --help` prompts for help language and prints command help instead of opening the launcher.
- `repo-trust html/json/check --help` prompts for help language and does not require `TARGET`.
- `repo-trust-kr html/json/check` prints Korean command headers, dashboard labels, write notices, and next-action guidance with the shared Kali-style terminal theme.
- Product CLI GitHub URL commands use GitHub API read-only metadata by default and never clone repositories.
- `--parse-only` parses a GitHub URL without GitHub API access.
- Legacy `repotrust scan` keeps parse-only GitHub URL behavior unless `--remote` is provided.
- `GITHUB_TOKEN` may be set for private repository access or higher rate limits, but token values must not appear in output.
- `--fail-under` exits with code `1` when the score is below the threshold.
- `--config` applies explicit file-based policy to local scans, product remote scans, and explicit legacy remote scans when the file exists and is valid.
- `repo-trust gate` writes JSON first and exits `1` when `policy.fail_under` or `[policy.profiles]` requirements fail.
- `rules.disabled` removes matching finding IDs before scoring and reporting.
- `severity_overrides` changes finding severity before score and assessment recalculation.
- `examples/github-actions-repotrust-gate.yml` is a copyable GitHub Actions snippet, not an active workflow in this repository.
- JSON report content remains valid JSON when stdout is redirected.
- JSON report `schema_version` is `1.2` and includes top-level `assessment` with `profiles`.
- Remote API failure, parse-only, and partial scan scenarios must show low/medium confidence instead of adoption-ready results.
- Remote release/tag freshness tests must distinguish stale release/tag evidence from no-release practice and optional API failure.
- Public readiness requires local self-scan grade `A`, high confidence, full coverage, and no medium/high findings.

## CLI Exit-Code Matrix

| Scenario | Expected exit code | Report output | Status output |
| --- | ---: | --- | --- |
| `repo-trust` without subcommand | 0 | selected workflow result | Console Mode shell on stderr |
| `repo-trust --help` | 0 | help text | no launcher |
| `repo-trust html/json` with GitHub URL | 0 unless `--fail-under` fails | dated file in `result/` unless `--output` is set | stderr RESULT dashboard with report path at bottom |
| `repo-trust check` with GitHub URL | 0 unless `--fail-under` fails | terminal report only | stderr RESULT dashboard |
| `repo-trust gate` with passing policy | 0 | JSON stdout or `--output` file | stderr summary |
| `repo-trust gate` with failing score/profile policy | 1 | JSON still emitted first | stderr summary and policy failure |
| `repo-trust ... --parse-only` with GitHub URL | 0 unless `--fail-under` fails | parse-only finding `target.github_not_fetched` | stderr RESULT dashboard |
| Existing local path with default threshold | 0 | stdout unless `--output` is set | stderr summary |
| Missing local path | 0 | finding `target.local_path_missing` | stderr summary |
| Local path with `--remote` | 2 | no report | usage error on stderr |
| Legacy GitHub URL without `--remote` | 0 | parse-only finding `target.github_not_fetched` | stderr summary |
| Legacy GitHub URL with `--remote` and API/auth/rate-limit failure finding | 0 unless `--fail-under` fails | remote finding in report | stderr summary |
| Any scan with `--fail-under` above score | 1 | report is still emitted | stderr summary |
| Any scan with valid `--output` | scan-dependent | report file only, stdout empty | stderr write notice and summary |
| Invalid config, missing config, invalid option, or missing target | 2 | no report | usage error on stderr |

## Fixture Repositories

Small fixture repositories live under `tests/fixtures/repos/`.

- `good-python`: a repository with clear README, license, security policy, CI, Dependabot config, dependency manifest, and lockfile.
- `risky-install`: a repository with README install commands that intentionally trigger install safety findings.

Generate sample reports from fixtures:

```bash
.venv/bin/repo-trust check tests/fixtures/repos/good-python
.venv/bin/repo-trust json tests/fixtures/repos/good-python --output /tmp/repotrust-good.json
.venv/bin/repo-trust html tests/fixtures/repos/risky-install --output /tmp/repotrust-risky.html
```

Validate redirected JSON:

```bash
.venv/bin/python -m json.tool /tmp/repotrust-good.json
```

Assessment contract checks:

```bash
.venv/bin/repo-trust json https://github.com/openai/codex --parse-only --output /tmp/repotrust-parse-only.json
.venv/bin/python -m json.tool /tmp/repotrust-parse-only.json
```

Expected parse-only JSON includes `assessment.verdict=insufficient_evidence`, `assessment.confidence=low`, `assessment.coverage=metadata_only`, and a capped score.

Public readiness self-scan:

```bash
.venv/bin/repo-trust json . --output /tmp/repotrust-self.json
.venv/bin/python -m json.tool /tmp/repotrust-self.json
.venv/bin/repo-trust html . --output /tmp/repotrust-self.html
```

Expected self-scan result: grade `A`, high confidence, full coverage, detected CI workflow, and no medium/high findings.

## Validation Philosophy

RepoTrust is a trust-reporting tool. Tests should protect user confidence: clear findings, stable output, conservative scoring, and no unannounced network behavior.

## Lockfile Validation

The repository uses `pylock.toml`, generated by pip's `pip lock` command, as the committed dependency lockfile. Regenerate it when `pyproject.toml` dependencies change:

```bash
.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml
```

## Packaging Verification

Before release readiness review, verify install behavior from a clean wheel environment:

```bash
python3 -m venv /tmp/repotrust-clean/.venv
/tmp/repotrust-clean/.venv/bin/python -m pip install --upgrade pip
/tmp/repotrust-clean/.venv/bin/python -m pip wheel --no-deps . --wheel-dir /tmp/repotrust-clean/dist
/tmp/repotrust-clean/.venv/bin/python -m pip install /tmp/repotrust-clean/dist/repotrust-*.whl
/tmp/repotrust-clean/.venv/bin/repo-trust --version
/tmp/repotrust-clean/.venv/bin/repo-trust-kr --version
/tmp/repotrust-clean/.venv/bin/repotrust --version
/tmp/repotrust-clean/.venv/bin/repo-trust json tests/fixtures/repos/good-python --output /tmp/repotrust-clean/good.json
/tmp/repotrust-clean/.venv/bin/repo-trust gate tests/fixtures/repos/good-python --output /tmp/repotrust-clean/gate.json
/tmp/repotrust-clean/.venv/bin/repo-trust html tests/fixtures/repos/risky-install --output /tmp/repotrust-clean/risky.html
/tmp/repotrust-clean/.venv/bin/repotrust scan tests/fixtures/repos/good-python --format json --output /tmp/repotrust-clean/legacy-good.json
/tmp/repotrust-clean/.venv/bin/python -m json.tool /tmp/repotrust-clean/good.json
/tmp/repotrust-clean/.venv/bin/python -m json.tool /tmp/repotrust-clean/gate.json
/tmp/repotrust-clean/.venv/bin/python -m json.tool /tmp/repotrust-clean/legacy-good.json
```

Expected behavior:

- Wheel build succeeds from `pyproject.toml`.
- `repo-trust`, `repo-trust-kr`, and legacy `repotrust` entrypoints print the package version.
- Product `gate` and legacy `scan` fixture JSON reports are written and remain valid JSON.
- Fixture HTML report generation succeeds from the installed wheel.

Then run the repository test suite from the development environment:

```bash
.venv/bin/python -m pytest -q
```

## PyPI/TestPyPI Release Validation

Release artifact validation uses the dev release toolchain from `.[dev]`:

```bash
rm -rf /tmp/repotrust-release
.venv/bin/python -m build --outdir /tmp/repotrust-release/dist
.venv/bin/python -m twine check /tmp/repotrust-release/dist/*
```

Expected behavior:

- `python -m build` creates both `repotrust-<version>.tar.gz` and `repotrust-<version>-py3-none-any.whl`.
- `twine check` reports `PASSED` for every distribution artifact.
- The version in artifact filenames matches `pyproject.toml` and `src/repotrust/__init__.py`.

TestPyPI upload is a remote write and requires either a TestPyPI API token or trusted publishing configured for this repository. Do not place token values in repository files, shell history examples, or reports.

```bash
.venv/bin/python -m twine upload --repository testpypi /tmp/repotrust-release/dist/*
```

After TestPyPI upload, verify install behavior from an isolated environment. Use PyPI as an extra index because TestPyPI should only host the package under test, not necessarily all dependencies:

```bash
python3 -m venv /tmp/repotrust-testpypi/.venv
/tmp/repotrust-testpypi/.venv/bin/python -m pip install --upgrade pip
/tmp/repotrust-testpypi/.venv/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  repotrust==0.2.0
/tmp/repotrust-testpypi/.venv/bin/repo-trust --version
/tmp/repotrust-testpypi/.venv/bin/repo-trust json tests/fixtures/repos/good-python --output /tmp/repotrust-testpypi/good.json
/tmp/repotrust-testpypi/.venv/bin/python -m json.tool /tmp/repotrust-testpypi/good.json
```

Production PyPI upload should happen only after TestPyPI install smoke or trusted publishing validation succeeds:

```bash
.venv/bin/python -m twine upload /tmp/repotrust-release/dist/*
```
