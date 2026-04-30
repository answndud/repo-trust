# Development Workflow

## Setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
```

Run the CLI:

```bash
.venv/bin/repotrust scan .
.venv/bin/repotrust scan . --format json
.venv/bin/repotrust scan . --format html --output report.html
```

Refresh the dependency lockfile after dependency changes:

```bash
.venv/bin/python -m pip lock -e '.[dev]' -o pylock.toml
```

Release artifact checks use the same dev environment:

```bash
rm -rf /tmp/repotrust-release
.venv/bin/python -m build --outdir /tmp/repotrust-release/dist
```

PyPI/TestPyPI upload is intentionally out of scope for this project. Publish source code and release notes through GitHub Releases.

## Change Workflow

1. Read `AGENTS.md` and the relevant file under `docs/`.
2. Inspect the existing implementation before changing behavior.
3. Keep changes scoped to the layer that owns the behavior.
4. Add or update tests for every behavior change.
5. Run the validation command in `docs/testing-and-validation.md`.
6. Summarize changed behavior and any remaining gaps.

## Post-v1 Iteration Loop

RepoTrust uses a lightweight Ralph-style loop through repository documents rather than a separate runner script.

Each iteration:

1. Promote exactly one small story from `docs/PLAN.md` `Pending` to `In Progress`.
2. Record the current state, blocker, validation plan, and next action in `docs/PROGRESS.md`.
3. Implement the story with tests and matching documentation changes.
4. Run the required validation command and any story-specific smoke checks.
5. Review `git diff --stat` and relevant diffs for regressions, missing tests, JSON contract drift, and documentation drift.
6. Append the completed story to `docs/COMPLETED.md`, then remove completed details from active docs.
7. Commit locally with a focused message.
8. Move to the next story until no active or pending story remains.

Loop constraints:

- Keep stories small enough to finish in one Codex context when practical.
- Do not copy external Ralph scripts or Claude/Amp-specific files into this repository unless there is a repeated local need.
- Preserve memory through git history, `docs/PLAN.md`, `docs/PROGRESS.md`, and `docs/COMPLETED.md`.
- Push only when explicitly requested, except when the current user instruction already includes a push step.

## Coding Rules

- Prefer dataclasses for core models unless validation needs justify another dependency.
- Keep rule IDs stable and shaped like `<category>.<specific_check>`.
- Keep recommendations specific enough that a maintainer can act on them.
- Keep terminal status output on stderr when report content is printed to stdout.
- Do not duplicate scanning logic inside renderers.
- Do not add production dependencies without a clear reason and test coverage.
- If dependencies change, regenerate `pylock.toml` with `pip lock` and include it in the same change.

## Report Behavior

- Markdown is the canonical human-readable report.
- JSON is the stable machine-readable report.
- HTML is a static rendering generated from the report content; it must not require a local server.

## Deferred Tooling

Do not add repository-local skills, MCP configuration, subagents, hooks, or rules by default. Reconsider only when the project has a repeated workflow that is expensive or error-prone enough to encode.
