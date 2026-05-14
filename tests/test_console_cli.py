from cli_helpers import plain_output, runner
from repotrust.cli import direct_app, direct_kr_app
from repotrust.console import run_console_mode
from repotrust.models import DetectedFiles, ScanResult, Target
from repotrust.scoring import calculate_score


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


def test_console_mode_help_returns_without_close_prompt_for_real_terminals():
    events = []
    inputs = iter(["?"])

    class FakeConsole:
        is_terminal = True

        def screen(self, hide_cursor=False):
            raise AssertionError("Console Mode should not use alternate screen")

        def print(self, *args, **kwargs):
            events.append("print")

        def input(self, *args, **kwargs):
            events.append(f"input:{args[0] if args else ''}")
            return next(inputs)

    run_console_mode(
        console=FakeConsole(),
        help_text=lambda: "help",
        version="0.2.10",
        run_workflow=lambda workflow: None,
    )

    input_events = [event for event in events if event.startswith("input:")]
    assert len(input_events) == 1


def test_direct_cli_root_starts_interactive_launcher():
    result = runner.invoke(direct_app, [], input="q\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust v0.2.10" in stderr
    assert "설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다." in stderr
    assert "처음이면: [L] 로컬 검사 -> [S] 안전 설치 -> [J] JSON 저장." in stderr
    assert "작업 선택:" in stderr
    assert "[G]  GitHub 저장소" in stderr
    assert "기본은 API 없이 URL 확인" in stderr
    assert "[L]  로컬 저장소" in stderr
    assert "파일 근거까지 로컬 검사" in stderr
    assert "[C]  빠른 점검" in stderr
    assert "[J]  JSON 내보내기" in stderr
    assert "[S]  안전 설치" in stderr
    assert "설치 전 다음 단계 안내" in stderr
    assert "[N]  다음 조치" in stderr
    assert "검사 후 우선순위별 행동 계획" in stderr
    assert "[T]  Tutorial" not in stderr
    assert "[T]  튜토리얼" not in stderr
    assert "[P]  Samples" not in stderr
    assert "[P]  샘플" not in stderr
    assert "[M]  Compare JSON" not in stderr
    assert "[M]  JSON 비교" not in stderr
    assert "Create before/after HTML report" not in stderr
    assert "개선 전/후 HTML 만들기" not in stderr
    assert "Recent:" not in stderr
    assert "최근 리포트:" not in stderr
    assert "[?] 도움말   [Q] 종료" in stderr
    assert "→ 키를 누르세요" in stderr
    assert "+-- select workflow" not in stderr
    assert "repotrust㉿local" not in stderr
    assert "세션을 종료했습니다." in stderr
    assert "Scan local repository" not in stderr


def test_direct_kr_cli_root_starts_korean_interactive_launcher():
    result = runner.invoke(direct_kr_app, [], input="q\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert result.stdout == ""
    assert "RepoTrust v0.2.10" in stderr
    assert "설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다." in stderr
    assert "처음이면: [L] 로컬 검사 -> [S] 안전 설치 -> [J] JSON 저장." in stderr
    assert "작업 선택:" in stderr
    assert "[G]  GitHub 저장소" in stderr
    assert "기본은 API 없이 URL 확인" in stderr
    assert "[L]  로컬 저장소" in stderr
    assert "파일 근거까지 로컬 검사" in stderr
    assert "[C]  빠른 점검" in stderr
    assert "[J]  JSON 내보내기" in stderr
    assert "[S]  안전 설치" in stderr
    assert "설치 전 다음 단계 안내" in stderr
    assert "[N]  다음 조치" in stderr
    assert "검사 후 우선순위별 행동 계획" in stderr
    assert "[T]  튜토리얼" not in stderr
    assert "[P]  샘플" not in stderr
    assert "[M]  JSON 비교" not in stderr
    assert "개선 전/후 HTML 만들기" not in stderr
    assert "최근 리포트:" not in stderr
    assert "[?] 도움말   [Q] 종료" in stderr
    assert "→ 키를 누르세요" in stderr
    assert "+-- 워크플로우 선택" not in stderr
    assert "repotrust㉿local" not in stderr
    assert "세션을 종료했습니다." in stderr
    assert "Scan local repository" not in stderr


def test_direct_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_app, [], input="01\n.\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: 로컬 저장소" in stderr
    assert "로컬 저장소 경로 입력:" in stderr
    assert "[B] 뒤로" in stderr
    assert "분석 중..." in stderr
    assert "RESULT:" in result.stderr
    assert "이유" in result.stderr
    assert "다음 행동" in result.stderr
    assert "전체 리포트 열기:" in result.stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_github_shortcut_shows_input_and_processing(monkeypatch, tmp_path):
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
        direct_app,
        [],
        input="g\nhttps://github.com/owner/repo\n",
        prog_name="repo-trust",
    )

    assert result.exit_code == 0
    assert "선택됨: GitHub 저장소" in result.stderr
    assert "GitHub URL 입력:" in result.stderr
    assert "예: https://github.com/openai/openai-python" in result.stderr
    assert "[B] 뒤로" in result.stderr
    assert "분석 중..." in result.stderr
    assert "RESULT:" in result.stderr
    assert "전체 리포트 열기:" in result.stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_json_export_uses_generic_target_prompt(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_app, [], input="j\n.\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: JSON 내보내기" in stderr
    assert "검사할 대상 입력:" in stderr
    assert "GitHub URL 입력:" not in stderr
    assert "예: https://github.com/openai/openai-python" not in stderr
    assert "분석 중..." in stderr
    assert "전체 리포트 열기:" in stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_safe_install_workflow():
    result = runner.invoke(
        direct_app,
        [],
        input="s\ntests/fixtures/repos/risky-install\n",
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: 안전 설치 안내" in stderr
    assert "검사할 대상 입력:" in stderr
    assert "분석 중..." in stderr
    assert "RepoTrust 안전 설치 안내" in stderr
    assert "실행 전 체크리스트:" in stderr
    assert "아직 README 설치 명령을 실행하지 마세요." in stderr
    assert "고위험 설치 근거" in stderr


def test_direct_cli_interactive_next_steps_workflow():
    result = runner.invoke(
        direct_app,
        [],
        input="n\ntests/fixtures/repos/risky-install\n",
        prog_name="repo-trust",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: 다음 조치 계획" in stderr
    assert "RepoTrust 다음 조치" in stderr
    assert "1. 중단: 아직 README 설치 명령을 실행하지 마세요." in stderr
    assert "repo-trust-kr explain install.risky.shell_pipe_install" in stderr


def test_direct_kr_cli_interactive_safe_install_workflow():
    result = runner.invoke(
        direct_kr_app,
        [],
        input="s\ntests/fixtures/repos/risky-install\n",
        prog_name="repo-trust-kr",
    )
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: 안전 설치 안내" in stderr
    assert "검사할 대상 입력:" in stderr
    assert "분석 중..." in stderr
    assert "RepoTrust 안전 설치 안내" in stderr
    assert "실행 전 체크리스트:" in stderr
    assert "아직 README 설치 명령을 실행하지 마세요." in stderr
    assert "고위험 설치 근거" in stderr


def test_direct_kr_cli_interactive_local_html_workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(direct_kr_app, [], input="01\n.\n", prog_name="repo-trust-kr")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "로컬 저장소 경로 입력:" in stderr
    assert "선택됨: 로컬 저장소" in result.stderr
    assert "분석 중..." in result.stderr
    assert "RESULT:" in result.stderr
    assert "이유" in result.stderr
    assert "다음 행동" in result.stderr
    assert "전체 리포트 열기:" in result.stderr
    assert (tmp_path / "result").exists()


def test_direct_cli_interactive_back_returns_to_home_without_scan():
    result = runner.invoke(direct_app, [], input="l\nb\nq\n", prog_name="repo-trust")
    stderr = plain_output(result.stderr)

    assert result.exit_code == 0
    assert "선택됨: 로컬 저장소" in stderr
    assert "[B] 뒤로" in stderr
    assert "작업 선택으로 돌아갑니다." in stderr
    assert stderr.count("작업 선택:") == 2
    assert "분석 중..." not in stderr
