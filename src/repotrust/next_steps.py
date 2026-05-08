from __future__ import annotations

from .finding_catalog import get_finding_reference
from .install_advice import readme_install_commands
from .models import Category, Finding, ScanResult, Severity


def render_next_steps(result: ScanResult, *, locale: str = "en") -> str:
    """Render a beginner-friendly action plan from a scan result."""
    if locale == "ko":
        return _render_ko(result)
    return _render_en(result)


def _render_en(result: ScanResult) -> str:
    priority_findings = _priority_findings(result)
    lines = [
        "RepoTrust Next Steps",
        "",
        f"Target: {result.target.raw}",
        f"Verdict: {result.assessment.verdict}",
        f"Score: {result.score.total}/{result.score.max_score} ({result.score.grade})",
        f"Confidence: {result.assessment.confidence} ({result.assessment.coverage})",
        "",
    ]

    if not priority_findings:
        lines.extend(
            [
                "No blocking findings were found by the enabled checks.",
                "",
                "Do this next:",
                f"1. Review install advice: repo-trust safe-install {result.target.raw}",
                f"2. Save an HTML report: repo-trust html {result.target.raw}",
                "3. Confirm the license and your project policy before adopting it.",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(["Start here:"])
    high_install = [
        finding
        for finding in priority_findings
        if finding.category == Category.INSTALL_SAFETY and finding.severity == Severity.HIGH
    ]
    if high_install:
        lines.append("1. Stop: do not run the README install commands yet.")
        commands = readme_install_commands(result)
        if commands:
            lines.append("   README commands to avoid for now:")
            for command in commands[:4]:
                lines.append(f"   - {command}")
            if len(commands) > 4:
                lines.append(f"   - ... {len(commands) - 4} more")
        lines.append(
            f"   Review install advice first: repo-trust safe-install {result.target.raw}"
        )
    else:
        lines.append("1. Review the findings below before installing or adopting this repository.")

    next_number = 2
    for finding in priority_findings:
        if finding in high_install:
            continue
        lines.append(f"{next_number}. {_action_line(finding)}")
        next_number += 1

    lines.extend(
        [
            "",
            "Copyable commands:",
            f"- repo-trust html {result.target.raw}",
            f"- repo-trust safe-install {result.target.raw}",
        ]
    )
    for finding in priority_findings[:3]:
        lines.append(f"- repo-trust explain {finding.id}")

    lines.extend(["", "Details:"])
    for finding in priority_findings:
        lines.append(
            f"- {finding.id} [{finding.severity.value}/{finding.category.value}]: "
            f"{finding.evidence}"
        )

    return "\n".join(lines).rstrip() + "\n"


def _render_ko(result: ScanResult) -> str:
    priority_findings = _priority_findings(result)
    lines = [
        "RepoTrust 다음 조치",
        "",
        f"대상: {result.target.raw}",
        f"판단: {result.assessment.verdict}",
        f"점수: {result.score.total}/{result.score.max_score} ({result.score.grade})",
        f"신뢰도: {result.assessment.confidence} ({result.assessment.coverage})",
        "",
    ]

    if not priority_findings:
        lines.extend(
            [
                "현재 검사 기준에서는 차단할 finding을 찾지 못했습니다.",
                "",
                "다음에 할 일:",
                f"1. 설치 안내 확인: repo-trust-kr safe-install {result.target.raw}",
                f"2. HTML 리포트 저장: repo-trust-kr html {result.target.raw}",
                "3. 의존성으로 추가하기 전 license와 팀 정책을 확인하세요.",
            ]
        )
        return "\n".join(lines).rstrip() + "\n"

    lines.extend(["여기부터 진행하세요:"])
    high_install = [
        finding
        for finding in priority_findings
        if finding.category == Category.INSTALL_SAFETY and finding.severity == Severity.HIGH
    ]
    if high_install:
        lines.append("1. 중단: 아직 README 설치 명령을 실행하지 마세요.")
        commands = readme_install_commands(result)
        if commands:
            lines.append("   지금은 피해야 할 README 명령:")
            for command in commands[:4]:
                lines.append(f"   - {command}")
            if len(commands) > 4:
                lines.append(f"   - ... {len(commands) - 4}개 더 있음")
        lines.append(
            f"   먼저 설치 안내를 확인하세요: repo-trust-kr safe-install {result.target.raw}"
        )
    else:
        lines.append("1. 설치하거나 의존성으로 추가하기 전에 아래 finding을 검토하세요.")

    next_number = 2
    for finding in priority_findings:
        if finding in high_install:
            continue
        lines.append(f"{next_number}. {_ko_action_line(finding)}")
        next_number += 1

    lines.extend(
        [
            "",
            "복사해서 실행할 명령:",
            f"- repo-trust-kr html {result.target.raw}",
            f"- repo-trust-kr safe-install {result.target.raw}",
        ]
    )
    for finding in priority_findings[:3]:
        lines.append(f"- repo-trust-kr explain {finding.id}")

    lines.extend(["", "세부 근거:"])
    for finding in priority_findings:
        lines.append(
            f"- {finding.id} [{finding.severity.value}/{finding.category.value}]: "
            f"{finding.evidence}"
        )

    return "\n".join(lines).rstrip() + "\n"


def _priority_findings(result: ScanResult) -> list[Finding]:
    actionable = [
        finding
        for finding in result.findings
        if finding.severity in {Severity.HIGH, Severity.MEDIUM}
        and not finding.id.startswith("remote.github_metadata_collected")
    ]
    return sorted(actionable, key=_finding_priority)


def _finding_priority(finding: Finding) -> tuple[int, int, str]:
    severity_rank = {
        Severity.HIGH: 0,
        Severity.MEDIUM: 1,
        Severity.LOW: 2,
        Severity.INFO: 3,
    }[finding.severity]
    category_rank = _category_rank(finding)
    return (severity_rank, category_rank, finding.id)


def _category_rank(finding: Finding) -> int:
    if finding.category == Category.INSTALL_SAFETY and finding.severity == Severity.HIGH:
        return 0
    if finding.id == "hygiene.no_license":
        return 1
    if finding.id == "security.no_ci":
        return 2
    if finding.id == "security.no_policy":
        return 3
    if finding.category == Category.SECURITY_POSTURE:
        return 4
    if finding.category == Category.INSTALL_SAFETY:
        return 5
    if finding.category == Category.PROJECT_HYGIENE:
        return 6
    if finding.category == Category.README_QUALITY:
        return 7
    return 8


def _action_line(finding: Finding) -> str:
    if finding.id == "hygiene.no_license":
        return "Review license: add or confirm a LICENSE file before adopting it."
    if finding.id == "security.no_ci":
        return "Review CI: add automated checks or confirm where tests run."
    if finding.id == "security.no_policy":
        return "Review security policy: add SECURITY.md or a vulnerability reporting path."
    reference = get_finding_reference(finding.id)
    action = reference.action if reference else finding.recommendation
    return f"Review {finding.id}: {action}"


def _ko_action_line(finding: Finding) -> str:
    if finding.id == "hygiene.no_license":
        return "License 확인: 의존성으로 추가하기 전에 LICENSE 파일을 추가하거나 재사용 가능 여부를 확인하세요."
    if finding.id == "security.no_ci":
        return "CI 확인: 자동 테스트가 어디서 실행되는지 확인하거나 workflow를 추가하세요."
    if finding.id == "security.no_policy":
        return "보안 정책 확인: SECURITY.md 또는 취약점 제보 경로를 추가하세요."
    if finding.id == "security.no_lockfile":
        return "Lockfile 확인: 애플리케이션이라면 lockfile을 commit하고, 의도적으로 없다면 이유를 문서화하세요."
    if finding.id == "install.risky.global_package_install":
        return "전역 설치 검토: 프로젝트별 가상환경이나 로컬 설치를 우선하고 전역 설치는 피하세요."
    if finding.id == "install.risky.marks_downloaded_code_executable":
        return "실행 권한 검토: 파일 출처와 내용을 확인하기 전에는 실행 권한을 주지 마세요."
    if finding.id == "install.risky.vcs_direct_install":
        return "직접 VCS 설치 검토: registry artifact, 고정 release, 검토된 commit hash를 우선하세요."
    reference = get_finding_reference(finding.id)
    action = reference.action if reference else finding.recommendation
    return f"{finding.id} 검토: {action}"
