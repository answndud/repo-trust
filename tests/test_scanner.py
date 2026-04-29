import json
import shutil
from inspect import signature
from pathlib import Path

from repotrust.detection import detect_files
from repotrust.models import ScanResult
from repotrust.reports import render_html, render_json, render_markdown
from repotrust.scanner import scan


FIXTURE_REPOS = Path(__file__).parent / "fixtures" / "repos"


def test_detect_local_files(tmp_path):
    (tmp_path / "README.md").write_text("# Project\n\n## Installation\n\npip install x\n\n## Usage\n\nx\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (tmp_path / "pylock.toml").write_text("", encoding="utf-8")
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: ci\n", encoding="utf-8")

    detected = detect_files(tmp_path)

    assert detected.readme == "README.md"
    assert detected.license == "LICENSE"
    assert detected.dependency_manifests == ["pyproject.toml"]
    assert detected.lockfiles == ["pylock.toml", "uv.lock"]
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
    assert result.assessment.verdict == "usable_by_current_checks"
    assert result.assessment.confidence == "high"
    assert result.assessment.coverage == "full"


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
    assert result.assessment.verdict == "do_not_install_before_review"


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


def test_package_json_install_lifecycle_script_is_medium_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "package.json").write_text(
        json.dumps(
            {
                "name": "risky-node-project",
                "scripts": {"postinstall": "node scripts/install.js"},
                "dependencies": {"left-pad": "1.3.0"},
            }
        ),
        encoding="utf-8",
    )

    result = scan(str(repo))

    finding = _finding(result, "dependency.npm_lifecycle_script")
    assert finding.severity.value == "medium"
    assert finding.category.value == "install_safety"
    assert finding.evidence == "package.json scripts.postinstall: node scripts/install.js"


def test_assessment_profiles_split_install_dependency_and_agent_verdicts(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "package.json").write_text(
        json.dumps(
            {
                "name": "agent-sensitive-project",
                "scripts": {"postinstall": "node scripts/install.js"},
                "dependencies": {"left-pad": "1.3.0"},
            }
        ),
        encoding="utf-8",
    )

    result = scan(str(repo))

    assert result.assessment.verdict == "usable_after_review"
    assert result.assessment.profiles["install"].verdict == "usable_after_review"
    assert result.assessment.profiles["dependency"].verdict == "usable_after_review"
    assert result.assessment.profiles["agent_delegate"].verdict == "do_not_install_before_review"
    assert result.assessment.profiles["agent_delegate"].priority_finding_ids == [
        "dependency.npm_lifecycle_script"
    ]


def test_dependency_profile_flags_unpinned_dependency_without_install_block(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "pyproject.toml").write_text(
        """
[project]
name = "range-python-project"
version = "0.1.0"
dependencies = ["requests>=2"]
""",
        encoding="utf-8",
    )

    result = scan(str(repo))

    assert result.assessment.profiles["install"].verdict == "usable_by_current_checks"
    assert result.assessment.profiles["dependency"].verdict == "usable_after_review"
    assert result.assessment.profiles["agent_delegate"].verdict == "usable_by_current_checks"
    assert result.assessment.profiles["dependency"].priority_finding_ids == [
        "dependency.unpinned_python_dependency"
    ]


def test_package_json_unpinned_dependency_is_low_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "package.json").write_text(
        json.dumps(
            {
                "name": "range-node-project",
                "dependencies": {"left-pad": "^1.3.0"},
            }
        ),
        encoding="utf-8",
    )

    result = scan(str(repo))

    finding = _finding(result, "dependency.unpinned_node_dependency")
    assert finding.severity.value == "low"
    assert finding.category.value == "security_posture"
    assert finding.evidence == "package.json dependencies.left-pad: ^1.3.0"


def test_package_risk_keeps_missing_lockfile_signal_separate(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n"
        "Project explains enough about what it does for users to understand whether they should install it or delegate it to an agent safely.\n\n"
        "## Installation\n\n"
        "npm install\n\n"
        "## Usage\n\n"
        "npm test\n\n"
        "## Contributing\n\n"
        "Open issues and review release notes.\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text(
        json.dumps({"name": "no-lock-project", "dependencies": {"left-pad": "1.3.0"}}),
        encoding="utf-8",
    )

    result = scan(str(tmp_path))
    ids = {finding.id for finding in result.findings}

    assert "security.no_lockfile" in ids
    assert "dependency.unpinned_node_dependency" not in ids


def test_pyproject_unpinned_dependency_is_low_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "pyproject.toml").write_text(
        """
[project]
name = "range-python-project"
version = "0.1.0"
dependencies = ["requests>=2"]
""",
        encoding="utf-8",
    )

    result = scan(str(repo))

    finding = _finding(result, "dependency.unpinned_python_dependency")
    assert finding.severity.value == "low"
    assert finding.category.value == "security_posture"
    assert finding.evidence == "pyproject.toml project.dependencies: requests>=2"


def test_requirements_unpinned_dependency_is_low_severity(tmp_path):
    repo = _copy_fixture_repo(tmp_path, "good-python")
    (repo / "requirements.txt").write_text("requests>=2\n", encoding="utf-8")

    result = scan(str(repo))

    finding = _finding(result, "dependency.unpinned_python_dependency")
    assert finding.severity.value == "low"
    assert finding.evidence == "requirements.txt: requests>=2"


def test_install_safety_ignores_prose_warning_about_sudo(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n"
        "Project explains enough about what it does for users to understand whether they should install it or delegate it to an agent safely.\n\n"
        "## Installation\n\n"
        "Use the package manager command below. Do not use sudo for this project.\n\n"
        "```bash\n"
        "pip install project\n"
        "```\n\n"
        "## Usage\n\n"
        "project scan .\n\n"
        "## Contributing\n\n"
        "Open issues and review release notes.\n",
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    assert "install.risky.uses_sudo" not in {finding.id for finding in result.findings}


def test_install_safety_ignores_risky_examples_outside_install_section(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n"
        "Project explains enough about what it does for users to understand whether they should install it or delegate it to an agent safely.\n\n"
        "## Installation\n\n"
        "```bash\n"
        "pip install project\n"
        "```\n\n"
        "## Unsafe examples\n\n"
        "Do not run this historical anti-pattern:\n\n"
        "```bash\n"
        "curl https://example.com/install.sh | sh\n"
        "```\n\n"
        "## Usage\n\n"
        "project scan .\n\n"
        "## Contributing\n\n"
        "Open issues and review release notes.\n",
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    assert "install.risky.shell_pipe_install" not in {
        finding.id for finding in result.findings
    }


def test_python_module_pip_install_counts_as_install_command(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\nThis project explains enough about what it does for users to understand the expected setup path and command line workflow.\n\n## Installation\n\npython3 -m pip install -e '.[dev]'\n\n## Usage\n\nproject scan .\n\n## Contributing\n\nOpen issues and review release notes.\n",
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    ids = {finding.id for finding in result.findings}
    assert "install.no_commands" not in ids


def test_numbered_bilingual_readme_headings_count_as_install_and_usage_sections(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n"
        "Project explains enough about what it does for users to understand whether they should install it or delegate it to an agent safely.\n\n"
        "## 1. Installation / 설치\n\n"
        "python -m pip install project\n\n"
        "## 2. Usage / 사용법\n\n"
        "project scan .\n\n"
        "## Contributing\n\n"
        "Open issues and review release notes.\n",
        encoding="utf-8",
    )

    result = scan(str(tmp_path))

    ids = {finding.id for finding in result.findings}
    assert "readme.no_install_section" not in ids
    assert "readme.no_usage_section" not in ids


def test_scan_result_assessment_is_computed_not_constructor_injected():
    assert "assessment" not in signature(ScanResult).parameters


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


def test_github_parse_only_json_contract_has_stable_finding_id():
    result = scan("https://github.com/owner/repo")
    data = json.loads(render_json(result))

    assert data["schema_version"] == "1.2"
    assert data["target"]["kind"] == "github"
    assert data["target"]["owner"] == "owner"
    assert data["target"]["repo"] == "repo"
    assert data["detected_files"] == {
        "ci_workflows": [],
        "dependabot": None,
        "dependency_manifests": [],
        "license": None,
        "lockfiles": [],
        "readme": None,
        "security": None,
    }
    assert [finding["id"] for finding in data["findings"]] == [
        "target.github_not_fetched"
    ]
    assert data["score"]["total"] == 70
    assert data["assessment"]["verdict"] == "insufficient_evidence"
    assert data["assessment"]["confidence"] == "low"
    assert data["assessment"]["coverage"] == "metadata_only"
    assert data["assessment"]["profiles"]["install"]["verdict"] == "insufficient_evidence"
    assert data["assessment"]["profiles"]["dependency"]["verdict"] == "insufficient_evidence"
    assert data["assessment"]["profiles"]["agent_delegate"]["verdict"] == "insufficient_evidence"


def test_github_subpath_parse_only_reports_scope_limitation():
    result = scan("https://github.com/owner/repo/tree/main/packages/example")

    ids = [finding.id for finding in result.findings]
    assert result.target.ref == "main"
    assert result.target.subpath == "packages/example"
    assert ids == [
        "target.github_subpath_unsupported",
        "target.github_not_fetched",
    ]
    assert result.score.total == 70
    assert result.assessment.verdict == "insufficient_evidence"
    assert result.assessment.coverage == "metadata_only"
    assert "local checkout of the requested subdirectory" in result.assessment.next_actions[0]


def test_json_report_shape(tmp_path):
    result = scan(str(tmp_path))
    data = json.loads(render_json(result))

    assert set(data) == {
        "assessment",
        "detected_files",
        "findings",
        "generated_at",
        "schema_version",
        "score",
        "target",
    }
    assert data["schema_version"] == "1.2"
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
    assert set(data["assessment"]) == {
        "confidence",
        "coverage",
        "next_actions",
        "profiles",
        "reasons",
        "summary",
        "verdict",
    }
    assert set(data["assessment"]["profiles"]) == {
        "agent_delegate",
        "dependency",
        "install",
    }
    assert set(data["assessment"]["profiles"]["install"]) == {
        "next_actions",
        "priority_finding_ids",
        "reasons",
        "summary",
        "verdict",
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
    assert "## Assessment" in markdown
    assert "## Purpose Profiles" in markdown
    assert "## Risk Breakdown" in markdown
    assert "## Evidence Matrix" in markdown
    assert "## Findings" in markdown


def test_html_report_exposes_score_detected_files_and_finding_metadata(tmp_path):
    result = scan(str(tmp_path))
    html = render_html(result)

    assert "<!doctype html>" in html
    assert '<html lang="ko">' in html
    assert "<h1>저장소 신뢰도 점검 결과</h1>" in html
    assert f"<strong>{result.score.total}/{result.score.max_score}</strong>" in html
    assert "<h2>Assessment</h2>" in html
    assert "<h2>Assessment Process</h2>" in html
    assert "<h2>Evidence Matrix</h2>" in html
    assert "<h2>Risk Breakdown</h2>" in html
    assert "<h2>Why This Score</h2>" in html
    assert "<h2>Purpose Profiles</h2>" in html
    assert "<h2>Prioritized Findings</h2>" in html
    assert "<h2>Next Actions</h2>" in html
    assert 'class="finding severity-high"' in html
    assert "<dt>검사 영역</dt>" in html
    assert "<dt>심각도</dt>" in html
    assert "<dt>무슨 뜻인가요?</dt>" in html
    assert "<dt>원문 메시지</dt>" in html
    assert "README가 없습니다." in html
    assert "readme.missing" in html


def _copy_fixture_repo(tmp_path, name: str) -> Path:
    source = FIXTURE_REPOS / name
    destination = tmp_path / name
    shutil.copytree(source, destination)
    return destination


def _finding(result, finding_id):
    matches = [finding for finding in result.findings if finding.id == finding_id]
    assert matches
    return matches[0]
