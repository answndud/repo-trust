from __future__ import annotations

from pathlib import Path

from .detection import detect_files
from .models import DetectedFiles, ScanResult
from .rules import github_not_fetched_finding, local_path_missing_finding, run_local_rules
from .scoring import calculate_score
from .targets import parse_target


def scan(target_text: str) -> ScanResult:
    target = parse_target(target_text)

    if target.kind == "github":
        findings = [github_not_fetched_finding()]
        return ScanResult(
            target=target,
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings),
        )

    repo_path = Path(target.path or target.raw).expanduser()
    if not repo_path.is_dir():
        findings = [local_path_missing_finding(repo_path)]
        return ScanResult(
            target=target,
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings),
        )

    detected = detect_files(repo_path)
    findings = run_local_rules(repo_path, detected)
    return ScanResult(
        target=target,
        detected_files=detected,
        findings=findings,
        score=calculate_score(findings),
    )

