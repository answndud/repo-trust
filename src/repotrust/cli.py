from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from . import __version__
from .config import ConfigError, RepoTrustConfig, load_config
from .models import ScanResult
from .reports import render_report
from .scanner import ScanInputError, scan as scan_target
from .targets import parse_target

app = typer.Typer(
    help="Evaluate repository trust signals and generate reports.",
    invoke_without_command=True,
)
direct_app = typer.Typer(
    help="Inspect repository trust signals and write clear local reports.",
    add_completion=False,
    invoke_without_command=True,
)
status_console = Console(stderr=True)


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Evaluate repository trust signals and generate reports."""
    if version:
        typer.echo(f"repotrust {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def scan(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to scan.")],
    report_format: Annotated[
        ReportFormat,
        typer.Option(
            "--format",
            "-f",
            help="Report format: markdown, json, or html.",
        ),
    ] = ReportFormat.MARKDOWN,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write the report to this file."),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    remote: Annotated[
        bool,
        typer.Option("--remote", help="Use GitHub API remote scan for GitHub URL targets."),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal summary."),
    ] = False,
) -> None:
    """Scan a repository target."""
    _run_scan(
        target=target,
        report_format=report_format,
        output=output,
        config=config,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.callback()
def product_main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Inspect repository trust signals and write clear local reports."""
    if version:
        typer.echo(f"repo-trust {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_interactive_launcher(ctx)
        raise typer.Exit()


@direct_app.command("html")
def html_report(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Custom output path. Defaults to result/<target>-YYYY-MM-DD.html.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = False,
) -> None:
    """Write an HTML trust report."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.HTML,
        output=output,
        config=config,
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.command("json")
def json_report(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Custom output path. Defaults to result/<target>-YYYY-MM-DD.json.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = False,
) -> None:
    """Write a JSON trust report."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.JSON,
        output=output,
        config=config,
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.command("check")
def check(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = True,
) -> None:
    """Inspect a target and print a terminal dashboard."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.MARKDOWN,
        output=None,
        config=config,
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
        terminal_only=True,
    )


def _run_product_scan(
    *,
    target: str,
    report_format: ReportFormat,
    output: Path | None,
    config: Path | None,
    parse_only: bool,
    fail_under: int | None,
    verbose: bool,
    terminal_only: bool = False,
) -> None:
    parsed_target = parse_target(target)
    if parse_only and parsed_target.kind != "github":
        raise typer.BadParameter(
            "--parse-only can only be used with GitHub URL targets.",
            param_hint="--parse-only",
        )

    remote = parsed_target.kind == "github" and not parse_only
    mode = _scan_mode(parsed_target.kind, remote)
    output_path = None if terminal_only else output or _default_output_path(target, report_format)

    _print_header(target=target, mode=mode, report_format=report_format)
    _run_scan(
        target=target,
        report_format=report_format,
        output=output_path,
        config=config,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
        dashboard=True,
        output_label=output_path,
    )


def _run_interactive_launcher(ctx: typer.Context) -> None:
    _print_launcher_header()
    while True:
        _print_launcher_menu()
        choice = Prompt.ask(
            "Select workflow",
            choices=["1", "2", "3", "4", "5", "q"],
            default="1",
            console=status_console,
        )
        if choice == "q":
            status_console.print("[dim]Session closed.[/dim]")
            return
        if choice == "5":
            status_console.print(ctx.get_help())
            return
        _run_launcher_choice(choice)
        return


def _print_launcher_header() -> None:
    status_console.print(
        Panel.fit(
            "[bold cyan]RepoTrust Console[/bold cyan]\n"
            "[dim]Repository trust intelligence for local paths and GitHub URLs[/dim]\n\n"
            "[bold]Fast paths[/bold]\n"
            "  repo-trust html <target>\n"
            "  repo-trust json <target>\n"
            "  repo-trust check <target>",
            title="REPO-TRUST",
            subtitle=f"v{__version__}",
            border_style="cyan",
        )
    )


def _print_launcher_menu() -> None:
    table = Table(title="Choose an operation", show_header=True, header_style="bold cyan")
    table.add_column("No.", justify="center", style="cyan", no_wrap=True)
    table.add_column("Workflow")
    table.add_column("Result")
    table.add_row("1", "Local repository scan", "HTML report in result/")
    table.add_row("2", "GitHub URL scan", "HTML report in result/")
    table.add_row("3", "GitHub URL scan", "JSON report in result/")
    table.add_row("4", "Quick terminal check", "Dashboard only")
    table.add_row("5", "Show help", "Command reference")
    table.add_row("q", "Quit", "Exit without scanning")
    status_console.print(table)


def _run_launcher_choice(choice: str) -> None:
    if choice == "1":
        target = Prompt.ask("Local path", default=".", console=status_console)
        _run_product_scan(
            target=target,
            report_format=ReportFormat.HTML,
            output=None,
            config=None,
            parse_only=False,
            fail_under=None,
            verbose=False,
        )
        return

    if choice == "2":
        target = Prompt.ask("GitHub URL", console=status_console)
        _run_product_scan(
            target=target,
            report_format=ReportFormat.HTML,
            output=None,
            config=None,
            parse_only=False,
            fail_under=None,
            verbose=False,
        )
        return

    if choice == "3":
        target = Prompt.ask("GitHub URL", console=status_console)
        _run_product_scan(
            target=target,
            report_format=ReportFormat.JSON,
            output=None,
            config=None,
            parse_only=False,
            fail_under=None,
            verbose=False,
        )
        return

    target = Prompt.ask("Local path or GitHub URL", default=".", console=status_console)
    _run_product_scan(
        target=target,
        report_format=ReportFormat.MARKDOWN,
        output=None,
        config=None,
        parse_only=False,
        fail_under=None,
        verbose=True,
        terminal_only=True,
    )


def _run_scan(
    *,
    target: str,
    report_format: ReportFormat,
    output: Path | None,
    config: Path | None,
    remote: bool,
    fail_under: int | None,
    verbose: bool,
    dashboard: bool = False,
    output_label: Path | None = None,
) -> None:
    normalized_format = report_format.value
    loaded_config = _load_cli_config(config)

    try:
        result = scan_target(target, weights=loaded_config.weights, remote=remote)
    except ScanInputError as exc:
        raise typer.BadParameter(str(exc), param_hint="--remote") from exc
    rendered = render_report(result, normalized_format)
    if output:
        output = _resolve_output_path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        status_console.print(f"Wrote {normalized_format} report to [bold]{output}[/bold]")
    else:
        if dashboard:
            status_console.print(rendered)
        else:
            sys.stdout.write(rendered)

    if dashboard:
        _print_dashboard(result, verbose, output_label=output)
    else:
        _print_summary(result, verbose)

    effective_fail_under = fail_under if fail_under is not None else loaded_config.fail_under
    if effective_fail_under is not None and result.score.total < effective_fail_under:
        raise typer.Exit(code=1)


def _resolve_output_path(output: Path, today: date | None = None) -> Path:
    if output.is_absolute() or output.parent != Path("."):
        return output
    output_date = today or date.today()
    dated_name = f"{output.stem}-{output_date.isoformat()}{output.suffix}"
    return Path("result") / dated_name


def _default_output_path(
    target: str,
    report_format: ReportFormat,
    today: date | None = None,
) -> Path:
    output_date = today or date.today()
    filename = f"{_target_slug(target)}-{output_date.isoformat()}.{_format_extension(report_format)}"
    return Path("result") / filename


def _target_slug(target: str) -> str:
    parsed_target = parse_target(target)
    if parsed_target.kind == "github" and parsed_target.repo:
        return _safe_slug(parsed_target.repo)

    path = Path(parsed_target.path or parsed_target.raw).expanduser()
    name = path.resolve().name if path.name in {"", "."} else path.name
    return _safe_slug(name or "repository")


def _safe_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "repository"


def _format_extension(report_format: ReportFormat) -> str:
    if report_format == ReportFormat.HTML:
        return "html"
    if report_format == ReportFormat.JSON:
        return "json"
    return "md"


def _scan_mode(kind: str, remote: bool) -> str:
    if kind == "github" and remote:
        return "GitHub remote"
    if kind == "github":
        return "GitHub parse-only"
    return "local"


def _load_cli_config(config_path: Path | None) -> RepoTrustConfig:
    if config_path is None:
        return RepoTrustConfig()
    try:
        return load_config(config_path)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc), param_hint="--config") from exc


def _print_header(*, target: str, mode: str, report_format: ReportFormat) -> None:
    status_console.print(
        Panel.fit(
            f"[bold cyan]RepoTrust[/bold cyan]\n"
            f"[dim]target[/dim] {target}\n"
            f"[dim]mode[/dim] {mode}  [dim]format[/dim] {report_format.value}",
            border_style="cyan",
        )
    )


def _print_dashboard(result: ScanResult, verbose: bool, output_label: Path | None) -> None:
    status_console.print(
        Panel(
            _scorecard_text(result, output_label),
            title="RepoTrust Dashboard",
            border_style=_risk_border_style(result.score.risk_label),
        )
    )
    status_console.print(_category_table(result))
    status_console.print(_evidence_table(result))

    if verbose and result.findings:
        _print_findings(result)


def _print_summary(result, verbose: bool) -> None:
    table = Table(title="RepoTrust Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Target", result.target.raw)
    table.add_row("Score", f"{result.score.total}/{result.score.max_score}")
    table.add_row("Grade", result.score.grade)
    table.add_row("Risk", result.score.risk_label)
    table.add_row("Findings", str(len(result.findings)))
    status_console.print(table)

    if verbose and result.findings:
        _print_findings(result)


def _print_findings(result: ScanResult) -> None:
    finding_table = Table(title="Findings")
    finding_table.add_column("Severity")
    finding_table.add_column("ID")
    finding_table.add_column("Message")
    for finding in result.findings:
        finding_table.add_row(finding.severity.value, finding.id, finding.message)
    status_console.print(finding_table)


def _finding_counts(result: ScanResult) -> str:
    counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in result.findings:
        counts[finding.severity.value] += 1
    return "  ".join(f"{name}:{count}" for name, count in counts.items())


def _scorecard_text(result: ScanResult, output_label: Path | None) -> str:
    output = str(output_label) if output_label is not None else "terminal only"
    return (
        f"[dim]Target[/dim] {result.target.raw}\n"
        f"[dim]Mode[/dim] {_scan_mode(result.target.kind, _is_remote_result(result))}\n\n"
        f"[bold]Score[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
        f"[bold]Grade[/bold] [bold]{result.score.grade}[/bold]  "
        f"[bold]Risk[/bold] {_risk_badge(result.score.risk_label)}\n"
        f"[bold]Findings[/bold] {_finding_counts(result)}\n"
        f"[bold]Output[/bold] {output}\n\n"
        f"[bold]Next[/bold] {_next_action(result, output_label)}"
    )


def _category_table(result: ScanResult) -> Table:
    table = Table(title="Category Scores", header_style="bold cyan")
    table.add_column("Category")
    table.add_column("Score", justify="right")
    table.add_column("Signal")
    for category, score in result.score.categories.items():
        table.add_row(category, f"{score}/100", _score_bar(score))
    return table


def _evidence_table(result: ScanResult) -> Table:
    detected = result.detected_files
    table = Table(title="Evidence Snapshot", header_style="bold cyan")
    table.add_column("Signal")
    table.add_column("Status")
    table.add_row("README", _present_value(detected.readme))
    table.add_row("LICENSE", _present_value(detected.license))
    table.add_row("SECURITY", _present_value(detected.security))
    table.add_row("CI workflows", _present_count(detected.ci_workflows))
    table.add_row("Dependency manifests", _present_count(detected.dependency_manifests))
    table.add_row("Lockfiles", _present_count(detected.lockfiles))
    table.add_row("Dependabot", _present_value(detected.dependabot))
    return table


def _score_bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    empty = 10 - filled
    style = "green" if score >= 90 else "yellow" if score >= 70 else "red"
    return f"[{style}]{'█' * filled}{'░' * empty}[/{style}]"


def _present_value(value: str | None) -> str:
    if value:
        return f"[green]found[/green] [dim]{value}[/dim]"
    return "[red]missing[/red]"


def _present_count(values: list[str]) -> str:
    if values:
        return f"[green]{len(values)} found[/green] [dim]{', '.join(values[:3])}[/dim]"
    return "[red]missing[/red]"


def _risk_badge(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        style = "red"
    elif "moderate" in normalized:
        style = "yellow"
    else:
        style = "green"
    return f"[bold {style}]{risk_label.upper()}[/bold {style}]"


def _risk_border_style(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "red"
    if "moderate" in normalized:
        return "yellow"
    return "green"


def _next_action(result: ScanResult, output_label: Path | None) -> str:
    if output_label is not None:
        return "Open the report and review high or medium findings before installing."
    if result.findings:
        return "Review the findings above before installing or delegating this repository."
    return "No findings detected by the current rule set."


def _is_remote_result(result: ScanResult) -> bool:
    return any(finding.id.startswith("remote.") for finding in result.findings)
