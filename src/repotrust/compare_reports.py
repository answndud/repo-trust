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
    persisting: list[str]
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
    outcome = _html_outcome(summary, locale=locale)
    labels = {
        "old_target": "이전 대상" if locale == "ko" else "Old target",
        "new_target": "최신 대상" if locale == "ko" else "New target",
        "score": "점수" if locale == "ko" else "Score",
        "grade": "등급" if locale == "ko" else "Grade",
        "verdict": "판단" if locale == "ko" else "Verdict",
        "added": "새로 생긴 문제" if locale == "ko" else "New issues",
        "resolved": "좋아진 점" if locale == "ko" else "Improvements",
        "severity": "심각도 변경" if locale == "ko" else "Severity changes",
        "persisting": "아직 남은 문제" if locale == "ko" else "Still remaining",
        "none": "없음" if locale == "ko" else "None",
    }
    descriptions = {
        "added": (
            "수정 후 새로 나타난 finding입니다. 설치나 채택 전에 먼저 확인하세요."
            if locale == "ko"
            else "Findings that appeared in the newer report. Review these before installing or adopting."
        ),
        "resolved": (
            "이전 리포트에는 있었지만 최신 리포트에서는 사라진 finding입니다."
            if locale == "ko"
            else "Findings that existed before and disappeared in the newer report."
        ),
        "severity": (
            "같은 finding의 심각도가 바뀐 항목입니다."
            if locale == "ko"
            else "Findings whose severity changed between the two reports."
        ),
        "persisting": (
            "아직 최신 리포트에도 남아 있는 finding입니다."
            if locale == "ko"
            else "Findings that still exist in the newer report."
        ),
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
    .outcome {{ margin: 0 0 18px; border-left: 4px solid #2563eb; }}
    .outcome strong {{ display: block; font-size: 18px; margin-bottom: 6px; }}
    .section-note {{ color: #64748b; margin-top: -8px; }}
    .label {{ display: block; color: #64748b; font-size: 13px; margin-bottom: 6px; }}
    .value {{ font-size: 18px; font-weight: 700; }}
    code {{ background: #eef2f7; border-radius: 4px; padding: 2px 5px; }}
    button {{ border: 1px solid #cbd5e1; border-radius: 6px; background: #ffffff; color: #334155; cursor: pointer; font: inherit; font-size: 13px; margin-left: 8px; padding: 4px 8px; }}
    button:hover {{ background: #f1f5f9; }}
    ul {{ padding-left: 20px; }}
    li {{ margin: 6px 0; }}
    .finding-actions {{ white-space: nowrap; }}
  </style>
</head>
<body>
  <main>
    <h1>{html.escape(title)}</h1>
    <section class="outcome">
      <strong>{html.escape(outcome[0])}</strong>
      <span>{html.escape(outcome[1])}</span>
    </section>
    <div class="summary">
      {_html_metric(labels["old_target"], summary.old_target)}
      {_html_metric(labels["new_target"], summary.new_target)}
      {_html_metric(labels["score"], f"{summary.old_score} -> {summary.new_score} ({summary.delta:+d})")}
      {_html_metric(labels["grade"], f"{summary.old_grade} -> {summary.new_grade}")}
      {_html_metric(labels["verdict"], f"{summary.old_verdict} -> {summary.new_verdict}")}
    </div>
    {_html_findings_section(labels["resolved"], descriptions["resolved"], summary.resolved, labels["none"])}
    {_html_findings_section(labels["added"], descriptions["added"], summary.added, labels["none"])}
    {_html_severity_section(labels["severity"], descriptions["severity"], summary.severity_changes, labels["none"])}
    {_html_findings_section(labels["persisting"], descriptions["persisting"], summary.persisting, labels["none"])}
  </main>
  <script>
    function copyRepoTrustValue(button) {{
      var value = button.getAttribute("data-copy-value");
      function markCopied() {{
        var original = button.textContent;
        button.textContent = button.getAttribute("data-copied-label") || "Copied";
        setTimeout(function () {{ button.textContent = original; }}, 1200);
      }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(value).then(markCopied).catch(function () {{ fallbackCopy(value); markCopied(); }});
      }} else {{
        fallbackCopy(value);
        markCopied();
      }}
    }}
    function fallbackCopy(value) {{
      var textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }}
  </script>
</body>
</html>
"""


def _html_outcome(summary: CompareSummary, *, locale: str) -> tuple[str, str]:
    if summary.delta > 0:
        return (
            ("개선됨", "점수가 올랐습니다. 해결된 finding과 아직 남은 finding을 함께 확인하세요.")
            if locale == "ko"
            else ("Improved", "The score increased. Review resolved findings and anything still remaining.")
        )
    if summary.delta < 0:
        return (
            ("악화됨", "점수가 내려갔습니다. 새로 생긴 문제와 심각도 변경을 먼저 확인하세요.")
            if locale == "ko"
            else ("Worse", "The score decreased. Check new issues and severity changes first.")
        )
    return (
        ("점수 변화 없음", "점수는 같지만 finding 변화가 있을 수 있습니다. 아래 섹션을 확인하세요.")
        if locale == "ko"
        else ("No score change", "The score stayed the same, but finding details may still have changed.")
    )


def _html_metric(label: str, value: str) -> str:
    return (
        '<div class="metric">'
        f'<span class="label">{html.escape(label)}</span>'
        f'<span class="value">{html.escape(value)}</span>'
        "</div>"
    )


def _html_findings_section(
    title: str,
    description: str,
    finding_ids: list[str],
    none_label: str,
) -> str:
    items = f"<p>{html.escape(none_label)}.</p>"
    if finding_ids:
        items = "<ul>" + "".join(
            f"<li>{_html_finding_with_actions(finding_id)}</li>" for finding_id in finding_ids
        ) + "</ul>"
    return (
        f"<section><h2>{html.escape(title)}: {len(finding_ids)}</h2>"
        f'<p class="section-note">{html.escape(description)}</p>{items}</section>'
    )


def _html_severity_section(
    title: str,
    description: str,
    changes: list[SeverityChange],
    none_label: str,
) -> str:
    items = f"<p>{html.escape(none_label)}.</p>"
    if changes:
        items = "<ul>" + "".join(
            "<li>"
            f"{_html_finding_with_actions(change.finding_id)}: "
            f"{html.escape(str(change.old_severity))} -> {html.escape(str(change.new_severity))}"
            "</li>"
            for change in changes
        ) + "</ul>"
    return (
        f"<section><h2>{html.escape(title)}: {len(changes)}</h2>"
        f'<p class="section-note">{html.escape(description)}</p>{items}</section>'
    )


def _html_finding_with_actions(finding_id: str) -> str:
    escaped_id = html.escape(finding_id)
    explain_command = f"repo-trust explain {finding_id}"
    return (
        f"<code>{escaped_id}</code>"
        '<span class="finding-actions">'
        f'<button type="button" onclick="copyRepoTrustValue(this)" data-copy-value="{escaped_id}" data-copied-label="Copied">Copy ID</button>'
        f'<button type="button" onclick="copyRepoTrustValue(this)" data-copy-value="{html.escape(explain_command)}" data-copied-label="Copied">Copy explain</button>'
        "</span>"
    )


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
