from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from .models import Category, DetectedFiles, Finding, Severity


INSTALL_SECTION_RE = re.compile(r"^#{1,6}\s+.*\b(install|installation|setup)\b", re.I | re.M)
USAGE_SECTION_RE = re.compile(r"^#{1,6}\s+.*\b(usage|quickstart|quick start|example)\b", re.I | re.M)
MAINTENANCE_RE = re.compile(r"\b(contributing|maintain|support|changelog|release)\b", re.I)
INSTALL_COMMAND_RE = re.compile(
    r"(?im)^\s*(?:[`$>]\s*)?(?:\.venv/bin/)?(python3?\s+-m\s+pip|pip|pipx|npm|pnpm|yarn|uv|poetry|go|cargo|curl|wget|brew|docker)\b.*$"
)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
COMMAND_START_RE = re.compile(
    r"(?i)^(?:sudo\s+)?(?:\.venv/bin/)?"
    r"(?:python3?\s+-m\s+pip|python3?|pip|pipx|npm|pnpm|yarn|uv|poetry|go|cargo|curl|wget|brew|docker|bash|sh|chmod)\b"
)
COMMAND_PROMPT_RE = re.compile(r"^(?:\$|>)\s+")
PYTHON_PINNED_RE = re.compile(r"(?:^|[;\s])[^;\s]+(?:(?:===|==)[^;\s]+| @ [^;\s]+)")
NODE_EXACT_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
NPM_INSTALL_LIFECYCLE_SCRIPTS = ("preinstall", "install", "postinstall", "prepare")
NODE_DEPENDENCY_SECTIONS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
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
    findings.extend(package_risk_rules(repo_path, detected))
    findings.extend(project_hygiene_rules(detected))
    return findings


def github_not_fetched_finding() -> Finding:
    return Finding(
        id="target.github_not_fetched",
        category=Category.TARGET,
        severity=Severity.INFO,
        message="GitHub URL was parsed without remote metadata collection.",
        evidence="The scanner did not clone the repository or call the GitHub API for this run.",
        recommendation="Run repo-trust html/json/check without --parse-only, or scan a local checkout for file-level analysis.",
    )


def github_subpath_unsupported_finding(subpath: str) -> Finding:
    return Finding(
        id="target.github_subpath_unsupported",
        category=Category.TARGET,
        severity=Severity.MEDIUM,
        message="GitHub tree/blob subpath URLs are not scanned at subdirectory scope.",
        evidence=f"Requested subpath: {subpath}",
        recommendation="Scan a local checkout of that subdirectory, or pass the repository root URL if a root-level assessment is intended.",
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
    install_commands = _install_command_lines(readme_text)
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
        evidence = _first_matching_command(install_commands, risky_pattern["pattern"])
        if evidence:
            findings.append(
                Finding(
                    id=risky_pattern["id"],
                    category=Category.INSTALL_SAFETY,
                    severity=risky_pattern["severity"],
                    message=f"README install instructions include a risky pattern: {risky_pattern['label']}.",
                    evidence=evidence,
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


def package_risk_rules(repo_path: Path, detected: DetectedFiles) -> list[Finding]:
    findings: list[Finding] = []
    if "package.json" in detected.dependency_manifests:
        package_data = _read_json_object(repo_path / "package.json")
        findings.extend(_node_package_findings(package_data))

    python_dependency = _first_unpinned_python_dependency(repo_path, detected)
    if python_dependency:
        findings.append(
            Finding(
                id="dependency.unpinned_python_dependency",
                category=Category.SECURITY_POSTURE,
                severity=Severity.LOW,
                message="Python dependency declaration is not pinned to an exact version.",
                evidence=python_dependency,
                recommendation="Pin direct dependencies or rely on a committed lockfile and review dependency update policy.",
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


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _read_toml_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as toml_file:
            data = tomllib.load(toml_file)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


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


def _install_command_lines(readme_text: str) -> list[str]:
    commands: list[str] = []
    in_install_section = False
    install_heading_level: int | None = None
    in_code_block = False

    for raw_line in readme_text.splitlines():
        line = raw_line.strip()
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        heading = HEADING_RE.match(line)
        if heading and not in_code_block:
            level = len(heading.group(1))
            title = heading.group(2)
            if (
                in_install_section
                and install_heading_level is not None
                and level <= install_heading_level
            ):
                in_install_section = False
                install_heading_level = None
            if INSTALL_SECTION_RE.search(f"{heading.group(1)} {title}"):
                in_install_section = True
                install_heading_level = level
            continue

        if not in_install_section:
            continue

        command = _normalize_command_line(line)
        if command and _looks_like_command(command):
            commands.append(command)

    return commands


def _normalize_command_line(line: str) -> str:
    command = line.strip().strip("`").strip()
    command = COMMAND_PROMPT_RE.sub("", command)
    return command.strip()


def _looks_like_command(line: str) -> bool:
    if not line or line.startswith("#"):
        return False
    return bool(COMMAND_START_RE.search(line) or INSTALL_COMMAND_RE.search(line))


def _first_matching_command(commands: list[str], pattern: re.Pattern[str]) -> str | None:
    for command in commands:
        if pattern.search(command):
            return command
    return None


def _node_package_findings(package_data: dict[str, Any]) -> list[Finding]:
    findings = []
    lifecycle_script = _first_npm_lifecycle_script(package_data)
    if lifecycle_script:
        findings.append(
            Finding(
                id="dependency.npm_lifecycle_script",
                category=Category.INSTALL_SAFETY,
                severity=Severity.MEDIUM,
                message="package.json defines an npm install lifecycle script.",
                evidence=lifecycle_script,
                recommendation="Review install lifecycle scripts before installing or delegating this repository to an agent.",
            )
        )

    unpinned_dependency = _first_unpinned_node_dependency(package_data)
    if unpinned_dependency:
        findings.append(
            Finding(
                id="dependency.unpinned_node_dependency",
                category=Category.SECURITY_POSTURE,
                severity=Severity.LOW,
                message="Node dependency declaration is not pinned to an exact version.",
                evidence=unpinned_dependency,
                recommendation="Pin direct dependencies or commit a package lockfile and review dependency update policy.",
            )
        )
    return findings


def _first_npm_lifecycle_script(package_data: dict[str, Any]) -> str | None:
    scripts = package_data.get("scripts")
    if not isinstance(scripts, dict):
        return None
    for script_name in NPM_INSTALL_LIFECYCLE_SCRIPTS:
        command = scripts.get(script_name)
        if isinstance(command, str) and command.strip():
            return f"package.json scripts.{script_name}: {command.strip()}"
    return None


def _first_unpinned_node_dependency(package_data: dict[str, Any]) -> str | None:
    for section_name in NODE_DEPENDENCY_SECTIONS:
        dependencies = package_data.get(section_name)
        if not isinstance(dependencies, dict):
            continue
        for package_name, version in sorted(dependencies.items()):
            if isinstance(version, str) and not _is_pinned_node_version(version):
                return f"package.json {section_name}.{package_name}: {version}"
    return None


def _is_pinned_node_version(version: str) -> bool:
    return bool(NODE_EXACT_VERSION_RE.match(version.strip()))


def _first_unpinned_python_dependency(
    repo_path: Path,
    detected: DetectedFiles,
) -> str | None:
    if "pyproject.toml" in detected.dependency_manifests:
        dependency = _first_unpinned_pyproject_dependency(repo_path / "pyproject.toml")
        if dependency:
            return dependency

    for manifest in ("requirements.txt", "requirements-dev.txt"):
        if manifest not in detected.dependency_manifests:
            continue
        dependency = _first_unpinned_requirement(repo_path / manifest, manifest)
        if dependency:
            return dependency
    return None


def _first_unpinned_pyproject_dependency(path: Path) -> str | None:
    data = _read_toml_object(path)
    project = data.get("project")
    if not isinstance(project, dict):
        return None

    dependencies = project.get("dependencies")
    if isinstance(dependencies, list):
        for dependency in dependencies:
            if isinstance(dependency, str) and not _is_pinned_python_requirement(dependency):
                return f"pyproject.toml project.dependencies: {dependency}"

    optional_dependencies = project.get("optional-dependencies")
    if isinstance(optional_dependencies, dict):
        for group_name, group_dependencies in sorted(optional_dependencies.items()):
            if not isinstance(group_dependencies, list):
                continue
            for dependency in group_dependencies:
                if isinstance(dependency, str) and not _is_pinned_python_requirement(dependency):
                    return f"pyproject.toml project.optional-dependencies.{group_name}: {dependency}"
    return None


def _first_unpinned_requirement(path: Path, manifest: str) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        requirement = line.strip()
        if not requirement or requirement.startswith(("#", "-", "git+", "http://", "https://")):
            continue
        if not _is_pinned_python_requirement(requirement):
            return f"{manifest}: {requirement}"
    return None


def _is_pinned_python_requirement(requirement: str) -> bool:
    normalized = requirement.strip()
    if not normalized:
        return True
    return bool(PYTHON_PINNED_RE.search(normalized))
