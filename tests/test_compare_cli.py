import json

from cli_helpers import plain_output, runner
from repotrust.cli import direct_app, direct_kr_app


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


def test_direct_cli_compare_rejects_removed_export_options(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
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
        ],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "No such option: --format" in stderr


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
