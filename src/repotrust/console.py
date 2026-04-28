from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


@dataclass(frozen=True)
class ConsoleWorkflow:
    target: str
    report_format: str
    terminal_only: bool = False
    parse_only: bool = False
    verbose: bool = False


RunWorkflow = Callable[[ConsoleWorkflow], None]


def run_console_mode(
    *,
    console: Console,
    help_text: Callable[[], str],
    version: str,
    run_workflow: RunWorkflow,
    result_dir: Path = Path("result"),
) -> None:
    """Run the interactive product shell for humans."""
    _print_console_home(console=console, version=version, result_dir=result_dir)
    choice = Prompt.ask(
        "Select",
        choices=["1", "2", "3", "4", "5", "6", "q"],
        default="1",
        console=console,
    )
    if choice == "q":
        console.print("[dim]Session closed.[/dim]")
        return
    if choice == "5":
        _print_recent_reports(console=console, result_dir=result_dir)
        return
    if choice == "6":
        console.print(help_text())
        return

    run_workflow(_prompt_workflow(choice, console=console))


def _print_console_home(*, console: Console, version: str, result_dir: Path) -> None:
    console.print(
        Panel(
            "[bold cyan]RepoTrust Console[/bold cyan]\n"
            "[dim]Repository trust intelligence for dependencies, agents, and audits[/dim]\n\n"
            "[bold]Mission[/bold]\n"
            "  Decide whether a repository is safe enough to install, depend on, or hand to an AI agent.\n\n"
            "[bold]Command Mode[/bold]\n"
            "  repo-trust html <target>   repo-trust json <target>   repo-trust check <target>",
            title="REPO-TRUST",
            subtitle=f"v{version}",
            border_style="cyan",
        )
    )
    console.print(_workflow_table())
    console.print(_recent_summary_panel(result_dir))


def _workflow_table() -> Table:
    table = Table(title="Workflows", header_style="bold cyan", show_lines=True)
    table.add_column("Key", justify="center", style="cyan", no_wrap=True)
    table.add_column("Action", style="bold")
    table.add_column("Use When")
    table.add_column("Output")
    table.add_row("1", "Scan local repository", "You already have a checkout", "HTML report")
    table.add_row("2", "Scan GitHub URL", "You want a browser-readable remote report", "HTML report")
    table.add_row("3", "Export GitHub URL", "You need automation-friendly data", "JSON report")
    table.add_row("4", "Quick check", "You want a terminal assessment now", "Dashboard")
    table.add_row("5", "List recent reports", "You want to find prior scan artifacts", "File list")
    table.add_row("6", "Command reference", "You want flags and direct commands", "Help")
    table.add_row("q", "Quit", "No scan", "Exit")
    return table


def _recent_summary_panel(result_dir: Path) -> Panel:
    reports = _recent_reports(result_dir, limit=3)
    if not reports:
        body = "[dim]No saved reports yet. HTML and JSON commands write to result/ by default.[/dim]"
    else:
        body = "\n".join(f"  {path}" for path in reports)
    return Panel(body, title="Recent Reports", border_style="dim")


def _print_recent_reports(*, console: Console, result_dir: Path) -> None:
    reports = _recent_reports(result_dir, limit=10)
    table = Table(title="Recent Reports", header_style="bold cyan")
    table.add_column("No.", justify="right", style="cyan")
    table.add_column("Path")
    table.add_column("Type")
    if reports:
        for index, path in enumerate(reports, start=1):
            table.add_row(str(index), str(path), path.suffix.lstrip(".") or "report")
    else:
        table.add_row("-", "No reports found in result/", "-")
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


def _prompt_workflow(choice: str, *, console: Console) -> ConsoleWorkflow:
    if choice == "1":
        return ConsoleWorkflow(
            target=Prompt.ask("Local path", default=".", console=console),
            report_format="html",
        )
    if choice == "2":
        return ConsoleWorkflow(
            target=Prompt.ask("GitHub URL", console=console),
            report_format="html",
        )
    if choice == "3":
        return ConsoleWorkflow(
            target=Prompt.ask("GitHub URL", console=console),
            report_format="json",
        )
    return ConsoleWorkflow(
        target=Prompt.ask("Local path or GitHub URL", default=".", console=console),
        report_format="markdown",
        terminal_only=True,
        verbose=True,
    )
