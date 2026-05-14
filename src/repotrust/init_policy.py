from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


POLICY_FILENAME = "repotrust.toml"
WORKFLOW_PATH = Path(".github") / "workflows" / "repotrust.yml"


@dataclass(frozen=True)
class InitPolicyResult:
    written: list[Path]
    skipped: list[Path]


def init_policy_files(
    directory: Path,
    *,
    version: str,
    force: bool = False,
) -> InitPolicyResult:
    root = directory.expanduser()
    root.mkdir(parents=True, exist_ok=True)

    targets = {
        root / POLICY_FILENAME: policy_template(),
        root / WORKFLOW_PATH: workflow_template(version),
    }
    written: list[Path] = []
    skipped: list[Path] = []

    for path, content in targets.items():
        if path.exists() and not force:
            skipped.append(path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return InitPolicyResult(written=written, skipped=skipped)


def policy_template() -> str:
    return """# RepoTrust CI policy.
#
# Adjust this file for your repository before making it a required gate.

[policy]
fail_under = 85

[policy.profiles]
install = "usable_after_review"
dependency = "usable_after_review"
agent_delegate = "usable_after_review"

[rules]
# Example exception: allow projects that intentionally use an external issue tracker.
# Remove this unless your team has accepted that support-path exception.
disabled = ["remote.github_issues_disabled"]

[severity_overrides]
# Lower this only when your organization has an alternate vulnerability reporting
# process documented outside the scanned repository.
"security.no_policy" = "low"

[weights]
readme_quality = 0.25
install_safety = 0.30
security_posture = 0.25
project_hygiene = 0.20
"""


def workflow_template(version: str) -> str:
    wheel_url = (
        "https://github.com/answndud/repo-trust/releases/download/"
        f"v{version}/repotrust-{version}-py3-none-any.whl"
    )
    return f"""name: RepoTrust Gate

on:
  pull_request:
  workflow_dispatch:

jobs:
  repotrust:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install RepoTrust
        run: python -m pip install {wheel_url}

      - name: Run RepoTrust gate
        run: repo-trust gate . --config repotrust.toml --output repotrust-report.json

      - name: Upload RepoTrust report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: repotrust-report
          path: repotrust-report.json
"""
