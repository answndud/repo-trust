import json
import shutil
from pathlib import Path

from repotrust.detection import detect_files
from repotrust.reports import render_json, render_markdown
from repotrust.scanner import scan


FIXTURE_REPOS = Path(__file__).parent / "fixtures" / "repos"


def test_detect_local_files(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n\n## Installation\n\npip install x\n\n## Usage\n\nx\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: ci\n", encoding="utf-8")

    detected = detect_files(tmp_path)

    assert detected.readme == "README.md"
    assert detected.license == "LICENSE"
    assert detected.dependency_manifests == ["pyproject.toml"]
    assert detected.lockfiles == ["uv.lock"]
    assert detected.ci_workflows == [".github/workflows/ci.yml"]


def test_missing_readme_produces_finding(tmp_path):
    result = scan(str(tmp_path))

    ids = {finding.id for finding in result.findings}
    assert "readme.missing" in ids
    assert result.score.total < 100


def test_good_readme_has_no_readme_findings(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")

    result = scan(str(repo))

    assert not [finding for finding in result.findings if finding.category.value == "readme_quality"]
    assert result.score.total >= 90


def test_readme_without_project_purpose_produces_finding(tmp_path):
    readme = """# Thin Project

## Installation

```bash
pip install thin-project
```

## Usage

```bash
thin-project scan .
```

## Contributing

Open issues and review the changelog for release notes.
"""
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "README.md").write_text(readme, encoding="utf-8")

    result = scan(str(repo))

    ids = {finding.id for finding in result.findings}
    assert "readme.no_project_purpose" in ids


def test_curl_pipe_shell_is_high_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "risky-install")

    result = scan(str(repo))

    risky = [finding for finding in result.findings if finding.id == "install.risky.shell_pipe_install"]
    assert risky
    assert risky[0].severity.value == "high"


def test_process_substitution_shell_is_high_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "risky-install")

    result = scan(str(repo))

    risky = [finding for finding in result.findings if finding.id == "install.risky.process_substitution_shell"]
    assert risky
    assert risky[0].severity.value == "high"
    assert risky[0].evidence == "bash <(curl -fsSL https://example.com/install.sh)"


def test_python_inline_execution_is_high_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "risky-install")

    result = scan(str(repo))

    risky = [finding for finding in result.findings if finding.id == "install.risky.python_inline_execution"]
    assert risky
    assert risky[0].severity.value == "high"
    assert risky[0].evidence.startswith("python -c")


def test_direct_vcs_install_is_medium_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "risky-install")

    result = scan(str(repo))

    risky = [finding for finding in result.findings if finding.id == "install.risky.vcs_direct_install"]
    assert risky
    assert risky[0].severity.value == "medium"
    assert risky[0].evidence == "pip install git+https://github.com/example/project.git"


def test_python_module_pip_install_counts_as_install_command(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\nThis project explains enough about what it does for users to understand the expected setup path and command line workflow.\n\n## Installation\n\npython3 -m pip install -e '.[dev]'\n\n## Usage\n\nproject scan .\n\n## Contributing\n\nOpen issues and review release notes.\n",
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    ids = {finding.id for finding in result.findings}
    assert "install.no_commands" not in ids


def test_security_and_ci_findings(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n## Installation\n\npip install project\n\n## Usage\n\nproject\n" + "More docs. " * 60,
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    ids = {finding.id for finding in result.findings}
    assert "security.no_policy" in ids
    assert "security.no_ci" in ids


def test_github_url_is_parsed_but_not_fetched():
    result = scan("https://github.com/owner/repo")

    assert result.target.kind == "github"
    assert result.target.owner == "owner"
    assert result.detected_files.readme is None
    assert [finding.id for finding in result.findings] == ["target.github_not_fetched"]


def test_json_report_shape(tmp_path):
    result = scan(str(tmp_path))
    data = json.loads(render_json(result))

    assert set(data) == {
        "detected_files",
        "findings",
        "generated_at",
        "schema_version",
        "score",
        "target",
    }
    assert data["schema_version"] == "1.0"
    assert set(data["target"]) == {
        "host",
        "kind",
        "owner",
        "path",
        "raw",
        "ref",
        "repo",
        "subpath",
    }
    assert data["target"]["kind"] == "local"
    assert set(data["detected_files"]) == {
        "ci_workflows",
        "dependabot",
        "dependency_manifests",
        "license",
        "lockfiles",
        "readme",
        "security",
    }
    assert set(data["score"]) == {
        "categories",
        "grade",
        "max_score",
        "risk_label",
        "total",
    }
    assert data["findings"]
    assert set(data["findings"][0]) == {
        "category",
        "evidence",
        "id",
        "message",
        "recommendation",
        "severity",
    }


def test_markdown_report_sections(tmp_path):
    result = scan(str(tmp_path))
    markdown = render_markdown(result)

    assert "# RepoTrust Report" in markdown
    assert "## Category Scores" in markdown
    assert "## Detected Files" in markdown
    assert "## Findings" in markdown


def _copy_fixture_repo(tmp_path, name: str) -> Path:
    source = FIXTURE_REPOS / name
    destination = tmp_path / name
    shutil.copytree(source, destination)
    return destination
