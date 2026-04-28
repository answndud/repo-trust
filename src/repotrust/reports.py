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
    markdown = render_markdown(result)
    body = _markdownish_to_html(markdown)
    title = html.escape(f"RepoTrust Report - {result.target.raw}")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; color: #1f2933; background: #f7f8fa; }}
    main {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}
    h1, h2, h3 {{ color: #102a43; }}
    h1 {{ margin-top: 0; }}
    code {{ background: #e7eef5; padding: 2px 5px; border-radius: 4px; }}
    ul {{ padding-left: 24px; }}
    li {{ margin: 6px 0; }}
    .report {{ background: #ffffff; border: 1px solid #d9e2ec; border-radius: 8px; padding: 28px; }}
    .finding {{ border-left: 4px solid #627d98; padding: 10px 14px; margin: 14px 0; background: #f8fafc; }}
  </style>
</head>
<body>
  <main>
    <section class="report">
{body}
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


def _markdownish_to_html(markdown: str) -> str:
    lines = []
    in_list = False
    in_finding = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            if in_list:
                lines.append("      </ul>")
                in_list = False
            continue
        if line.startswith("### "):
            if in_list:
                lines.append("      </ul>")
                in_list = False
            if in_finding:
                lines.append("      </div>")
            in_finding = True
            lines.append('      <div class="finding">')
            lines.append(f"        <h3>{_inline_html(line[4:])}</h3>")
        elif line.startswith("## "):
            if in_list:
                lines.append("      </ul>")
                in_list = False
            if in_finding:
                lines.append("      </div>")
                in_finding = False
            lines.append(f"      <h2>{_inline_html(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                lines.append("      </ul>")
                in_list = False
            lines.append(f"      <h1>{_inline_html(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                lines.append("      <ul>")
                in_list = True
            lines.append(f"        <li>{_inline_html(line[2:])}</li>")
        else:
            if in_list:
                lines.append("      </ul>")
                in_list = False
            lines.append(f"      <p>{_inline_html(line)}</p>")
    if in_list:
        lines.append("      </ul>")
    if in_finding:
        lines.append("      </div>")
    return "\n".join(lines)


def _inline_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = escaped.replace("**", "")
    return _replace_inline_code(escaped)


def _replace_inline_code(text: str) -> str:
    parts = text.split("`")
    if len(parts) == 1:
        return text
    rendered = []
    for index, part in enumerate(parts):
        if index % 2 == 0:
            rendered.append(part)
        else:
            rendered.append(f"<code>{part}</code>")
    return "".join(rendered)

