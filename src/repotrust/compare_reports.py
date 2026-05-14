from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SeverityChange:
    finding_id: str
    old_severity: str | None
    new_severity: str | None


@dataclass(frozen=True)
class CompareSummary:
    old_score: int
    new_score: int
    delta: int
    old_grade: str
    new_grade: str
    old_verdict: str
    new_verdict: str
    added: list[str]
    resolved: list[str]
    persisting: list[str]
    severity_changes: list[SeverityChange]
    persisting_count: int


def render_compare_reports(
    old_data: dict,
    new_data: dict,
    *,
    locale: str,
) -> str:
    summary = _compare_reports_summary(old_data, new_data)
    return _compare_reports_text(summary, locale=locale)


def _compare_reports_summary(old_data: dict, new_data: dict) -> CompareSummary:
    old_findings = _finding_map(old_data)
    new_findings = _finding_map(new_data)
    old_ids = set(old_findings)
    new_ids = set(new_findings)
    added = sorted(new_ids - old_ids)
    resolved = sorted(old_ids - new_ids)
    persisting = sorted(old_ids & new_ids)
    changed = []
    for finding_id in persisting:
        old_severity = old_findings[finding_id].get("severity")
        new_severity = new_findings[finding_id].get("severity")
        if old_severity != new_severity:
            changed.append(
                SeverityChange(
                    finding_id=finding_id,
                    old_severity=old_severity,
                    new_severity=new_severity,
                )
            )

    old_score = _score_total(old_data)
    new_score = _score_total(new_data)
    delta = new_score - old_score
    return CompareSummary(
        old_score=old_score,
        new_score=new_score,
        delta=delta,
        old_grade=str(old_data["score"].get("grade", "?")),
        new_grade=str(new_data["score"].get("grade", "?")),
        old_verdict=str(old_data["assessment"].get("verdict", "?")),
        new_verdict=str(new_data["assessment"].get("verdict", "?")),
        added=added,
        resolved=resolved,
        persisting=persisting,
        severity_changes=changed,
        persisting_count=len(persisting),
    )


def _compare_reports_text(summary: CompareSummary, *, locale: str) -> str:
    if locale == "ko":
        lines = [
            "RepoTrust Report Compare",
            f"점수: {summary.old_score} -> {summary.new_score} ({summary.delta:+d})",
            f"등급: {summary.old_grade} -> {summary.new_grade}",
            f"판단: {summary.old_verdict} -> {summary.new_verdict}",
            "",
            f"새 finding: {len(summary.added)}",
        ]
        lines.extend(f"+ {finding_id}" for finding_id in summary.added)
        lines.append(f"해결된 finding: {len(summary.resolved)}")
        lines.extend(f"- {finding_id}" for finding_id in summary.resolved)
        lines.append(f"심각도 변경: {len(summary.severity_changes)}")
        lines.extend(
            f"* {change.finding_id}: {change.old_severity} -> {change.new_severity}"
            for change in summary.severity_changes
        )
        lines.append(f"유지된 finding: {summary.persisting_count}")
        return "\n".join(lines)

    lines = [
        "RepoTrust Report Compare",
        f"Score: {summary.old_score} -> {summary.new_score} ({summary.delta:+d})",
        f"Grade: {summary.old_grade} -> {summary.new_grade}",
        f"Verdict: {summary.old_verdict} -> {summary.new_verdict}",
        "",
        f"Added findings: {len(summary.added)}",
    ]
    lines.extend(f"+ {finding_id}" for finding_id in summary.added)
    lines.append(f"Resolved findings: {len(summary.resolved)}")
    lines.extend(f"- {finding_id}" for finding_id in summary.resolved)
    lines.append(f"Severity changes: {len(summary.severity_changes)}")
    lines.extend(
        f"* {change.finding_id}: {change.old_severity} -> {change.new_severity}"
        for change in summary.severity_changes
    )
    lines.append(f"Persisting findings: {summary.persisting_count}")
    return "\n".join(lines)


def _finding_map(report: dict) -> dict[str, dict]:
    findings = {}
    for finding in report.get("findings", []):
        if isinstance(finding, dict) and isinstance(finding.get("id"), str):
            findings[finding["id"]] = finding
    return findings


def _score_total(report: dict) -> int:
    value = report["score"].get("total", 0)
    return value if isinstance(value, int) else 0
