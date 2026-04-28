from __future__ import annotations

from enum import Enum
from pathlib import Path
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import ConfigError, RepoTrustConfig, load_config
from .reports import render_report
from .scanner import ScanInputError, scan as scan_target

app = typer.Typer(
    help="Evaluate repository trust signals and generate reports.",
    invoke_without_command=True,
)
direct_app = typer.Typer(
    help="Evaluate repository trust signals and generate reports.",
    add_completion=False,
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


@direct_app.command()
def run(
    ctx: typer.Context,
    target: Annotated[
        str | None,
        typer.Argument(help="Local path or GitHub URL to scan."),
    ] = None,
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
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Scan a repository target."""
    if version:
        typer.echo(f"repo-trust {__version__}")
        raise typer.Exit()
    if target is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()
    _run_scan(
        target=target,
        report_format=report_format,
        output=output,
        config=config,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
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
) -> None:
    normalized_format = report_format.value
    loaded_config = _load_cli_config(config)

    try:
        result = scan_target(target, weights=loaded_config.weights, remote=remote)
    except ScanInputError as exc:
        raise typer.BadParameter(str(exc), param_hint="--remote") from exc
    rendered = render_report(result, normalized_format)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        status_console.print(f"Wrote {normalized_format} report to [bold]{output}[/bold]")
    else:
        sys.stdout.write(rendered)

    _print_summary(result, verbose)

    effective_fail_under = fail_under if fail_under is not None else loaded_config.fail_under
    if effective_fail_under is not None and result.score.total < effective_fail_under:
        raise typer.Exit(code=1)


def _load_cli_config(config_path: Path | None) -> RepoTrustConfig:
    if config_path is None:
        return RepoTrustConfig()
    try:
        return load_config(config_path)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc), param_hint="--config") from exc


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
        finding_table = Table(title="Findings")
        finding_table.add_column("Severity")
        finding_table.add_column("ID")
        finding_table.add_column("Message")
        for finding in result.findings:
            finding_table.add_row(finding.severity.value, finding.id, finding.message)
        status_console.print(finding_table)
