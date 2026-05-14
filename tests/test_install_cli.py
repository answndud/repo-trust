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
    assert "Before you run anything:" in result.stdout
    assert "Confirm the command came from the repository README" in result.stdout
    assert "README install commands found:" in result.stdout
    assert "Do not run the README install commands yet." in result.stdout
    assert "install.risky.shell_pipe_install" in result.stdout
    assert "curl https://example.com/install.sh | sh" in result.stdout
    assert "disposable virtual machine, container, or fresh virtual environment" in result.stdout


def test_direct_cli_safe_install_suggests_python_virtualenv_for_good_fixture():
    result = runner.invoke(
        direct_app,
        ["safe-install", "tests/fixtures/repos/good-python"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "Install verdict: usable_by_current_checks" in result.stdout
    assert "Before you run anything:" in result.stdout
    assert "Treat source installs as code execution" in result.stdout
    assert "README install commands found:" in result.stdout
    assert "pip install good-python-project" in result.stdout
    assert "Isolated review/install pattern:" in result.stdout
    assert "python3 -m venv .venv" in result.stdout
    assert ".venv/bin/python -m pip install -e ." in result.stdout
    assert "Do not run the README install commands yet." not in result.stdout


def test_direct_cli_next_steps_prioritizes_risky_fixture_actions():
    result = runner.invoke(
        direct_app,
        ["next-steps", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "RepoTrust Next Steps" in result.stdout
    assert "1. Stop: do not run the README install commands yet." in result.stdout
    assert "repo-trust safe-install tests/fixtures/repos/risky-install" in result.stdout
    assert "curl https://example.com/install.sh | sh" in result.stdout
    assert result.stdout.index("1. Stop") < result.stdout.index("Review license")
    assert result.stdout.index("Review license") < result.stdout.index("Review CI")
    assert result.stdout.index("Review CI") < result.stdout.index("Review security policy")
    assert result.stdout.index("Review security policy") < result.stdout.index(
        "install.risky.global_package_install"
    )
    assert "repo-trust explain install.risky.shell_pipe_install" in result.stdout


def test_direct_cli_next_steps_has_short_good_fixture_checklist():
    result = runner.invoke(
        direct_app,
        ["next-steps", "tests/fixtures/repos/good-python"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "No blocking findings were found by the enabled checks." in result.stdout
    assert "repo-trust safe-install tests/fixtures/repos/good-python" in result.stdout
    assert "repo-trust html tests/fixtures/repos/good-python" in result.stdout


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
    assert "1. Stop: do not run the README install commands yet." in result.stdout
    assert "Review license" in result.stdout
    assert "repo-trust explain install.risky.shell_pipe_install" in result.stdout


def test_direct_kr_cli_next_steps_outputs_korean_action_plan():
    result = runner.invoke(
        direct_kr_app,
        ["next-steps", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust-kr",
    )

    assert result.exit_code == 0
    assert "RepoTrust 다음 조치" in result.stdout
    assert "1. 중단: 아직 README 설치 명령을 실행하지 마세요." in result.stdout
    assert "License 확인" in result.stdout
    assert "CI 확인" in result.stdout
    assert "보안 정책 확인" in result.stdout
    assert "repo-trust-kr explain install.risky.shell_pipe_install" in result.stdout


def test_direct_cli_safe_install_audit_includes_install_time_surface():
    result = runner.invoke(
        direct_app,
        ["safe-install", "--audit", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "RepoTrust Safe Install Advice" in result.stdout
    assert "RepoTrust Install Audit" in result.stdout
    assert "README install commands:" in result.stdout
    assert "curl https://example.com/install.sh | sh" in result.stdout
    assert "audit.install.risky.shell_pipe_install [high]" in result.stdout
    assert "audit.install.risky.python_inline_execution [high]" in result.stdout
    assert "audit.install.risky.vcs_direct_install [medium]" in result.stdout


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
    (tmp_path / "Makefile").write_text("install:\n\ttrue\n", encoding="utf-8")
    (tmp_path / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (tmp_path / "install.sh").write_text("#!/bin/sh\n", encoding="utf-8")
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
    assert result.stderr == ""
    assert "audit.install.python_build_backend [medium]" in result.stdout
    assert "audit.install.python_setup_py [medium]" in result.stdout
    assert "audit.install.npm_lifecycle_script [medium]" in result.stdout
    assert "audit.install.makefile [low]" in result.stdout
    assert "audit.install.dockerfile [low]" in result.stdout
    assert "audit.install.root_shell_script [medium]" in result.stdout
    assert "audit.install.vcs_dependency [medium]" in result.stdout


def test_direct_cli_safe_install_audit_github_url_explains_local_checkout_requirement():
    result = runner.invoke(
        direct_app,
        ["safe-install", "--audit", "https://github.com/openai/codex"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "Scope: local checkout required" in result.stdout
    assert "audit.install.local_checkout_required [info]" in result.stdout


def test_direct_cli_audit_install_command_is_removed():
    result = runner.invoke(
        direct_app,
        ["audit-install", "tests/fixtures/repos/risky-install"],
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 2
    assert "No such command" in stderr


def test_direct_cli_safe_install_audit_scans_local_subdir(tmp_path):
    package_dir = tmp_path / "packages" / "tool"
    package_dir.mkdir(parents=True)
    (package_dir / "README.md").write_text(
        "# Tool\n\n"
        "## Getting Started\n\n"
        "pip install .\n",
        encoding="utf-8",
    )
    (package_dir / "setup.py").write_text("print('setup')\n", encoding="utf-8")

    result = runner.invoke(
        direct_app,
        ["safe-install", "--audit", str(tmp_path), "--subdir", "packages/tool"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    assert "packages/tool" in result.stdout
    assert "audit.install.python_setup_py [medium]" in result.stdout


def test_direct_cli_safe_install_explains_parse_only_evidence_gap():
    result = runner.invoke(
        direct_app,
        ["safe-install", "https://github.com/openai/codex"],
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "Install verdict: insufficient_evidence" in result.stdout
    assert "Before you run anything:" in result.stdout
    assert "README install commands found:" not in result.stdout
    assert "does not have enough file evidence" in result.stdout
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
    assert "실행 전 체크리스트:" in result.stdout
    assert "README에서 발견한 설치 명령:" in result.stdout
    assert "아직 README 설치 명령을 실행하지 마세요." in result.stdout
    assert "고위험 설치 근거" in result.stdout
