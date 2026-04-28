import json

from typer.testing import CliRunner

from repotrust.cli import app
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "repotrust 0.1.0"


def test_cli_root_without_command_shows_help():
    result = runner.invoke(app, [], prog_name="repotrust")

    assert result.exit_code == 0
    assert "Usage: repotrust" in result.stdout
    assert "scan" in result.stdout
    assert "--version" in result.stdout


def test_cli_scan_help_shows_format_choices():
    result = runner.invoke(app, ["scan", "--help"])

    assert result.exit_code == 0
    assert "Local path or GitHub URL to scan" in result.stdout
    assert "[markdown|json|html]" in result.stdout
    assert "--remote" in result.stdout


def test_cli_scan_markdown(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "markdown"])

    assert result.exit_code == 0
    assert "# RepoTrust Report" in result.output
    assert "RepoTrust Summary" in result.output


def test_cli_scan_json(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["schema_version"] == "1.0"
    assert data["target"]["kind"] == "local"
    assert "RepoTrust Summary" in result.stderr
    assert "RepoTrust Summary" not in result.stdout


def test_cli_remote_rejects_local_path(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--remote"])

    assert result.exit_code == 2
    assert "--remote" in result.stderr
    assert "GitHub URL" in result.stderr


def test_cli_github_url_without_remote_remains_parse_only():
    result = runner.invoke(app, ["scan", "https://github.com/owner/repo", "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["target"]["kind"] == "github"
    assert data["target"]["owner"] == "owner"
    assert [finding["id"] for finding in data["findings"]] == ["target.github_not_fetched"]


def test_cli_github_url_with_remote_enters_remote_boundary(monkeypatch):
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        finding = Finding(
            id="remote.github_metadata_collected",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub repository metadata was collected.",
            evidence="Repository metadata endpoint returned a successful response.",
            recommendation="Continue remote scan.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(
                raw=target_text,
                kind="github",
                host="github.com",
                owner="owner",
                repo="repo",
            ),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        app,
        ["scan", "https://github.com/owner/repo", "--remote", "--format", "json"],
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["target"]["kind"] == "github"
    assert [finding["id"] for finding in data["findings"]] == ["remote.github_metadata_collected"]
    assert calls == [("https://github.com/owner/repo", None, True)]


def test_cli_remote_failure_finding_keeps_json_stdout_and_summary_stderr(monkeypatch):
    def fake_scan(target_text, weights=None, remote=False):
        finding = Finding(
            id="remote.github_api_error",
            category=Category.TARGET,
            severity=Severity.MEDIUM,
            message="GitHub API returned an unexpected error.",
            evidence="GitHub API returned HTTP 500.",
            recommendation="Retry later.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(
                raw=target_text,
                kind="github",
                host="github.com",
                owner="owner",
                repo="repo",
            ),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        app,
        ["scan", "https://github.com/owner/repo", "--remote", "--format", "json"],
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert [finding["id"] for finding in data["findings"]] == ["remote.github_api_error"]
    assert "RepoTrust Summary" in result.stderr
    assert "RepoTrust Summary" not in result.stdout


def test_cli_scan_html_output(tmp_path):
    output = tmp_path / "report.html"

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "html", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "<!doctype html>" in output.read_text(encoding="utf-8")
    assert result.stdout == ""
    assert "Wrote html report" in result.stderr
    assert "RepoTrust Summary" in result.stderr


def test_cli_missing_local_path_reports_finding_without_usage_error(tmp_path):
    missing = tmp_path / "missing"

    result = runner.invoke(app, ["scan", str(missing), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["target"]["kind"] == "local"
    assert [finding["id"] for finding in data["findings"]] == ["target.local_path_missing"]
    assert "RepoTrust Summary" in result.stderr


def test_cli_config_fail_under_is_used(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 100\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(config)])

    assert result.exit_code == 1


def test_cli_fail_under_overrides_config(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 100\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(config), "--fail-under", "0"])

    assert result.exit_code == 0


def test_cli_config_weights_affect_score(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[weights]
readme_quality = 1.0
install_safety = 0.0
security_posture = 0.0
project_hygiene = 0.0
""",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["score"]["total"] == data["score"]["categories"]["readme_quality"]


def test_cli_remote_scan_receives_config_weights(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        """
[weights]
readme_quality = 1.0
install_safety = 0.0
security_posture = 0.0
project_hygiene = 0.0
""",
        encoding="utf-8",
    )
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        return ScanResult(
            target=Target(
                raw=target_text,
                kind="github",
                host="github.com",
                owner="owner",
                repo="repo",
            ),
            detected_files=DetectedFiles(),
            findings=[],
            score=calculate_score([], weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        app,
        [
            "scan",
            "https://github.com/owner/repo",
            "--remote",
            "--format",
            "json",
            "--config",
            str(config),
        ],
    )

    assert result.exit_code == 0
    assert calls == [
        (
            "https://github.com/owner/repo",
            {
                "readme_quality": 1.0,
                "install_safety": 0.0,
                "security_posture": 0.0,
                "project_hygiene": 0.0,
            },
            True,
        )
    ]


def test_cli_remote_scan_config_fail_under_is_used(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 99\n", encoding="utf-8")

    def fake_scan(target_text, weights=None, remote=False):
        finding = Finding(
            id="remote.github_issues_disabled",
            category=Category.PROJECT_HYGIENE,
            severity=Severity.LOW,
            message="GitHub issue tracking is disabled.",
            evidence="Repository metadata has has_issues=false.",
            recommendation="Confirm support path.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(
                raw=target_text,
                kind="github",
                host="github.com",
                owner="owner",
                repo="repo",
            ),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        app,
        ["scan", "https://github.com/owner/repo", "--remote", "--config", str(config)],
    )

    assert result.exit_code == 1
    assert "RepoTrust Summary" in result.stderr


def test_cli_invalid_config_exits_with_usage_error(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[weights]\nreadme_quality = 1.0\n", encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(config)])

    assert result.exit_code == 2
    assert "--config" in result.stderr
    assert "must define exactly" in result.stderr


def test_cli_missing_config_exits_with_usage_error(tmp_path):
    missing_config = tmp_path / "missing.toml"

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(missing_config)])

    assert result.exit_code == 2
    assert "--config" in result.stderr
    assert "does not exist" in result.stderr


def test_cli_fail_under(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--fail-under", "100"])

    assert result.exit_code == 1


def test_cli_invalid_format_exits_with_usage_error(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "xml"])

    assert result.exit_code == 2
    assert "Invalid value for" in result.stderr
    assert "xml" in result.stderr


def test_cli_missing_target_exits_with_usage_error():
    result = runner.invoke(app, ["scan"])

    assert result.exit_code == 2
    assert "Missing argument" in result.stderr
    assert "TARGET" in result.stderr
