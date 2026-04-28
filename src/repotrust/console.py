from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .console_i18n import ConsoleLocale, ConsoleText, console_text


@dataclass(frozen=True)
class ConsoleWorkflow:
    target: str
    report_format: str
    terminal_only: bool = False
    parse_only: bool = False
    verbose: bool = False
    locale: ConsoleLocale = "en"


RunWorkflow = Callable[[ConsoleWorkflow], None]


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
    text = console_text(locale)
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

    run_workflow(_prompt_workflow(choice, console=console, text=text, locale=locale))


def _print_console_home(
    *,
    console: Console,
    version: str,
    result_dir: Path,
    text: ConsoleText,
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


def _workflow_table(text: ConsoleText) -> Table:
    table = Table(title=str(text["workflows_title"]), header_style="bold cyan", show_lines=True)
    table.add_column(str(text["key_column"]), justify="center", style="cyan", no_wrap=True)
    table.add_column(str(text["action_column"]), style="bold")
    table.add_column(str(text["use_when_column"]))
    table.add_column(str(text["output_column"]))
    for row in text["workflows"]:
        table.add_row(*row)
    return table


def _recent_summary_panel(result_dir: Path, text: ConsoleText) -> Panel:
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
    text: ConsoleText,
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
    text: ConsoleText,
    locale: ConsoleLocale,
) -> ConsoleWorkflow:
    if choice == "1":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["local_path_prompt"]), default=".", console=console),
            report_format="html",
            locale=locale,
        )
    if choice == "2":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["github_url_prompt"]), console=console),
            report_format="html",
            locale=locale,
        )
    if choice == "3":
        return ConsoleWorkflow(
            target=Prompt.ask(str(text["github_url_prompt"]), console=console),
            report_format="json",
            locale=locale,
        )
    return ConsoleWorkflow(
        target=Prompt.ask(str(text["any_target_prompt"]), default=".", console=console),
        report_format="markdown",
        terminal_only=True,
        verbose=True,
        locale=locale,
    )
