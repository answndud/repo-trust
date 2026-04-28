from __future__ import annotations

import html
import json

from .models import Finding, ScanResult


def render_report(result: ScanResult, report_format: str) -> str:
    if report_format == "json":
        return render_json(result)
    if report_format == "html":
        return render_html(result)
    return render_markdown(result)


def render_json(result: ScanResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown(result: ScanResult) -> str:
    lines = [
        "# RepoTrust Report",
        "",
        f"- Target: `{result.target.raw}`",
        f"- Target type: `{result.target.kind}`",
        f"- Score: **{result.score.total}/{result.score.max_score}** ({result.score.grade}, {result.score.risk_label})",
        f"- Generated at: `{result.generated_at}`",
        "",
        "## Category Scores",
        "",
    ]
    for category, score in result.score.categories.items():
        lines.append(f"- `{category}`: {score}/100")

    lines.extend(["", "## Detected Files", ""])
    detected = result.detected_files.to_dict()
    for key, value in detected.items():
        display = value if value else "None"
        if isinstance(value, list):
            display = ", ".join(value) if value else "None"
        lines.append(f"- `{key}`: {display}")

    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No findings. The repository passed all enabled v1 checks.")
    else:
        for finding in result.findings:
            lines.extend(_finding_markdown(finding))
    lines.append("")
    return "\n".join(lines)


def render_html(result: ScanResult) -> str:
    title = html.escape(f"RepoTrust Report - {result.target.raw}")
    category_items = "\n".join(
        f'          <li><span class="label">{html.escape(category)}</span><span>{score}/100</span></li>'
        for category, score in result.score.categories.items()
    )
    detected_items = "\n".join(
        f'          <li><span class="label">{html.escape(key)}</span><span>{html.escape(_display_value(value))}</span></li>'
        for key, value in result.detected_files.to_dict().items()
    )
    findings = "\n".join(_finding_html(finding) for finding in result.findings)
    if not findings:
        findings = '        <p class="empty">No findings. The repository passed all enabled v1 checks.</p>'

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #1f2933; background: #f7f8fa; line-height: 1.5; }}
    main {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}
    h1, h2, h3 {{ color: #102a43; }}
    h1 {{ margin: 0 0 16px; }}
    h2 {{ margin-top: 32px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 8px 16px; margin: 0; }}
    dt {{ font-weight: 700; color: #334e68; }}
    dd {{ margin: 0; }}
    code {{ background: #e7eef5; padding: 2px 5px; border-radius: 4px; }}
    ul {{ padding-left: 0; list-style: none; }}
    li {{ margin: 6px 0; }}
    .report {{ background: #ffffff; border: 1px solid #d9e2ec; border-radius: 8px; padding: 28px; }}
    .score {{ display: inline-flex; align-items: baseline; gap: 10px; margin: 6px 0 18px; }}
    .score strong {{ font-size: 2rem; color: #102a43; }}
    .score span {{ color: #52606d; }}
    .data-list li {{ display: flex; justify-content: space-between; gap: 16px; border-bottom: 1px solid #edf2f7; padding: 7px 0; }}
    .label {{ color: #486581; font-weight: 700; }}
    .finding {{ border-left: 4px solid #627d98; border-radius: 4px; padding: 12px 14px; margin: 14px 0; background: #f8fafc; }}
    .finding h3 {{ margin: 0 0 8px; }}
    .finding dl {{ grid-template-columns: 120px 1fr; }}
    .severity-info {{ border-left-color: #627d98; }}
    .severity-low {{ border-left-color: #2f855a; }}
    .severity-medium {{ border-left-color: #b7791f; }}
    .severity-high {{ border-left-color: #c53030; }}
    .empty {{ color: #52606d; }}
  </style>
</head>
<body>
  <main>
    <section class="report">
      <h1>RepoTrust Report</h1>
      <div class="score">
        <strong>{result.score.total}/{result.score.max_score}</strong>
        <span>{html.escape(result.score.grade)} &middot; {html.escape(result.score.risk_label)}</span>
      </div>
      <dl>
        <dt>Target</dt><dd><code>{html.escape(result.target.raw)}</code></dd>
        <dt>Target type</dt><dd><code>{html.escape(result.target.kind)}</code></dd>
        <dt>Generated at</dt><dd><code>{html.escape(result.generated_at)}</code></dd>
      </dl>

      <h2>Category Scores</h2>
      <ul class="data-list">
{category_items}
      </ul>

      <h2>Detected Files</h2>
      <ul class="data-list">
{detected_items}
      </ul>

      <h2>Findings</h2>
{findings}
    </section>
  </main>
</body>
</html>
"""


def _finding_markdown(finding: Finding) -> list[str]:
    return [
        f"### {finding.id}",
        "",
        f"- Category: `{finding.category.value}`",
        f"- Severity: `{finding.severity.value}`",
        f"- Message: {finding.message}",
        f"- Evidence: {finding.evidence}",
        f"- Recommendation: {finding.recommendation}",
        "",
    ]


def _finding_html(finding: Finding) -> str:
    severity = html.escape(finding.severity.value)
    return f"""        <article class="finding severity-{severity}">
          <h3>{html.escape(finding.id)}</h3>
          <dl>
            <dt>Category</dt><dd><code>{html.escape(finding.category.value)}</code></dd>
            <dt>Severity</dt><dd><code>{severity}</code></dd>
            <dt>Message</dt><dd>{html.escape(finding.message)}</dd>
            <dt>Evidence</dt><dd>{html.escape(finding.evidence)}</dd>
            <dt>Recommendation</dt><dd>{html.escape(finding.recommendation)}</dd>
          </dl>
        </article>"""


def _display_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "None"
    return str(value) if value else "None"
