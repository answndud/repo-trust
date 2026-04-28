from __future__ import annotations

from pathlib import Path

from .detection import detect_files
from .models import DetectedFiles, ScanResult
from .remote import scan_remote_github
from .rules import github_not_fetched_finding, local_path_missing_finding, run_local_rules
from .scoring import calculate_score
from .targets import parse_target


class ScanInputError(ValueError):
    pass


def scan(
    target_text: str,
    weights: dict[str, float] | None = None,
    remote: bool = False,
) -> ScanResult:
    target = parse_target(target_text)

    if target.kind == "github":
        if remote:
            return scan_remote_github(target, weights=weights)
        findings = [github_not_fetched_finding()]
        return ScanResult(
            target=target,
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    if remote:
        raise ScanInputError("--remote can only be used with GitHub URL targets.")

    repo_path = Path(target.path or target.raw).expanduser()
    if not repo_path.is_dir():
        findings = [local_path_missing_finding(repo_path)]
        return ScanResult(
            target=target,
            detected_files=DetectedFiles(),
            findings=findings,
            score=calculate_score(findings, weights=weights),
        )

    detected = detect_files(repo_path)
    findings = run_local_rules(repo_path, detected)
    return ScanResult(
        target=target,
        detected_files=detected,
        findings=findings,
        score=calculate_score(findings, weights=weights),
    )
