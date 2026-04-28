import json

from typer.testing import CliRunner

from repotrust.cli import app


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


def test_cli_scan_html_output(tmp_path):
    output = tmp_path / "report.html"

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "html", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "<!doctype html>" in output.read_text(encoding="utf-8")


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
