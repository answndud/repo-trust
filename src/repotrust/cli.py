from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
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
        typer.echo(ctx.get_help())
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
    table = Table(title="RepoTrust Dashboard", show_header=False)
    table.add_column("Metric", style="dim")
    table.add_column("Value")
    table.add_row("Target", result.target.raw)
    table.add_row("Mode", _scan_mode(result.target.kind, _is_remote_result(result)))
    table.add_row("Score", f"{result.score.total}/{result.score.max_score}")
    table.add_row("Grade", result.score.grade)
    table.add_row("Risk", _risk_badge(result.score.risk_label))
    table.add_row("Findings", _finding_counts(result))
    if output_label is not None:
        table.add_row("Output", str(output_label))
    table.add_row("Next", _next_action(result, output_label))
    status_console.print(table)

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


def _risk_badge(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        style = "red"
    elif "moderate" in normalized:
        style = "yellow"
    else:
        style = "green"
    return f"[bold {style}]{risk_label.upper()}[/bold {style}]"


def _next_action(result: ScanResult, output_label: Path | None) -> str:
    if output_label is not None:
        return "Open the report and review high or medium findings before installing."
    if result.findings:
        return "Review the findings above before installing or delegating this repository."
    return "No findings detected by the current rule set."


def _is_remote_result(result: ScanResult) -> bool:
    return any(finding.id.startswith("remote.") for finding in result.findings)
