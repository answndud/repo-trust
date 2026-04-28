from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .dashboard_i18n import (
    beginner_summary,
    category_label,
    confidence_label,
    coverage_label,
    evidence_label,
    format_label,
    localized_actions,
    message_text,
    mode_label,
    recommendation_text,
    risk_label as localized_risk_label,
    severity_label,
    status_text,
    text,
)
from .evidence import evidence_rows
from .models import Finding, ScanResult


def print_command_header(
    *,
    console: Console,
    target: str,
    mode: str,
    report_format: str,
    locale: str = "en",
) -> None:
    if locale == "ko":
        console.print(
            Panel(
                f"[bold cyan]RepoTrust 한국어 모드[/bold cyan]\n"
                f"[dim]검사 대상[/dim] {target}\n"
                f"[dim]검사 방식[/dim] {mode_label(mode, locale)}  "
                f"[dim]리포트 형식[/dim] {format_label(report_format, locale)}",
                title="명령 모드",
                border_style="cyan",
            )
        )
        return
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
    locale: str = "en",
) -> None:
    console.print(
        Panel(
            _assessment_text(
                result=result,
                mode=mode,
                output_label=output_label,
                locale=locale,
            ),
            title=text("assessment_title", locale),
            border_style=_risk_border_style(result.score.risk_label),
        )
    )
    console.print(_risk_breakdown_table(result, locale=locale))
    console.print(_evidence_table(result, locale=locale))
    console.print(_top_findings_table(result, locale=locale))
    console.print(
        Panel(
            _next_actions_text(result, output_label, locale=locale),
            title=text("next_actions_title", locale),
            border_style="cyan",
        )
    )

    if verbose and result.findings:
        print_findings(console=console, result=result, locale=locale)


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


def print_findings(*, console: Console, result: ScanResult, locale: str = "en") -> None:
    finding_table = Table(title=text("findings_title", locale))
    finding_table.add_column(text("severity_column", locale))
    finding_table.add_column("ID")
    finding_table.add_column(text("message_column", locale))
    for finding in result.findings:
        finding_table.add_row(
            severity_label(finding.severity.value, locale),
            finding.id,
            message_text(finding.message, locale),
        )
    console.print(finding_table)


def _assessment_text(
    *,
    result: ScanResult,
    mode: str,
    output_label: Path | None,
    locale: str,
) -> str:
    output = str(output_label) if output_label is not None else text("terminal_only", locale)
    assessment = result.assessment
    if locale == "ko":
        return (
            f"[bold]결론[/bold] {_verdict(result, locale)}\n"
            f"[bold]확실도[/bold] {_confidence_badge(assessment.confidence, locale)}  "
            f"[bold]검사 범위[/bold] {_coverage_badge(assessment.coverage, locale)}\n"
            f"[bold]점수[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
            f"[bold]등급[/bold] [bold]{result.score.grade}[/bold]  "
            f"[bold]위험도[/bold] {_risk_badge(result.score.risk_label, locale)}\n"
            f"[bold]발견 항목[/bold] {_finding_counts(result, locale)}\n\n"
            f"{beginner_summary(result)}\n\n"
            f"[dim]검사 대상[/dim] {result.target.raw}\n"
            f"[dim]검사 방식[/dim] {mode_label(mode, locale)}\n"
            f"[dim]결과 파일[/dim] {output}"
        )
    return (
        f"[bold]Verdict[/bold] {_verdict(result, locale)}  [dim]{assessment.verdict}[/dim]\n"
        f"[bold]Confidence[/bold] {_confidence_badge(assessment.confidence, locale)}  "
        f"[bold]Coverage[/bold] {_coverage_badge(assessment.coverage, locale)}\n"
        f"[bold]Score[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
        f"[bold]Grade[/bold] [bold]{result.score.grade}[/bold]  "
        f"[bold]Risk[/bold] {_risk_badge(result.score.risk_label, locale)}\n"
        f"[bold]Findings[/bold] {_finding_counts(result, locale)}\n\n"
        f"{assessment.summary}\n\n"
        f"[dim]Target[/dim] {result.target.raw}\n"
        f"[dim]Mode[/dim] {mode}\n"
        f"[dim]Output[/dim] {output}"
    )


def _risk_breakdown_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=text("risk_breakdown_title", locale), header_style="bold cyan")
    table.add_column(text("area_column", locale))
    table.add_column(text("score_column", locale), justify="right")
    table.add_column(text("signal_column", locale))
    table.add_column(text("read_column", locale))
    for category, score in result.score.categories.items():
        table.add_row(
            category_label(category, locale),
            f"{score}/100",
            _score_bar(score),
            _score_label(score, locale),
        )
    return table


def _evidence_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=text("evidence_title", locale), header_style="bold cyan")
    table.add_column(text("signal_column", locale))
    table.add_column(text("status_column", locale))
    table.add_column(text("evidence_column", locale))
    for row in evidence_rows(result):
        table.add_row(evidence_label(row.label, locale), status_text(row, locale), row.value)
    return table


def _top_findings_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=text("top_findings_title", locale), header_style="bold cyan")
    table.add_column(text("severity_column", locale))
    table.add_column("ID")
    table.add_column(text("recommendation_column", locale))
    findings = sorted(result.findings, key=_finding_sort_key)[:5]
    if not findings:
        table.add_row("-", text("no_findings", locale), text("no_action_required", locale))
        return table
    for finding in findings:
        table.add_row(
            severity_label(finding.severity.value, locale),
            finding.id,
            recommendation_text(finding.recommendation, locale),
        )
    return table


def _next_actions_text(result: ScanResult, output_label: Path | None, *, locale: str) -> str:
    actions = localized_actions(result, locale)
    if output_label is not None:
        if locale == "ko":
            actions.append(f"{output_label} 파일을 열어서 자세한 근거를 확인하세요.")
        else:
            actions.append(f"Open {output_label} for the full evidence trail.")
    else:
        actions.append(text("save_html_action", locale))
    return "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))


def _finding_sort_key(finding: Finding) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return severity_rank.get(finding.severity.value, 9), finding.id


def _finding_counts(result: ScanResult, locale: str) -> str:
    counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in result.findings:
        counts[finding.severity.value] += 1
    return "  ".join(f"{severity_label(name, locale)}:{count}" for name, count in counts.items())


def _score_bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    empty = 10 - filled
    style = "green" if score >= 90 else "yellow" if score >= 70 else "red"
    return f"[{style}]{'█' * filled}{'░' * empty}[/{style}]"


def _score_label(score: int, locale: str) -> str:
    if score >= 90:
        return "좋음" if locale == "ko" else "clean"
    if score >= 70:
        return "확인 필요" if locale == "ko" else "review"
    return "주의" if locale == "ko" else "attention"


def _risk_badge(risk_label: str, locale: str) -> str:
    style = _risk_border_style(risk_label)
    label = localized_risk_label(risk_label) if locale == "ko" else risk_label.upper()
    return f"[bold {style}]{label}[/bold {style}]"


def _risk_border_style(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "red"
    if "moderate" in normalized:
        return "yellow"
    return "green"


def _verdict(result: ScanResult, locale: str) -> str:
    verdict = result.assessment.verdict
    if verdict == "do_not_install_before_review":
        if locale == "ko":
            return "[bold red]검토 전 설치 금지[/bold red]"
        return "[bold red]do not install before review[/bold red]"
    if verdict == "insufficient_evidence":
        if locale == "ko":
            return "[bold yellow]근거 부족[/bold yellow]"
        return "[bold yellow]insufficient evidence[/bold yellow]"
    if verdict == "usable_after_review":
        if locale == "ko":
            return "[bold yellow]검토 후 사용 가능[/bold yellow]"
        return "[bold yellow]usable after review[/bold yellow]"
    if locale == "ko":
        return "[bold green]현재 검사 기준으로 사용 가능[/bold green]"
    return "[bold green]usable by current checks[/bold green]"


def _confidence_badge(confidence: str, locale: str) -> str:
    style = "green" if confidence == "high" else "yellow" if confidence == "medium" else "red"
    label = confidence_label(confidence) if locale == "ko" else confidence.upper()
    return f"[bold {style}]{label}[/bold {style}]"


def _coverage_badge(coverage: str, locale: str) -> str:
    style = "green" if coverage == "full" else "yellow" if coverage == "partial" else "red"
    label = coverage_label(coverage) if locale == "ko" else coverage.upper()
    return f"[bold {style}]{label}[/bold {style}]"
