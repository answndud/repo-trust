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

## Change Workflow

1. Read `AGENTS.md` and the relevant file under `docs/`.
2. Inspect the existing implementation before changing behavior.
3. Keep changes scoped to the layer that owns the behavior.
4. Add or update tests for every behavior change.
5. Run the validation command in `docs/testing-and-validation.md`.
6. Summarize changed behavior and any remaining gaps.

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
