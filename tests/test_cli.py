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

PRODUCT_TERMINAL_FILES = [
    Path("src/repotrust/console.py"),
    Path("src/repotrust/console_i18n.py"),
    Path("src/repotrust/dashboard.py"),
    Path("src/repotrust/dashboard_i18n.py"),
    Path("src/repotrust/help_i18n.py"),
    Path("src/repotrust/terminal_theme.py"),
]
FORBIDDEN_TERMINAL_THEME_TERMS = {
    "magenta",
    "pink",
    "bright_green",
    "repo-trust // console",
    "repotrust // 명령 모드",
}


def test_product_terminal_theme_avoids_failed_visual_terms():
    source = "\n".join(path.read_text(encoding="utf-8") for path in PRODUCT_TERMINAL_FILES)

    for term in FORBIDDEN_TERMINAL_THEME_TERMS:
        assert term not in source


def test_cli_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "repotrust 0.2.10"


def test_direct_cli_version():
    result = runner.invoke(direct_app, ["--version"], prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust 0.2.10"


def test_direct_kr_cli_version():
    result = runner.invoke(direct_kr_app, ["--version"], prog_name="repo-trust-kr")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust-kr 0.2.10"


def test_cli_root_without_command_shows_help():
    result = runner.invoke(app, [], prog_name="repotrust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage:" in stdout
    assert "repotrust" in stdout
    assert "scan" in stdout
    assert "--version" in stdout


def test_cli_scan_help_shows_format_choices():
    result = runner.invoke(app, ["scan", "--help"])
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Local path or GitHub URL to scan" in stdout
    assert "markdown" in stdout
    assert "json" in stdout
    assert "html" in stdout
    assert "--remote" in stdout


def test_cli_scan_markdown(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "markdown"])

    assert result.exit_code == 0
    assert "# RepoTrust Report" in result.output
    assert "RepoTrust Summary" in result.output


def test_cli_scan_json(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["schema_version"] == "1.2"
    assert data["assessment"]["coverage"] == "full"
    assert data["target"]["kind"] == "local"
    assert "RepoTrust Summary" in result.stderr
    assert "RepoTrust Summary" not in result.stdout


def test_legacy_cli_scan_prints_deprecation_notice(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json"])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "Deprecated: repotrust scan is a legacy compatibility command." in stderr
    assert "Prefer repo-trust" in stderr
    assert "html/json/check" in stderr
    assert json.loads(result.stdout)["target"]["kind"] == "local"


def test_repo_self_scan_is_public_readiness_clean():
    result = runner.invoke(
        direct_app,
        ["json", ".", "--output", "/tmp/repotrust-self-test.json"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    data = json.loads(Path("/tmp/repotrust-self-test.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.2"
    assert data["score"]["grade"] == "A"
    assert data["assessment"]["confidence"] == "high"
    assert data["assessment"]["coverage"] == "full"
    assert not [
        finding
        for finding in data["findings"]
        if finding["severity"] in {"medium", "high"}
    ]
    assert data["detected_files"]["ci_workflows"]


def test_direct_cli_tutorial_outputs_copyable_first_run_commands():
    result = runner.invoke(direct_app, ["tutorial"], prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "RepoTrust Beginner Tutorial" in result.stdout
    assert "repo-trust html ." in result.stdout
    assert "repo-trust safe-install ." in result.stdout
    assert "repo-trust json ." in result.stdout
    assert "repo-trust check https://github.com/owner/repo" in result.stdout
    assert "[L] local scan, [S] safe install, then [J] export JSON" in result.stdout


def test_direct_kr_cli_tutorial_outputs_korean_first_run_commands():
    result = runner.invoke(direct_kr_app, ["tutorial"], prog_name="repo-trust-kr")

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "RepoTrust 초보자 튜토리얼" in result.stdout
    assert "repo-trust-kr html ." in result.stdout
    assert "repo-trust-kr safe-install ." in result.stdout
    assert "repo-trust-kr json ." in result.stdout
    assert "repo-trust-kr check https://github.com/owner/repo" in result.stdout
    assert "[L] 로컬 검사, [S] 안전 설치, [J] JSON 저장" in result.stdout


def test_direct_cli_samples_writes_good_and_risky_gallery(tmp_path):
    result = runner.invoke(
        direct_app,
        ["samples", "--output-dir", str(tmp_path)],
        prog_name="repo-trust",
    )

    good_html = tmp_path / f"sample-good-{date.today().isoformat()}.html"
    good_json = tmp_path / f"sample-good-{date.today().isoformat()}.json"
    risky_html = tmp_path / f"sample-risky-{date.today().isoformat()}.html"
    risky_json = tmp_path / f"sample-risky-{date.today().isoformat()}.json"
    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust Sample Report Gallery" in result.stderr
    assert "Open with: open" in result.stderr
    assert good_html.name in result.stderr.replace("\n", "")
    for path in [good_html, good_json, risky_html, risky_json]:
        assert path.exists()
    risky_report = risky_html.read_text(encoding="utf-8")
    assert "Next isolated step" not in risky_report
    assert "<dt>설명</dt>" in risky_report
    assert "<dt>추천 조치</dt>" in risky_report
    assert "<script>" not in risky_report
    good_report = json.loads(good_json.read_text(encoding="utf-8"))
    risky_report_json = json.loads(risky_json.read_text(encoding="utf-8"))
    assert good_report["score"]["total"] == 100
    assert good_report["score"]["grade"] == "A"
    assert good_report["assessment"]["confidence"] == "high"
    assert good_report["findings"] == []
    assert risky_report_json["score"]["total"] == 57
    assert risky_report_json["score"]["grade"] == "F"
    assert risky_report_json["assessment"]["confidence"] == "high"
    assert risky_report_json["score"]["categories"]["install_safety"] == 30
    assert len(risky_report_json["findings"]) == 7


def test_direct_kr_cli_samples_outputs_korean_gallery(tmp_path):
    result = runner.invoke(
        direct_kr_app,
        ["samples", "--output-dir", str(tmp_path)],
        prog_name="repo-trust-kr",
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust 샘플 리포트 갤러리" in result.stderr
    assert "열기 명령: open" in result.stderr
    assert (tmp_path / f"sample-good-{date.today().isoformat()}.html").exists()


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
    assert data["target"]["kind"] == "local"
    assert data["target"]["path"].endswith("packages/tool")
    assert data["detected_files"]["readme"] == "README.md"
    assert data["detected_files"]["dependency_manifests"] == ["pyproject.toml"]


def test_legacy_cli_scan_scans_local_subdir(tmp_path):
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

    result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--subdir", "packages/tool", "--format", "json"],
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["target"]["path"].endswith("packages/tool")
    assert data["detected_files"]["readme"] == "README.md"


def test_direct_cli_subdir_rejects_github_url():
    result = runner.invoke(
        direct_app,
        ["check", "https://github.com/openai/codex", "--subdir", "packages/tool"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--subdir can only be used with local path" in stderr


def test_direct_cli_subdir_rejects_parent_traversal(tmp_path):
    result = runner.invoke(
        direct_app,
        ["json", str(tmp_path), "--subdir", "../outside"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--subdir must be a relative path inside" in stderr


def test_direct_cli_help_shows_product_commands_without_launcher():
    result = runner.invoke(direct_app, ["--help"], prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage:" in stdout
    assert "html" in stdout
    assert "json" in stdout
    assert "check" in stdout
    assert "gate" in stdout
    assert "explain" in stdout
    assert "next-steps" in stdout
    assert "init-policy" not in stdout
    assert "audit-install" not in stdout
    assert "compare" in stdout
    assert "RepoTrust Console" not in stdout


def test_direct_kr_cli_help_shows_korean_product_commands():
    result = runner.invoke(direct_kr_app, ["--help"], prog_name="repo-trust-kr")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "사용법:" in stdout
    assert "HTML 신뢰 리포트를 저장합니다." in stdout
    assert "파일 저장 없이 터미널 대시보드로 검사합니다." in stdout
    assert "JSON 리포트를 출력하고 정책 실패를 exit code로 표시합니다." in stdout
    assert "검사 결과에서 초보자용 다음 조치 계획을 보여줍니다." in stdout
    assert "CI 정책 시작 파일을 생성합니다." not in stdout
    assert "설치 시점 실행 표면을 점검합니다." not in stdout
    assert "finding ID의 의미와 추천 조치를 설명합니다." in stdout
    assert "두 JSON 리포트의 점수와 finding 변화를 비교합니다." in stdout


def test_direct_kr_cli_help_does_not_open_launcher():
    result = runner.invoke(direct_kr_app, ["--help"], prog_name="repo-trust-kr")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "사용법:" in stdout
    assert "html" in stdout
    assert "json" in stdout
    assert "check" in stdout
    assert "explain" in stdout
    assert "RepoTrust 한국어 콘솔" not in stdout


def test_direct_cli_subcommand_help_shows_english_without_target():
    result = runner.invoke(direct_app, ["html", "--help"], prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage: repo-trust html" in stdout
    assert "TARGET  Local path or GitHub URL to inspect." in stdout
    assert "--parse-only" in stdout


def test_direct_kr_cli_subcommand_help_shows_korean_without_target():
    result = runner.invoke(
        direct_kr_app,
        ["check", "--help"],
        prog_name="repo-trust-kr",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "사용법: repo-trust check" in stdout
    assert "파일을 저장하지 않고 터미널 대시보드로 검사합니다." in stdout
    assert "--fail-under" in stdout


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
    assert "Default severity: high" in stdout
    assert "Meaning:" in stdout
    assert "Recommended action:" in stdout


def test_direct_kr_cli_explain_finding_id():
    result = runner.invoke(
        direct_kr_app,
        ["explain", "install.risky.uses_sudo"],
        prog_name="repo-trust-kr",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Finding: install.risky.uses_sudo" in stdout
    assert "영역: install_safety" in stdout
    assert "기본 심각도: high" in stdout
    assert "추천 조치:" in stdout


def test_direct_cli_explain_unknown_finding_exits_with_suggestions():
    result = runner.invoke(
        direct_app,
        ["explain", "unknown.finding"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 1
    assert "Unknown finding ID: unknown.finding" in stderr
    assert "install.risky.uses_sudo" in stderr


def test_direct_cli_dashboard_explains_top_three_findings_summary(tmp_path):
    result = runner.invoke(
        direct_app,
        ["check", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "Showing top 3 of" in stderr
    assert "See the Findings section" in stderr
    assert "full list." in stderr


def test_cli_scan_html_output(tmp_path):
    output = tmp_path / "report.html"

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "html", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    assert "<!doctype html>" in output.read_text(encoding="utf-8")
    assert result.stdout == ""
    assert "Wrote html report" in result.stderr
    assert "RepoTrust Summary" in result.stderr


def test_cli_filename_only_output_writes_dated_result_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["scan", ".", "--format", "html", "--output", "report.html"])

    output = tmp_path / "result" / f"report-{date.today().isoformat()}.html"
    assert result.exit_code == 0
    assert output.exists()
    assert '<html lang="ko">' in output.read_text(encoding="utf-8")
    assert f"Wrote html report to {output.relative_to(tmp_path)}" in plain_output(result.stderr)


def test_resolve_output_path_dates_filename_only_paths():
    assert _resolve_output_path(Path("report.html"), today=date(2026, 4, 28)) == Path(
        "result/report-2026-04-28.html"
    )


def test_resolve_output_path_keeps_explicit_locations():
    assert _resolve_output_path(Path("reports/report.html"), today=date(2026, 4, 28)) == Path(
        "reports/report.html"
    )
    assert _resolve_output_path(Path("/tmp/report.html"), today=date(2026, 4, 28)) == Path(
        "/tmp/report.html"
    )


def test_default_output_path_uses_github_repo_name():
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
    assert data["target"]["kind"] == "local"
    assert [finding["id"] for finding in data["findings"]] == ["target.local_path_missing"]
    assert data["score"]["total"] == 0
    assert data["assessment"]["verdict"] == "do_not_install_before_review"
    assert data["assessment"]["coverage"] == "failed"
    assert data["assessment"]["confidence"] == "low"
    assert "RepoTrust Summary" in result.stderr


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
