from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .reports import render_report
from .scanner import scan as scan_target

app = typer.Typer(help="Evaluate repository trust signals and generate reports.")
report_console = Console()
status_console = Console(stderr=True)


@app.callback()
def main() -> None:
    """Evaluate repository trust signals and generate reports."""


@app.command()
def scan(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to scan.")],
    report_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Report format: markdown, json, or html.",
        ),
    ] = "markdown",
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write the report to this file."),
    ] = None,
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
    normalized_format = report_format.lower()
    if normalized_format not in {"markdown", "json", "html"}:
        raise typer.BadParameter("--format must be one of: markdown, json, html")

    result = scan_target(target)
    rendered = render_report(result, normalized_format)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        status_console.print(f"Wrote {normalized_format} report to [bold]{output}[/bold]")
    else:
        report_console.print(rendered, markup=False)

    _print_summary(result, verbose)

    if fail_under is not None and result.score.total < fail_under:
        raise typer.Exit(code=1)


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
