from __future__ import annotations

from dataclasses import dataclass

from .models import ScanResult
from .remote_markers import (
    REMOTE_CONTENTS_ENDPOINT,
    REMOTE_README_ENDPOINT,
)


@dataclass(frozen=True)
class EvidenceRow:
    key: str
    label: str
    status: str
    value: str


EVIDENCE_LABELS = {
    "readme": "README",
    "license": "LICENSE",
    "security": "SECURITY",
    "ci_workflows": "CI workflows",
    "dependency_manifests": "Dependency manifests",
    "lockfiles": "Lockfiles",
    "dependabot": "Dependabot",
}


def evidence_rows(result: ScanResult) -> list[EvidenceRow]:
    detected = result.detected_files
    values = {
        "readme": detected.readme,
        "license": detected.license,
        "security": detected.security,
        "ci_workflows": detected.ci_workflows,
        "dependency_manifests": detected.dependency_manifests,
        "lockfiles": detected.lockfiles,
        "dependabot": detected.dependabot,
    }
    unknown = _unknown_evidence_keys(result)
    readme_content_unknown = any(
        finding.id == "remote.readme_content_unavailable" for finding in result.findings
    )
    return [
        EvidenceRow(
            key=key,
            label=EVIDENCE_LABELS[key],
            status=_status_for_value(
                values[key],
                key in unknown
                and (
                    not values[key]
                    or (key == "readme" and readme_content_unknown)
                ),
            ),
            value=_display_value(values[key]),
        )
        for key in EVIDENCE_LABELS
    ]


def _unknown_evidence_keys(result: ScanResult) -> set[str]:
    coverage = result.assessment.coverage if result.assessment else "full"
    if coverage in {"failed", "metadata_only"}:
        return set(EVIDENCE_LABELS)

    unknown: set[str] = set()
    for finding in result.findings:
        if finding.id == "remote.readme_content_unavailable":
            unknown.add("readme")
        if finding.id != "remote.github_partial_scan":
            continue
        evidence = finding.evidence.lower()
        if REMOTE_CONTENTS_ENDPOINT in evidence:
            unknown.update(
                {
                    "readme",
                    "license",
                    "security",
                    "dependency_manifests",
                    "lockfiles",
                }
            )
        if REMOTE_README_ENDPOINT.lower() in evidence:
            unknown.add("readme")
    return unknown


def _status_for_value(value: object, unknown: bool) -> str:
    if unknown:
        return "unknown"
    if value:
        return "found"
    return "missing"


def _display_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) if value else "-"
    return str(value) if value else "-"
