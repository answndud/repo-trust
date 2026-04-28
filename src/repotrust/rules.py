from __future__ import annotations

import re
from pathlib import Path

from .models import Category, DetectedFiles, Finding, Severity


INSTALL_SECTION_RE = re.compile(r"^#{1,6}\s+.*\b(install|installation|setup)\b", re.I | re.M)
USAGE_SECTION_RE = re.compile(r"^#{1,6}\s+.*\b(usage|quickstart|quick start|example)\b", re.I | re.M)
MAINTENANCE_RE = re.compile(r"\b(contributing|maintain|support|changelog|release)\b", re.I)
INSTALL_COMMAND_RE = re.compile(
    r"(?im)^\s*(?:[`$>]\s*)?(pip|pipx|npm|pnpm|yarn|uv|poetry|go|cargo|curl|wget|brew|docker)\b.*$"
)
RISKY_INSTALL_PATTERNS = (
    {
        "id": "install.risky.shell_pipe_install",
        "pattern": re.compile(r"\b(curl|wget)\b[^\n|;&]*\|\s*(sh|bash)\b", re.I),
        "label": "Shell pipe install",
        "severity": Severity.HIGH,
    },
    {
        "id": "install.risky.process_substitution_shell",
        "pattern": re.compile(r"\b(?:bash|sh)\s+<\(\s*(?:curl|wget)\b", re.I),
        "label": "Process substitution shell execution",
        "severity": Severity.HIGH,
    },
    {
        "id": "install.risky.python_inline_execution",
        "pattern": re.compile(r"\bpython3?\s+-c\s+['\"]", re.I),
        "label": "Python inline execution",
        "severity": Severity.HIGH,
    },
    {
        "id": "install.risky.uses_sudo",
        "pattern": re.compile(r"\bsudo\b", re.I),
        "label": "Uses sudo",
        "severity": Severity.HIGH,
    },
    {
        "id": "install.risky.global_package_install",
        "pattern": re.compile(r"\bnpm\s+install\s+-g\b|\byarn\s+global\s+add\b", re.I),
        "label": "Global package install",
        "severity": Severity.MEDIUM,
    },
    {
        "id": "install.risky.vcs_direct_install",
        "pattern": re.compile(r"\b(?:pip|uv)\s+install\s+git\+https?://", re.I),
        "label": "Direct VCS package install",
        "severity": Severity.MEDIUM,
    },
    {
        "id": "install.risky.marks_downloaded_code_executable",
        "pattern": re.compile(r"\bchmod\s+\+x\b", re.I),
        "label": "Marks downloaded code executable",
        "severity": Severity.MEDIUM,
    },
)


def run_local_rules(repo_path: Path, detected: DetectedFiles) -> list[Finding]:
    readme_text = _read_text(repo_path / detected.readme) if detected.readme else ""
    findings: list[Finding] = []
    findings.extend(readme_quality_rules(detected, readme_text))
    findings.extend(install_safety_rules(detected, readme_text))
    findings.extend(security_posture_rules(detected))
    findings.extend(project_hygiene_rules(detected))
    return findings


def github_not_fetched_finding() -> Finding:
    return Finding(
        id="target.github_not_fetched",
        category=Category.TARGET,
        severity=Severity.INFO,
        message="GitHub URL parsing is implemented, but remote scanning is not enabled in v1.",
        evidence="The scanner did not clone the repository or call the GitHub API.",
        recommendation="Use a local checkout for full analysis until remote scanning is added.",
    )


def local_path_missing_finding(path: Path) -> Finding:
    return Finding(
        id="target.local_path_missing",
        category=Category.TARGET,
        severity=Severity.HIGH,
        message="The target local path does not exist or is not a directory.",
        evidence=str(path),
        recommendation="Pass a valid local repository path.",
    )


def readme_quality_rules(detected: DetectedFiles, readme_text: str) -> list[Finding]:
    findings: list[Finding] = []
    if not detected.readme:
        return [
            Finding(
                id="readme.missing",
                category=Category.README_QUALITY,
                severity=Severity.HIGH,
                message="README file is missing.",
                evidence="No README.md, README.rst, README.txt, or README found at repository root.",
                recommendation="Add a README with purpose, installation, usage, and support information.",
            )
        ]

    if len(readme_text.strip()) < 300:
        findings.append(
            Finding(
                id="readme.too_short",
                category=Category.README_QUALITY,
                severity=Severity.MEDIUM,
                message="README is too short to establish usage confidence.",
                evidence=f"{detected.readme} has {len(readme_text.strip())} characters.",
                recommendation="Expand the README with project purpose, install steps, examples, and troubleshooting notes.",
            )
        )
    if not _has_project_purpose(readme_text):
        findings.append(
            Finding(
                id="readme.no_project_purpose",
                category=Category.README_QUALITY,
                severity=Severity.MEDIUM,
                message="README does not clearly explain what the project does.",
                evidence=detected.readme,
                recommendation="Add a short overview near the top that explains the project purpose, target users, and expected use case.",
            )
        )
    if not INSTALL_SECTION_RE.search(readme_text):
        findings.append(
            Finding(
                id="readme.no_install_section",
                category=Category.README_QUALITY,
                severity=Severity.MEDIUM,
                message="README does not include an obvious installation section.",
                evidence=detected.readme,
                recommendation="Add an Installation or Setup section with supported install methods.",
            )
        )
    if not USAGE_SECTION_RE.search(readme_text):
        findings.append(
            Finding(
                id="readme.no_usage_section",
                category=Category.README_QUALITY,
                severity=Severity.MEDIUM,
                message="README does not include an obvious usage or example section.",
                evidence=detected.readme,
                recommendation="Add a Usage, Quickstart, or Examples section with copyable commands.",
            )
        )
    if not MAINTENANCE_RE.search(readme_text):
        findings.append(
            Finding(
                id="readme.no_maintenance_signal",
                category=Category.README_QUALITY,
                severity=Severity.LOW,
                message="README does not mention contribution, support, changelog, or maintenance expectations.",
                evidence=detected.readme,
                recommendation="Document how users should report issues, contribute, or find release notes.",
            )
        )
    return findings


def install_safety_rules(detected: DetectedFiles, readme_text: str) -> list[Finding]:
    if not detected.readme:
        return [
            Finding(
                id="install.no_readme_to_audit",
                category=Category.INSTALL_SAFETY,
                severity=Severity.MEDIUM,
                message="Install safety cannot be audited because README is missing.",
                evidence="No README install instructions were available.",
                recommendation="Add documented install commands that avoid unaudited shell execution.",
            )
        ]

    findings: list[Finding] = []
    install_commands = INSTALL_COMMAND_RE.findall(readme_text)
    if not install_commands:
        findings.append(
            Finding(
                id="install.no_commands",
                category=Category.INSTALL_SAFETY,
                severity=Severity.LOW,
                message="README does not expose recognizable install commands.",
                evidence=detected.readme,
                recommendation="Provide explicit install commands so users and automation can review them before running.",
            )
        )

    for risky_pattern in RISKY_INSTALL_PATTERNS:
        match = risky_pattern["pattern"].search(readme_text)
        if match:
            findings.append(
                Finding(
                    id=risky_pattern["id"],
                    category=Category.INSTALL_SAFETY,
                    severity=risky_pattern["severity"],
                    message=f"README install instructions include a risky pattern: {risky_pattern['label']}.",
                    evidence=_line_for_match(readme_text, match.start()),
                    recommendation="Prefer package-manager installs with pinned versions, checksums, or reviewed scripts.",
                )
            )
    return findings


def security_posture_rules(detected: DetectedFiles) -> list[Finding]:
    findings: list[Finding] = []
    if not detected.security:
        findings.append(
            Finding(
                id="security.no_policy",
                category=Category.SECURITY_POSTURE,
                severity=Severity.MEDIUM,
                message="No security policy file was found.",
                evidence="Missing SECURITY.md or .github/SECURITY.md.",
                recommendation="Add SECURITY.md with supported versions and vulnerability reporting instructions.",
            )
        )
    if not detected.dependabot:
        findings.append(
            Finding(
                id="security.no_dependabot",
                category=Category.SECURITY_POSTURE,
                severity=Severity.LOW,
                message="No Dependabot configuration was found.",
                evidence="Missing .github/dependabot.yml or .github/dependabot.yaml.",
                recommendation="Enable Dependabot or another dependency update workflow.",
            )
        )
    if not detected.ci_workflows:
        findings.append(
            Finding(
                id="security.no_ci",
                category=Category.SECURITY_POSTURE,
                severity=Severity.MEDIUM,
                message="No GitHub Actions workflows were found.",
                evidence="Missing .github/workflows/*.yml or *.yaml.",
                recommendation="Add CI to run tests, linting, or security checks before changes are merged.",
            )
        )
    if detected.dependency_manifests and not detected.lockfiles:
        findings.append(
            Finding(
                id="security.no_lockfile",
                category=Category.SECURITY_POSTURE,
                severity=Severity.MEDIUM,
                message="Dependency manifests exist without a detected lockfile.",
                evidence=", ".join(detected.dependency_manifests),
                recommendation="Commit lockfiles where appropriate to improve reproducibility.",
            )
        )
    return findings


def project_hygiene_rules(detected: DetectedFiles) -> list[Finding]:
    findings: list[Finding] = []
    if not detected.license:
        findings.append(
            Finding(
                id="hygiene.no_license",
                category=Category.PROJECT_HYGIENE,
                severity=Severity.MEDIUM,
                message="No root license file was found.",
                evidence="Missing LICENSE, LICENSE.md, LICENSE.txt, or COPYING.",
                recommendation="Add a license file so reuse terms are clear.",
            )
        )
    if not detected.dependency_manifests:
        findings.append(
            Finding(
                id="hygiene.no_manifest",
                category=Category.PROJECT_HYGIENE,
                severity=Severity.LOW,
                message="No recognized dependency manifest was found.",
                evidence="Missing package.json, pyproject.toml, requirements.txt, or go.mod.",
                recommendation="Add standard project metadata if this repository is installable software.",
            )
        )
    return findings


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _has_project_purpose(readme_text: str) -> bool:
    in_code_block = False
    for raw_line in readme_text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line:
            continue
        if line.startswith(("#", "-", "*", ">", "[!", "|")):
            continue
        if len(line) >= 80 and len(line.split()) >= 10:
            return True
    return False


def _line_for_match(text: str, offset: int) -> str:
    line_start = text.rfind("\n", 0, offset) + 1
    line_end = text.find("\n", offset)
    if line_end == -1:
        line_end = len(text)
    return text[line_start:line_end].strip()
