import json
from datetime import date
from pathlib import Path

from cli_helpers import plain_output, runner
from repotrust.cli import (
    ReportFormat,
    _default_output_path,
    _resolve_output_path,
    app,
    direct_app,
    direct_kr_app,
)


def test_product_cli_version():
    result = runner.invoke(direct_app, ["--version"], prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust 0.2.10"


def test_direct_cli_root_prints_command_help_without_console_mode():
    result = runner.invoke(direct_app, [], prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "Usage: repo-trust [OPTIONS] COMMAND [ARGS]..." in stdout
    assert "repo-trust check ." in stdout
    assert "Console Mode" not in stdout


def test_legacy_cli_scan_json_keeps_stdout_machine_readable(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["schema_version"] == "1.2"
    assert data["target"]["kind"] == "local"
    assert "RepoTrust Summary" in result.stderr
    assert "RepoTrust Summary" not in result.stdout
    assert "Deprecated: repotrust scan is a legacy compatibility command." in result.stderr


def test_direct_cli_help_exposes_current_product_commands():
    result = runner.invoke(direct_app, ["--help"], prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    for command in ["html", "json", "check", "gate", "explain", "next-steps", "compare"]:
        assert command in stdout
    assert "init-policy" not in stdout
    assert "audit-install" not in stdout


def test_direct_kr_cli_help_uses_korean_labels():
    result = runner.invoke(direct_kr_app, ["--help"], prog_name="repo-trust-kr")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "사용법:" in stdout
    assert "HTML 신뢰 리포트를 저장합니다." in stdout
    assert "finding ID의 의미와 추천 조치를 설명합니다." in stdout
    assert "콘솔 모드" not in stdout


def test_samples_command_writes_good_and_risky_gallery(tmp_path):
    result = runner.invoke(
        direct_app,
        ["samples", "--output-dir", str(tmp_path)],
        prog_name="repo-trust",
    )

    good_json = tmp_path / f"sample-good-{date.today().isoformat()}.json"
    risky_html = tmp_path / f"sample-risky-{date.today().isoformat()}.html"
    risky_json = tmp_path / f"sample-risky-{date.today().isoformat()}.json"
    assert result.exit_code == 0
    assert good_json.exists()
    assert risky_html.exists()
    assert risky_json.exists()
    assert "<script>" not in risky_html.read_text(encoding="utf-8")
    assert json.loads(good_json.read_text(encoding="utf-8"))["score"]["total"] == 100
    assert json.loads(risky_json.read_text(encoding="utf-8"))["score"]["grade"] == "F"


def test_direct_cli_json_scans_local_subdir(tmp_path):
    package_dir = tmp_path / "packages" / "tool"
    package_dir.mkdir(parents=True)
    (package_dir / "README.md").write_text(
        "# Tool\n\n"
        "Tool explains enough about its purpose and setup path for a monorepo package scan.\n\n"
        "## Installation\n\n"
        "pip install tool\n\n"
        "## Usage\n\n"
        "tool scan .\n\n"
        "## Contributing\n\n"
        "Open issues and review release notes.\n",
        encoding="utf-8",
    )
    (package_dir / "pyproject.toml").write_text(
        "[project]\nname = \"tool\"\nversion = \"0.1.0\"\n",
        encoding="utf-8",
    )
    output = tmp_path / "report.json"

    result = runner.invoke(
        direct_app,
        ["json", str(tmp_path), "--subdir", "packages/tool", "--output", str(output)],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["target"]["path"].endswith("packages/tool")
    assert data["detected_files"]["readme"] == "README.md"


def test_direct_cli_subdir_rejects_invalid_targets(tmp_path):
    github_result = runner.invoke(
        direct_app,
        ["check", "https://github.com/openai/codex", "--subdir", "packages/tool"],
        prog_name="repo-trust",
    )
    traversal_result = runner.invoke(
        direct_app,
        ["json", str(tmp_path), "--subdir", "../outside"],
        prog_name="repo-trust",
    )

    assert github_result.exit_code == 2
    assert "--subdir can only be used with local path" in plain_output(github_result.stderr)
    assert traversal_result.exit_code == 2
    assert "--subdir must be a relative path inside" in plain_output(traversal_result.stderr)


def test_direct_cli_explain_finding_id():
    result = runner.invoke(
        direct_app,
        ["explain", "install.risky.uses_sudo"],
        prog_name="repo-trust",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Finding: install.risky.uses_sudo" in stdout
    assert "Category: install_safety" in stdout
    assert "Recommended action:" in stdout


def test_direct_cli_check_summarizes_large_finding_list():
    result = runner.invoke(
        direct_app,
        ["check", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "Showing top 3 of" in stderr
    assert "full list." in stderr


def test_cli_scan_html_output_file(tmp_path):
    output = tmp_path / "report.html"

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "html", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "<!doctype html>" in output.read_text(encoding="utf-8")
    assert result.stdout == ""


def test_output_path_helpers_keep_stable_naming():
    assert _resolve_output_path(Path("report.html"), today=date(2026, 4, 28)) == Path(
        "result/report-2026-04-28.html"
    )
    assert _resolve_output_path(Path("reports/report.html"), today=date(2026, 4, 28)) == Path(
        "reports/report.html"
    )
    assert _default_output_path(
        "https://github.com/OpenAI/codex.git",
        report_format=ReportFormat.HTML,
        today=date(2026, 4, 28),
    ) == Path("result/codex-2026-04-28.html")


def test_cli_missing_local_path_reports_finding_without_usage_error(tmp_path):
    missing = tmp_path / "missing"

    result = runner.invoke(app, ["scan", str(missing), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert [finding["id"] for finding in data["findings"]] == ["target.local_path_missing"]
    assert data["assessment"]["coverage"] == "failed"


def test_cli_usage_errors_for_invalid_format_and_missing_target(tmp_path):
    invalid_format = runner.invoke(app, ["scan", str(tmp_path), "--format", "xml"])
    missing_target = runner.invoke(app, ["scan"])

    assert invalid_format.exit_code == 2
    assert "xml" in invalid_format.stderr
    assert missing_target.exit_code == 2
    assert "TARGET" in missing_target.stderr
