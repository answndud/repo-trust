import json
import re
from datetime import date
from pathlib import Path

from typer.testing import CliRunner

from repotrust.cli import (
    ReportFormat,
    _default_output_path,
    _resolve_output_path,
    app,
    direct_app,
    direct_kr_app,
)
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


runner = CliRunner()
ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
PRODUCT_TERMINAL_FILES = [
    Path("src/repotrust/console.py"),
    Path("src/repotrust/console_i18n.py"),
    Path("src/repotrust/dashboard.py"),
    Path("src/repotrust/dashboard_i18n.py"),
    Path("src/repotrust/help_i18n.py"),
    Path("src/repotrust/terminal_theme.py"),
]
FORBIDDEN_TERMINAL_THEME_TERMS = {
    "cyan",
    "magenta",
    "pink",
    "bright_green",
    "green",
    "repo-trust // console",
    "repotrust // 명령 모드",
}


def plain_output(text: str) -> str:
    return ANSI_ESCAPE_RE.sub("", text)


def test_product_terminal_theme_avoids_failed_visual_terms():
    source = "\n".join(path.read_text(encoding="utf-8") for path in PRODUCT_TERMINAL_FILES)

    for term in FORBIDDEN_TERMINAL_THEME_TERMS:
        assert term not in source


def test_cli_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "repotrust 0.1.0"


def test_direct_cli_version():
    result = runner.invoke(direct_app, ["--version"], prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust 0.1.0"


def test_direct_kr_cli_version():
    result = runner.invoke(direct_kr_app, ["--version"], prog_name="repo-trust-kr")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust-kr 0.1.0"


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
    assert data["schema_version"] == "1.1"
    assert data["assessment"]["coverage"] == "full"
    assert data["target"]["kind"] == "local"
    assert "RepoTrust Summary" in result.stderr
    assert "RepoTrust Summary" not in result.stdout


def test_repo_self_scan_is_public_readiness_clean():
    result = runner.invoke(
        direct_app,
        ["json", ".", "--output", "/tmp/repotrust-self-test.json"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    data = json.loads(Path("/tmp/repotrust-self-test.json").read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.1"
    assert data["score"]["grade"] == "A"
    assert data["assessment"]["confidence"] == "high"
    assert data["assessment"]["coverage"] == "full"
    assert not [
        finding
        for finding in data["findings"]
        if finding["severity"] in {"medium", "high"}
    ]
    assert data["detected_files"]["ci_workflows"]


def test_direct_cli_root_starts_interactive_launcher():
    result = runner.invoke(direct_app, [], input="q\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust Console" in stderr
    assert "repotrust㉿local" in stderr
    assert "└─$ select" in stderr
    assert "workflows" in stderr
    assert "Scan local repository" in stderr
    assert "Scan GitHub URL" in stderr


def test_direct_kr_cli_root_starts_korean_interactive_launcher():
    result = runner.invoke(direct_kr_app, [], input="q\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "repotrust㉿local" in stderr
    assert "└─$ 선택" in stderr
    assert "RepoTrust 한국어 콘솔" in stderr
    assert "워크플로우" in stderr
    assert "로컬 저장소 검사" in stderr
    assert "GitHub URL 검사" in stderr
    assert "세션을 종료했습니다." in stderr
    assert "Scan local repository" not in stderr


def test_direct_cli_help_shows_product_commands_without_launcher():
    result = runner.invoke(direct_app, ["--help"], input="1\n", prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "repotrust㉿help" in stdout
    assert "└─$ help language" in stdout
    assert "Usage:" in stdout
    assert "html" in stdout
    assert "json" in stdout
    assert "check" in stdout
    assert "RepoTrust Console" not in stdout


def test_direct_cli_help_can_show_korean_product_commands():
    result = runner.invoke(direct_app, ["--help"], input="2\n", prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "repotrust㉿help" in stdout
    assert "02 한국어" in stdout
    assert "사용법:" in stdout
    assert "HTML 신뢰 리포트를 저장합니다." in stdout
    assert "파일 저장 없이 터미널 대시보드로 검사합니다." in stdout


def test_direct_kr_cli_help_shows_shared_product_commands_without_launcher():
    result = runner.invoke(direct_kr_app, ["--help"], input="1\n", prog_name="repo-trust-kr")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage:" in stdout
    assert "html" in stdout
    assert "json" in stdout
    assert "check" in stdout
    assert "RepoTrust 한국어 콘솔" not in stdout


def test_direct_cli_subcommand_help_can_show_korean_without_target():
    result = runner.invoke(direct_app, ["html", "--help"], input="2\n", prog_name="repo-trust")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "사용법: repo-trust html" in stdout
    assert "대상  검사할 로컬 경로 또는 GitHub URL입니다." in stdout
    assert "--parse-only" in stdout


def test_direct_kr_cli_subcommand_help_can_show_english_without_target():
    result = runner.invoke(
        direct_kr_app,
        ["check", "--help"],
        input="1\n",
        prog_name="repo-trust-kr",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage: repo-trust check" in stdout
    assert "Inspect a target and print a terminal dashboard." in stdout
    assert "--fail-under" in stdout


def test_direct_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_app, [], input="1\n.\n", prog_name="repo-trust")

    assert result.exit_code == 0
    assert "Trust Assessment" in result.stderr
    assert "Risk Breakdown" in result.stderr
    assert "Evidence" in result.stderr
    assert "Wrote html report" in result.stderr


def test_direct_kr_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_kr_app, [], input="1\n.\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "로컬 경로" in stderr
    assert "신뢰도 검사 결과" in result.stderr
    assert "어디가 괜찮고 어디를 봐야 하나" in result.stderr
    assert "확인한 근거" in result.stderr
    assert "html 리포트를" in result.stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_recent_reports_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result_dir = tmp_path / "result"
    result_dir.mkdir()
    (result_dir / "repo-2026-04-28.html").write_text("<html></html>", encoding="utf-8")
    (result_dir / "repo-2026-04-28.json").write_text("{}", encoding="utf-8")

    result = runner.invoke(direct_app, [], input="5\n", prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "recent reports" in result.stderr
    assert "repo-2026-04-28.html" in result.stderr
    assert "repo-2026-04-28.json" in result.stderr


def test_direct_cli_html_github_url_remote_scan_writes_default_output(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
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
        direct_app,
        ["html", "https://github.com/owner/repo"],
        prog_name="repo-trust",
    )

    output = tmp_path / "result" / f"repo-{date.today().isoformat()}.html"
    assert result.exit_code == 0
    assert result.stdout == ""
    assert output.exists()
    assert "<!doctype html>" in output.read_text(encoding="utf-8")
    assert calls == [("https://github.com/owner/repo", None, True)]
    assert "RepoTrust" in result.stderr
    assert "Trust Assessment" in result.stderr
    assert "Risk Breakdown" in result.stderr
    assert "Evidence" in result.stderr
    assert "Top Findings" in result.stderr
    assert f"result/repo-{date.today().isoformat()}.html" in plain_output(result.stderr)


def test_direct_cli_json_github_url_remote_scan_writes_default_output(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
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
            score=calculate_score([]),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        direct_app,
        ["json", "https://github.com/owner/repo"],
        prog_name="repo-trust",
    )

    output = tmp_path / "result" / f"repo-{date.today().isoformat()}.json"
    assert result.exit_code == 0
    assert result.stdout == ""
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["target"]["kind"] == "github"
    assert calls == [("https://github.com/owner/repo", None, True)]
    assert "Trust Assessment" in result.stderr


def test_direct_cli_check_github_url_prints_terminal_dashboard(monkeypatch):
    def fake_scan(target_text, weights=None, remote=False):
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
        direct_app,
        ["check", "https://github.com/owner/repo"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "# RepoTrust Report" not in result.stderr
    assert "repotrust㉿scan" in result.stderr
    assert "Trust Assessment" in result.stderr
    assert "Confidence" in result.stderr
    assert "Coverage" in result.stderr
    assert "remote.github_metadata_collected" in result.stderr


def test_direct_kr_cli_check_github_url_prints_korean_dashboard(monkeypatch):
    def fake_scan(target_text, weights=None, remote=False):
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
        direct_kr_app,
        ["check", "https://github.com/owner/repo"],
        prog_name="repo-trust-kr",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "# RepoTrust Report" not in result.stderr
    assert "repotrust㉿scan" in stderr
    assert "검사 방식 GitHub 원격 검사" in stderr
    assert "신뢰도 검사 결과" in stderr
    assert "결론" in stderr
    assert "확실도" in stderr
    assert "어디가 괜찮고 어디를 봐야 하나" in stderr
    assert "확인한 근거" in stderr
    assert "먼저 볼 문제" in stderr
    assert "다음에 할 일" in stderr
    assert "정보" in stderr


def test_direct_kr_cli_json_writes_file_with_korean_status(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    def fake_scan(target_text, weights=None, remote=False):
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
            score=calculate_score([]),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        direct_kr_app,
        ["json", "https://github.com/owner/repo"],
        prog_name="repo-trust-kr",
    )

    output = tmp_path / "result" / f"repo-{date.today().isoformat()}.json"
    assert result.exit_code == 0
    assert result.stdout == ""
    assert output.exists()
    assert "json 리포트를" in result.stderr
    assert "신뢰도 검사 결과" in result.stderr
    assert "결과 파일" in result.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.1"
    assert data["target"]["kind"] == "github"


def test_direct_cli_parse_only_github_url_skips_remote(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        finding = Finding(
            id="target.github_not_fetched",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub URL was parsed without remote metadata collection.",
            evidence="Remote scan was not requested.",
            recommendation="Run repo-trust without --parse-only for repository metadata.",
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
        direct_app,
        ["json", "https://github.com/owner/repo", "--parse-only"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert calls == [("https://github.com/owner/repo", None, False)]


def test_cli_remote_rejects_local_path(tmp_path):
    result = runner.invoke(app, ["scan", str(tmp_path), "--remote"])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--remote" in stderr
    assert "GitHub URL" in stderr


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
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "must define exactly" in stderr


def test_cli_missing_config_exits_with_usage_error(tmp_path):
    missing_config = tmp_path / "missing.toml"

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(missing_config)])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "does not exist" in stderr


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
