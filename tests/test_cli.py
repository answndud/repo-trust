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
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score

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


def test_direct_cli_init_policy_command_is_removed():
    result = runner.invoke(
        direct_app,
        ["init-policy"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "No such command" in stderr


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
    assert f"Open with: open result/repo-{date.today().isoformat()}.html" in plain_output(
        result.stderr
    )


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
    assert "열기 명령: open result/" in plain_output(result.stderr)
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


def test_cli_config_rejects_weights_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        "[weights]\nreadme_quality = 1.0\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "Unknown config section(s): weights" in stderr


def test_cli_config_rejects_rules_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text('[rules]\ndisabled = ["security.no_policy"]\n', encoding="utf-8")

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "Unknown config section(s): rules" in stderr


def test_cli_config_rejects_severity_overrides_section(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        '[severity_overrides]\n"security.no_policy" = "low"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["scan", str(tmp_path), "--format", "json", "--config", str(config)])
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "--config" in stderr
    assert "Unknown config section(s): severity_overrides" in stderr


def test_cli_remote_scan_does_not_receive_config_weights(monkeypatch, tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 0\n", encoding="utf-8")
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
    assert calls == [("https://github.com/owner/repo", None, True)]


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
    assert "Unknown config section(s): weights" in stderr


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


def test_direct_cli_gate_rejects_removed_profile_policy(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text(
        '[policy.profiles]\nagent_delegate = "usable_after_review"\n',
        encoding="utf-8",
    )

    result = runner.invoke(
        direct_app,
        ["gate", str(tmp_path), "--config", str(config)],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "--config" in stderr
    assert "Unknown [policy] key(s): profiles" in stderr


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
