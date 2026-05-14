import json

from cli_helpers import plain_output, runner
from repotrust.cli import app, direct_app
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


def test_direct_cli_init_policy_command_is_removed():
    result = runner.invoke(
        direct_app,
        ["init-policy"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "No such command" in stderr


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
