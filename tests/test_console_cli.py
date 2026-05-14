from cli_helpers import plain_output, runner
from repotrust.cli import direct_app
from repotrust.console import run_console_mode


def test_console_mode_does_not_use_alternate_screen_for_real_terminals():
    events = []

    class FakeConsole:
        is_terminal = True

        def screen(self, hide_cursor=False):
            raise AssertionError("Console Mode should not use alternate screen")

        def print(self, *args, **kwargs):
            events.append("print")

        def input(self, *args, **kwargs):
            events.append(f"input:{args[0] if args else ''}")
            return "q"

    run_console_mode(
        console=FakeConsole(),
        help_text=lambda: "help",
        version="0.2.10",
        run_workflow=lambda workflow: None,
    )

    assert len([event for event in events if event.startswith("input:")]) == 1


def test_direct_cli_root_starts_interactive_launcher():
    result = runner.invoke(direct_app, [], input="q\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust v0.2.10" in stderr
    assert "작업 선택:" in stderr
    assert "[L]  로컬 저장소" in stderr
    assert "[S]  안전 설치" in stderr
    assert "[?] 도움말   [Q] 종료" in stderr
    assert "세션을 종료했습니다." in stderr


def test_direct_cli_interactive_back_returns_to_home_without_scan():
    result = runner.invoke(direct_app, [], input="l\nb\nq\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "작업 선택으로 돌아갑니다." in stderr
    assert stderr.count("작업 선택:") == 2
    assert "분석 중..." not in stderr
