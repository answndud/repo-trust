from __future__ import annotations

from dataclasses import dataclass

from .models import Category, Severity


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
    "remote.readme_content_unavailable": "README 파일은 발견했지만 내용을 가져오지 못해 README 품질과 설치 명령 안전성을 완전히 검사하지 못했습니다.",
}


@dataclass(frozen=True)
class FindingReference:
    id: str
    category: Category
    severity: Severity
    action: str

    @property
    def title(self) -> str:
        return FINDING_TITLES.get(self.id, self.id)

    @property
    def explanation(self) -> str:
        return FINDING_EXPLANATIONS.get(self.id, "No detailed explanation is registered yet.")


FINDING_REFERENCES: dict[str, FindingReference] = {
    "target.github_not_fetched": FindingReference(
        "target.github_not_fetched",
        Category.TARGET,
        Severity.INFO,
        "Run with --remote for read-only GitHub metadata, or scan a local checkout for file-level evidence.",
    ),
    "target.github_subpath_unsupported": FindingReference(
        "target.github_subpath_unsupported",
        Category.TARGET,
        Severity.MEDIUM,
        "Scan a local checkout of that subdirectory when subpath-level assessment matters.",
    ),
    "target.local_path_missing": FindingReference(
        "target.local_path_missing",
        Category.TARGET,
        Severity.HIGH,
        "Pass an existing repository directory before relying on the assessment.",
    ),
    "readme.missing": FindingReference(
        "readme.missing",
        Category.README_QUALITY,
        Severity.HIGH,
        "Add a README with purpose, installation, usage, and support information.",
    ),
    "readme.too_short": FindingReference(
        "readme.too_short",
        Category.README_QUALITY,
        Severity.MEDIUM,
        "Expand the README with project purpose, install steps, examples, and troubleshooting notes.",
    ),
    "readme.no_project_purpose": FindingReference(
        "readme.no_project_purpose",
        Category.README_QUALITY,
        Severity.MEDIUM,
        "Add a short overview near the top that explains the project purpose and expected use case.",
    ),
    "readme.no_install_section": FindingReference(
        "readme.no_install_section",
        Category.README_QUALITY,
        Severity.MEDIUM,
        "Add an Installation or Setup section with supported install methods.",
    ),
    "readme.no_usage_section": FindingReference(
        "readme.no_usage_section",
        Category.README_QUALITY,
        Severity.MEDIUM,
        "Add a Usage, Quickstart, or Examples section with copyable commands.",
    ),
    "readme.no_maintenance_signal": FindingReference(
        "readme.no_maintenance_signal",
        Category.README_QUALITY,
        Severity.LOW,
        "Document how users should report issues, contribute, or find release notes.",
    ),
    "install.no_readme_to_audit": FindingReference(
        "install.no_readme_to_audit",
        Category.INSTALL_SAFETY,
        Severity.MEDIUM,
        "Add documented install commands that avoid unaudited shell execution.",
    ),
    "install.no_commands": FindingReference(
        "install.no_commands",
        Category.INSTALL_SAFETY,
        Severity.LOW,
        "Provide explicit install commands so users and automation can review them before running.",
    ),
    "install.risky.shell_pipe_install": FindingReference(
        "install.risky.shell_pipe_install",
        Category.INSTALL_SAFETY,
        Severity.HIGH,
        "Prefer package-manager installs with pinned versions, checksums, or reviewed scripts.",
    ),
    "install.risky.process_substitution_shell": FindingReference(
        "install.risky.process_substitution_shell",
        Category.INSTALL_SAFETY,
        Severity.HIGH,
        "Download and review the script before execution, or use a packaged installer.",
    ),
    "install.risky.python_inline_execution": FindingReference(
        "install.risky.python_inline_execution",
        Category.INSTALL_SAFETY,
        Severity.HIGH,
        "Replace inline execution with reviewed scripts or package-manager installation.",
    ),
    "install.risky.uses_sudo": FindingReference(
        "install.risky.uses_sudo",
        Category.INSTALL_SAFETY,
        Severity.HIGH,
        "Review the command and prefer a user-scoped or isolated install path before using elevated privileges.",
    ),
    "install.risky.global_package_install": FindingReference(
        "install.risky.global_package_install",
        Category.INSTALL_SAFETY,
        Severity.MEDIUM,
        "Prefer project-local environments or review the package before installing globally.",
    ),
    "install.risky.vcs_direct_install": FindingReference(
        "install.risky.vcs_direct_install",
        Category.INSTALL_SAFETY,
        Severity.MEDIUM,
        "Prefer pinned releases, package registry artifacts, or reviewed commit hashes.",
    ),
    "install.risky.marks_downloaded_code_executable": FindingReference(
        "install.risky.marks_downloaded_code_executable",
        Category.INSTALL_SAFETY,
        Severity.MEDIUM,
        "Verify the source and content of the file before granting execute permission.",
    ),
    "dependency.npm_lifecycle_script": FindingReference(
        "dependency.npm_lifecycle_script",
        Category.INSTALL_SAFETY,
        Severity.MEDIUM,
        "Review install lifecycle scripts before installing or delegating setup to an agent.",
    ),
    "dependency.unpinned_node_dependency": FindingReference(
        "dependency.unpinned_node_dependency",
        Category.SECURITY_POSTURE,
        Severity.LOW,
        "Use exact versions or rely on a committed lockfile and update policy.",
    ),
    "dependency.unpinned_python_dependency": FindingReference(
        "dependency.unpinned_python_dependency",
        Category.SECURITY_POSTURE,
        Severity.LOW,
        "Use exact pins or rely on a committed lockfile and update policy.",
    ),
    "security.no_policy": FindingReference(
        "security.no_policy",
        Category.SECURITY_POSTURE,
        Severity.MEDIUM,
        "Add SECURITY.md or document vulnerability reporting somewhere users can find it.",
    ),
    "security.no_dependabot": FindingReference(
        "security.no_dependabot",
        Category.SECURITY_POSTURE,
        Severity.LOW,
        "Add Dependabot or document another dependency update process.",
    ),
    "security.no_ci": FindingReference(
        "security.no_ci",
        Category.SECURITY_POSTURE,
        Severity.MEDIUM,
        "Add CI workflow evidence or document where automated checks run.",
    ),
    "security.no_lockfile": FindingReference(
        "security.no_lockfile",
        Category.SECURITY_POSTURE,
        Severity.MEDIUM,
        "Commit a lockfile for applications, or document why the project intentionally omits one.",
    ),
    "hygiene.no_license": FindingReference(
        "hygiene.no_license",
        Category.PROJECT_HYGIENE,
        Severity.MEDIUM,
        "Add a license file before others adopt or redistribute the project.",
    ),
    "hygiene.no_manifest": FindingReference(
        "hygiene.no_manifest",
        Category.PROJECT_HYGIENE,
        Severity.LOW,
        "Add a standard package manifest or document why the repository is not installable.",
    ),
    "remote.github_metadata_collected": FindingReference(
        "remote.github_metadata_collected",
        Category.TARGET,
        Severity.INFO,
        "No action required; this confirms --remote collected read-only metadata.",
    ),
    "remote.github_rate_limited": FindingReference(
        "remote.github_rate_limited",
        Category.TARGET,
        Severity.MEDIUM,
        "Retry later or set GITHUB_TOKEN for higher rate limits.",
    ),
    "remote.github_unauthorized": FindingReference(
        "remote.github_unauthorized",
        Category.TARGET,
        Severity.MEDIUM,
        "Check repository visibility and token permissions.",
    ),
    "remote.github_not_found": FindingReference(
        "remote.github_not_found",
        Category.TARGET,
        Severity.MEDIUM,
        "Verify the owner/repo URL and token access.",
    ),
    "remote.github_api_error": FindingReference(
        "remote.github_api_error",
        Category.TARGET,
        Severity.MEDIUM,
        "Retry or inspect GitHub API status before trusting remote evidence.",
    ),
    "remote.github_partial_scan": FindingReference(
        "remote.github_partial_scan",
        Category.TARGET,
        Severity.MEDIUM,
        "Treat unavailable remote signals as unknown and retry or scan a local checkout.",
    ),
    "remote.readme_content_unavailable": FindingReference(
        "remote.readme_content_unavailable",
        Category.README_QUALITY,
        Severity.MEDIUM,
        "Scan a local checkout for full README and install safety analysis.",
    ),
    "remote.github_archived": FindingReference(
        "remote.github_archived",
        Category.PROJECT_HYGIENE,
        Severity.MEDIUM,
        "Look for a maintained fork or confirm archived status is acceptable for your use.",
    ),
    "remote.github_issues_disabled": FindingReference(
        "remote.github_issues_disabled",
        Category.PROJECT_HYGIENE,
        Severity.LOW,
        "Find the project's support or issue reporting channel before adoption.",
    ),
}


def get_finding_reference(finding_id: str) -> FindingReference | None:
    return FINDING_REFERENCES.get(finding_id)


def all_finding_references() -> list[FindingReference]:
    return [FINDING_REFERENCES[key] for key in sorted(FINDING_REFERENCES)]
