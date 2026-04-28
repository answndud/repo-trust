from __future__ import annotations

from .models import Category, Finding, Score, Severity


WEIGHTS = {
    Category.README_QUALITY.value: 0.25,
    Category.INSTALL_SAFETY.value: 0.30,
    Category.SECURITY_POSTURE.value: 0.25,
    Category.PROJECT_HYGIENE.value: 0.20,
}

DEDUCTIONS = {
    Severity.INFO: 0,
    Severity.LOW: 8,
    Severity.MEDIUM: 18,
    Severity.HIGH: 35,
}

SCORE_CAPS_BY_FINDING_ID = {
    "target.local_path_missing": 0,
    "remote.github_rate_limited": 60,
    "remote.github_unauthorized": 60,
    "remote.github_not_found": 60,
    "remote.github_api_error": 60,
    "target.github_not_fetched": 70,
    "remote.github_partial_scan": 85,
    "remote.readme_content_unavailable": 85,
}


def calculate_score(findings: list[Finding], weights: dict[str, float] | None = None) -> Score:
    active_weights = weights or WEIGHTS
    categories = {category: 100 for category in WEIGHTS}
    for finding in findings:
        category = finding.category.value
        if category not in categories:
            continue
        categories[category] = max(0, categories[category] - DEDUCTIONS[finding.severity])

    total = round(
        sum(categories[category] * weight for category, weight in active_weights.items())
    )
    total = _apply_score_caps(total, findings)
    grade, risk_label = grade_for_score(total)
    return Score(categories=categories, total=total, grade=grade, risk_label=risk_label)


def grade_for_score(score: int) -> tuple[str, str]:
    if score >= 90:
        return "A", "Low risk"
    if score >= 80:
        return "B", "Moderate-low risk"
    if score >= 70:
        return "C", "Moderate risk"
    if score >= 60:
        return "D", "Elevated risk"
    return "F", "High risk"


def _apply_score_caps(total: int, findings: list[Finding]) -> int:
    caps = [
        SCORE_CAPS_BY_FINDING_ID[finding.id]
        for finding in findings
        if finding.id in SCORE_CAPS_BY_FINDING_ID
    ]
    if not caps:
        return total
    return min(total, min(caps))
