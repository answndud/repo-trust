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
    profile_label,
    recommendation_text,
    risk_label as localized_risk_label,
    severity_label,
    status_text,
    text,
)
from .evidence import evidence_rows
from .models import Finding, ScanResult
from .terminal_theme import (
    badge,
    kali_inline_kv,
    kali_kv,
    kali_prompt_header,
    kali_section,
    kali_table,
    muted,
    state_style,
)


def print_command_header(
    *,
    console: Console,
    target: str,
    mode: str,
    report_format: str,
    locale: str = "en",
) -> None:
    if locale == "ko":
        console.print(kali_prompt_header("scan", "target"))
        console.print(kali_kv("검사 대상", target))
        console.print(
            f"[bright_black]│[/] "
            f"{kali_inline_kv('검사 방식', mode_label(mode, locale))}  "
            f"{kali_inline_kv('리포트 형식', format_label(report_format, locale))}"
        )
        return
    console.print(kali_prompt_header("scan", "target"))
    console.print(kali_kv("target", target))
    console.print(
        f"[bright_black]│[/] "
        f"{kali_inline_kv('mode', mode)}  {kali_inline_kv('format', report_format)}"
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
    console.print(_result_header(result, locale=locale))
    console.print(_result_summary(result, mode=mode, locale=locale))
    console.print(_block_title("WHY", "이유", locale))
    console.print(_why_text(result, locale=locale))
    console.print(_block_title("PROFILES", "목적별 판단", locale))
    console.print(_profiles_text(result, locale=locale))
    console.print(_block_title("ACTIONS", "다음 행동", locale))
    console.print(_next_actions_text(result, output_label, locale=locale))
    console.print(_block_title("REPORT", "리포트", locale))
    console.print(_report_text(output_label, locale=locale))

    if _has_complete_evidence(result):
        console.print(_block_title("DETAILS", "세부 정보", locale))
        console.print(_risk_breakdown_table(result, locale=locale))
        console.print(_evidence_table(result, locale=locale))
    else:
        console.print(_block_title("DETAILS", "세부 정보", locale))
        console.print(_incomplete_details_text(result, locale=locale))


def print_legacy_summary(*, console: Console, result: ScanResult, verbose: bool) -> None:
    console.print(kali_section("RepoTrust Summary"))
    table = kali_table()
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
    console.print(kali_section(text("findings_title", locale)))
    finding_table = kali_table()
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


def _result_header(result: ScanResult, *, locale: str) -> str:
    line = "─" * 36
    if locale == "ko":
        return f"[bright_black]{line}[/]\n{_headline(result, locale)}\n[bright_black]{line}[/]"
    return f"[bright_black]{line}[/]\n{_headline(result, locale)}\n[bright_black]{line}[/]"


def _headline(result: ScanResult, locale: str) -> str:
    verdict = result.assessment.verdict
    if locale == "ko":
        if verdict == "do_not_install_before_review":
            return "[red bold]RESULT: 설치하지 마세요[/]"
        if verdict == "insufficient_evidence":
            return "[yellow bold]RESULT: 판단 근거 부족[/]"
        if verdict == "usable_after_review":
            return "[yellow bold]RESULT: 검토 후 사용 가능[/]"
        return "[blue bold]RESULT: 현재 기준 통과[/]"
    if verdict == "do_not_install_before_review":
        return "[red bold]RESULT: DO NOT INSTALL[/]"
    if verdict == "insufficient_evidence":
        return "[yellow bold]RESULT: INSUFFICIENT EVIDENCE[/]"
    if verdict == "usable_after_review":
        return "[yellow bold]RESULT: REVIEW BEFORE USE[/]"
    return "[blue bold]RESULT: USABLE BY CURRENT CHECKS[/]"


def _result_summary(result: ScanResult, *, mode: str, locale: str) -> str:
    assessment = result.assessment
    confidence_reason = _confidence_reason(result, locale=locale)
    if locale == "ko":
        return (
            f"Risk: {_risk_badge(result.score.risk_label, locale)}\n"
            f"Score: {badge(f'{result.score.total}/{result.score.max_score}', style='blue')}  "
            f"Grade: {badge(result.score.grade, style='white')}\n"
            f"Confidence: {_confidence_badge(assessment.confidence, locale)} {muted(confidence_reason)}\n"
            f"Target: {result.target.raw}\n"
            f"Mode: {mode_label(mode, locale)}"
        )
    return (
        f"Risk: {_risk_badge(result.score.risk_label, locale)}\n"
        f"Score: {badge(f'{result.score.total}/{result.score.max_score}', style='blue')}  "
        f"Grade: {badge(result.score.grade, style='white')}\n"
        f"Confidence: {_confidence_badge(assessment.confidence, locale)} {muted(confidence_reason)}\n"
        f"Target: {result.target.raw}\n"
        f"Mode: {mode}"
    )


def _confidence_reason(result: ScanResult, *, locale: str) -> str:
    coverage = result.assessment.coverage
    if locale == "ko":
        if coverage == "failed":
            return "(분석 실패)"
        if coverage in {"metadata_only", "partial"}:
            return "(분석이 완전하지 않음)"
        return "(확인 가능한 근거를 충분히 검사함)"
    if coverage == "failed":
        return "(analysis failed)"
    if coverage in {"metadata_only", "partial"}:
        return "(analysis incomplete)"
    return "(available evidence checked)"


def _block_title(en: str, ko: str, locale: str) -> str:
    return f"\n[bright_black]{'─' * 36}[/]\n[bold]{ko if locale == 'ko' else en}[/]"


def _why_text(result: ScanResult, *, locale: str) -> str:
    if not result.findings:
        if locale == "ko":
            return "현재 규칙에서 차단할 문제를 찾지 못했습니다."
        return "No blocking issues were found by the enabled checks."

    findings = sorted(result.findings, key=_finding_sort_key)[:3]
    lines: list[str] = []
    for finding in findings:
        prefix = "!" if finding.severity.value in {"high", "medium"} else "-"
        message = message_text(finding.message, locale)
        recommendation = recommendation_text(finding.recommendation, locale)
        lines.append(f"{prefix} {message}\n  → {recommendation}")
    return "\n".join(lines)


def _report_text(output_label: Path | None, *, locale: str) -> str:
    if output_label is None:
        return "파일 저장 안 함" if locale == "ko" else "No file written for this terminal-only check."
    if locale == "ko":
        return f"전체 리포트 열기:\n→ {output_label}"
    return f"Open full report:\n→ {output_label}"


def _has_complete_evidence(result: ScanResult) -> bool:
    return result.assessment.coverage == "full"


def _incomplete_details_text(result: ScanResult, *, locale: str) -> str:
    if locale == "ko":
        if result.assessment.coverage == "failed":
            return "분석이 실패해 세부 점수와 근거 표를 신뢰할 수 없습니다."
        return "분석이 완전하지 않아 일부 세부 점수와 근거 표를 생략합니다."
    if result.assessment.coverage == "failed":
        return "Analysis failed — detailed scores and evidence are unavailable."
    return "Analysis incomplete — detailed scores and evidence may be unavailable."


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
            f"{kali_kv('결론', _verdict(result, locale))}\n"
            f"[bright_black]│[/] "
            f"{kali_inline_kv('확실도', _confidence_badge(assessment.confidence, locale))}  "
            f"{kali_inline_kv('검사 범위', _coverage_badge(assessment.coverage, locale))}\n"
            f"[bright_black]│[/] "
            f"{kali_inline_kv('점수', badge(f'{result.score.total}/{result.score.max_score}', style='blue'))}  "
            f"{kali_inline_kv('등급', badge(result.score.grade, style='white'))}  "
            f"{kali_inline_kv('위험도', _risk_badge(result.score.risk_label, locale))}\n"
            f"{kali_kv('발견 항목', _finding_counts(result, locale))}\n\n"
            f"{beginner_summary(result)}\n\n"
            f"{kali_kv('검사 대상', result.target.raw)}\n"
            f"{kali_kv('검사 방식', mode_label(mode, locale))}\n"
            f"{kali_kv('결과 파일', output)}"
        )
    return (
        f"{kali_kv('Verdict', f'{_verdict(result, locale)}  [bright_black]{assessment.verdict}[/]')}\n"
        f"[bright_black]│[/] "
        f"{kali_inline_kv('Confidence', _confidence_badge(assessment.confidence, locale))}  "
        f"{kali_inline_kv('Coverage', _coverage_badge(assessment.coverage, locale))}\n"
        f"[bright_black]│[/] "
        f"{kali_inline_kv('Score', badge(f'{result.score.total}/{result.score.max_score}', style='blue'))}  "
        f"{kali_inline_kv('Grade', badge(result.score.grade, style='white'))}  "
        f"{kali_inline_kv('Risk', _risk_badge(result.score.risk_label, locale))}\n"
        f"{kali_kv('Findings', _finding_counts(result, locale))}\n\n"
        f"{assessment.summary}\n\n"
        f"{kali_kv('Target', result.target.raw)}\n"
        f"{kali_kv('Mode', mode)}\n"
        f"{kali_kv('Output', output)}"
    )


def _risk_breakdown_table(result: ScanResult, *, locale: str) -> Table:
    table = kali_table()
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
    table = kali_table()
    table.add_column(text("signal_column", locale))
    table.add_column(text("status_column", locale))
    table.add_column(text("evidence_column", locale))
    for row in evidence_rows(result):
        table.add_row(evidence_label(row.label, locale), status_text(row, locale), row.value)
    return table


def _top_findings_table(result: ScanResult, *, locale: str) -> Table:
    table = kali_table()
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
    if any(finding.id == "target.local_path_missing" for finding in result.findings):
        if locale == "ko":
            actions = [
                "올바른 로컬 저장소 경로로 다시 실행하세요.",
                "예: repo-trust /your/project/path",
            ]
        else:
            actions = [
                "Re-run with a valid repository path.",
                "Example: repo-trust /your/project/path",
            ]
        return "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))

    actions = localized_actions(result, locale)
    if output_label is None:
        actions.append(text("save_html_action", locale))
    return "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))


def _profiles_text(result: ScanResult, *, locale: str) -> str:
    lines = []
    for key, profile in result.assessment.profiles.items():
        label = profile_label(key, locale)
        verdict = _verdict_badge(profile.verdict, locale)
        if profile.priority_finding_ids:
            priority = ", ".join(profile.priority_finding_ids)
        else:
            priority = "없음" if locale == "ko" else "none"
        lines.append(
            f"{kali_inline_kv(label, verdict)}  "
            f"{muted(profile.summary)}\n"
            f"  {kali_inline_kv('priority', priority)}"
        )
    return "\n".join(lines)


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
    style = "blue" if score >= 90 else "yellow" if score >= 70 else "red"
    return f"[{style}]{'█' * filled}{'░' * empty}[/{style}]"


def _score_label(score: int, locale: str) -> str:
    if score >= 90:
        return "좋음" if locale == "ko" else "clean"
    if score >= 70:
        return "확인 필요" if locale == "ko" else "review"
    return "주의" if locale == "ko" else "attention"


def _risk_badge(risk_label: str, locale: str) -> str:
    style = state_style(risk_label)
    label = localized_risk_label(risk_label) if locale == "ko" else risk_label.upper()
    return badge(label, style=style)


def _verdict(result: ScanResult, locale: str) -> str:
    return _verdict_badge(result.assessment.verdict, locale)


def _verdict_badge(verdict: str, locale: str) -> str:
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
        return badge("현재 검사 기준으로 사용 가능", style="blue")
    return badge("usable by current checks", style="blue")


def _confidence_badge(confidence: str, locale: str) -> str:
    label = confidence_label(confidence) if locale == "ko" else confidence.upper()
    return badge(label, style=state_style(confidence))


def _coverage_badge(coverage: str, locale: str) -> str:
    label = coverage_label(coverage) if locale == "ko" else coverage.upper()
    return badge(label, style=state_style(coverage))
