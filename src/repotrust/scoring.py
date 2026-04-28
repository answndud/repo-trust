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


def calculate_score(findings: list[Finding]) -> Score:
    categories = {category: 100 for category in WEIGHTS}
    for finding in findings:
        category = finding.category.value
        if category not in categories:
            continue
        categories[category] = max(0, categories[category] - DEDUCTIONS[finding.severity])

    total = round(
        sum(categories[category] * weight for category, weight in WEIGHTS.items())
    )
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

