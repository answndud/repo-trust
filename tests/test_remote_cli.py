import json
from datetime import date

from cli_helpers import plain_output, runner
from repotrust.cli import app, direct_app, direct_kr_app
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


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
