# Architecture

RepoTrust is intentionally small and offline-first. The CLI scans a target, creates a structured `ScanResult`, scores findings with explainable heuristics, and renders reports from that result.

## Current Package Layout

- `src/repotrust/cli.py`: Typer CLI entrypoint and terminal behavior.
- `src/repotrust/config.py`: explicit TOML config loading and validation.
- `src/repotrust/scanner.py`: orchestration for local targets and GitHub URL targets.
- `src/repotrust/targets.py`: target classification and GitHub URL parsing.
- `src/repotrust/detection.py`: root-level repository file detection.
- `src/repotrust/rules.py`: deterministic rule checks that emit findings.
- `src/repotrust/scoring.py`: category scores, total score, grade, and risk label.
- `src/repotrust/reports.py`: Markdown, JSON, and static HTML report rendering.
- `src/repotrust/models.py`: dataclass models shared across the scanner.
- `tests/`: pytest coverage for parsing, scanning, reports, and CLI behavior.

## Data Flow

1. `repotrust scan <target>` enters through `cli.py`.
2. If `--config <path>` is provided, `config.py` loads and validates the local policy file.
3. `scanner.scan()` calls `targets.parse_target()`.
4. Local paths are inspected with `detection.detect_files()`.
5. Rule functions in `rules.py` emit `Finding` objects.
6. `scoring.calculate_score()` converts findings into category and total scores.
7. `reports.render_report()` renders Markdown, JSON, or HTML from `ScanResult`.

GitHub URLs currently stop after parsing. The result includes an informational finding that remote scanning is not enabled.

## Extension Boundaries

- Add new repository file checks in `detection.py`.
- Add new trust checks in `rules.py`.
- Add or adjust scoring weights only in `scoring.py`.
- Add report presentation changes in `reports.py`, without re-checking repository state.
- Add CLI options in `cli.py`, then cover them with CLI tests.

## Design Constraints

- Rule logic must be deterministic, offline, and fast.
- Findings must remain stable enough for users to grep, diff, and build CI policy around them.
- JSON output is a public-ish interface; avoid breaking key names without a deliberate migration.
- Keep local project knowledge in repository files so Codex can discover it without relying on external chat history.

## Reference Basis

This harness follows the Codex guidance that project instructions should live in `AGENTS.md` and deeper repository knowledge should be discoverable through repository-local docs. The linked blog post is treated only as a reference index; Codex official documentation is the standard for Codex-specific conventions.
