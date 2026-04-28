from __future__ import annotations

from pathlib import Path

from rich.console import Console
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
from .terminal_theme import badge, data_table, header, inline_kv, kv, section, status_style


def print_command_header(
    *,
    console: Console,
    target: str,
    mode: str,
    report_format: str,
    locale: str = "en",
) -> None:
    if locale == "ko":
        console.print(header("repotrust", "명령 모드"))
        console.print(kv("검사 대상", target))
        console.print(
            f"{inline_kv('검사 방식', mode_label(mode, locale))}  "
            f"{inline_kv('리포트 형식', format_label(report_format, locale))}"
        )
        return
    console.print(header("RepoTrust", "COMMAND MODE"))
    console.print(kv("target", target))
    console.print(f"{inline_kv('mode', mode)}  {inline_kv('format', report_format)}")


def print_assessment_dashboard(
    *,
    console: Console,
    result: ScanResult,
    mode: str,
    verbose: bool,
    output_label: Path | None,
    locale: str = "en",
) -> None:
    console.print(section(text("assessment_title", locale)))
    console.print(
        _assessment_text(
            result=result,
            mode=mode,
            output_label=output_label,
            locale=locale,
        )
    )
    console.print(section(text("risk_breakdown_title", locale)))
    console.print(_risk_breakdown_table(result, locale=locale))
    console.print(section(text("evidence_title", locale)))
    console.print(_evidence_table(result, locale=locale))
    console.print(section(text("top_findings_title", locale)))
    console.print(_top_findings_table(result, locale=locale))
    console.print(section(text("next_actions_title", locale)))
    console.print(_next_actions_text(result, output_label, locale=locale))

    if verbose and result.findings:
        print_findings(console=console, result=result, locale=locale)


def print_legacy_summary(*, console: Console, result: ScanResult, verbose: bool) -> None:
    console.print(section("RepoTrust Summary"))
    table = data_table()
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
    console.print(section(text("findings_title", locale)))
    finding_table = data_table()
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
            f"{kv('결론', _verdict(result, locale))}\n"
            f"{inline_kv('확실도', _confidence_badge(assessment.confidence, locale))}  "
            f"{inline_kv('검사 범위', _coverage_badge(assessment.coverage, locale))}\n"
            f"{inline_kv('점수', badge(f'{result.score.total}/{result.score.max_score}', style='green'))}  "
            f"{inline_kv('등급', badge(result.score.grade, style='green'))}  "
            f"{inline_kv('위험도', _risk_badge(result.score.risk_label, locale))}\n"
            f"{kv('발견 항목', _finding_counts(result, locale))}\n\n"
            f"{beginner_summary(result)}\n\n"
            f"{kv('검사 대상', result.target.raw)}\n"
            f"{kv('검사 방식', mode_label(mode, locale))}\n"
            f"{kv('결과 파일', output)}"
        )
    return (
        f"{kv('Verdict', f'{_verdict(result, locale)}  [dim]{assessment.verdict}[/dim]')}\n"
        f"{inline_kv('Confidence', _confidence_badge(assessment.confidence, locale))}  "
        f"{inline_kv('Coverage', _coverage_badge(assessment.coverage, locale))}\n"
        f"{inline_kv('Score', badge(f'{result.score.total}/{result.score.max_score}', style='green'))}  "
        f"{inline_kv('Grade', badge(result.score.grade, style='green'))}  "
        f"{inline_kv('Risk', _risk_badge(result.score.risk_label, locale))}\n"
        f"{kv('Findings', _finding_counts(result, locale))}\n\n"
        f"{assessment.summary}\n\n"
        f"{kv('Target', result.target.raw)}\n"
        f"{kv('Mode', mode)}\n"
        f"{kv('Output', output)}"
    )


def _risk_breakdown_table(result: ScanResult, *, locale: str) -> Table:
    table = data_table()
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
    table = data_table()
    table.add_column(text("signal_column", locale))
    table.add_column(text("status_column", locale))
    table.add_column(text("evidence_column", locale))
    for row in evidence_rows(result):
        table.add_row(evidence_label(row.label, locale), status_text(row, locale), row.value)
    return table


def _top_findings_table(result: ScanResult, *, locale: str) -> Table:
    table = data_table()
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
    style = status_style(risk_label)
    label = localized_risk_label(risk_label) if locale == "ko" else risk_label.upper()
    return badge(label, style=style)


def _verdict(result: ScanResult, locale: str) -> str:
    verdict = result.assessment.verdict
    if verdict == "do_not_install_before_review":
        if locale == "ko":
            return badge("검토 전 설치 금지", style="red")
        return badge("do not install before review", style="red")
    if verdict == "insufficient_evidence":
        if locale == "ko":
            return badge("근거 부족", style="yellow")
        return badge("insufficient evidence", style="yellow")
    if verdict == "usable_after_review":
        if locale == "ko":
            return badge("검토 후 사용 가능", style="yellow")
        return badge("usable after review", style="yellow")
    if locale == "ko":
        return badge("현재 검사 기준으로 사용 가능", style="green")
    return badge("usable by current checks", style="green")


def _confidence_badge(confidence: str, locale: str) -> str:
    label = confidence_label(confidence) if locale == "ko" else confidence.upper()
    return badge(label, style=status_style(confidence))


def _coverage_badge(coverage: str, locale: str) -> str:
    label = coverage_label(coverage) if locale == "ko" else coverage.upper()
    return badge(label, style=status_style(coverage))
