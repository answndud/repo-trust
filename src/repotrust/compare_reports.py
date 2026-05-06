from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import html


class CompareFormat(str, Enum):
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"


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
    old_target: str
    new_target: str
    added: list[str]
    resolved: list[str]
    severity_changes: list[SeverityChange]
    persisting_count: int


def render_compare_reports(
    old_data: dict,
    new_data: dict,
    *,
    output_format: CompareFormat,
    locale: str,
) -> str:
    summary = _compare_reports_summary(old_data, new_data)
    if output_format == CompareFormat.MARKDOWN:
        return _compare_reports_markdown(summary, locale=locale)
    if output_format == CompareFormat.HTML:
        return _compare_reports_html(summary, locale=locale)
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
        old_target=_report_target_label(old_data),
        new_target=_report_target_label(new_data),
        added=added,
        resolved=resolved,
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


def _compare_reports_markdown(summary: CompareSummary, *, locale: str) -> str:
    if locale == "ko":
        return "\n".join(
            [
                "# RepoTrust 비교 리포트",
                "",
                f"- 이전 대상: `{summary.old_target}`",
                f"- 최신 대상: `{summary.new_target}`",
                f"- 점수: **{summary.old_score} -> {summary.new_score} ({summary.delta:+d})**",
                f"- 등급: **{summary.old_grade} -> {summary.new_grade}**",
                f"- 판단: `{summary.old_verdict}` -> `{summary.new_verdict}`",
                "",
                _markdown_findings_section("새 finding", summary.added, "+"),
                _markdown_findings_section("해결된 finding", summary.resolved, "-"),
                _markdown_severity_section("심각도 변경", summary.severity_changes),
                f"## 유지된 finding: {summary.persisting_count}",
                "",
            ]
        )

    return "\n".join(
        [
            "# RepoTrust Compare Report",
            "",
            f"- Old target: `{summary.old_target}`",
            f"- New target: `{summary.new_target}`",
            f"- Score: **{summary.old_score} -> {summary.new_score} ({summary.delta:+d})**",
            f"- Grade: **{summary.old_grade} -> {summary.new_grade}**",
            f"- Verdict: `{summary.old_verdict}` -> `{summary.new_verdict}`",
            "",
            _markdown_findings_section("Added findings", summary.added, "+"),
            _markdown_findings_section("Resolved findings", summary.resolved, "-"),
            _markdown_severity_section("Severity changes", summary.severity_changes),
            f"## Persisting findings: {summary.persisting_count}",
            "",
        ]
    )


def _markdown_findings_section(title: str, finding_ids: list[str], marker: str) -> str:
    lines = [f"## {title}: {len(finding_ids)}", ""]
    if not finding_ids:
        lines.append("None.")
        return "\n".join(lines)
    lines.extend(f"- `{marker} {finding_id}`" for finding_id in finding_ids)
    return "\n".join(lines)


def _markdown_severity_section(title: str, changes: list[SeverityChange]) -> str:
    lines = [f"## {title}: {len(changes)}", ""]
    if not changes:
        lines.append("None.")
        return "\n".join(lines)
    lines.extend(
        f"- `{change.finding_id}`: `{change.old_severity}` -> `{change.new_severity}`"
        for change in changes
    )
    return "\n".join(lines)


def _compare_reports_html(summary: CompareSummary, *, locale: str) -> str:
    title = "RepoTrust 비교 리포트" if locale == "ko" else "RepoTrust Compare Report"
    labels = {
        "old_target": "이전 대상" if locale == "ko" else "Old target",
        "new_target": "최신 대상" if locale == "ko" else "New target",
        "score": "점수" if locale == "ko" else "Score",
        "grade": "등급" if locale == "ko" else "Grade",
        "verdict": "판단" if locale == "ko" else "Verdict",
        "added": "새 finding" if locale == "ko" else "Added findings",
        "resolved": "해결된 finding" if locale == "ko" else "Resolved findings",
        "severity": "심각도 변경" if locale == "ko" else "Severity changes",
        "persisting": "유지된 finding" if locale == "ko" else "Persisting findings",
        "none": "없음" if locale == "ko" else "None",
    }
    return f"""<!doctype html>
<html lang="{html.escape(locale)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #1f2937; background: #f8fafc; }}
    main {{ max-width: 960px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1 {{ margin: 0 0 20px; font-size: 32px; }}
    h2 {{ margin-top: 28px; font-size: 20px; }}
    .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }}
    .metric, section {{ border: 1px solid #d5dbe3; background: #ffffff; border-radius: 8px; padding: 16px; }}
    .label {{ display: block; color: #64748b; font-size: 13px; margin-bottom: 6px; }}
    .value {{ font-size: 18px; font-weight: 700; }}
    code {{ background: #eef2f7; border-radius: 4px; padding: 2px 5px; }}
    ul {{ padding-left: 20px; }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(title)}</h1>
    <div class="summary">
      {_html_metric(labels["old_target"], summary.old_target)}
      {_html_metric(labels["new_target"], summary.new_target)}
      {_html_metric(labels["score"], f"{summary.old_score} -> {summary.new_score} ({summary.delta:+d})")}
      {_html_metric(labels["grade"], f"{summary.old_grade} -> {summary.new_grade}")}
      {_html_metric(labels["verdict"], f"{summary.old_verdict} -> {summary.new_verdict}")}
    </div>
    {_html_findings_section(labels["added"], summary.added, labels["none"])}
    {_html_findings_section(labels["resolved"], summary.resolved, labels["none"])}
    {_html_severity_section(labels["severity"], summary.severity_changes, labels["none"])}
    <section>
      <h2>{html.escape(labels["persisting"])}: {summary.persisting_count}</h2>
    </section>
  </main>
</body>
</html>
"""


def _html_metric(label: str, value: str) -> str:
    return (
        '<div class="metric">'
        f'<span class="label">{html.escape(label)}</span>'
        f'<span class="value">{html.escape(value)}</span>'
        "</div>"
    )


def _html_findings_section(title: str, finding_ids: list[str], none_label: str) -> str:
    items = f"<p>{html.escape(none_label)}.</p>"
    if finding_ids:
        items = "<ul>" + "".join(
            f"<li><code>{html.escape(finding_id)}</code></li>" for finding_id in finding_ids
        ) + "</ul>"
    return f"<section><h2>{html.escape(title)}: {len(finding_ids)}</h2>{items}</section>"


def _html_severity_section(
    title: str,
    changes: list[SeverityChange],
    none_label: str,
) -> str:
    items = f"<p>{html.escape(none_label)}.</p>"
    if changes:
        items = "<ul>" + "".join(
            "<li>"
            f"<code>{html.escape(change.finding_id)}</code>: "
            f"{html.escape(str(change.old_severity))} -> {html.escape(str(change.new_severity))}"
            "</li>"
            for change in changes
        ) + "</ul>"
    return f"<section><h2>{html.escape(title)}: {len(changes)}</h2>{items}</section>"


def _finding_map(report: dict) -> dict[str, dict]:
    findings = {}
    for finding in report.get("findings", []):
        if isinstance(finding, dict) and isinstance(finding.get("id"), str):
            findings[finding["id"]] = finding
    return findings


def _score_total(report: dict) -> int:
    value = report["score"].get("total", 0)
    return value if isinstance(value, int) else 0


def _report_target_label(report: dict) -> str:
    target = report.get("target")
    if isinstance(target, dict):
        raw = target.get("raw") or target.get("path") or target.get("repo")
        if isinstance(raw, str) and raw:
            return raw
    return "unknown"
