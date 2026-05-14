from __future__ import annotations

from dataclasses import dataclass

from .models import Category, Severity
from .reports import FINDING_EXPLANATIONS, FINDING_TITLES


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
