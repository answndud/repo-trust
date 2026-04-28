from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .evidence import EvidenceRow, evidence_rows
from .models import Finding, ScanResult


def print_command_header(
    *,
    console: Console,
    target: str,
    mode: str,
    report_format: str,
) -> None:
    console.print(
        Panel(
            f"[bold cyan]RepoTrust[/bold cyan]\n"
            f"[dim]target[/dim] {target}\n"
            f"[dim]mode[/dim] {mode}  [dim]format[/dim] {report_format}",
            title="COMMAND MODE",
            border_style="cyan",
        )
    )


def print_assessment_dashboard(
    *,
    console: Console,
    result: ScanResult,
    mode: str,
    verbose: bool,
    output_label: Path | None,
) -> None:
    console.print(
        Panel(
            _assessment_text(result=result, mode=mode, output_label=output_label),
            title="Trust Assessment",
            border_style=_risk_border_style(result.score.risk_label),
        )
    )
    console.print(_risk_breakdown_table(result))
    console.print(_evidence_table(result))
    console.print(_top_findings_table(result))
    console.print(
        Panel(
            _next_actions_text(result, output_label),
            title="Next Actions",
            border_style="cyan",
        )
    )

    if verbose and result.findings:
        print_findings(console=console, result=result)


def print_legacy_summary(*, console: Console, result: ScanResult, verbose: bool) -> None:
    table = Table(title="RepoTrust Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Target", result.target.raw)
    table.add_row("Score", f"{result.score.total}/{result.score.max_score}")
    table.add_row("Grade", result.score.grade)
    table.add_row("Risk", result.score.risk_label)
    table.add_row("Findings", str(len(result.findings)))
    console.print(table)

    if verbose and result.findings:
        print_findings(console=console, result=result)


def print_findings(*, console: Console, result: ScanResult) -> None:
    finding_table = Table(title="Findings")
    finding_table.add_column("Severity")
    finding_table.add_column("ID")
    finding_table.add_column("Message")
    for finding in result.findings:
        finding_table.add_row(finding.severity.value, finding.id, finding.message)
    console.print(finding_table)


def _assessment_text(
    *,
    result: ScanResult,
    mode: str,
    output_label: Path | None,
) -> str:
    output = str(output_label) if output_label is not None else "terminal only"
    assessment = result.assessment
    return (
        f"[bold]Verdict[/bold] {_verdict(result)}  [dim]{assessment.verdict}[/dim]\n"
        f"[bold]Confidence[/bold] {_confidence_badge(assessment.confidence)}  "
        f"[bold]Coverage[/bold] {_coverage_badge(assessment.coverage)}\n"
        f"[bold]Score[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
        f"[bold]Grade[/bold] [bold]{result.score.grade}[/bold]  "
        f"[bold]Risk[/bold] {_risk_badge(result.score.risk_label)}\n"
        f"[bold]Findings[/bold] {_finding_counts(result)}\n\n"
        f"{assessment.summary}\n\n"
        f"[dim]Target[/dim] {result.target.raw}\n"
        f"[dim]Mode[/dim] {mode}\n"
        f"[dim]Output[/dim] {output}"
    )


def _risk_breakdown_table(result: ScanResult) -> Table:
    table = Table(title="Risk Breakdown", header_style="bold cyan")
    table.add_column("Area")
    table.add_column("Score", justify="right")
    table.add_column("Signal")
    table.add_column("Read")
    for category, score in result.score.categories.items():
        table.add_row(category, f"{score}/100", _score_bar(score), _score_label(score))
    return table


def _evidence_table(result: ScanResult) -> Table:
    table = Table(title="Evidence", header_style="bold cyan")
    table.add_column("Signal")
    table.add_column("Status")
    table.add_column("Evidence")
    for row in evidence_rows(result):
        table.add_row(row.label, _status_text(row), row.value)
    return table


def _top_findings_table(result: ScanResult) -> Table:
    table = Table(title="Top Findings", header_style="bold cyan")
    table.add_column("Severity")
    table.add_column("ID")
    table.add_column("Recommendation")
    findings = sorted(result.findings, key=_finding_sort_key)[:5]
    if not findings:
        table.add_row("-", "No findings", "No action required by the current rule set.")
        return table
    for finding in findings:
        table.add_row(finding.severity.value.upper(), finding.id, finding.recommendation)
    return table


def _next_actions_text(result: ScanResult, output_label: Path | None) -> str:
    actions = list(result.assessment.next_actions)
    if output_label is not None:
        actions.append(f"Open {output_label} for the full evidence trail.")
    else:
        actions.append("Save an HTML report when you need a shareable review artifact.")
    return "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))


def _finding_sort_key(finding: Finding) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return severity_rank.get(finding.severity.value, 9), finding.id


def _finding_counts(result: ScanResult) -> str:
    counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in result.findings:
        counts[finding.severity.value] += 1
    return "  ".join(f"{name}:{count}" for name, count in counts.items())


def _score_bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    empty = 10 - filled
    style = "green" if score >= 90 else "yellow" if score >= 70 else "red"
    return f"[{style}]{'█' * filled}{'░' * empty}[/{style}]"


def _score_label(score: int) -> str:
    if score >= 90:
        return "clean"
    if score >= 70:
        return "review"
    return "attention"


def _risk_badge(risk_label: str) -> str:
    style = _risk_border_style(risk_label)
    return f"[bold {style}]{risk_label.upper()}[/bold {style}]"


def _risk_border_style(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "red"
    if "moderate" in normalized:
        return "yellow"
    return "green"


def _verdict(result: ScanResult) -> str:
    verdict = result.assessment.verdict
    if verdict == "do_not_install_before_review":
        return "[bold red]do not install before review[/bold red]"
    if verdict == "insufficient_evidence":
        return "[bold yellow]insufficient evidence[/bold yellow]"
    if verdict == "usable_after_review":
        return "[bold yellow]usable after review[/bold yellow]"
    return "[bold green]usable by current checks[/bold green]"


def _confidence_badge(confidence: str) -> str:
    style = "green" if confidence == "high" else "yellow" if confidence == "medium" else "red"
    return f"[bold {style}]{confidence.upper()}[/bold {style}]"


def _coverage_badge(coverage: str) -> str:
    style = "green" if coverage == "full" else "yellow" if coverage == "partial" else "red"
    return f"[bold {style}]{coverage.upper()}[/bold {style}]"


def _status_text(row: EvidenceRow) -> str:
    if row.status == "found":
        return "[green]found[/green]"
    if row.status == "unknown":
        return "[yellow]unknown[/yellow]"
    return "[red]missing[/red]"
