# Architecture

RepoTrust is intentionally small and offline-first. The CLI scans a target, creates a structured `ScanResult`, scores findings with explainable heuristics, and renders reports from that result.

## Current Package Layout

- `src/repotrust/cli.py`: Typer CLI entrypoints, localized product help, and command orchestration. `repo-trust` and `repo-trust-kr` share the same product commands; the legacy `repotrust scan` entrypoint remains separate.
- `src/repotrust/console.py`: interactive Console Mode shell, focused shortcut-based Home/Input/Processing flow, legacy numeric choice normalization, and recent report listing.
- `src/repotrust/console_i18n.py`: localized Console Mode titles, workflow menu labels, prompt labels, and recent report messages.
- `src/repotrust/dashboard.py`: locale-aware Command Mode terminal assessment renderer and legacy summary renderer.
- `src/repotrust/dashboard_i18n.py`: localized dashboard labels, finding message translations, recommendation translations, and beginner-oriented Korean status text.
- `src/repotrust/help_i18n.py`: localized product help text and help language selector for `repo-trust` direct commands.
- `src/repotrust/terminal_theme.py`: shared Kali-style terminal prompt, section, badge, and table primitives for product terminal UI.
- `src/repotrust/evidence.py`: shared evidence matrix status mapping for found, missing, and unknown signals.
- `src/repotrust/remote_markers.py`: shared remote endpoint labels used by remote findings and evidence unknown mapping.
- `src/repotrust/config.py`: explicit TOML config loading, validation, finding policy adjustment, and profile gate thresholds.
- `src/repotrust/scanner.py`: orchestration for local targets and GitHub URL targets.
- `src/repotrust/targets.py`: target classification and GitHub URL parsing.
- `src/repotrust/detection.py`: root-level repository file detection.
- `src/repotrust/remote.py`: explicit GitHub remote scan implementation, GitHub API failure mapping, and remote metadata detection.
- `src/repotrust/rules.py`: deterministic rule checks that emit findings.
- `src/repotrust/scoring.py`: category scores, scan completeness score caps, total score, grade, and risk label.
- `src/repotrust/reports.py`: Markdown, JSON, and static HTML report rendering.
- `src/repotrust/models.py`: dataclass models shared across the scanner, including machine-readable assessment.
- `tests/`: pytest coverage for parsing, scanning, reports, and CLI behavior.

## Data Flow

1. `repo-trust` English Console Mode, `repo-trust-kr` Korean Console Mode, `repo-trust html/json/check <target>`, or legacy `repotrust scan <target>` enters through `cli.py`.
2. If `--config <path>` is provided, `config.py` loads and validates the local policy file.
3. `scanner.scan()` calls `targets.parse_target()`.
4. Local paths are inspected with `detection.detect_files()`.
5. Rule functions in `rules.py` emit `Finding` objects.
6. `scoring.calculate_score()` converts findings into category scores, applies scan completeness caps, and returns total score.
7. If config policy disables findings or overrides severity, `config.py` adjusts findings and recalculates score and assessment.
8. `ScanResult` attaches an `Assessment` with verdict, confidence, coverage, reasons, and next actions.
9. `reports.render_report()` renders Markdown, JSON, or HTML from `ScanResult`.
10. `repo-trust gate` compares the adjusted score and profile verdicts with policy thresholds after the JSON report has been written.

The product CLI treats GitHub URLs as remote scans by default for `repo-trust html/json/check`. Users can pass `--parse-only` to inspect the URL without GitHub API access. `repo-trust-kr` provides the same product commands and workflows with Korean Console Mode text, Korean status messages, and Korean terminal dashboard labels. Product `--help` prompts for English or Korean help before printing root or direct command help. Console Mode uses Rich alternate screen only for real terminals, so it opens like a pager without covering visible scrollback; non-TTY tests and pipes keep normal output. Console Mode Home is action-driven: four primary shortcuts `[G]`, `[L]`, `[C]`, `[J]`, a compact recent-report count, and a controls line for `[R]`, `[?]`, and `[Q]`. Selection prints an explicit `Selected:` state before the target input prompt; GitHub input includes an example URL; target input accepts `[B] Back` to return to Home without scanning. Legacy numeric input `1`-`6` and zero-padded values remain accepted for compatibility. Command Mode dashboards, help, and legacy summaries continue to use Kali-style prompt primitives such as `┌──(repotrust㉿...)-[...]` and `└─$`. Report rendering, JSON shape, and scan behavior are shared. The legacy `repotrust scan` command keeps its original explicit `--remote` opt-in behavior. Remote scans enter `remote.py`, which owns GitHub REST access, remote failure finding conversion, remote metadata-to-`DetectedFiles` conversion, and remote use of the existing rule/scoring/report contract.

## Extension Boundaries

- Add new repository file checks in `detection.py`.
- Add new trust checks in `rules.py`.
- Add or adjust scoring weights only in `scoring.py`.
- Add report presentation changes in `reports.py`, without re-checking repository state.
- Add terminal presentation changes in `terminal_theme.py`, `console.py`, or `dashboard.py`; do not put scanning/scoring decisions in terminal renderers.
- Add CLI options in `cli.py`, then cover them with CLI tests.
- Add remote GitHub behavior in `remote.py`; keep local scanning deterministic and network-free.

## Design Constraints

- Rule logic must be deterministic, offline, and fast.
- Findings must remain stable enough for users to grep, diff, and build CI policy around them.
- JSON output is a public-ish interface; avoid breaking key names without a deliberate migration.
- Keep local project knowledge in repository files so Codex can discover it without relying on external chat history.

## Reference Basis

This harness follows the Codex guidance that project instructions should live in `AGENTS.md` and deeper repository knowledge should be discoverable through repository-local docs. The linked blog post is treated only as a reference index; Codex official documentation is the standard for Codex-specific conventions.
