from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

ConsoleLocale = str


@dataclass(frozen=True)
class ConsoleWorkflow:
    target: str
    report_format: str
    terminal_only: bool = False
    parse_only: bool = False
    verbose: bool = False


RunWorkflow = Callable[[ConsoleWorkflow], None]


CONSOLE_TEXT = {
    "en": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust Console",
        "tagline": "Repository trust intelligence for dependencies, agents, and audits",
        "mission_label": "Mission",
        "mission": (
            "Decide whether a repository is safe enough to install, depend on, "
            "or hand to an AI agent."
        ),
        "command_mode_label": "Command Mode",
        "command_mode": (
            "repo-trust html <target>   repo-trust json <target>   repo-trust check <target>"
        ),
        "workflows_title": "Workflows",
        "key_column": "Key",
        "action_column": "Action",
        "use_when_column": "Use When",
        "output_column": "Output",
        "workflows": [
            ("1", "Scan local repository", "You already have a checkout", "HTML report"),
            ("2", "Scan GitHub URL", "You want a browser-readable remote report", "HTML report"),
            ("3", "Export GitHub URL", "You need automation-friendly data", "JSON report"),
            ("4", "Quick check", "You want a terminal assessment now", "Dashboard"),
            ("5", "List recent reports", "You want to find prior scan artifacts", "File list"),
            ("6", "Command reference", "You want flags and direct commands", "Help"),
            ("q", "Quit", "No scan", "Exit"),
        ],
        "recent_reports_title": "Recent Reports",
        "no_saved_reports": (
            "No saved reports yet. HTML and JSON commands write to result/ by default."
        ),
        "no_reports_found": "No reports found in result/",
        "number_column": "No.",
        "path_column": "Path",
        "type_column": "Type",
        "select_prompt": "Select",
        "session_closed": "Session closed.",
        "local_path_prompt": "Local path",
        "github_url_prompt": "GitHub URL",
        "any_target_prompt": "Local path or GitHub URL",
    },
    "ko": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust 한국어 콘솔",
        "tagline": "dependency, agent, audit를 위한 저장소 신뢰도 점검 도구",
        "mission_label": "목적",
        "mission": (
            "저장소를 설치하거나 의존성으로 추가하거나 AI agent에게 맡겨도 되는지 "
            "확인 가능한 근거로 판단합니다."
        ),
        "command_mode_label": "명령 모드",
        "command_mode": (
            "repo-trust html <대상>   repo-trust json <대상>   repo-trust check <대상>"
        ),
        "workflows_title": "워크플로우",
        "key_column": "번호",
        "action_column": "작업",
        "use_when_column": "언제 쓰나",
        "output_column": "결과",
        "workflows": [
            ("1", "로컬 저장소 검사", "이미 clone한 폴더가 있을 때", "HTML 리포트"),
            ("2", "GitHub URL 검사", "브라우저용 원격 리포트가 필요할 때", "HTML 리포트"),
            ("3", "GitHub URL 내보내기", "자동화용 데이터가 필요할 때", "JSON 리포트"),
            ("4", "빠른 점검", "터미널에서 바로 판단할 때", "대시보드"),
            ("5", "최근 리포트 목록", "이전 결과 파일을 찾을 때", "파일 목록"),
            ("6", "명령어 도움말", "직접 명령과 옵션을 확인할 때", "도움말"),
            ("q", "종료", "검사하지 않음", "종료"),
        ],
        "recent_reports_title": "최근 리포트",
        "no_saved_reports": (
            "아직 저장된 리포트가 없습니다. HTML/JSON 명령은 기본적으로 result/에 저장됩니다."
        ),
        "no_reports_found": "result/에서 리포트를 찾지 못했습니다.",
        "number_column": "번호",
        "path_column": "경로",
        "type_column": "형식",
        "select_prompt": "선택",
        "session_closed": "세션을 종료했습니다.",
        "local_path_prompt": "로컬 경로",
        "github_url_prompt": "GitHub URL",
        "any_target_prompt": "로컬 경로 또는 GitHub URL",
    },
}


def run_console_mode(
    *,
    console: Console,
    help_text: Callable[[], str],
    version: str,
    run_workflow: RunWorkflow,
    result_dir: Path = Path("result"),
    locale: ConsoleLocale = "en",
) -> None:
    """Run the interactive product shell for humans."""
    text = _console_text(locale)
    _print_console_home(console=console, version=version, result_dir=result_dir, text=text)
    choice = Prompt.ask(
        text["select_prompt"],
        choices=["1", "2", "3", "4", "5", "6", "q"],
        default="1",
        console=console,
    )
    if choice == "q":
        console.print(f"[dim]{text['session_closed']}[/dim]")
        return
    if choice == "5":
        _print_recent_reports(console=console, result_dir=result_dir, text=text)
        return
    if choice == "6":
        console.print(help_text())
        return

    run_workflow(_prompt_workflow(choice, console=console, text=text))


def _console_text(locale: ConsoleLocale) -> dict[str, object]:
    return CONSOLE_TEXT.get(locale, CONSOLE_TEXT["en"])


def _print_console_home(
    *,
    console: Console,
    version: str,
    result_dir: Path,
    text: dict[str, object],
) -> None:
    console.print(
        Panel(
            f"[bold cyan]{text['console_title']}[/bold cyan]\n"
            f"[dim]{text['tagline']}[/dim]\n\n"
            f"[bold]{text['mission_label']}[/bold]\n"
            f"  {text['mission']}\n\n"
            f"[bold]{text['command_mode_label']}[/bold]\n"
            f"  {text['command_mode']}",
            title=str(text["brand_title"]),
            subtitle=f"v{version}",
            border_style="cyan",
        )
    )
    console.print(_workflow_table(text))
    console.print(_recent_summary_panel(result_dir, text))


def _workflow_table(text: dict[str, object]) -> Table:
    table = Table(title=str(text["workflows_title"]), header_style="bold cyan", show_lines=True)
    table.add_column(str(text["key_column"]), justify="center", style="cyan", no_wrap=True)
    table.add_column(str(text["action_column"]), style="bold")
    table.add_column(str(text["use_when_column"]))
    table.add_column(str(text["output_column"]))
    for row in text["workflows"]:
        table.add_row(*row)
    return table


def _recent_summary_panel(result_dir: Path, text: dict[str, object]) -> Panel:
    reports = _recent_reports(result_dir, limit=3)
    if not reports:
        body = f"[dim]{text['no_saved_reports']}[/dim]"
    else:
        body = "\n".join(f"  {path}" for path in reports)
    return Panel(body, title=str(text["recent_reports_title"]), border_style="dim")


def _print_recent_reports(
    *,
    console: Console,
    result_dir: Path,
    text: dict[str, object],
) -> None:
    reports = _recent_reports(result_dir, limit=10)
    table = Table(title=str(text["recent_reports_title"]), header_style="bold cyan")
    table.add_column(str(text["number_column"]), justify="right", style="cyan")
    table.add_column(str(text["path_column"]))
    table.add_column(str(text["type_column"]))
    if reports:
        for index, path in enumerate(reports, start=1):
            table.add_row(str(index), str(path), path.suffix.lstrip(".") or "report")
    else:
        table.add_row("-", str(text["no_reports_found"]), "-")
    console.print(table)


def _recent_reports(result_dir: Path, limit: int) -> list[Path]:
    if not result_dir.exists():
        return []
    reports = [
        path
        for path in result_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".html", ".json", ".md"}
    ]
    reports.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return reports[:limit]


def _prompt_workflow(
    choice: str,
    *,
    console: Console,
    text: dict[str, object],
) -> ConsoleWorkflow:
    if choice == "1":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["local_path_prompt"]), default=".", console=console),
            report_format="html",
        )
    if choice == "2":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["github_url_prompt"]), console=console),
            report_format="html",
        )
    if choice == "3":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["github_url_prompt"]), console=console),
            report_format="json",
        )
    return ConsoleWorkflow(
        target=Prompt.ask(str(text["any_target_prompt"]), default=".", console=console),
        report_format="markdown",
        terminal_only=True,
        verbose=True,
    )
