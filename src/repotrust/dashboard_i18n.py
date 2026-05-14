from __future__ import annotations

from .evidence import EvidenceRow
from .models import ScanResult

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

RECOMMENDATION_KO = {
    "Continue remote scan with repository root contents and README content.": (
        "원격 저장소 root 파일과 README 내용을 계속 확인하세요."
    ),
    "Retry later or provide a GITHUB_TOKEN with sufficient rate limit.": (
        "나중에 다시 실행하거나 충분한 rate limit이 있는 GITHUB_TOKEN을 설정하세요."
    ),
    "Provide a GITHUB_TOKEN with repository read access or verify repository visibility.": (
        "읽기 권한이 있는 GITHUB_TOKEN을 설정하거나 저장소 공개 상태를 확인하세요."
    ),
    "Verify the owner/repo URL and repository visibility.": (
        "owner/repo URL이 맞는지, 저장소가 접근 가능한지 확인하세요."
    ),
    "Retry later or inspect GitHub API availability and repository permissions.": (
        "나중에 다시 시도하거나 GitHub API 상태와 저장소 권한을 확인하세요."
    ),
    "Treat the project as read-only unless a maintained fork or replacement is available.": (
        "관리되는 fork나 대체 프로젝트가 없다면 읽기 전용 참고용으로만 보세요."
    ),
    "Confirm where maintainers accept bug reports, security questions, and support requests before adopting the project.": (
        "사용하기 전에 버그 신고, 보안 문의, 지원 요청을 어디로 해야 하는지 확인하세요."
    ),
    "Review release notes, changelog, and maintenance status before adopting the repository.": (
        "사용하기 전에 release notes, changelog, 유지보수 상태를 확인하세요."
    ),
    "Retry later or verify repository permissions before treating missing remote signals as absent.": (
        "빠진 신호를 없다고 판단하기 전에 나중에 다시 시도하거나 저장소 권한을 확인하세요."
    ),
    "Retry remote scan later or scan a local checkout for full README and install safety analysis.": (
        "나중에 원격 검사를 다시 하거나 로컬로 clone해서 README와 설치 안전을 자세히 확인하세요."
    ),
    "Run repo-trust html/json/check/gate with --remote, or scan a local checkout for file-level analysis.": (
        "--remote로 원격 조회를 명시하거나 로컬 checkout을 검사해 파일 수준 근거를 확인하세요."
    ),
    "Scan a local checkout of that subdirectory, or pass the repository root URL if a root-level assessment is intended.": (
        "해당 하위 폴더를 로컬로 checkout해서 검사하거나, 루트 저장소 평가가 목적이면 repository root URL을 입력하세요."
    ),
    "Pass a valid local repository path.": "올바른 로컬 저장소 경로를 입력하세요.",
    "Add a README with purpose, installation, usage, and support information.": (
        "목적, 설치, 사용법, 지원 정보를 담은 README를 추가하세요."
    ),
    "Expand the README with project purpose, install steps, examples, and troubleshooting notes.": (
        "README에 프로젝트 목적, 설치 단계, 예시, 문제 해결 방법을 더 자세히 적으세요."
    ),
    "Add a short overview near the top that explains the project purpose, target users, and expected use case.": (
        "README 위쪽에 프로젝트 목적, 대상 사용자, 사용 상황을 짧게 설명하세요."
    ),
    "Add an Installation or Setup section with supported install methods.": (
        "지원하는 설치 방법을 담은 Installation 또는 Setup 섹션을 추가하세요."
    ),
    "Add a Usage, Quickstart, or Examples section with copyable commands.": (
        "복사해서 실행할 수 있는 명령이 있는 Usage, Quickstart, Examples 섹션을 추가하세요."
    ),
    "Document how users should report issues, contribute, or find release notes.": (
        "문제 신고, 기여 방법, 릴리스 노트를 어디서 볼 수 있는지 문서화하세요."
    ),
    "Add documented install commands that avoid unaudited shell execution.": (
        "검토되지 않은 shell 실행을 피하는 설치 명령을 문서화하세요."
    ),
    "Provide explicit install commands so users and automation can review them before running.": (
        "사용자와 자동화가 실행 전에 검토할 수 있도록 설치 명령을 명확히 적으세요."
    ),
    "Prefer package-manager installs with pinned versions, checksums, or reviewed scripts.": (
        "버전 고정, checksum, 검토된 스크립트가 있는 패키지 관리자 설치를 우선하세요."
    ),
    "Review install lifecycle scripts before installing or delegating this repository to an agent.": (
        "설치하거나 agent에게 맡기기 전에 install lifecycle script 내용을 직접 확인하세요."
    ),
    "Pin direct dependencies or commit a package lockfile and review dependency update policy.": (
        "직접 dependency를 고정하거나 package lockfile을 커밋하고 업데이트 정책을 확인하세요."
    ),
    "Pin direct dependencies or rely on a committed lockfile and review dependency update policy.": (
        "직접 dependency를 고정하거나 커밋된 lockfile과 업데이트 정책을 함께 확인하세요."
    ),
    "Add SECURITY.md with supported versions and vulnerability reporting instructions.": (
        "지원 버전과 취약점 신고 방법을 담은 SECURITY.md를 추가하세요."
    ),
    "Enable Dependabot or another dependency update workflow.": (
        "Dependabot 또는 다른 의존성 업데이트 자동화를 켜세요."
    ),
    "Add CI to run tests, linting, or security checks before changes are merged.": (
        "변경이 병합되기 전에 테스트, lint, 보안 검사를 실행하는 CI를 추가하세요."
    ),
    "Commit lockfiles where appropriate to improve reproducibility.": (
        "재현 가능한 설치를 위해 필요한 lockfile을 커밋하세요."
    ),
    "Add a license file so reuse terms are clear.": (
        "재사용 조건이 분명하도록 라이선스 파일을 추가하세요."
    ),
    "Add standard project metadata if this repository is installable software.": (
        "설치 가능한 소프트웨어라면 표준 프로젝트 metadata를 추가하세요."
    ),
}

MESSAGE_KO = {
    "GitHub repository metadata was collected.": "GitHub 저장소 기본 정보를 확인했습니다.",
    "GitHub API rate limit prevented remote scan completion.": (
        "GitHub API 사용량 제한 때문에 원격 검사를 끝내지 못했습니다."
    ),
    "GitHub API authentication or authorization failed.": (
        "GitHub API 인증 또는 권한 확인에 실패했습니다."
    ),
    "GitHub repository was not found or is not visible.": (
        "GitHub 저장소를 찾을 수 없거나 볼 권한이 없습니다."
    ),
    "GitHub API returned an unexpected error.": "GitHub API에서 예상하지 못한 오류가 났습니다.",
    "GitHub repository is archived.": "GitHub 저장소가 archived 상태입니다.",
    "GitHub issue tracking is disabled.": "GitHub issue 기능이 꺼져 있습니다.",
    "GitHub remote scan completed with partial metadata.": (
        "GitHub 원격 검사가 일부 정보만 확인한 상태로 끝났습니다."
    ),
    "README exists but its content could not be fetched for remote analysis.": (
        "README는 있지만 원격 분석을 위해 내용을 가져오지 못했습니다."
    ),
    "GitHub URL was parsed without remote metadata collection.": (
        "GitHub URL 형식만 확인했고 원격 정보는 가져오지 않았습니다."
    ),
    "GitHub tree/blob subpath URLs are not scanned at subdirectory scope.": (
        "GitHub tree/blob 하위 경로는 하위 폴더 단위로 검사하지 않습니다."
    ),
    "The target local path does not exist or is not a directory.": (
        "입력한 로컬 경로가 없거나 폴더가 아닙니다."
    ),
    "README file is missing.": "README 파일이 없습니다.",
    "README is too short to establish usage confidence.": (
        "README가 너무 짧아서 사용법을 믿고 판단하기 어렵습니다."
    ),
    "README does not clearly explain what the project does.": (
        "README가 프로젝트가 무엇을 하는지 분명히 설명하지 않습니다."
    ),
    "README does not include an obvious installation section.": (
        "README에 설치 방법 섹션이 잘 보이지 않습니다."
    ),
    "README does not include an obvious usage or example section.": (
        "README에 사용법이나 예시 섹션이 잘 보이지 않습니다."
    ),
    "README does not mention contribution, support, changelog, or maintenance expectations.": (
        "README에 기여, 지원, 변경 기록, 유지보수 안내가 부족합니다."
    ),
    "Install safety cannot be audited because README is missing.": (
        "README가 없어서 설치 안전성을 확인할 수 없습니다."
    ),
    "README does not expose recognizable install commands.": (
        "README에서 알아볼 수 있는 설치 명령을 찾지 못했습니다."
    ),
    "package.json defines an npm install lifecycle script.": (
        "package.json에 npm 설치 lifecycle script가 있습니다."
    ),
    "Node dependency declaration is not pinned to an exact version.": (
        "Node dependency가 exact version으로 고정되어 있지 않습니다."
    ),
    "Python dependency declaration is not pinned to an exact version.": (
        "Python dependency가 exact version으로 고정되어 있지 않습니다."
    ),
    "No security policy file was found.": "보안 정책 파일을 찾지 못했습니다.",
    "No Dependabot configuration was found.": "Dependabot 설정을 찾지 못했습니다.",
    "No GitHub Actions workflows were found.": "GitHub Actions workflow를 찾지 못했습니다.",
    "Dependency manifests exist without a detected lockfile.": (
        "의존성 목록은 있지만 lockfile을 찾지 못했습니다."
    ),
    "No root license file was found.": "루트 라이선스 파일을 찾지 못했습니다.",
    "No recognized dependency manifest was found.": (
        "알아볼 수 있는 의존성 manifest를 찾지 못했습니다."
    ),
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


def recommendation_text(recommendation: str, locale: str) -> str:
    if locale != "ko":
        return recommendation
    return RECOMMENDATION_KO.get(recommendation, recommendation)


def message_text(message: str, locale: str) -> str:
    if locale != "ko":
        return message
    risky_prefix = "README install instructions include a risky pattern: "
    if message.startswith(risky_prefix):
        pattern = message.removeprefix(risky_prefix).removesuffix(".")
        return f"README 설치 안내에 위험한 방식이 있습니다: {_risky_pattern_label(pattern)}."
    return MESSAGE_KO.get(message, message)


def status_text(row: EvidenceRow, locale: str) -> str:
    if row.status == "found":
        return "[blue]있음[/blue]" if locale == "ko" else "[blue]found[/blue]"
    if row.status == "unknown":
        return "[yellow]확인 못함[/yellow]" if locale == "ko" else "[yellow]unknown[/yellow]"
    return "[red]없음[/red]" if locale == "ko" else "[red]missing[/red]"


def _risky_pattern_label(label: str) -> str:
    return {
        "Shell pipe install": "shell pipe 설치",
        "Process substitution shell execution": "process substitution shell 실행",
        "Python inline execution": "Python inline 실행",
        "Direct VCS package install": "직접 VCS 패키지 설치",
    }.get(label, label)
