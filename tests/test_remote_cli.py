import json

from cli_helpers import plain_output, runner
from repotrust.cli import direct_app, direct_kr_app
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


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

    assert result.exit_code == 0
    assert (tmp_path / "result").exists()
    assert calls == [("https://github.com/owner/repo", None, False)]


def test_direct_cli_remote_option_enters_remote_boundary(monkeypatch):
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
        ["json", "https://github.com/owner/repo", "--remote"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert calls == [("https://github.com/owner/repo", None, True)]


def test_direct_cli_rejects_invalid_remote_option_combinations(tmp_path):
    local_remote = runner.invoke(
        direct_app,
        ["json", str(tmp_path), "--remote"],
        prog_name="repo-trust",
    )
    remote_parse_only = runner.invoke(
        direct_app,
        ["json", "https://github.com/owner/repo", "--remote", "--parse-only"],
        prog_name="repo-trust",
    )

    assert local_remote.exit_code == 2
    assert "GitHub URL" in plain_output(local_remote.stderr)
    assert remote_parse_only.exit_code == 2
    assert "--parse-only" in plain_output(remote_parse_only.stderr)


def test_direct_kr_cli_check_github_url_prints_korean_parse_only_status(monkeypatch):
    def fake_scan(target_text, weights=None, remote=False):
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
    assert "GitHub URL만 확인" in stderr
    assert "GitHub URL을 원격 조회 없이 파싱만 했습니다." in stderr
