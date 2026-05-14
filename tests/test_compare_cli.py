import json

from cli_helpers import plain_output, runner
from repotrust.cli import direct_app


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
    assert "Score: 51 -> 100 (+49)" in stdout
    assert "Resolved findings: 12" in stdout


def test_direct_cli_compare_rejects_invalid_or_removed_inputs(tmp_path):
    old_report = tmp_path / "old.json"
    new_report = tmp_path / "new.json"
    old_report.write_text(
        json.dumps(
            {
                "schema_version": "1.2",
                "score": {"total": 80, "grade": "B"},
                "assessment": {"verdict": "usable_after_review"},
                "findings": [],
            }
        ),
        encoding="utf-8",
    )
    new_report.write_text("not json", encoding="utf-8")

    invalid_report = runner.invoke(
        direct_app,
        ["compare", str(old_report), str(new_report)],
        prog_name="repo-trust",
    )
    removed_option = runner.invoke(
        direct_app,
        ["compare", str(old_report), str(old_report), "--format", "html"],
        prog_name="repo-trust",
    )

    assert invalid_report.exit_code == 1
    assert "Invalid JSON report" in plain_output(invalid_report.stderr)
    assert removed_option.exit_code == 2
    assert "No such option: --format" in plain_output(removed_option.stderr)
