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
from repotrust.console import run_console_mode
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
    "magenta",
    "pink",
    "bright_green",
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
    assert result.stdout.strip() == "repotrust 0.2.3"


def test_direct_cli_version():
    result = runner.invoke(direct_app, ["--version"], prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust 0.2.3"


def test_direct_kr_cli_version():
    result = runner.invoke(direct_kr_app, ["--version"], prog_name="repo-trust-kr")

    assert result.exit_code == 0
    assert result.stdout.strip() == "repo-trust-kr 0.2.3"


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


def test_direct_cli_root_starts_interactive_launcher():
    result = runner.invoke(direct_app, [], input="q\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust v0.2.3" in stderr
    assert "Offline-first trust checks before installing a repository." in stderr
    assert "Select action:" in stderr
    assert "[G]  GitHub repo" in stderr
    assert "URL check without API by default" in stderr
    assert "[L]  Local repo" in stderr
    assert "Full file-level local scan" in stderr
    assert "[C]  Quick check" in stderr
    assert "[J]  Export JSON" in stderr
    assert "Recent:" in stderr
    assert "[R] Reports   [?] Help   [Q] Quit" in stderr
    assert "→ Press a key" in stderr
    assert "+-- select workflow" not in stderr
    assert "repotrust㉿local" not in stderr
    assert "Scan local repository" not in stderr


def test_direct_kr_cli_root_starts_korean_interactive_launcher():
    result = runner.invoke(direct_kr_app, [], input="q\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust v0.2.3" in stderr
    assert "설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다." in stderr
    assert "작업 선택:" in stderr
    assert "[G]  GitHub 저장소" in stderr
    assert "기본은 API 없이 URL 확인" in stderr
    assert "[L]  로컬 저장소" in stderr
    assert "파일 근거까지 로컬 검사" in stderr
    assert "[C]  빠른 점검" in stderr
    assert "[J]  JSON 내보내기" in stderr
    assert "최근 리포트:" in stderr
    assert "[R] 리포트   [?] 도움말   [Q] 종료" in stderr
    assert "→ 키를 누르세요" in stderr
    assert "+-- 워크플로우 선택" not in stderr
    assert "repotrust㉿local" not in stderr
    assert "세션을 종료했습니다." in stderr
    assert "Scan local repository" not in stderr


def test_console_mode_uses_alternate_screen_for_real_terminals():
    events = []

    class FakeScreen:
        def __enter__(self):
            events.append("screen-enter")
            return self

        def __exit__(self, exc_type, exc, tb):
            events.append("screen-exit")

    class FakeConsole:
        is_terminal = True

        def screen(self, hide_cursor=False):
            events.append(f"hide_cursor={hide_cursor}")
            return FakeScreen()

        def print(self, *args, **kwargs):
            events.append("print")

        def input(self, *args, **kwargs):
            events.append(f"input:{args[0] if args else ''}")
            return "q"

    run_console_mode(
        console=FakeConsole(),
        help_text=lambda: "help",
        version="0.2.3",
        run_workflow=lambda workflow: None,
    )

    assert events[0] == "hide_cursor=False"
    assert "screen-enter" in events
    assert "screen-exit" in events
    assert len([event for event in events if event.startswith("input:")]) == 1


def test_console_mode_pauses_before_restoring_after_workflow():
    events = []
    inputs = iter(["5", ""])

    class FakeScreen:
        def __enter__(self):
            events.append("screen-enter")
            return self

        def __exit__(self, exc_type, exc, tb):
            events.append("screen-exit")

    class FakeConsole:
        is_terminal = True

        def screen(self, hide_cursor=False):
            return FakeScreen()

        def print(self, *args, **kwargs):
            events.append("print")

        def input(self, *args, **kwargs):
            events.append(f"input:{args[0] if args else ''}")
            return next(inputs)

    run_console_mode(
        console=FakeConsole(),
        help_text=lambda: "help",
        version="0.2.3",
        run_workflow=lambda workflow: None,
    )

    input_events = [event for event in events if event.startswith("input:")]
    assert len(input_events) == 2
    assert events.index(input_events[-1]) < events.index("screen-exit")


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
    assert "gate" in stdout
    assert "explain" in stdout
    assert "compare" in stdout
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
    assert "JSON 리포트를 출력하고 정책 실패를 exit code로 표시합니다." in stdout
    assert "finding ID의 의미와 추천 조치를 설명합니다." in stdout
    assert "두 JSON 리포트의 점수와 finding 변화를 비교합니다." in stdout


def test_direct_kr_cli_help_shows_shared_product_commands_without_launcher():
    result = runner.invoke(direct_kr_app, ["--help"], input="1\n", prog_name="repo-trust-kr")
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "Usage:" in stdout
    assert "html" in stdout
    assert "json" in stdout
    assert "check" in stdout
    assert "explain" in stdout
    assert "compare" in stdout
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


def test_direct_cli_compare_reports(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"

    old_result = runner.invoke(
        direct_app,
        ["json", "tests/fixtures/repos/risky-install", "--output", str(old_report)],
        prog_name="repo-trust",
    )
    new_result = runner.invoke(
        direct_app,
        ["json", "tests/fixtures/repos/good-python", "--output", str(new_report)],
        prog_name="repo-trust",
    )
    assert old_result.exit_code == 0
    assert new_result.exit_code == 0

    result = runner.invoke(
        direct_app,
        ["compare", str(old_report), str(new_report)],
        prog_name="repo-trust",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "RepoTrust Report Compare" in stdout
    assert "Score: 51 -> 100 (+49)" in stdout
    assert "Grade: F -> A" in stdout
    assert "Resolved findings: 12" in stdout
    assert "- install.risky.uses_sudo" in stdout
    assert "Added findings: 0" in stdout


def test_direct_cli_compare_writes_markdown_report(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
    output = tmp_path / "compare.md"

    old_result = runner.invoke(
        direct_app,
        ["json", "tests/fixtures/repos/risky-install", "--output", str(old_report)],
        prog_name="repo-trust",
    )
    new_result = runner.invoke(
        direct_app,
        ["json", "tests/fixtures/repos/good-python", "--output", str(new_report)],
        prog_name="repo-trust",
    )
    assert old_result.exit_code == 0
    assert new_result.exit_code == 0

    result = runner.invoke(
        direct_app,
        [
            "compare",
            str(old_report),
            str(new_report),
            "--format",
            "markdown",
            "--output",
            str(output),
        ],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)
    markdown = output.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Wrote markdown comparison report" in stderr
    assert "# RepoTrust Compare Report" in markdown
    assert "- Score: **51 -> 100 (+49)**" in markdown
    assert "## Resolved findings: 12" in markdown
    assert "- `- install.risky.uses_sudo`" in markdown


def test_direct_cli_compare_writes_html_report(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
    output = tmp_path / "compare.html"
    old_report.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "score": {"total": 80, "grade": "B"},
                "assessment": {"verdict": "usable_after_review"},
                "target": {"raw": "before"},
                "findings": [
                    {"id": "security.no_policy", "severity": "medium"},
                    {"id": "security.no_ci", "severity": "low"},
                ],
            }
        ),
        encoding="utf-8",
    )
    new_report.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "score": {"total": 70, "grade": "C"},
                "assessment": {"verdict": "do_not_install_before_review"},
                "target": {"raw": "after"},
                "findings": [
                    {"id": "security.no_ci", "severity": "medium"},
                    {"id": "install.risky.uses_sudo", "severity": "high"},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        direct_app,
        [
            "compare",
            str(old_report),
            str(new_report),
            "--format",
            "html",
            "--output",
            str(output),
        ],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)
    html = output.read_text(encoding="utf-8")

    assert result.exit_code == 0
    assert "Wrote html comparison report" in stderr
    assert "<!doctype html>" in html
    assert "RepoTrust Compare Report" in html
    assert "80 -&gt; 70 (-10)" in html
    assert "Worse" in html
    assert "New issues: 1" in html
    assert "Improvements: 1" in html
    assert "Still remaining: 1" in html
    assert "install.risky.uses_sudo" in html
    assert "security.no_policy" in html
    assert "security.no_ci" in html
    assert "low -> medium" in html
    assert 'data-copy-value="install.risky.uses_sudo"' in html
    assert 'data-copy-value="repo-trust explain install.risky.uses_sudo"' in html
    assert "copyRepoTrustValue" in html


def test_direct_kr_cli_compare_reports(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
    old_report.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "score": {"total": 80, "grade": "B"},
                "assessment": {"verdict": "usable_after_review"},
                "findings": [
                    {"id": "security.no_policy", "severity": "medium"},
                ],
            }
        ),
        encoding="utf-8",
    )
    new_report.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "score": {"total": 92, "grade": "A"},
                "assessment": {"verdict": "usable_by_current_checks"},
                "findings": [],
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        direct_kr_app,
        ["compare", str(old_report), str(new_report)],
        prog_name="repo-trust-kr",
    )
    stdout = plain_output(result.stdout)

    assert result.exit_code == 0
    assert "점수: 80 -> 92 (+12)" in stdout
    assert "해결된 finding: 1" in stdout
    assert "- security.no_policy" in stdout


def test_direct_cli_compare_invalid_report_exits_cleanly(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
    old_report.write_text("{}", encoding="utf-8")
    new_report.write_text("not json", encoding="utf-8")

    result = runner.invoke(
        direct_app,
        ["compare", str(old_report), str(new_report)],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 1
    assert "Not a RepoTrust JSON report" in stderr


def test_direct_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_app, [], input="01\n.\n", prog_name="repo-trust")

    assert result.exit_code == 0
    assert "Selected: Local repository" in result.stderr
    assert "Enter local repository path:" in result.stderr
    assert "[B] Back" in result.stderr
    assert "Running analysis..." in result.stderr
    assert "RESULT:" in result.stderr
    assert "WHY" in result.stderr
    assert "ACTIONS" in result.stderr
    assert "Open full report:" in result.stderr


def test_direct_cli_interactive_github_shortcut_shows_input_and_processing(monkeypatch, tmp_path):
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
        direct_app,
        [],
        input="g\nhttps://github.com/owner/repo\n",
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "Selected: GitHub repository" in result.stderr
    assert "Enter GitHub URL:" in result.stderr
    assert "Example: https://github.com/openai/openai-python" in result.stderr
    assert "[B] Back" in result.stderr
    assert "Running analysis..." in result.stderr
    assert "RESULT:" in result.stderr
    assert "Open full report:" in result.stderr


def test_direct_cli_interactive_json_export_uses_generic_target_prompt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_app, [], input="j\n.\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "Selected: JSON export" in stderr
    assert "Enter repository target:" in stderr
    assert "Enter GitHub URL:" not in stderr
    assert "Example: https://github.com/openai/openai-python" not in stderr
    assert "Running analysis..." in stderr
    assert "Open full report:" in stderr


def test_direct_kr_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_kr_app, [], input="01\n.\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "로컬 저장소 경로 입력:" in stderr
    assert "선택됨: 로컬 저장소" in result.stderr
    assert "분석 중..." in result.stderr
    assert "RESULT:" in result.stderr
    assert "이유" in result.stderr
    assert "다음 행동" in result.stderr
    assert "전체 리포트 열기:" in result.stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_back_returns_to_home_without_scan():
    result = runner.invoke(direct_app, [], input="l\nb\nq\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "Selected: Local repository" in stderr
    assert "[B] Back" in stderr
    assert "Back to action selection." in stderr
    assert stderr.count("Select action:") == 2
    assert "Running analysis..." not in stderr


def test_direct_cli_interactive_recent_reports_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result_dir = tmp_path / "result"
    result_dir.mkdir()
    (result_dir / "repo-2026-04-28.html").write_text("<html></html>", encoding="utf-8")
    (result_dir / "repo-2026-04-28.json").write_text("{}", encoding="utf-8")

    result = runner.invoke(direct_app, [], input="05\n", prog_name="repo-trust")

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "recent reports" in result.stderr
    assert "repo-2026-04-28.html" in result.stderr
    assert "repo-2026-04-28.json" in result.stderr


def test_direct_cli_html_github_url_defaults_to_parse_only(monkeypatch, tmp_path):
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
            recommendation="Run repo-trust with --remote for repository metadata.",
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
    assert calls == [("https://github.com/owner/repo", None, False)]
    assert "RESULT:" in result.stderr
    assert "WHY" in result.stderr
    assert "ACTIONS" in result.stderr
    assert "Open full report:" in result.stderr
    assert f"result/repo-{date.today().isoformat()}.html" in plain_output(result.stderr)


def test_direct_cli_json_github_url_defaults_to_parse_only(monkeypatch, tmp_path):
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
    assert calls == [("https://github.com/owner/repo", None, False)]
    assert "RESULT:" in result.stderr
    assert "Open full report:" in result.stderr


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


def test_direct_cli_json_github_url_remote_option_enters_remote_boundary(monkeypatch, tmp_path):
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
        ["json", "https://github.com/owner/repo", "--remote"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert calls == [("https://github.com/owner/repo", None, True)]


def test_direct_cli_check_github_url_prints_terminal_dashboard(monkeypatch):
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        finding = Finding(
            id="target.github_not_fetched",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub URL was parsed without remote metadata collection.",
            evidence="Remote scan was not requested.",
            recommendation="Run repo-trust with --remote for repository metadata.",
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
    assert "RESULT:" in result.stderr
    assert "Confidence" in result.stderr
    assert "WHY" in result.stderr
    assert "GitHub URL was parsed without remote metadata collection." in result.stderr
    assert calls == [("https://github.com/owner/repo", None, False)]


def test_direct_kr_cli_check_github_url_prints_korean_dashboard(monkeypatch):
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        finding = Finding(
            id="target.github_not_fetched",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub URL was parsed without remote metadata collection.",
            evidence="Remote scan was not requested.",
            recommendation="Run repo-trust with --remote for repository metadata.",
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
    assert "RESULT:" in stderr
    assert "GitHub URL만 확인" in stderr
    assert "이유" in stderr
    assert "다음 행동" in stderr
    assert "GitHub URL 형식만 확인했고 원격 정보는 가져오지 않았습니다." in stderr
    assert calls == [("https://github.com/owner/repo", None, False)]


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
    assert "RESULT:" in result.stderr
    assert "전체 리포트 열기:" in result.stderr
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.2"
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
            recommendation="Run repo-trust with --remote for repository metadata.",
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


def test_direct_cli_remote_rejects_local_path(tmp_path):
    result = runner.invoke(
        direct_app,
        ["json", str(tmp_path), "--remote"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--remote" in stderr
    assert "GitHub URL" in stderr


def test_direct_cli_remote_and_parse_only_cannot_be_combined():
    result = runner.invoke(
        direct_app,
        ["json", "https://github.com/owner/repo", "--remote", "--parse-only"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--parse-only" in stderr
    assert "--remote" in stderr


def test_direct_cli_gate_github_url_defaults_to_parse_only(monkeypatch, tmp_path):
    output = tmp_path / "gate.json"
    calls = []

    def fake_scan(target_text, weights=None, remote=False):
        calls.append((target_text, weights, remote))
        finding = Finding(
            id="target.github_not_fetched",
            category=Category.TARGET,
            severity=Severity.INFO,
            message="GitHub URL was parsed without remote metadata collection.",
            evidence="Remote scan was not requested.",
            recommendation="Run repo-trust with --remote for repository metadata.",
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
        ["gate", "https://github.com/owner/repo", "--output", str(output)],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert output.exists()
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


def test_cli_config_can_disable_findings(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text('[rules]\ndisabled = ["security.no_policy"]\n', encoding="utf-8")

    def fake_scan(target_text, weights=None, remote=False):
        finding = Finding(
            id="security.no_policy",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="No security policy file was found.",
            evidence="No SECURITY.md or .github/SECURITY.md was detected.",
            recommendation="Add a SECURITY.md file.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(raw=target_text, kind="local", path=target_text),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["findings"] == []
    assert data["score"]["total"] == 100


def test_cli_config_can_override_finding_severity(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        '[severity_overrides]\n"security.no_policy" = "low"\n',
        encoding="utf-8",
    )

    def fake_scan(target_text, weights=None, remote=False):
        finding = Finding(
            id="security.no_policy",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="No security policy file was found.",
            evidence="No SECURITY.md or .github/SECURITY.md was detected.",
            recommendation="Add a SECURITY.md file.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(raw=target_text, kind="local", path=target_text),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["findings"][0]["severity"] == "low"
    assert data["score"]["categories"]["security_posture"] == 92


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


def test_cli_invalid_policy_does_not_echo_secret_values(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        '[severity_overrides]\n"security.no_policy" = "ghp_secret_value"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(config)])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "ghp_secret_value" not in stderr


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


def test_direct_cli_gate_preserves_json_when_profile_policy_fails(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        '[policy.profiles]\nagent_delegate = "usable_after_review"\n',
        encoding="utf-8",
    )

    def fake_scan(target_text, weights=None, remote=False):
        finding = Finding(
            id="install.npm_lifecycle_script",
            category=Category.INSTALL_SAFETY,
            severity=Severity.MEDIUM,
            message="package.json contains install lifecycle scripts.",
            evidence="package.json scripts include postinstall.",
            recommendation="Review install scripts before delegation.",
        )
        findings = [finding]
        return ScanResult(
            target=Target(raw=target_text, kind="local", path=target_text),
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    monkeypatch.setattr("repotrust.cli.scan_target", fake_scan)

    result = runner.invoke(
        direct_app,
        ["gate", str(tmp_path), "--config", str(config)],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 1
    data = json.loads(result.stdout)
    assert data["assessment"]["profiles"]["agent_delegate"]["verdict"] == (
        "do_not_install_before_review"
    )
    assert "Policy gate failed" in stderr
    assert "profile agent_delegate" in stderr


def test_direct_cli_gate_example_policy_passes_good_fixture(tmp_path):
    output = tmp_path / "gate.json"

    result = runner.invoke(
        direct_app,
        [
            "gate",
            "tests/fixtures/repos/good-python",
            "--config",
            "examples/repotrust.toml",
            "--output",
            str(output),
        ],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stdout == ""
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.2"
    assert data["score"]["total"] == 100


def test_direct_cli_gate_example_policy_fails_risky_fixture_but_writes_json(tmp_path):
    output = tmp_path / "gate.json"

    result = runner.invoke(
        direct_app,
        [
            "gate",
            "tests/fixtures/repos/risky-install",
            "--config",
            "examples/repotrust.toml",
            "--output",
            str(output),
        ],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 1
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["assessment"]["profiles"]["install"]["verdict"] == (
        "do_not_install_before_review"
    )
    assert "Policy gate failed" in stderr


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
