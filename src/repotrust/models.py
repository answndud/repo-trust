from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


JSON_SCHEMA_VERSION = "1.1"


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
class Assessment:
    verdict: str
    confidence: str
    coverage: str
    summary: str
    reasons: list[str]
    next_actions: list[str]

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
    )


def _coverage(finding_ids: set[str]) -> str:
    if "target.local_path_missing" in finding_ids:
        return "failed"
    if finding_ids & REMOTE_FAILURE_IDS:
        return "failed"
    if "target.github_not_fetched" in finding_ids:
        return "metadata_only"
    if {
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
    if verdict == "do_not_install_before_review":
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
        "remote.github_partial_scan",
        "remote.readme_content_unavailable",
    } & finding_ids:
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
