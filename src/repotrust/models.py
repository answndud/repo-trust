from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


JSON_SCHEMA_VERSION = "1.0"


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
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": JSON_SCHEMA_VERSION,
            "target": self.target.to_dict(),
            "detected_files": self.detected_files.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "score": self.score.to_dict(),
            "generated_at": self.generated_at,
        }
