from __future__ import annotations

import html
import json

from .evidence import EvidenceRow, evidence_rows
from .finding_catalog import get_finding_reference
from .models import JSON_SCHEMA_VERSION, AssessmentProfile, Finding, ScanResult


CATEGORY_LABELS = {
    "readme_quality": "README 품질",
    "install_safety": "설치 안전성",
    "security_posture": "보안 태세",
    "project_hygiene": "프로젝트 관리 상태",
    "target": "검사 대상",
}

CATEGORY_DESCRIPTIONS = {
    "readme_quality": "README가 프로젝트 목적, 설치 방법, 사용 방법을 충분히 설명하는지 봅니다.",
    "install_safety": "README의 설치 명령이 위험한 원격 스크립트 실행이나 검증 없는 설치를 유도하는지 봅니다.",
    "security_posture": "SECURITY.md, CI, Dependabot, lockfile처럼 보안과 재현성을 돕는 신호를 봅니다.",
    "project_hygiene": "LICENSE, dependency manifest 등 프로젝트를 dependency로 쓰기 전 확인할 관리 신호를 봅니다.",
    "target": "로컬 경로인지 GitHub URL인지, 원격 내용을 실제로 가져왔는지 같은 검사 대상 상태를 봅니다.",
}

SEVERITY_LABELS = {
    "info": "정보",
    "low": "낮음",
    "medium": "중간",
    "high": "높음",
}

RISK_LABELS = {
    "Low risk": "낮은 위험",
    "Moderate-low risk": "낮거나 중간 수준의 위험",
    "Moderate risk": "중간 위험",
    "High risk": "높은 위험",
}

TARGET_KIND_LABELS = {
    "local": "로컬 저장소",
    "github": "GitHub URL",
}

ASSESSMENT_LABELS = {
    "usable_by_current_checks": "현재 검사 기준 사용 가능",
    "usable_after_review": "검토 후 사용 가능",
    "insufficient_evidence": "판단 근거 부족",
    "do_not_install_before_review": "설치 전 검토 필요",
}

PROFILE_LABELS = {
    "install": "Install",
    "dependency": "Dependency",
    "agent_delegate": "Agent delegation",
}

PROFILE_LABELS_KO = {
    "install": "설치",
    "dependency": "의존성 채택",
    "agent_delegate": "AI agent 위임",
}

CONFIDENCE_LABELS = {
    "high": "높음",
    "medium": "중간",
    "low": "낮음",
}

COVERAGE_LABELS = {
    "full": "전체 검사",
    "partial": "부분 검사",
    "metadata_only": "메타데이터/URL만 검사",
    "failed": "검사 실패",
}

EVIDENCE_STATUS_LABELS = {
    "found": "확인됨",
    "missing": "없음",
    "unknown": "확인 못함",
}


def render_report(result: ScanResult, report_format: str) -> str:
    if report_format == "json":
        return render_json(result)
    if report_format == "html":
        return render_html(result)
    return render_markdown(result)


def render_json(result: ScanResult) -> str:
    return json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n"


def render_markdown(result: ScanResult) -> str:
    assessment = result.assessment
    lines = [
        "# RepoTrust Report",
        "",
        f"- Target: `{result.target.raw}`",
        f"- Target type: `{result.target.kind}`",
        f"- Score: **{result.score.total}/{result.score.max_score}** ({result.score.grade}, {result.score.risk_label})",
        f"- Verdict: `{assessment.verdict}`",
        f"- Confidence: `{assessment.confidence}`",
        f"- Coverage: `{assessment.coverage}`",
        f"- Generated at: `{result.generated_at}`",
        "",
        "## Assessment",
        "",
        assessment.summary,
        "",
        "### Reasons",
        "",
    ]
    for reason in assessment.reasons:
        lines.append(f"- {reason}")

    lines.extend(["", "### Next Actions", ""])
    for action in assessment.next_actions:
        lines.append(f"- {action}")

    lines.extend(["", "## Purpose Profiles", ""])
    for key, profile in assessment.profiles.items():
        lines.extend(_profile_markdown(key, profile))

    lines.extend([
        "",
        "## Risk Breakdown",
        "",
    ])
    for category, score in result.score.categories.items():
        lines.append(f"- `{category}`: {score}/100")

    lines.extend(["", "## Evidence Matrix", ""])
    for row in evidence_rows(result):
        lines.append(f"- `{row.key}`: {row.status} ({row.value})")

    lines.extend(["", "## Findings", ""])
    if not result.findings:
        lines.append("No findings. The repository passed all enabled v1 checks.")
    else:
        lines.append(
            "Assessment and purpose-profile summaries highlight up to 3 priority finding IDs. "
            f"This section lists all {len(result.findings)} findings sorted by severity."
        )
        lines.append("")
        for finding in sorted(result.findings, key=_finding_sort_key):
            lines.extend(_finding_markdown(finding))
    lines.append("")
    return "\n".join(lines)


def render_html(result: ScanResult) -> str:
    title = html.escape(f"RepoTrust 리포트 - {result.target.raw}")
    assessment = result.assessment
    finding_count = len(result.findings)
    category_items = "\n".join(
        _category_html(category, score)
        for category, score in result.score.categories.items()
    )
    evidence_items = "\n".join(_evidence_row_html(row) for row in evidence_rows(result))
    process_items = "\n".join(
        f"          <li>{html.escape(item)}</li>" for item in _assessment_process(result)
    )
    reason_items = "\n".join(
        f"          <li>{html.escape(reason)}</li>" for reason in assessment.reasons
    )
    next_action_items = "\n".join(
        f"          <li>{html.escape(action)}</li>" for action in assessment.next_actions
    )
    findings = "\n".join(
        _finding_html(finding) for finding in sorted(result.findings, key=_finding_sort_key)
    )
    profile_items = "\n".join(
        _profile_html(key, profile) for key, profile in assessment.profiles.items()
    )
    if not findings:
        findings = """        <article class="empty-state">
          <h3>현재 활성화된 검사에서 문제를 찾지 못했습니다.</h3>
          <p>README, 설치 명령, 보안 정책, CI, dependency 관련 기본 신호가 현재 rule set을 통과했습니다. 그래도 실제 도입 전에는 라이선스와 조직 내부 정책을 별도로 확인하세요.</p>
        </article>"""

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: light; --ink: #17212b; --muted: #5c6670; --line: #d9dee5; --soft: #f4f6f8; --panel: #ffffff; --accent: #0f766e; --warn: #9a6700; --danger: #b42318; --unknown: #475569; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; margin: 0; color: var(--ink); background: #eef2f5; line-height: 1.58; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 40px 24px; }}
    h1, h2, h3 {{ color: #111827; line-height: 1.25; }}
    h1 {{ margin: 0 0 10px; font-size: 2rem; }}
    h2 {{ margin: 34px 0 12px; font-size: 1.35rem; }}
    h3 {{ margin: 0 0 8px; font-size: 1.05rem; }}
    p {{ margin: 0 0 12px; }}
    code {{ background: #e8edf2; padding: 2px 6px; border-radius: 4px; font-size: 0.93em; }}
    ul {{ margin: 0; padding-left: 20px; }}
    .report {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 30px; }}
    .eyebrow {{ color: var(--muted); font-size: 0.9rem; font-weight: 700; margin: 0 0 6px; text-transform: uppercase; }}
    .lead {{ color: #3d4852; font-size: 1.03rem; max-width: 860px; }}
    .assessment-grid {{ display: grid; grid-template-columns: minmax(260px, 0.95fr) minmax(320px, 1.05fr); gap: 18px; margin: 24px 0; }}
    .score-panel, .section-panel, .finding, .empty-state {{ border: 1px solid var(--line); border-radius: 8px; background: #fbfcfd; padding: 18px; }}
    .score {{ display: flex; align-items: baseline; gap: 12px; margin: 8px 0 12px; }}
    .score strong {{ font-size: 2.5rem; color: #0f172a; }}
    .score span {{ color: var(--muted); font-weight: 700; }}
    .verdict {{ font-weight: 800; color: {_verdict_color(assessment.verdict)}; }}
    .pill-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }}
    .pill {{ display: inline-block; border: 1px solid var(--line); border-radius: 999px; background: #ffffff; padding: 4px 10px; font-size: 0.86rem; font-weight: 800; }}
    .profile-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; padding-left: 0; list-style: none; }}
    .profile-grid li {{ border: 1px solid #e3e8ef; border-radius: 8px; background: #ffffff; padding: 14px; }}
    .profile-verdict {{ font-weight: 800; margin: 4px 0 8px; }}
    .meta {{ display: grid; grid-template-columns: 150px 1fr; gap: 8px 16px; margin: 18px 0 0; }}
    .meta dt, .finding dt {{ font-weight: 700; color: #374151; }}
    .meta dd, .finding dd {{ margin: 0; }}
    .data-list {{ display: grid; gap: 12px; padding-left: 0; list-style: none; }}
    .data-list li {{ border: 1px solid #e3e8ef; border-radius: 8px; background: #ffffff; padding: 14px; }}
    .evidence-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; padding-left: 0; list-style: none; }}
    .evidence-grid li {{ border: 1px solid #e3e8ef; border-radius: 8px; background: #ffffff; padding: 14px; }}
    .item-head {{ display: flex; justify-content: space-between; gap: 12px; align-items: baseline; margin-bottom: 6px; }}
    .label {{ color: #17212b; font-weight: 800; }}
    .value {{ color: #17212b; font-weight: 700; }}
    .description {{ color: var(--muted); margin: 0; }}
    .finding {{ border-left: 5px solid #64748b; margin: 16px 0; background: #ffffff; }}
    .finding header {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; margin-bottom: 12px; }}
    .finding dl {{ display: grid; grid-template-columns: 130px 1fr; gap: 10px 16px; margin: 0; }}
    .badge {{ display: inline-block; border-radius: 999px; padding: 3px 10px; color: #ffffff; font-size: 0.8rem; font-weight: 800; white-space: nowrap; }}
    .severity-info {{ border-left-color: #64748b; }}
    .severity-low {{ border-left-color: #15803d; }}
    .severity-medium {{ border-left-color: var(--warn); }}
    .severity-high {{ border-left-color: var(--danger); }}
    .badge-info {{ background: #64748b; }}
    .badge-low {{ background: #15803d; }}
    .badge-medium {{ background: var(--warn); }}
    .badge-high {{ background: var(--danger); }}
    .status-found {{ color: #15803d; }}
    .status-missing {{ color: var(--danger); }}
    .status-unknown {{ color: var(--unknown); }}
    .next-steps li {{ margin: 7px 0; }}
    .empty-state {{ color: #374151; }}
    @media (max-width: 720px) {{
      main {{ padding: 20px 12px; }}
      .report {{ padding: 20px; }}
      .assessment-grid, .meta, .finding dl {{ grid-template-columns: 1fr; }}
      .finding header, .item-head {{ display: block; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="report">
      <p class="eyebrow">RepoTrust 정적 HTML 리포트</p>
      <h1>저장소 신뢰도 점검 결과</h1>
      <p class="lead">이 리포트는 점수뿐 아니라 검사 완성도, 판단 신뢰도, 확인된 근거와 확인하지 못한 근거를 함께 보여줍니다.</p>

      <div class="assessment-grid">
        <section class="score-panel" aria-label="Assessment">
          <h2>Assessment</h2>
          <p class="verdict">{html.escape(_assessment_label(assessment.verdict))}</p>
          <div class="score">
            <strong>{result.score.total}/{result.score.max_score}</strong>
            <span>{html.escape(result.score.grade)} · {html.escape(_risk_label_ko(result.score.risk_label))}</span>
          </div>
          <p>{html.escape(assessment.summary)}</p>
          <div class="pill-row">
            <span class="pill">Confidence: {html.escape(_confidence_label(assessment.confidence))}</span>
            <span class="pill">Coverage: {html.escape(_coverage_label(assessment.coverage))}</span>
            <span class="pill">Verdict ID: <code>{html.escape(assessment.verdict)}</code></span>
          </div>
        </section>
        <section class="section-panel" aria-label="Assessment Process">
          <h2>Assessment Process</h2>
          <ul class="next-steps">
{process_items}
          </ul>
        </section>
      </div>

      <dl class="meta">
        <dt>검사 대상</dt><dd><code>{html.escape(result.target.raw)}</code></dd>
        <dt>대상 종류</dt><dd>{html.escape(_target_kind_ko(result.target.kind))} <code>{html.escape(result.target.kind)}</code></dd>
        <dt>생성 시각</dt><dd><code>{html.escape(result.generated_at)}</code></dd>
      </dl>

      <h2>Evidence Matrix</h2>
      <p>확인됨은 실제 근거를 찾았다는 뜻이고, 없음은 확인 가능한 범위에서 찾지 못했다는 뜻입니다. 확인 못함은 API 실패나 parse-only처럼 근거 자체를 보지 못한 상태입니다.</p>
      <ul class="evidence-grid">
{evidence_items}
      </ul>

      <h2>Risk Breakdown</h2>
      <p>각 영역은 100점 만점입니다. 총점은 finding 감점 뒤 scan completeness cap이 적용될 수 있습니다.</p>
      <ul class="data-list">
{category_items}
      </ul>

      <h2>Why This Score</h2>
      <section class="section-panel">
        <ul class="next-steps">
{reason_items}
        </ul>
      </section>

      <h2>Purpose Profiles</h2>
      <p>같은 finding을 설치, dependency 채택, AI agent 위임 목적별로 다시 읽은 판단입니다.</p>
      <ul class="profile-grid">
{profile_items}
      </ul>

      <h2>Prioritized Findings</h2>
      <p>Assessment와 Purpose Profiles의 priority ID는 상위 3개 항목만 요약합니다. 이 섹션은 전체 {finding_count}개 finding을 심각도 순으로 모두 나열하며, 각 항목은 안정적인 ID, 설명, 실제 근거, 추천 조치를 함께 보여줍니다.</p>
{findings}

      <h2>Next Actions</h2>
      <section class="section-panel">
        <ul class="next-steps">
{next_action_items}
        </ul>
      </section>

      <h2>Report Metadata</h2>
      <ul class="data-list">
        <li>
          <div class="item-head">
            <span class="label">JSON schema</span>
            <span class="value">{html.escape(JSON_SCHEMA_VERSION)}</span>
          </div>
          <p class="description">이 리포트의 JSON 출력에는 machine-readable assessment와 purpose profiles가 포함됩니다.</p>
        </li>
      </ul>
    </section>
  </main>
</body>
</html>
"""


def _profile_markdown(key: str, profile: AssessmentProfile) -> list[str]:
    lines = [
        f"### {PROFILE_LABELS.get(key, key)}",
        "",
        f"- Verdict: `{profile.verdict}`",
        f"- Summary: {profile.summary}",
        f"- Priority finding IDs: `{', '.join(profile.priority_finding_ids) or 'none'}`",
        "",
        "Reasons:",
        "",
    ]
    for reason in profile.reasons:
        lines.append(f"- {reason}")
    lines.extend(["", "Next actions:", ""])
    for action in profile.next_actions:
        lines.append(f"- {action}")
    lines.append("")
    return lines


def _profile_html(key: str, profile: AssessmentProfile) -> str:
    reasons = "\n".join(
        f"              <li>{html.escape(reason)}</li>" for reason in profile.reasons
    )
    actions = "\n".join(
        f"              <li>{html.escape(action)}</li>" for action in profile.next_actions
    )
    priority = ", ".join(profile.priority_finding_ids) or "none"
    return f"""        <li>
          <h3>{html.escape(PROFILE_LABELS_KO.get(key, key))}</h3>
          <p class="profile-verdict" style="color: {_verdict_color(profile.verdict)};">{html.escape(_assessment_label(profile.verdict))}</p>
          <p class="description">{html.escape(profile.summary)}</p>
          <p><strong>Priority findings:</strong> <code>{html.escape(priority)}</code></p>
          <details>
            <summary>판단 이유와 다음 조치</summary>
            <ul>
{reasons}
            </ul>
            <ul>
{actions}
            </ul>
          </details>
        </li>"""


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
    severity_label = _severity_ko(finding.severity.value)
    category_label = _category_label(finding.category.value)
    category = html.escape(finding.category.value)
    finding_id = html.escape(finding.id)
    return f"""        <article class="finding severity-{severity}" data-severity="{severity}" data-category="{category}">
          <header>
            <div>
              <h3>{html.escape(_finding_title(finding))}</h3>
              <p class="description"><code>{finding_id}</code></p>
            </div>
            <span class="badge badge-{severity}">{html.escape(severity_label)}</span>
          </header>
          <dl>
            <dt>검사 영역</dt><dd>{html.escape(category_label)} <code>{category}</code></dd>
            <dt>심각도</dt><dd>{html.escape(severity_label)} <code>{severity}</code></dd>
            <dt>설명</dt><dd>{html.escape(_finding_explanation(finding))}</dd>
            <dt>원문 메시지</dt><dd>{html.escape(finding.message)}</dd>
            <dt>실제 근거</dt><dd>{html.escape(finding.evidence)}</dd>
            <dt>추천 조치</dt><dd>{html.escape(finding.recommendation)}</dd>
          </dl>
        </article>"""


def _evidence_row_html(row: EvidenceRow) -> str:
    status_label = EVIDENCE_STATUS_LABELS.get(row.status, row.status)
    description = _evidence_status_description(row)
    return f"""        <li>
          <div class="item-head">
            <span class="label">{html.escape(row.label)} <code>{html.escape(row.key)}</code></span>
            <span class="value status-{html.escape(row.status)}">{html.escape(status_label)}</span>
          </div>
          <p><code>{html.escape(row.value)}</code></p>
          <p class="description">{html.escape(description)}</p>
        </li>"""


def _evidence_status_description(row: EvidenceRow) -> str:
    if row.status == "unknown":
        return "이번 실행에서는 이 신호를 확인할 충분한 원격 근거를 가져오지 못했습니다."
    if row.status == "found":
        return "이번 실행에서 실제 근거를 확인했습니다."
    return "이번 실행에서 확인 가능한 범위 안에서는 찾지 못했습니다."


def _assessment_process(result: ScanResult) -> list[str]:
    assessment = result.assessment
    process = [
        f"Target parsed as {result.target.kind}.",
        f"Coverage classified as {assessment.coverage}; confidence is {assessment.confidence}.",
    ]
    if assessment.coverage == "full":
        process.append("All enabled evidence sources for this target type were evaluated.")
    elif assessment.coverage == "partial":
        process.append("Some evidence sources failed, so affected signals are marked unknown.")
    elif assessment.coverage == "metadata_only":
        process.append("Repository files were not fetched; this is not a file-level trust assessment.")
    else:
        process.append("Remote scan failed before repository file evidence could be evaluated.")
    process.append("Findings were scored, then any scan completeness cap was applied.")
    return process


def _assessment_label(verdict: str) -> str:
    return ASSESSMENT_LABELS.get(verdict, verdict)


def _confidence_label(confidence: str) -> str:
    return CONFIDENCE_LABELS.get(confidence, confidence)


def _coverage_label(coverage: str) -> str:
    return COVERAGE_LABELS.get(coverage, coverage)


def _verdict_color(verdict: str) -> str:
    if verdict == "do_not_install_before_review":
        return "var(--danger)"
    if verdict in {"insufficient_evidence", "usable_after_review"}:
        return "var(--warn)"
    return "var(--accent)"


def _finding_sort_key(finding: Finding) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return severity_rank.get(finding.severity.value, 9), finding.id


def _category_html(category: str, score: int) -> str:
    label = _category_label(category)
    description = _category_description(category, score)
    return f"""          <li>
            <div class="item-head">
              <span class="label">{html.escape(label)} <code>{html.escape(category)}</code></span>
              <span class="value">{score}/100</span>
            </div>
            <p class="description">{html.escape(description)}</p>
          </li>"""


def _category_label(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def _category_description(category: str, score: int) -> str:
    base = CATEGORY_DESCRIPTIONS.get(
        category,
        "이 영역의 신뢰 신호를 점검합니다.",
    )
    if score >= 90:
        suffix = "현재 점수는 양호합니다."
    elif score >= 70:
        suffix = "일부 보완할 점이 있습니다."
    else:
        suffix = "우선적으로 확인해야 할 약점이 있습니다."
    return f"{base} {suffix}"


def _finding_title(finding: Finding) -> str:
    reference = get_finding_reference(finding.id)
    return reference.title if reference else finding.message


def _finding_explanation(finding: Finding) -> str:
    reference = get_finding_reference(finding.id)
    return reference.explanation if reference else finding.message


def _severity_ko(severity: str) -> str:
    return SEVERITY_LABELS.get(severity, severity)


def _risk_label_ko(risk_label: str) -> str:
    return RISK_LABELS.get(risk_label, risk_label)


def _target_kind_ko(kind: str) -> str:
    return TARGET_KIND_LABELS.get(kind, kind)
