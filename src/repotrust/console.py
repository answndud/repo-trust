from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt

from .console_i18n import ConsoleLocale, ConsoleText, console_text
from .terminal_theme import badge, data_table, header, kv, muted, section


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
        str(text["select_prompt"]),
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
    console.print(header(str(text["brand_title"]).lower(), "console"))
    console.print(muted(f"{text['console_title']}  v{version}"))
    console.print(str(text["tagline"]))
    console.print(kv(str(text["mission_label"]).lower(), str(text["mission"])))
    console.print(kv(str(text["command_mode_label"]).lower(), str(text["command_mode"])))
    console.print(section(str(text["workflows_title"]).lower()))
    for line in _workflow_lines(text):
        console.print(line)
    console.print(section(str(text["recent_reports_title"]).lower()))
    for line in _recent_summary_lines(result_dir, text):
        console.print(line)


def _workflow_lines(text: ConsoleText) -> list[str]:
    lines = []
    for key, action, use_when, output in text["workflows"]:
        key_label = f"0{key}" if str(key).isdigit() else str(key)
        output_label = str(output).lower()
        lines.append(
            f"  {badge(key_label, bold=False)}  "
            f"[bold]{action}[/bold] [dim]->[/dim] {output_label:<12} "
            f"[dim]{use_when}[/dim]"
        )
    return lines


def _recent_summary_lines(result_dir: Path, text: ConsoleText) -> list[str]:
    reports = _recent_reports(result_dir, limit=3)
    if not reports:
        return [f"  {muted(text['no_saved_reports'])}"]
    return [f"  {muted(path)}" for path in reports]


def _print_recent_reports(
    *,
    console: Console,
    result_dir: Path,
    text: ConsoleText,
) -> None:
    reports = _recent_reports(result_dir, limit=10)
    console.print(section(str(text["recent_reports_title"]).lower()))
    table = data_table()
    table.add_column(str(text["number_column"]), justify="right", style="green")
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
