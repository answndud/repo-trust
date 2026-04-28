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
    title = html.escape(f"RepoTrust 리포트 - {result.target.raw}")
    verdict = _score_verdict(result)
    category_items = "\n".join(_category_html(category, score) for category, score in result.score.categories.items())
    detected_items = "\n".join(_detected_file_html(key, value) for key, value in result.detected_files.to_dict().items())
    findings = "\n".join(_finding_html(finding) for finding in result.findings)
    if not findings:
        findings = """        <article class="empty-state">
          <h3>현재 활성화된 검사에서 문제를 찾지 못했습니다.</h3>
          <p>README, 설치 명령, 보안 정책, CI, dependency 관련 기본 신호가 v1 기준을 통과했습니다. 그래도 실제 도입 전에는 라이선스, 운영 정책, 내부 보안 기준을 별도로 확인하세요.</p>
        </article>"""

    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: light; --ink: #17212b; --muted: #5c6670; --line: #d9dee5; --soft: #f4f6f8; --panel: #ffffff; --accent: #0f766e; --warn: #9a6700; --danger: #b42318; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; margin: 0; color: var(--ink); background: #eef2f5; line-height: 1.65; }}
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
    .summary-grid {{ display: grid; grid-template-columns: minmax(220px, 0.8fr) minmax(280px, 1.2fr); gap: 18px; margin: 24px 0; }}
    .score-panel, .guide-panel, .section-panel, .finding, .empty-state {{ border: 1px solid var(--line); border-radius: 8px; background: #fbfcfd; padding: 18px; }}
    .score {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 10px; }}
    .score strong {{ font-size: 2.4rem; color: #0f172a; }}
    .score span {{ color: var(--muted); font-weight: 700; }}
    .verdict {{ font-weight: 700; color: {verdict["color"]}; }}
    .meta {{ display: grid; grid-template-columns: 150px 1fr; gap: 8px 16px; margin: 18px 0 0; }}
    .meta dt, .finding dt {{ font-weight: 700; color: #374151; }}
    .meta dd, .finding dd {{ margin: 0; }}
    .data-list {{ display: grid; gap: 12px; padding-left: 0; list-style: none; }}
    .data-list li {{ border: 1px solid #e3e8ef; border-radius: 8px; background: #ffffff; padding: 14px; }}
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
    .next-steps li {{ margin: 7px 0; }}
    .empty-state {{ color: #374151; }}
    @media (max-width: 720px) {{
      main {{ padding: 20px 12px; }}
      .report {{ padding: 20px; }}
      .summary-grid, .meta, .finding dl {{ grid-template-columns: 1fr; }}
      .finding header, .item-head {{ display: block; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="report">
      <p class="eyebrow">RepoTrust 정적 HTML 리포트</p>
      <h1>저장소 신뢰도 점검 결과</h1>
      <p class="lead">이 리포트는 저장소를 설치하거나 dependency로 추가하기 전에 확인해야 할 기본 신뢰 신호를 설명합니다. 점수만 보고 결정하지 말고, 아래의 발견 항목과 추천 조치를 함께 확인하세요.</p>

      <div class="summary-grid">
        <section class="score-panel" aria-label="전체 점수">
          <h2>전체 판단</h2>
          <div class="score">
            <strong>{result.score.total}/{result.score.max_score}</strong>
            <span>{html.escape(result.score.grade)} · {html.escape(_risk_label_ko(result.score.risk_label))}</span>
          </div>
          <p class="verdict">{html.escape(verdict["title"])}</p>
          <p>{html.escape(verdict["body"])}</p>
        </section>
        <section class="guide-panel" aria-label="읽는 방법">
          <h2>이 리포트 읽는 법</h2>
          <ul class="next-steps">
            <li><strong>전체 판단</strong>은 빠른 위험도 요약입니다.</li>
            <li><strong>검사 영역별 점수</strong>는 어떤 영역이 약한지 보여줍니다.</li>
            <li><strong>발견된 파일</strong>은 신뢰 판단에 사용한 실제 근거 파일입니다.</li>
            <li><strong>발견 항목</strong>은 지금 확인하거나 고쳐야 할 구체적인 문제입니다.</li>
          </ul>
        </section>
      </div>

      <dl class="meta">
        <dt>검사 대상</dt><dd><code>{html.escape(result.target.raw)}</code></dd>
        <dt>대상 종류</dt><dd>{html.escape(_target_kind_ko(result.target.kind))} <code>{html.escape(result.target.kind)}</code></dd>
        <dt>생성 시각</dt><dd><code>{html.escape(result.generated_at)}</code></dd>
      </dl>

      <h2>검사 영역별 점수</h2>
      <p>각 영역은 100점 만점입니다. 낮은 영역부터 확인하면 가장 먼저 보완할 지점을 찾기 쉽습니다.</p>
      <ul class="data-list">
{category_items}
      </ul>

      <h2>발견된 파일과 의미</h2>
      <p>아래 파일들은 RepoTrust가 신뢰 신호를 판단할 때 사용한 근거입니다. 없다고 해서 곧바로 위험하다는 뜻은 아니지만, 사용자가 직접 확인해야 할 항목이 늘어납니다.</p>
      <ul class="data-list">
{detected_items}
      </ul>

      <h2>발견 항목과 추천 조치</h2>
      <p>각 항목은 안정적인 ID, 심각도, 쉬운 설명, 실제 근거, 추천 조치를 포함합니다. <strong>high</strong>는 설치 전 반드시 확인하고, <strong>medium</strong>은 팀 정책에 맞게 보완 여부를 결정하세요.</p>
{findings}

      <h2>다음에 할 일</h2>
      <section class="section-panel">
        <ul class="next-steps">
          <li>심각도 <strong>high</strong> finding이 있으면 설치 명령을 그대로 실행하지 말고 README나 스크립트 내용을 먼저 검토하세요.</li>
          <li>보안 정책, CI, lockfile, Dependabot이 빠져 있으면 프로젝트 관리자가 보완할 수 있는지 확인하세요.</li>
          <li>GitHub URL을 <code>--remote</code> 없이 검사했다면 원격 내용은 가져오지 않은 것입니다. 실제 파일 기반 점검이 필요하면 로컬 checkout을 스캔하거나 <code>--remote</code>를 명시하세요.</li>
          <li>CI에서 사용하려면 <code>repo-trust . --format json --output report.json --fail-under 80</code>처럼 기준 점수를 설정하세요.</li>
        </ul>
      </section>
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
    severity_label = _severity_ko(finding.severity.value)
    category_label = _category_label(finding.category.value)
    return f"""        <article class="finding severity-{severity}">
          <header>
            <div>
              <h3>{html.escape(_finding_title(finding))}</h3>
              <p class="description"><code>{html.escape(finding.id)}</code></p>
            </div>
            <span class="badge badge-{severity}">{html.escape(severity_label)}</span>
          </header>
          <dl>
            <dt>검사 영역</dt><dd>{html.escape(category_label)} <code>{html.escape(finding.category.value)}</code></dd>
            <dt>심각도</dt><dd>{html.escape(severity_label)} <code>{severity}</code></dd>
            <dt>무슨 뜻인가요?</dt><dd>{html.escape(_finding_explanation(finding))}</dd>
            <dt>원문 메시지</dt><dd>{html.escape(finding.message)}</dd>
            <dt>실제 근거</dt><dd>{html.escape(finding.evidence)}</dd>
            <dt>추천 조치</dt><dd>{html.escape(finding.recommendation)}</dd>
          </dl>
        </article>"""


def _display_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "없음"
    return str(value) if value else "없음"


def _score_verdict(result: ScanResult) -> dict[str, str]:
    total = result.score.total
    high_count = sum(1 for finding in result.findings if finding.severity.value == "high")
    medium_count = sum(1 for finding in result.findings if finding.severity.value == "medium")
    if high_count:
        return {
            "title": "설치 전 반드시 확인이 필요합니다.",
            "body": f"high 심각도 항목이 {high_count}개 있습니다. README의 설치 명령이나 보안 관련 신호를 그대로 믿기 전에 근거와 추천 조치를 먼저 확인하세요.",
            "color": "var(--danger)",
        }
    if total >= 90:
        return {
            "title": "기본 신뢰 신호가 대체로 좋습니다.",
            "body": "v1 기준에서 큰 위험 신호는 적습니다. 그래도 dependency로 추가하기 전에는 라이선스와 조직 내부 정책을 별도로 확인하세요.",
            "color": "var(--accent)",
        }
    if total >= 75:
        return {
            "title": "사용 가능하지만 보완 확인이 필요합니다.",
            "body": f"medium 심각도 항목 {medium_count}개와 낮은 점수 영역을 확인하세요. 자동 설치나 CI 도입 전에는 발견 항목의 추천 조치를 검토하는 편이 좋습니다.",
            "color": "var(--warn)",
        }
    return {
        "title": "신뢰 신호가 부족합니다.",
        "body": "문서, 설치 안전성, 보안 정책, 프로젝트 관리 신호 중 여러 항목이 부족합니다. 초보자는 바로 설치하지 말고 로컬 격리 환경에서 검토하세요.",
        "color": "var(--danger)",
    }


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


def _detected_file_html(key: str, value: object) -> str:
    label = _detected_label(key)
    display = _display_value(value)
    description = _detected_description(key, value)
    return f"""          <li>
            <div class="item-head">
              <span class="label">{html.escape(label)} <code>{html.escape(key)}</code></span>
              <span class="value">{html.escape(display)}</span>
            </div>
            <p class="description">{html.escape(description)}</p>
          </li>"""


def _category_label(category: str) -> str:
    return {
        "readme_quality": "README 품질",
        "install_safety": "설치 안전성",
        "security_posture": "보안 태세",
        "project_hygiene": "프로젝트 관리 상태",
        "target": "검사 대상",
    }.get(category, category)


def _category_description(category: str, score: int) -> str:
    base = {
        "readme_quality": "README가 프로젝트 목적, 설치 방법, 사용 방법을 충분히 설명하는지 봅니다.",
        "install_safety": "README의 설치 명령이 위험한 원격 스크립트 실행이나 검증 없는 설치를 유도하는지 봅니다.",
        "security_posture": "SECURITY.md, CI, Dependabot, lockfile처럼 보안과 재현성을 돕는 신호를 봅니다.",
        "project_hygiene": "LICENSE, dependency manifest 등 프로젝트를 dependency로 쓰기 전 확인할 관리 신호를 봅니다.",
        "target": "로컬 경로인지 GitHub URL인지, 원격 내용을 실제로 가져왔는지 같은 검사 대상 상태를 봅니다.",
    }.get(category, "이 영역의 신뢰 신호를 점검합니다.")
    if score >= 90:
        suffix = "현재 점수는 양호합니다."
    elif score >= 70:
        suffix = "일부 보완할 점이 있습니다."
    else:
        suffix = "우선적으로 확인해야 할 약점이 있습니다."
    return f"{base} {suffix}"


def _detected_label(key: str) -> str:
    return {
        "readme": "README",
        "license": "라이선스",
        "security": "보안 정책",
        "ci_workflows": "CI workflow",
        "dependency_manifests": "Dependency manifest",
        "lockfiles": "Lockfile",
        "dependabot": "Dependabot 설정",
    }.get(key, key)


def _detected_description(key: str, value: object) -> str:
    present = bool(value)
    if isinstance(value, list):
        present = bool(value)
    descriptions = {
        "readme": (
            "사용자가 설치와 사용 방법을 이해할 수 있는 핵심 문서입니다."
            if present
            else "README가 없으면 목적, 설치 방법, 사용 방법을 사용자가 직접 추정해야 합니다."
        ),
        "license": (
            "라이선스 파일이 있어 dependency 사용 조건을 확인할 수 있습니다."
            if present
            else "라이선스가 없으면 회사나 공개 프로젝트에서 사용할 수 있는지 판단하기 어렵습니다."
        ),
        "security": (
            "취약점 신고와 보안 대응 경로를 확인할 수 있습니다."
            if present
            else "보안 문제를 어디로 신고해야 하는지 명확하지 않습니다."
        ),
        "ci_workflows": (
            "자동 테스트나 검증이 실행될 가능성이 있습니다."
            if present
            else "자동 검증 신호가 없어 변경 품질을 판단하기 어렵습니다."
        ),
        "dependency_manifests": (
            "프로젝트가 어떤 패키지와 도구 체계를 쓰는지 확인할 수 있습니다."
            if present
            else "dependency 선언 파일을 찾지 못해 설치 구조를 판단하기 어렵습니다."
        ),
        "lockfiles": (
            "고정된 dependency 버전으로 재현 가능한 설치에 도움이 됩니다."
            if present
            else "lockfile이 없으면 같은 명령을 실행해도 시간이 지나며 다른 dependency가 설치될 수 있습니다."
        ),
        "dependabot": (
            "dependency 업데이트를 자동으로 감지하는 설정이 있습니다."
            if present
            else "dependency 업데이트 관리가 자동화되어 있는지 확인되지 않습니다."
        ),
    }
    return descriptions.get(key, "검사 중 발견한 파일 신호입니다.")


def _finding_title(finding: Finding) -> str:
    return {
        "readme.missing": "README가 없습니다.",
        "readme.no_project_purpose": "README에 프로젝트 목적 설명이 부족합니다.",
        "install.no_commands": "README에서 설치 명령을 찾지 못했습니다.",
        "install.risky.shell_pipe_install": "원격 스크립트를 바로 shell로 실행하는 설치 명령이 있습니다.",
        "install.risky.process_substitution_shell": "process substitution으로 원격 스크립트를 실행합니다.",
        "install.risky.python_inline_execution": "Python inline 실행 설치 명령이 있습니다.",
        "install.risky.vcs_direct_install": "Git 저장소에서 직접 설치하는 명령이 있습니다.",
        "security.no_policy": "보안 정책 파일이 없습니다.",
        "security.no_ci": "CI workflow를 찾지 못했습니다.",
        "security.no_dependabot": "Dependabot 설정을 찾지 못했습니다.",
        "security.no_lockfile": "Lockfile을 찾지 못했습니다.",
        "hygiene.no_license": "라이선스 파일이 없습니다.",
        "target.github_not_fetched": "GitHub URL을 원격 조회 없이 파싱만 했습니다.",
        "remote.github_metadata_collected": "GitHub 원격 메타데이터를 수집했습니다.",
        "remote.github_rate_limited": "GitHub API rate limit에 걸렸습니다.",
        "remote.github_unauthorized": "GitHub API 인증 또는 권한 확인에 실패했습니다.",
        "remote.github_not_found": "GitHub 저장소를 찾을 수 없거나 볼 수 없습니다.",
        "remote.github_api_error": "GitHub API에서 예상하지 못한 오류가 발생했습니다.",
        "remote.github_partial_scan": "GitHub 원격 조회가 일부만 완료됐습니다.",
        "remote.github_archived": "GitHub 저장소가 archived 상태입니다.",
        "remote.github_issues_disabled": "GitHub Issues가 비활성화되어 있습니다.",
        "remote.readme_content_unavailable": "원격 README 내용 확인에 실패했습니다.",
        "target.local_path_missing": "로컬 경로를 찾을 수 없습니다.",
        "readme.too_short": "README가 너무 짧습니다.",
        "readme.no_install_section": "README에 설치 섹션이 없습니다.",
        "readme.no_usage_section": "README에 사용 예시 섹션이 없습니다.",
        "readme.no_maintenance_signal": "README에 유지보수/지원 안내가 부족합니다.",
        "install.no_readme_to_audit": "README가 없어 설치 안전성을 확인할 수 없습니다.",
        "hygiene.no_manifest": "Dependency manifest를 찾지 못했습니다.",
    }.get(finding.id, finding.message)


def _finding_explanation(finding: Finding) -> str:
    explanations = {
        "target.local_path_missing": "입력한 경로가 존재하지 않거나 디렉터리가 아닙니다. RepoTrust는 로컬 저장소 폴더를 기준으로 파일을 검사하므로 올바른 경로를 다시 지정해야 합니다.",
        "target.github_not_fetched": "기본 GitHub URL 스캔은 안전하게 URL만 해석합니다. 저장소 파일을 clone하거나 API로 가져오지 않았으므로 README, LICENSE, CI 같은 실제 파일 기반 판단은 아직 하지 않은 상태입니다.",
        "readme.missing": "README는 프로젝트 목적, 설치 방법, 사용 방법을 처음 확인하는 문서입니다. README가 없으면 사용자가 안전한 설치 경로를 판단하기 어렵습니다.",
        "readme.too_short": "README 길이가 너무 짧아 프로젝트 목적, 설치 방법, 사용 예시, 문제 해결 방법을 충분히 설명한다고 보기 어렵습니다.",
        "readme.no_project_purpose": "README 상단에서 이 프로젝트가 무엇을 하는지, 누가 쓰는지, 어떤 문제를 해결하는지 명확히 설명하지 않습니다.",
        "readme.no_install_section": "초보자가 따라 할 수 있는 설치 섹션을 찾지 못했습니다. 설치 방법이 흩어져 있거나 명확하지 않을 수 있습니다.",
        "readme.no_usage_section": "설치 후 어떤 명령을 실행해야 하는지, 최소 사용 예시가 무엇인지 확인하기 어렵습니다.",
        "readme.no_maintenance_signal": "이슈 제보, 기여 방법, changelog, release notes 같은 유지보수 신호가 README에 보이지 않습니다.",
        "install.no_readme_to_audit": "README가 없어서 설치 명령이 안전한지 검사할 수 없습니다. 사용자는 다른 파일이나 스크립트를 직접 찾아봐야 합니다.",
        "install.no_commands": "README에서 복사해서 실행할 수 있는 설치 명령을 찾지 못했습니다. 자동화나 초보자 사용 흐름이 불명확합니다.",
        "install.risky.shell_pipe_install": "curl이나 wget으로 받은 원격 스크립트를 바로 shell에 넘기는 방식입니다. 실행 전에 스크립트 내용을 검토하기 어렵고, 원격 내용이 바뀌면 설치 결과도 바뀔 수 있습니다.",
        "install.risky.process_substitution_shell": "원격 스크립트를 process substitution으로 shell에 직접 실행합니다. 일반적인 파일 검토 단계를 건너뛰므로 설치 전 확인이 어렵습니다.",
        "install.risky.python_inline_execution": "README가 Python 한 줄 실행으로 설치나 설정을 처리합니다. 실행되는 코드가 길거나 복잡하면 사용자가 의미를 검토하기 어렵습니다.",
        "install.risky.vcs_direct_install": "패키지 레지스트리의 고정된 배포본이 아니라 Git 저장소에서 직접 설치합니다. branch나 commit이 고정되지 않으면 시간이 지나며 설치 결과가 달라질 수 있습니다.",
        "security.no_policy": "SECURITY.md가 없으면 취약점 신고 방법, 지원 버전, 보안 대응 절차를 알기 어렵습니다.",
        "security.no_dependabot": "Dependabot이나 유사한 dependency 업데이트 자동화 신호를 찾지 못했습니다. 오래된 dependency가 방치될 가능성을 별도로 확인해야 합니다.",
        "security.no_ci": "GitHub Actions workflow를 찾지 못했습니다. 변경 시 테스트나 lint가 자동으로 실행되는지 확인되지 않습니다.",
        "security.no_lockfile": "Dependency manifest는 있지만 lockfile이 없습니다. 같은 설치 명령을 나중에 실행했을 때 다른 하위 dependency가 설치될 수 있습니다.",
        "hygiene.no_license": "라이선스 파일이 없으면 재사용, 배포, 회사 프로젝트 dependency 사용 가능 여부를 판단하기 어렵습니다.",
        "hygiene.no_manifest": "표준 dependency manifest를 찾지 못했습니다. 이 저장소가 어떤 패키지 생태계와 설치 방식을 쓰는지 확인하기 어렵습니다.",
        "remote.github_metadata_collected": "명시적으로 --remote를 사용해서 GitHub API에서 읽기 전용 메타데이터를 가져왔다는 정보성 항목입니다.",
        "remote.github_rate_limited": "GitHub API 호출 한도를 초과해 원격 조회를 완료하지 못했습니다. 잠시 후 다시 실행하거나 GITHUB_TOKEN을 설정해야 합니다.",
        "remote.github_unauthorized": "private 저장소이거나 token 권한이 부족해 GitHub API가 정보를 제공하지 않았습니다.",
        "remote.github_not_found": "owner/repo URL이 잘못됐거나, 저장소가 private이라 현재 인증 정보로 볼 수 없습니다.",
        "remote.github_api_error": "GitHub API가 예기치 않은 오류를 반환했습니다. 네트워크, GitHub 상태, 저장소 권한을 다시 확인해야 합니다.",
        "remote.github_partial_scan": "GitHub API 일부 endpoint가 실패했거나 접근할 수 없어 리포트가 제한된 정보로 만들어졌습니다.",
        "remote.github_archived": "archived 저장소는 일반적으로 더 이상 유지보수되지 않는 읽기 전용 상태입니다. 새 dependency로 채택하기 전에 maintained fork나 대안을 확인하세요.",
        "remote.github_issues_disabled": "Issues가 꺼져 있으면 버그 제보, 사용 질문, 지원 경로가 GitHub에 없을 수 있습니다.",
        "remote.readme_content_unavailable": "README 파일은 발견했지만 내용을 가져오지 못해 README 품질과 설치 명령 안전성을 완전히 검사하지 못했습니다.",
    }
    return explanations.get(finding.id, finding.message)


def _severity_ko(severity: str) -> str:
    return {
        "info": "정보",
        "low": "낮음",
        "medium": "중간",
        "high": "높음",
    }.get(severity, severity)


def _risk_label_ko(risk_label: str) -> str:
    return {
        "Low risk": "낮은 위험",
        "Moderate-low risk": "낮거나 중간 수준의 위험",
        "Moderate risk": "중간 위험",
        "High risk": "높은 위험",
    }.get(risk_label, risk_label)


def _target_kind_ko(kind: str) -> str:
    return {
        "local": "로컬 저장소",
        "github": "GitHub URL",
    }.get(kind, kind)
