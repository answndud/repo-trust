from __future__ import annotations

from .evidence import EvidenceRow
from .finding_catalog import get_finding_reference
from .models import Finding, ScanResult

TEXT = {
    "en": {
        "findings_title": "Findings",
        "area_column": "Area",
        "score_column": "Score",
        "signal_column": "Signal",
        "read_column": "Read",
        "status_column": "Status",
        "evidence_column": "Evidence",
        "severity_column": "Severity",
        "message_column": "Message",
        "save_html_action": "Save an HTML report when you need a shareable review artifact.",
    },
    "ko": {
        "findings_title": "발견 항목",
        "area_column": "영역",
        "score_column": "점수",
        "signal_column": "확인 항목",
        "read_column": "읽는 법",
        "status_column": "상태",
        "evidence_column": "근거",
        "severity_column": "심각도",
        "message_column": "설명",
        "save_html_action": "공유하거나 나중에 보려면 HTML 리포트를 저장하세요.",
    },
}


def text(key: str, locale: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"][key])


def localized_actions(result: ScanResult, locale: str) -> list[str]:
    if locale != "ko":
        return list(result.assessment.next_actions)
    if result.assessment.verdict == "do_not_install_before_review":
        return [
            "설치 명령을 바로 실행하지 마세요.",
            "심각도 높음 또는 보통 항목의 추천 조치를 먼저 확인하세요.",
        ]
    if result.assessment.verdict == "insufficient_evidence":
        return [
            "근거가 부족하므로 HTML 리포트를 저장해 빠진 항목을 확인하세요.",
            "GitHub URL이라면 --remote를 명시하거나 로컬 checkout을 검사해 파일 수준 근거를 확인하세요.",
        ]
    if result.assessment.verdict == "usable_after_review":
        return [
            "아래 발견 항목을 읽고 내 프로젝트에 문제가 되는지 확인하세요.",
            "팀이나 친구에게 공유할 때는 HTML 리포트를 함께 보내세요.",
        ]
    return [
        "점수와 근거가 기대와 맞는지 확인하세요.",
        "중요한 프로젝트에 쓰기 전에는 HTML 리포트를 저장해 보관하세요.",
    ]


def category_label(category: str, locale: str) -> str:
    if locale != "ko":
        return category
    return {
        "readme_quality": "README 설명",
        "install_safety": "설치 안전",
        "security_posture": "보안 준비",
        "project_hygiene": "프로젝트 관리",
    }.get(category, category)


def severity_label(severity: str, locale: str) -> str:
    if locale != "ko":
        return severity.upper() if severity in {"high", "medium", "low", "info"} else severity
    return {
        "high": "높음",
        "medium": "보통",
        "low": "낮음",
        "info": "정보",
    }.get(severity, severity)


def risk_label(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "위험 높음"
    if "moderate" in normalized:
        return "주의 필요"
    return "위험 낮음"


def confidence_label(confidence: str) -> str:
    return {"high": "높음", "medium": "보통", "low": "낮음"}.get(confidence, confidence)


def mode_label(mode: str, locale: str) -> str:
    if locale != "ko":
        return mode
    return {
        "local": "로컬 폴더",
        "GitHub remote": "GitHub 원격 검사",
        "GitHub parse-only": "GitHub URL만 확인",
    }.get(mode, mode)


def format_label(report_format: str, locale: str) -> str:
    if locale != "ko":
        return report_format
    return {
        "markdown": "터미널",
        "html": "HTML",
        "json": "JSON",
    }.get(report_format, report_format)


def profile_label(profile: str, locale: str) -> str:
    if locale != "ko":
        return {
            "install": "install",
            "dependency": "dependency",
            "agent_delegate": "agent delegate",
        }.get(profile, profile)
    return {
        "install": "설치",
        "dependency": "의존성",
        "agent_delegate": "agent 위임",
    }.get(profile, profile)


def evidence_label(label: str, locale: str) -> str:
    if locale != "ko":
        return label
    return {
        "README": "README 설명서",
        "LICENSE": "라이선스",
        "SECURITY": "보안 안내",
        "CI workflows": "자동 검사 설정",
        "Dependency manifests": "의존성 목록",
        "Lockfiles": "잠금 파일",
        "Dependabot": "의존성 업데이트 설정",
    }.get(label, label)


def finding_recommendation_text(finding: Finding, locale: str) -> str:
    if locale != "ko":
        return finding.recommendation
    reference = get_finding_reference(finding.id)
    return reference.action_ko if reference else finding.recommendation


def finding_message_text(finding: Finding, locale: str) -> str:
    if locale != "ko":
        return finding.message
    reference = get_finding_reference(finding.id)
    return reference.title if reference else finding.message


def status_text(row: EvidenceRow, locale: str) -> str:
    if row.status == "found":
        return "[blue]있음[/blue]" if locale == "ko" else "[blue]found[/blue]"
    if row.status == "unknown":
        return "[yellow]확인 못함[/yellow]" if locale == "ko" else "[yellow]unknown[/yellow]"
    return "[red]없음[/red]" if locale == "ko" else "[red]missing[/red]"
