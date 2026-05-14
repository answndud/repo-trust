from __future__ import annotations

import html
import json

from .evidence import EvidenceRow, evidence_rows
from .install_advice import readme_install_commands, safe_commands
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

DETECTED_LABELS = {
    "readme": "README",
    "license": "라이선스",
    "security": "보안 정책",
    "ci_workflows": "CI workflow",
    "dependency_manifests": "Dependency manifest",
    "lockfiles": "Lockfile",
    "dependabot": "Dependabot 설정",
}

DETECTED_DESCRIPTIONS = {
    "readme": (
        "사용자가 설치와 사용 방법을 이해할 수 있는 핵심 문서입니다.",
        "README가 없으면 목적, 설치 방법, 사용 방법을 사용자가 직접 추정해야 합니다.",
    ),
    "license": (
        "라이선스 파일이 있어 dependency 사용 조건을 확인할 수 있습니다.",
        "라이선스가 없으면 회사나 공개 프로젝트에서 사용할 수 있는지 판단하기 어렵습니다.",
    ),
    "security": (
        "취약점 신고와 보안 대응 경로를 확인할 수 있습니다.",
        "보안 문제를 어디로 신고해야 하는지 명확하지 않습니다.",
    ),
    "ci_workflows": (
        "자동 테스트나 검증이 실행될 가능성이 있습니다.",
        "자동 검증 신호가 없어 변경 품질을 판단하기 어렵습니다.",
    ),
    "dependency_manifests": (
        "프로젝트가 어떤 패키지와 도구 체계를 쓰는지 확인할 수 있습니다.",
        "dependency 선언 파일을 찾지 못해 설치 구조를 판단하기 어렵습니다.",
    ),
    "lockfiles": (
        "고정된 dependency 버전으로 재현 가능한 설치에 도움이 됩니다.",
        "lockfile이 없으면 같은 명령을 실행해도 시간이 지나며 다른 dependency가 설치될 수 있습니다.",
    ),
    "dependabot": (
        "dependency 업데이트를 자동으로 감지하는 설정이 있습니다.",
        "dependency 업데이트 관리가 자동화되어 있는지 확인되지 않습니다.",
    ),
}

FINDING_TITLES = {
    "readme.missing": "README가 없습니다.",
    "readme.no_project_purpose": "README에 프로젝트 목적 설명이 부족합니다.",
    "install.no_commands": "README에서 설치 명령을 찾지 못했습니다.",
    "install.risky.shell_pipe_install": "원격 스크립트를 바로 shell로 실행하는 설치 명령이 있습니다.",
    "install.risky.process_substitution_shell": "process substitution으로 원격 스크립트를 실행합니다.",
    "install.risky.python_inline_execution": "Python inline 실행 설치 명령이 있습니다.",
    "install.risky.uses_sudo": "설치 명령에 sudo가 포함되어 있습니다.",
    "install.risky.global_package_install": "전역 패키지 설치 명령이 있습니다.",
    "install.risky.vcs_direct_install": "Git 저장소에서 직접 설치하는 명령이 있습니다.",
    "install.risky.marks_downloaded_code_executable": "다운로드한 코드에 실행 권한을 부여합니다.",
    "dependency.npm_lifecycle_script": "npm 설치 lifecycle script가 있습니다.",
    "dependency.unpinned_node_dependency": "Node dependency가 exact version으로 고정되어 있지 않습니다.",
    "dependency.unpinned_python_dependency": "Python dependency가 exact version으로 고정되어 있지 않습니다.",
    "security.no_policy": "보안 정책 파일이 없습니다.",
    "security.no_ci": "CI workflow를 찾지 못했습니다.",
    "security.no_dependabot": "Dependabot 설정을 찾지 못했습니다.",
    "security.no_lockfile": "Lockfile을 찾지 못했습니다.",
    "hygiene.no_license": "라이선스 파일이 없습니다.",
    "target.github_not_fetched": "GitHub URL을 원격 조회 없이 파싱만 했습니다.",
    "target.github_subpath_unsupported": "GitHub subpath URL은 하위 폴더 단위로 검사하지 않습니다.",
    "remote.github_metadata_collected": "GitHub 원격 메타데이터를 수집했습니다.",
    "remote.github_rate_limited": "GitHub API rate limit에 걸렸습니다.",
    "remote.github_unauthorized": "GitHub API 인증 또는 권한 확인에 실패했습니다.",
    "remote.github_not_found": "GitHub 저장소를 찾을 수 없거나 볼 수 없습니다.",
    "remote.github_api_error": "GitHub API에서 예상하지 못한 오류가 발생했습니다.",
    "remote.github_partial_scan": "GitHub 원격 조회가 일부만 완료됐습니다.",
    "remote.github_archived": "GitHub 저장소가 archived 상태입니다.",
    "remote.github_issues_disabled": "GitHub Issues가 비활성화되어 있습니다.",
    "remote.release_or_tag_stale": "최신 release 또는 tag가 오래됐습니다.",
    "remote.readme_content_unavailable": "원격 README 내용 확인에 실패했습니다.",
    "target.local_path_missing": "로컬 경로를 찾을 수 없습니다.",
    "readme.too_short": "README가 너무 짧습니다.",
    "readme.no_install_section": "README에 설치 섹션이 없습니다.",
    "readme.no_usage_section": "README에 사용 예시 섹션이 없습니다.",
    "readme.no_maintenance_signal": "README에 유지보수/지원 안내가 부족합니다.",
    "install.no_readme_to_audit": "README가 없어 설치 안전성을 확인할 수 없습니다.",
    "hygiene.no_manifest": "Dependency manifest를 찾지 못했습니다.",
}

FINDING_EXPLANATIONS = {
    "target.local_path_missing": "입력한 경로가 존재하지 않거나 디렉터리가 아닙니다. RepoTrust는 로컬 저장소 폴더를 기준으로 파일을 검사하므로 올바른 경로를 다시 지정해야 합니다.",
    "target.github_not_fetched": "GitHub URL을 원격 조회 없이 파싱만 한 실행입니다. 저장소를 clone하거나 GitHub API로 가져오지 않았으므로 README, LICENSE, CI 같은 실제 파일 기반 판단은 아직 제한적입니다.",
    "target.github_subpath_unsupported": "GitHub tree/blob URL의 하위 경로는 파싱하지만, 현재 remote scan은 해당 하위 폴더만 따로 검사하지 않습니다. 리포트는 repository root 신호와 subpath 미지원 finding을 함께 보여줍니다.",
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
    "install.risky.uses_sudo": "설치 안내가 관리자 권한으로 명령을 실행하도록 요구합니다. 설치 스크립트나 패키지가 시스템 전체에 영향을 줄 수 있으므로 실행 전 내용을 더 엄격하게 검토해야 합니다.",
    "install.risky.global_package_install": "npm이나 yarn 전역 설치는 사용자 환경 전체에 명령과 dependency를 추가합니다. 프로젝트별 격리 환경이나 고정된 실행 방식을 우선 확인해야 합니다.",
    "install.risky.vcs_direct_install": "패키지 레지스트리의 고정된 배포본이 아니라 Git 저장소에서 직접 설치합니다. branch나 commit이 고정되지 않으면 시간이 지나며 설치 결과가 달라질 수 있습니다.",
    "install.risky.marks_downloaded_code_executable": "설치 안내가 파일에 실행 권한을 부여하도록 요구합니다. 다운로드한 파일이나 생성된 스크립트의 출처와 내용을 확인한 뒤 실행해야 합니다.",
    "dependency.npm_lifecycle_script": "npm install lifecycle script는 패키지 설치 중 자동 실행될 수 있습니다. 저장소를 설치하거나 AI agent에게 맡기기 전에 script 내용을 직접 검토해야 합니다.",
    "dependency.unpinned_node_dependency": "Node dependency version range나 tag는 시간이 지나며 다른 버전을 설치할 수 있습니다. lockfile과 업데이트 정책을 함께 확인해야 합니다.",
    "dependency.unpinned_python_dependency": "Python dependency version range나 미고정 선언은 시간이 지나며 다른 버전을 설치할 수 있습니다. lockfile과 업데이트 정책을 함께 확인해야 합니다.",
    "security.no_policy": "SECURITY.md가 없으면 취약점 신고 방법, 지원 버전, 보안 대응 절차를 알기 어렵습니다.",
    "security.no_dependabot": "Dependabot이나 유사한 dependency 업데이트 자동화 신호를 찾지 못했습니다. 오래된 dependency가 방치될 가능성을 별도로 확인해야 합니다.",
    "security.no_ci": "GitHub Actions workflow를 찾지 못했습니다. 변경 시 테스트나 lint가 자동으로 실행되는지 확인되지 않습니다.",
    "security.no_lockfile": "Dependency manifest는 있지만 lockfile이 없습니다. 같은 설치 명령을 나중에 실행했을 때 다른 하위 dependency가 설치될 수 있습니다.",
    "hygiene.no_license": "라이선스 파일이 없으면 재사용, 배포, 회사 프로젝트 dependency 사용 가능 여부를 판단하기 어렵습니다.",
    "hygiene.no_manifest": "표준 dependency manifest를 찾지 못했습니다. 이 저장소가 어떤 패키지 생태계와 설치 방식을 쓰는지 확인하기 어렵습니다.",
    "remote.github_metadata_collected": "GitHub API에서 읽기 전용 메타데이터를 가져왔다는 정보성 항목입니다. 이 remote 조회는 `--remote`를 명시했을 때만 실행됩니다.",
    "remote.github_rate_limited": "GitHub API 호출 한도를 초과해 원격 조회를 완료하지 못했습니다. 잠시 후 다시 실행하거나 GITHUB_TOKEN을 설정해야 합니다.",
    "remote.github_unauthorized": "private 저장소이거나 token 권한이 부족해 GitHub API가 정보를 제공하지 않았습니다.",
    "remote.github_not_found": "owner/repo URL이 잘못됐거나, 저장소가 private이라 현재 인증 정보로 볼 수 없습니다.",
    "remote.github_api_error": "GitHub API가 예기치 않은 오류를 반환했습니다. 네트워크, GitHub 상태, 저장소 권한을 다시 확인해야 합니다.",
    "remote.github_partial_scan": "GitHub API 일부 endpoint가 실패했거나 접근할 수 없어 리포트가 제한된 정보로 만들어졌습니다.",
    "remote.github_archived": "archived 저장소는 일반적으로 더 이상 유지보수되지 않는 읽기 전용 상태입니다. 새 dependency로 채택하기 전에 maintained fork나 대안을 확인하세요.",
    "remote.github_issues_disabled": "Issues가 꺼져 있으면 버그 제보, 사용 질문, 지원 경로가 GitHub에 없을 수 있습니다.",
    "remote.release_or_tag_stale": "패키지로 배포될 가능성이 있는 저장소에서 최신 release나 tag의 기준 날짜가 freshness 기준보다 오래됐습니다. release가 없다는 사실만으로 감점하지 않고, 확인 가능한 release/tag 날짜가 오래된 경우에만 낮은 심각도로 표시합니다.",
    "remote.readme_content_unavailable": "README 파일은 발견했지만 내용을 가져오지 못해 README 품질과 설치 명령 안전성을 완전히 검사하지 못했습니다.",
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
    safe_install_section = _safe_install_html(result)
    next_steps_section = _next_steps_html(result)
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
    .next-command {{ border: 1px solid #b6d9d3; border-left: 4px solid var(--accent); border-radius: 8px; background: #f0faf8; padding: 12px 14px; margin: 8px 0 18px; }}
    .next-command code {{ display: inline-block; background: #ffffff; border: 1px solid #c7e5df; padding: 6px 8px; }}
    .command-list {{ display: grid; gap: 8px; padding-left: 0; list-style: none; }}
    .command-list li {{ border: 1px solid #e3e8ef; border-radius: 6px; background: #ffffff; padding: 8px 10px; }}
    .next-steps-plan {{ border: 1px solid #d8e5f3; border-left: 4px solid #2563eb; border-radius: 8px; background: #f7fbff; padding: 14px; white-space: pre-wrap; overflow-wrap: anywhere; font: 0.94rem/1.56 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
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
    .finding-actions {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0; }}
    .copy-button {{ border: 1px solid var(--line); border-radius: 6px; background: #ffffff; color: #17212b; padding: 5px 8px; font: inherit; font-size: 0.84rem; font-weight: 800; cursor: pointer; }}
    .copy-button[data-copied="true"] {{ border-color: #15803d; color: #15803d; }}
    .finding-controls {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 14px 0 18px; }}
    .finding-controls button {{ border: 1px solid var(--line); border-radius: 6px; background: #ffffff; color: #17212b; padding: 7px 10px; font: inherit; font-size: 0.9rem; font-weight: 800; cursor: pointer; }}
    .finding-controls button[aria-pressed="true"] {{ background: #17212b; color: #ffffff; border-color: #17212b; }}
    .finding details {{ margin-top: 10px; }}
    .finding summary {{ cursor: pointer; color: #17212b; font-weight: 800; margin-bottom: 10px; }}
    .finding[hidden] {{ display: none; }}
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

{safe_install_section}

{next_steps_section}

      <h2>Purpose Profiles</h2>
      <p>같은 finding을 설치, dependency 채택, AI agent 위임 목적별로 다시 읽은 판단입니다.</p>
      <ul class="profile-grid">
{profile_items}
      </ul>

      <h2>Prioritized Findings</h2>
      <p>Assessment와 Purpose Profiles의 priority ID는 상위 3개 항목만 요약합니다. 이 섹션은 전체 {finding_count}개 finding을 심각도 순으로 모두 나열하며, 각 항목은 안정적인 ID, 왜 위험한지, 지금 할 일, 수용 가능한 조건, 실제 근거를 함께 보여줍니다.</p>
      <div class="finding-controls" aria-label="Finding filters">
        <button type="button" data-filter-type="all" data-filter-value="all" aria-pressed="true">전체</button>
        <button type="button" data-filter-type="severity" data-filter-value="high" aria-pressed="false">높음</button>
        <button type="button" data-filter-type="severity" data-filter-value="medium" aria-pressed="false">중간</button>
        <button type="button" data-filter-type="severity" data-filter-value="low" aria-pressed="false">낮음</button>
        <button type="button" data-filter-type="severity" data-filter-value="info" aria-pressed="false">정보</button>
        <button type="button" data-filter-type="category" data-filter-value="install_safety" aria-pressed="false">설치 안전성</button>
        <button type="button" data-filter-type="category" data-filter-value="security_posture" aria-pressed="false">보안 태세</button>
        <button type="button" data-action="expand-findings">전체 펼치기</button>
        <button type="button" data-action="collapse-findings">전체 접기</button>
      </div>
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
    <script>
      const controls = document.querySelectorAll('[data-filter-type]');
      const findings = document.querySelectorAll('.finding');
      controls.forEach((button) => {{
        button.addEventListener('click', () => {{
          controls.forEach((control) => control.setAttribute('aria-pressed', 'false'));
          button.setAttribute('aria-pressed', 'true');
          const type = button.dataset.filterType;
          const value = button.dataset.filterValue;
          findings.forEach((finding) => {{
            const show = type === 'all' || finding.dataset[type] === value;
            finding.hidden = !show;
          }});
        }});
      }});
      document.querySelector('[data-action="expand-findings"]')?.addEventListener('click', () => {{
        document.querySelectorAll('.finding details').forEach((detail) => detail.open = true);
      }});
      document.querySelector('[data-action="collapse-findings"]')?.addEventListener('click', () => {{
        document.querySelectorAll('.finding details').forEach((detail) => detail.open = false);
      }});
      async function copyText(value) {{
        if (navigator.clipboard?.writeText) {{
          await navigator.clipboard.writeText(value);
          return;
        }}
        const textarea = document.createElement('textarea');
        textarea.value = value;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        textarea.remove();
      }}
      document.querySelectorAll('[data-copy-value]').forEach((button) => {{
        button.addEventListener('click', async () => {{
          try {{
            await copyText(button.dataset.copyValue || '');
            const original = button.textContent;
            button.dataset.copied = 'true';
            button.textContent = '복사됨';
            setTimeout(() => {{
              button.dataset.copied = 'false';
              button.textContent = original;
            }}, 1400);
          }} catch (error) {{
            button.textContent = '복사 실패';
          }}
        }});
      }});
    </script>
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


def _safe_install_html(result: ScanResult) -> str:
    profile = result.assessment.profiles["install"]
    readme_commands = readme_install_commands(result)
    safe_pattern_commands = safe_commands(result, locale="ko")
    next_command_label, next_command, next_command_detail = _next_safe_command(
        result,
        safe_pattern_commands=safe_pattern_commands,
    )
    readme_items = _command_items_html(
        readme_commands,
        empty_text="로컬 README 설치 섹션에서 인식 가능한 설치 명령을 찾지 못했습니다.",
    )
    safe_pattern_items = _command_items_html(safe_pattern_commands)
    return f"""      <h2>Safe Install</h2>
      <section class="section-panel" aria-label="Safe Install">
        <p class="profile-verdict" style="color: {_verdict_color(profile.verdict)};">{html.escape(_assessment_label(profile.verdict))}</p>
        <p>{html.escape(_install_profile_summary_ko(profile.summary))}</p>
        <h3>Next isolated step</h3>
        <div class="next-command">
          <p><strong>{html.escape(next_command_label)}</strong></p>
          <p><code>{html.escape(next_command)}</code></p>
          <p class="description">{html.escape(next_command_detail)}</p>
        </div>
        <h3>실행 전 체크리스트</h3>
        <ul class="next-steps">
          <li>명령이 저장소 README나 신뢰할 수 있는 release notes에서 나온 것인지 확인하세요.</li>
          <li>source install은 코드 실행으로 보고 먼저 격리 환경에서 검토하세요.</li>
          <li>전역 설치, sudo, shell pipe보다 격리된 검토/설치 패턴을 우선하세요.</li>
          <li>고위험 근거가 보이면 멈추고 HTML 리포트의 install finding을 먼저 확인하세요.</li>
        </ul>
        <h3>README에서 발견한 설치 명령</h3>
        <ul class="command-list">
{readme_items}
        </ul>
        <h3>격리된 검토/설치 패턴</h3>
        <ul class="command-list">
{safe_pattern_items}
        </ul>
      </section>
"""


def _next_steps_html(result: ScanResult) -> str:
    from .next_steps import render_next_steps

    plan = render_next_steps(result, locale="ko")
    return f"""      <h2>Next Steps</h2>
      <section class="section-panel" aria-label="Next Steps">
        <p>리포트의 finding을 실행 순서로 다시 정리한 초보자용 조치 계획입니다. 자동 수정이나 외부 API 조회 없이 현재 리포트 근거만 사용합니다.</p>
        <pre class="next-steps-plan">{html.escape(plan)}</pre>
      </section>
"""


def _next_safe_command(
    result: ScanResult,
    *,
    safe_pattern_commands: list[str],
) -> tuple[str, str, str]:
    install_profile = result.assessment.profiles["install"]
    priority_finding = next(iter(install_profile.priority_finding_ids), "")
    if install_profile.verdict == "do_not_install_before_review" and priority_finding:
        return (
            "설치 대신 먼저 이 finding을 확인하세요.",
            f"repo-trust explain {priority_finding}",
            "고위험 설치 근거가 있으면 README 설치 명령이나 대체 설치 명령을 바로 실행하지 않는 것이 가장 안전합니다.",
        )
    if safe_pattern_commands:
        return (
            "설치가 필요하다면 이 격리 단계부터 시작하세요.",
            safe_pattern_commands[0],
            "README 명령이나 source install을 그대로 실행하기 전에 격리된 환경을 먼저 만드는 흐름입니다.",
        )
    return (
        "먼저 리포트 근거를 확인하세요.",
        f"repo-trust safe-install {result.target.raw}",
        "표준 manifest를 찾지 못해 설치 명령보다 안전 설치 안내를 먼저 확인해야 합니다.",
    )


def _command_items_html(commands: list[str], *, empty_text: str | None = None) -> str:
    if not commands:
        text = empty_text or "추천할 명령을 만들 근거가 부족합니다."
        return f"          <li>{html.escape(text)}</li>"
    return "\n".join(f"          <li><code>{html.escape(command)}</code></li>" for command in commands)


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


def _install_profile_summary_ko(summary: str) -> str:
    return {
        "Do not run the documented install commands before reviewing the high-risk install evidence.": (
            "고위험 설치 근거를 검토하기 전에는 문서의 설치 명령을 실행하지 마세요."
        ),
        "Install may be possible, but install-related findings should be reviewed first.": (
            "설치가 가능할 수 있지만, 설치 관련 finding을 먼저 검토해야 합니다."
        ),
        "Current checks did not find install-specific blockers.": (
            "현재 검사 기준에서는 설치를 막는 install-specific finding을 찾지 못했습니다."
        ),
        "RepoTrust did not collect enough file evidence to judge install safety.": (
            "RepoTrust가 설치 안전성을 판단할 파일 근거를 충분히 수집하지 못했습니다."
        ),
    }.get(summary, summary)


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
    explain_command = html.escape(f"repo-trust explain {finding.id}")
    action = _finding_action(finding)
    acceptance_note = _finding_acceptance_note(finding)
    return f"""        <article class="finding severity-{severity}" data-severity="{severity}" data-category="{category}">
          <header>
            <div>
              <h3>{html.escape(_finding_title(finding))}</h3>
              <p class="description"><code>{finding_id}</code></p>
              <div class="finding-actions" aria-label="Finding copy actions">
                <button type="button" class="copy-button" data-copy-value="{finding_id}">ID 복사</button>
                <button type="button" class="copy-button" data-copy-value="{explain_command}">explain 명령 복사</button>
              </div>
            </div>
            <span class="badge badge-{severity}">{html.escape(severity_label)}</span>
          </header>
          <details open>
            <summary>터미널 없이 읽는 설명과 근거</summary>
            <dl>
              <dt>검사 영역</dt><dd>{html.escape(category_label)} <code>{category}</code></dd>
              <dt>심각도</dt><dd>{html.escape(severity_label)} <code>{severity}</code></dd>
              <dt>왜 위험한가요?</dt><dd>{html.escape(_finding_explanation(finding))}</dd>
              <dt>지금 할 일</dt><dd>{html.escape(action)}</dd>
              <dt>언제 수용할 수 있나요?</dt><dd>{html.escape(acceptance_note)}</dd>
              <dt>원문 메시지</dt><dd>{html.escape(finding.message)}</dd>
              <dt>실제 근거</dt><dd>{html.escape(finding.evidence)}</dd>
              <dt>추천 조치</dt><dd>{html.escape(finding.recommendation)}</dd>
            </dl>
          </details>
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


def _detected_label(key: str) -> str:
    return DETECTED_LABELS.get(key, key)


def _detected_description(key: str, value: object) -> str:
    descriptions = DETECTED_DESCRIPTIONS.get(key)
    if not descriptions:
        return "검사 중 발견한 파일 신호입니다."
    present_text, missing_text = descriptions
    return present_text if _has_detected_value(value) else missing_text


def _finding_title(finding: Finding) -> str:
    return FINDING_TITLES.get(finding.id, finding.message)


def _finding_explanation(finding: Finding) -> str:
    return FINDING_EXPLANATIONS.get(finding.id, finding.message)


def _finding_action(finding: Finding) -> str:
    from .finding_catalog import get_finding_reference

    reference = get_finding_reference(finding.id)
    if reference:
        return reference.action
    return finding.recommendation


def _finding_acceptance_note(finding: Finding) -> str:
    severity = finding.severity.value
    category = finding.category.value

    if finding.id == "target.github_not_fetched":
        return "GitHub URL 형식만 확인해도 충분한 단계라면 수용할 수 있습니다. 파일 근거가 필요하면 로컬 checkout을 검사하거나 --remote를 명시하세요."
    if finding.id == "target.github_subpath_unsupported":
        return "repository root 수준 판단이면 참고 정보로 둘 수 있습니다. 하위 폴더만 채택할지 결정해야 한다면 local scan과 --subdir로 다시 확인하세요."
    remote_github_prefix = "remote" + ".github_"
    if finding.id.startswith(remote_github_prefix) or finding.id == "remote.readme_content_unavailable":
        return "원격 근거가 일시적으로 부족한 상태라면 재시도하거나 로컬 checkout으로 보강한 뒤 수용하세요."
    if severity == "high":
        return "근거를 직접 검토하고 더 안전한 설치/채택 경로가 확인되기 전에는 수용하지 않는 편이 좋습니다."
    if category == "install_safety":
        return "격리 환경에서 명령과 스크립트를 먼저 검토했고, 실행 범위와 버전이 의도한 대로 제한된 경우에만 수용하세요."
    if severity == "medium":
        return "팀 정책이나 사용 맥락상 예외가 문서화되어 있고, dependency 채택 전에 보완 계획이 있으면 수용할 수 있습니다."
    if severity == "low":
        return "낮은 우선순위의 보완 항목입니다. lockfile, release note, 내부 정책 같은 다른 근거가 충분하면 backlog로 둘 수 있습니다."
    return "정보성 항목입니다. 판단에 필요한 근거가 충분한지 확인한 뒤 참고로 남기면 됩니다."


def _severity_ko(severity: str) -> str:
    return SEVERITY_LABELS.get(severity, severity)


def _risk_label_ko(risk_label: str) -> str:
    return RISK_LABELS.get(risk_label, risk_label)


def _target_kind_ko(kind: str) -> str:
    return TARGET_KIND_LABELS.get(kind, kind)


def _has_detected_value(value: object) -> bool:
    return bool(value)
