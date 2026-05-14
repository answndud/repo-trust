import json

from cli_helpers import plain_output, runner
from repotrust.cli import app, direct_app
from repotrust.models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from repotrust.scoring import calculate_score


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


def test_cli_config_fail_under_and_cli_override(tmp_path):
    config = tmp_path / "repotrust.toml"
    config.write_text("[policy]\nfail_under = 100\n", encoding="utf-8")

    config_result = runner.invoke(app, ["scan", str(tmp_path), "--config", str(config)])
    override_result = runner.invoke(
        app,
        ["scan", str(tmp_path), "--config", str(config), "--fail-under", "0"],
    )

    assert config_result.exit_code == 1
    assert override_result.exit_code == 0


def test_cli_config_rejects_removed_policy_surface(tmp_path):
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
    assert "Unknown [policy] key(s): profiles" in stderr


def test_direct_cli_gate_example_policy_passes_and_fails_expected_fixtures(tmp_path):
    good_output = tmp_path / "good-gate.json"
    risky_output = tmp_path / "risky-gate.json"

    good_result = runner.invoke(
        direct_app,
        [
            "gate",
            "tests/fixtures/repos/good-python",
            "--config",
            "examples/repotrust.toml",
            "--output",
            str(good_output),
        ],
        prog_name="repo-trust",
    )
    risky_result = runner.invoke(
        direct_app,
        [
            "gate",
            "tests/fixtures/repos/risky-install",
            "--config",
            "examples/repotrust.toml",
            "--output",
            str(risky_output),
        ],
        prog_name="repo-trust",
    )

    assert good_result.exit_code == 0
    assert json.loads(good_output.read_text(encoding="utf-8"))["score"]["total"] == 100
    assert risky_result.exit_code == 1
    assert "Policy gate failed" in plain_output(risky_result.stderr)


def test_removed_init_policy_command_stays_unavailable():
    result = runner.invoke(
        direct_app,
        ["init-policy"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 2
    assert "No such command" in plain_output(result.stderr)
