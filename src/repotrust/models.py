from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


JSON_SCHEMA_VERSION = "1.2"


class Category(str, Enum):
    README_QUALITY = "readme_quality"
    INSTALL_SAFETY = "install_safety"
    SECURITY_POSTURE = "security_posture"
    PROJECT_HYGIENE = "project_hygiene"
    TARGET = "target"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Finding:
    id: str
    category: Category
    severity: Severity
    message: str
    evidence: str
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["category"] = self.category.value
        data["severity"] = self.severity.value
        return data


@dataclass(frozen=True)
class Score:
    categories: dict[str, int]
    total: int
    max_score: int = 100
    grade: str = "F"
    risk_label: str = "High risk"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssessmentProfile:
    verdict: str
    summary: str
    reasons: list[str]
    next_actions: list[str]
    priority_finding_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Assessment:
    verdict: str
    confidence: str
    coverage: str
    summary: str
    reasons: list[str]
    next_actions: list[str]
    profiles: dict[str, AssessmentProfile]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Target:
    raw: str
    kind: str
    path: str | None = None
    host: str | None = None
    owner: str | None = None
    repo: str | None = None
    ref: str | None = None
    subpath: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DetectedFiles:
    readme: str | None = None
    license: str | None = None
    security: str | None = None
    ci_workflows: list[str] = field(default_factory=list)
    dependency_manifests: list[str] = field(default_factory=list)
    lockfiles: list[str] = field(default_factory=list)
    dependabot: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScanResult:
    target: Target
    detected_files: DetectedFiles
    findings: list[Finding]
    score: Score
    assessment: Assessment = field(init=False)
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "assessment", assess_scan(self))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": JSON_SCHEMA_VERSION,
            "target": self.target.to_dict(),
            "detected_files": self.detected_files.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "score": self.score.to_dict(),
            "assessment": self.assessment.to_dict(),
            "generated_at": self.generated_at,
        }


REMOTE_FAILURE_IDS = {
    "remote.github_rate_limited",
    "remote.github_unauthorized",
    "remote.github_not_found",
    "remote.github_api_error",
}


def assess_scan(result: ScanResult) -> Assessment:
    finding_ids = {finding.id for finding in result.findings}
    high_findings = [finding for finding in result.findings if finding.severity == Severity.HIGH]
    medium_findings = [
        finding for finding in result.findings if finding.severity == Severity.MEDIUM
    ]

    coverage = _coverage(finding_ids)
    confidence = _confidence(coverage)
    if high_findings:
        verdict = "do_not_install_before_review"
        summary = "High severity findings require review before installing, depending on, or delegating this repository."
    elif coverage in {"failed", "metadata_only"}:
        verdict = "insufficient_evidence"
        summary = "RepoTrust could not collect enough repository evidence to make an adoption-ready assessment."
    elif medium_findings:
        verdict = "usable_after_review"
        summary = "The repository may be usable, but medium severity findings should be reviewed first."
    else:
        verdict = "usable_by_current_checks"
        summary = "The enabled RepoTrust checks did not find blocking trust issues."

    return Assessment(
        verdict=verdict,
        confidence=confidence,
        coverage=coverage,
        summary=summary,
        reasons=_assessment_reasons(result, coverage),
        next_actions=_assessment_next_actions(result, verdict, coverage),
        profiles=_assessment_profiles(result, coverage),
    )


def _assessment_profiles(
    result: ScanResult,
    coverage: str,
) -> dict[str, AssessmentProfile]:
    return {
        "install": _install_profile(result, coverage),
        "dependency": _dependency_profile(result, coverage),
        "agent_delegate": _agent_delegate_profile(result, coverage),
    }


def _install_profile(result: ScanResult, coverage: str) -> AssessmentProfile:
    install_findings = _sorted_findings(
        finding
        for finding in result.findings
        if finding.category == Category.INSTALL_SAFETY
    )
    if coverage in {"failed", "metadata_only"}:
        return _insufficient_profile(
            "Install",
            "RepoTrust did not collect enough file evidence to judge install safety.",
            result,
        )

    high_install = _filter_by_severity(install_findings, {Severity.HIGH})
    if high_install:
        return _profile(
            verdict="do_not_install_before_review",
            summary="Do not run the documented install commands before reviewing the high-risk install evidence.",
            reasons=_profile_reasons(
                "Install safety has high severity findings.",
                high_install,
            ),
            next_actions=[
                "Do not run README install commands until the high-risk command path is replaced or reviewed in isolation.",
                "Prefer a package-manager install with pinned versions, checksums, or reviewed source.",
            ],
            findings=high_install,
        )

    review_install = _filter_by_severity(
        install_findings,
        {Severity.MEDIUM, Severity.LOW},
    )
    if review_install:
        return _profile(
            verdict="usable_after_review",
            summary="Install may be possible, but install-related findings should be reviewed first.",
            reasons=_profile_reasons(
                "Install safety findings affect copy-paste install confidence.",
                review_install,
            ),
            next_actions=[
                "Review install findings before running commands on a host machine.",
                "Use a throwaway environment when install behavior is unclear.",
            ],
            findings=review_install,
        )

    if coverage == "partial":
        return _partial_profile("Install", result)

    return _profile(
        verdict="usable_by_current_checks",
        summary="Current checks did not find install-specific blockers.",
        reasons=["README install evidence passed the enabled install safety checks."],
        next_actions=[
            "Review the actual install command before running it in your environment.",
        ],
        findings=[],
    )


def _dependency_profile(result: ScanResult, coverage: str) -> AssessmentProfile:
    dependency_findings = _sorted_findings(
        finding
        for finding in result.findings
        if finding.category
        in {
            Category.SECURITY_POSTURE,
            Category.PROJECT_HYGIENE,
        }
        or finding.id.startswith("dependency.")
    )
    if coverage in {"failed", "metadata_only"}:
        return _insufficient_profile(
            "Dependency",
            "RepoTrust did not collect enough file evidence to judge dependency adoption.",
            result,
        )

    high_dependency = _filter_by_severity(dependency_findings, {Severity.HIGH})
    if high_dependency:
        return _profile(
            verdict="do_not_install_before_review",
            summary="Do not add this repository as a dependency before resolving high severity adoption risks.",
            reasons=_profile_reasons(
                "Dependency adoption has high severity findings.",
                high_dependency,
            ),
            next_actions=[
                "Resolve high severity dependency, security, or project hygiene findings before adoption.",
                "Keep the repository out of production dependency graphs until those findings are reviewed.",
            ],
            findings=high_dependency,
        )

    review_dependency = _filter_by_severity(
        dependency_findings,
        {Severity.MEDIUM, Severity.LOW},
    )
    if review_dependency:
        return _profile(
            verdict="usable_after_review",
            summary="Dependency adoption needs policy review for security posture, licensing, or reproducibility signals.",
            reasons=_profile_reasons(
                "Dependency-relevant findings affect adoption confidence.",
                review_dependency,
            ),
            next_actions=[
                "Review license, security policy, CI, lockfile, and dependency pinning findings before adopting.",
                "Document any accepted exceptions in your dependency review notes.",
            ],
            findings=review_dependency,
        )

    if coverage == "partial":
        return _partial_profile("Dependency", result)

    return _profile(
        verdict="usable_by_current_checks",
        summary="Current checks did not find dependency-adoption blockers.",
        reasons=["Security posture and project hygiene signals passed the enabled dependency checks."],
        next_actions=[
            "Confirm the license and organization policy before adding the dependency.",
        ],
        findings=[],
    )


def _agent_delegate_profile(result: ScanResult, coverage: str) -> AssessmentProfile:
    agent_findings = _sorted_findings(
        finding
        for finding in result.findings
        if finding.severity in {Severity.HIGH, Severity.MEDIUM}
        or finding.category == Category.INSTALL_SAFETY
    )
    if coverage in {"failed", "metadata_only"}:
        return _insufficient_profile(
            "Agent delegation",
            "RepoTrust did not collect enough file evidence to decide whether an agent should work in this repository.",
            result,
        )

    agent_blockers = _sorted_findings(
        finding
        for finding in agent_findings
        if finding.severity == Severity.HIGH
        or (
            finding.category == Category.INSTALL_SAFETY
            and finding.severity == Severity.MEDIUM
        )
    )
    if agent_blockers:
        return _profile(
            verdict="do_not_install_before_review",
            summary="Do not delegate this repository to an AI agent before reviewing install or high severity findings.",
            reasons=_profile_reasons(
                "Agent delegation is stricter because agents may run setup commands automatically.",
                agent_blockers,
            ),
            next_actions=[
                "Block autonomous setup or install execution until the priority findings are reviewed.",
                "Use a sandbox and explicit command allowlist if an agent must inspect the repository.",
            ],
            findings=agent_blockers,
        )

    review_agent = _filter_by_severity(agent_findings, {Severity.MEDIUM})
    if review_agent:
        return _profile(
            verdict="usable_after_review",
            summary="Agent delegation may be acceptable after reviewing medium severity findings.",
            reasons=_profile_reasons(
                "Medium severity findings can affect autonomous setup or maintenance work.",
                review_agent,
            ),
            next_actions=[
                "Review medium severity findings before allowing autonomous changes or command execution.",
                "Prefer read-only inspection until the review is complete.",
            ],
            findings=review_agent,
        )

    if coverage == "partial":
        return _partial_profile("Agent delegation", result)

    return _profile(
        verdict="usable_by_current_checks",
        summary="Current checks did not find blockers for cautious agent delegation.",
        reasons=["No high severity or agent-sensitive install findings were found by the enabled checks."],
        next_actions=[
            "Use normal sandboxing and review agent changes before merging.",
        ],
        findings=[],
    )


def _profile(
    *,
    verdict: str,
    summary: str,
    reasons: list[str],
    next_actions: list[str],
    findings: list[Finding],
) -> AssessmentProfile:
    return AssessmentProfile(
        verdict=verdict,
        summary=summary,
        reasons=reasons,
        next_actions=next_actions,
        priority_finding_ids=[finding.id for finding in findings[:3]],
    )


def _insufficient_profile(
    label: str,
    summary: str,
    result: ScanResult,
) -> AssessmentProfile:
    priority_findings = _sorted_findings(
        finding
        for finding in result.findings
        if finding.category == Category.TARGET
        or finding.id in REMOTE_FAILURE_IDS
    )
    return _profile(
        verdict="insufficient_evidence",
        summary=summary,
        reasons=_profile_reasons(
            f"{label} profile needs repository file evidence.",
            priority_findings,
        ),
        next_actions=[
            "Run a remote scan or scan a local checkout before relying on this profile.",
            "Do not treat missing evidence as an all-clear signal.",
        ],
        findings=priority_findings,
    )


def _partial_profile(label: str, result: ScanResult) -> AssessmentProfile:
    priority_findings = _sorted_findings(
        finding
        for finding in result.findings
        if finding.category == Category.TARGET
        or finding.id in {
            "remote.github_partial_scan",
            "remote.readme_content_unavailable",
        }
    )
    return _profile(
        verdict="usable_after_review",
        summary=f"{label} may be possible, but the scan had partial evidence.",
        reasons=_profile_reasons(
            f"{label} profile is limited by partial scan coverage.",
            priority_findings,
        ),
        next_actions=[
            "Retry the scan or use a local checkout before treating this profile as adoption-ready.",
            "Review findings that came from unavailable or root-scoped evidence.",
        ],
        findings=priority_findings,
    )


def _profile_reasons(prefix: str, findings: list[Finding]) -> list[str]:
    reasons = [prefix]
    for finding in findings[:3]:
        if finding.severity != Severity.INFO:
            reasons.append(f"{finding.id}: {finding.message}")
    return reasons


def _sorted_findings(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(list(findings), key=_finding_sort_key)


def _filter_by_severity(
    findings: list[Finding],
    severities: set[Severity],
) -> list[Finding]:
    return [finding for finding in findings if finding.severity in severities]


def _coverage(finding_ids: set[str]) -> str:
    if "target.local_path_missing" in finding_ids:
        return "failed"
    if finding_ids & REMOTE_FAILURE_IDS:
        return "failed"
    if "target.github_not_fetched" in finding_ids:
        return "metadata_only"
    if {
        "target.github_subpath_unsupported",
        "remote.github_partial_scan",
        "remote.readme_content_unavailable",
    } & finding_ids:
        return "partial"
    return "full"


def _confidence(coverage: str) -> str:
    if coverage == "full":
        return "high"
    if coverage == "partial":
        return "medium"
    return "low"


def _assessment_reasons(result: ScanResult, coverage: str) -> list[str]:
    reasons = []
    finding_ids = {finding.id for finding in result.findings}
    if "target.local_path_missing" in finding_ids:
        reasons.append("Target path could not be scanned because it does not exist or is not a directory.")
    elif coverage == "failed":
        reasons.append("Remote scan failed before repository contents could be verified.")
    elif coverage == "metadata_only":
        reasons.append("GitHub URL was parsed without fetching repository files or metadata.")
    elif coverage == "partial":
        if "target.github_subpath_unsupported" in finding_ids:
            reasons.append("GitHub subpath URL support is limited, so the report does not assess only the requested subdirectory.")
        else:
            reasons.append("Some remote endpoints failed, so unavailable signals are treated as unknown.")
    else:
        reasons.append("Repository evidence was collected for all enabled checks.")

    cap = _score_cap_reason(result)
    if cap:
        reasons.append(cap)

    priority_findings = sorted(result.findings, key=_finding_sort_key)
    for finding in priority_findings[:3]:
        if finding.severity != Severity.INFO:
            reasons.append(f"{finding.id}: {finding.message}")

    if len(reasons) == 1 and not result.findings:
        reasons.append("No findings were produced by the current rule set.")
    return reasons


def _assessment_next_actions(
    result: ScanResult,
    verdict: str,
    coverage: str,
) -> list[str]:
    finding_ids = {finding.id for finding in result.findings}
    if "target.github_subpath_unsupported" in finding_ids:
        actions = [
            "Scan a local checkout of the requested subdirectory, or pass the repository root URL if root-level assessment is intended."
        ]
        if coverage == "metadata_only":
            actions.append("Run a remote scan or scan a local checkout for file-level evidence.")
    elif verdict == "do_not_install_before_review":
        if any(finding.id == "target.local_path_missing" for finding in result.findings):
            actions = ["Pass a valid local repository path before relying on this assessment."]
        else:
            actions = ["Review every high severity finding before running install commands."]
    elif coverage == "failed":
        actions = ["Retry the remote scan later or set GITHUB_TOKEN before relying on the result."]
    elif coverage == "metadata_only":
        actions = ["Run a remote scan or scan a local checkout for file-level evidence."]
    elif coverage == "partial":
        actions = ["Retry the scan or use a local checkout to resolve unknown evidence."]
    elif verdict == "usable_after_review":
        actions = ["Review medium severity findings against your dependency policy."]
    else:
        actions = ["Confirm license and organization policy before adopting the repository."]

    actions.append("Use the findings and evidence matrix rather than the score alone.")
    if result.target.kind == "github" and coverage != "full":
        actions.append("Do not treat missing remote evidence as proof that files are absent.")
    return actions


def _score_cap_reason(result: ScanResult) -> str | None:
    finding_ids = {finding.id for finding in result.findings}
    if "target.local_path_missing" in finding_ids:
        return "Score is capped because the target path could not be scanned."
    if finding_ids & REMOTE_FAILURE_IDS:
        return "Score is capped because the remote scan did not collect repository file evidence."
    if "target.github_not_fetched" in finding_ids:
        return "Score is capped because parse-only mode cannot assess repository files."
    if {
        "target.github_subpath_unsupported",
        "remote.github_partial_scan",
        "remote.readme_content_unavailable",
    } & finding_ids:
        if "target.github_subpath_unsupported" in finding_ids:
            return "Score is capped because GitHub subpath URLs are not scanned at subdirectory scope."
        return "Score is capped because some remote evidence is unknown."
    return None


def _finding_sort_key(finding: Finding) -> tuple[int, str]:
    severity_rank = {
        Severity.HIGH: 0,
        Severity.MEDIUM: 1,
        Severity.LOW: 2,
        Severity.INFO: 3,
    }
    return severity_rank.get(finding.severity, 9), finding.id
