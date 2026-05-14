from cli_helpers import plain_output, runner
from repotrust.cli import direct_app, direct_kr_app


def test_direct_cli_safe_install_blocks_risky_readme_commands():
    result = runner.invoke(
        direct_app,
        ["safe-install", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "RepoTrust Safe Install Advice" in result.stdout
    assert "Do not run the README install commands yet." in result.stdout
    assert "install.risky.shell_pipe_install" in result.stdout
    assert "curl https://example.com/install.sh | sh" in result.stdout


def test_direct_cli_safe_install_suggests_isolated_install_for_good_fixture():
    result = runner.invoke(
        direct_app,
        ["safe-install", "tests/fixtures/repos/good-python"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "Install verdict: usable_by_current_checks" in result.stdout
    assert "pip install good-python-project" in result.stdout
    assert "python3 -m venv .venv" in result.stdout
    assert "Do not run the README install commands yet." not in result.stdout


def test_direct_cli_next_steps_reads_saved_json_without_rescanning(tmp_path, monkeypatch):
    report = tmp_path / "risky.json"
    json_result = runner.invoke(
        direct_app,
        ["json", "tests/fixtures/repos/risky-install", "--output", str(report)],
        prog_name="repo-trust",
    )
    assert json_result.exit_code == 0

    def fail_scan(*args, **kwargs):
        raise AssertionError("next-steps --from-json should not rescan")

    monkeypatch.setattr("repotrust.cli.scan_target", fail_scan)

    result = runner.invoke(
        direct_app,
        ["next-steps", "--from-json", str(report)],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "RepoTrust Next Steps" in result.stdout
    assert "repo-trust explain install.risky.shell_pipe_install" in result.stdout


def test_direct_cli_safe_install_audit_reports_install_time_files(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Project\n\n"
        "Project explains enough about install behavior for users and agents.\n\n"
        "## Getting Started\n\n"
        "pip install .\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        "[build-system]\nbuild-backend = \"setuptools.build_meta\"\n",
        encoding="utf-8",
    )
    (tmp_path / "setup.py").write_text("print('setup')\n", encoding="utf-8")
    (tmp_path / "package.json").write_text(
        '{"scripts": {"postinstall": "node install.js"}}',
        encoding="utf-8",
    )
    (tmp_path / "requirements.txt").write_text(
        "example @ git+https://github.com/example/project.git\n",
        encoding="utf-8",
    )

    result = runner.invoke(
        direct_app,
        ["safe-install", "--audit", str(tmp_path)],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "audit.install.python_build_backend [medium]" in result.stdout
    assert "audit.install.python_setup_py [medium]" in result.stdout
    assert "audit.install.npm_lifecycle_script [medium]" in result.stdout
    assert "audit.install.vcs_dependency [medium]" in result.stdout


def test_direct_cli_safe_install_parse_only_github_url_explains_evidence_gap():
    result = runner.invoke(
        direct_app,
        ["safe-install", "https://github.com/openai/codex"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "Install verdict: insufficient_evidence" in result.stdout
    assert "Scan a local checkout" in result.stdout
    assert "--remote" in result.stdout


def test_direct_kr_cli_safe_install_outputs_korean_advice():
    result = runner.invoke(
        direct_kr_app,
        ["safe-install", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust-kr",
    )

    assert result.exit_code == 0
    assert "RepoTrust 안전 설치 안내" in result.stdout
    assert "아직 README 설치 명령을 실행하지 마세요." in result.stdout


def test_removed_audit_install_command_stays_unavailable():
    result = runner.invoke(
        direct_app,
        ["audit-install", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 2
    assert "No such command" in plain_output(result.stderr)
