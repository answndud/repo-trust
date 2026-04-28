from __future__ import annotations

from .models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from .scoring import calculate_score


def scan_remote_github(
    target: Target,
    weights: dict[str, float] | None = None,
) -> ScanResult:
    finding = Finding(
        id="remote.github_not_implemented",
        category=Category.TARGET,
        severity=Severity.INFO,
        message="Remote GitHub scanning is enabled, but the HTTP client is not implemented yet.",
        evidence="Remote scan boundary reached without network access.",
        recommendation="Use local checkout scanning until remote GitHub scan implementation is complete.",
    )
    findings = [finding]
    return ScanResult(
        target=target,
        detected_files=DetectedFiles(),
        findings=findings,
        score=calculate_score(findings, weights=weights),
    )
