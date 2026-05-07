from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import Category, DetectedFiles, Finding, ScanResult, Severity, Target
from .reports import render_report
from .scoring import calculate_score


@dataclass(frozen=True)
class SampleReportSet:
    good_html: Path
    good_json: Path
    risky_html: Path
    risky_json: Path

    def paths(self) -> list[Path]:
        return [self.good_html, self.good_json, self.risky_html, self.risky_json]


def write_sample_gallery(output_dir: Path, *, today: date | None = None) -> SampleReportSet:
    output_date = today or date.today()
    output_dir.mkdir(parents=True, exist_ok=True)
    good = _good_sample()
    risky = _risky_sample()
    paths = SampleReportSet(
        good_html=output_dir / f"sample-good-{output_date.isoformat()}.html",
        good_json=output_dir / f"sample-good-{output_date.isoformat()}.json",
        risky_html=output_dir / f"sample-risky-{output_date.isoformat()}.html",
        risky_json=output_dir / f"sample-risky-{output_date.isoformat()}.json",
    )
    paths.good_html.write_text(render_report(good, "html"), encoding="utf-8")
    paths.good_json.write_text(render_report(good, "json"), encoding="utf-8")
    paths.risky_html.write_text(render_report(risky, "html"), encoding="utf-8")
    paths.risky_json.write_text(render_report(risky, "json"), encoding="utf-8")
    return paths


def render_sample_gallery_summary(paths: SampleReportSet, *, locale: str = "en") -> str:
    if locale == "ko":
        return (
            "RepoTrust 샘플 리포트 갤러리\n\n"
            "생성된 파일:\n"
            f"- 좋은 예시 HTML: {paths.good_html}\n"
            f"- 좋은 예시 JSON: {paths.good_json}\n"
            f"- 위험 예시 HTML: {paths.risky_html}\n"
            f"- 위험 예시 JSON: {paths.risky_json}\n\n"
            f"먼저 열어볼 파일: {paths.good_html}\n"
            f"열기 명령: open {paths.good_html}\n"
            f"위험 예시 열기: open {paths.risky_html}\n"
        )
    return (
        "RepoTrust Sample Report Gallery\n\n"
        "Generated files:\n"
        f"- Good example HTML: {paths.good_html}\n"
        f"- Good example JSON: {paths.good_json}\n"
        f"- Risky example HTML: {paths.risky_html}\n"
        f"- Risky example JSON: {paths.risky_json}\n\n"
        f"Start here: {paths.good_html}\n"
        f"Open with: open {paths.good_html}\n"
        f"Open risky example: open {paths.risky_html}\n"
    )


def _good_sample() -> ScanResult:
    findings: list[Finding] = []
    return ScanResult(
        target=Target(raw="sample://good-python", kind="local", path=None),
        detected_files=DetectedFiles(
            readme="README.md",
            license="LICENSE",
            security="SECURITY.md",
            ci_workflows=[".github/workflows/ci.yml"],
            dependency_manifests=["pyproject.toml"],
            lockfiles=["pylock.toml"],
            dependabot=".github/dependabot.yml",
        ),
        findings=findings,
        score=calculate_score(findings),
    )


def _risky_sample() -> ScanResult:
    findings = [
        Finding(
            id="install.risky.shell_pipe_install",
            category=Category.INSTALL_SAFETY,
            severity=Severity.HIGH,
            message="README install instructions include a risky pattern: Shell pipe install.",
            evidence="curl https://example.com/install.sh | sh",
            recommendation="Prefer package-manager installs with pinned versions, checksums, or reviewed scripts.",
        ),
        Finding(
            id="install.risky.uses_sudo",
            category=Category.INSTALL_SAFETY,
            severity=Severity.HIGH,
            message="README install instructions include a risky pattern: Sudo install usage.",
            evidence="sudo npm install -g risky-package",
            recommendation="Avoid running install commands with administrator privileges before review.",
        ),
        Finding(
            id="security.no_ci",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="No CI workflow was found.",
            evidence=".github/workflows/*.yml missing",
            recommendation="Add automated tests or CI workflow evidence before depending on the project.",
        ),
        Finding(
            id="security.no_policy",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="No security policy file was found.",
            evidence="SECURITY.md missing",
            recommendation="Add SECURITY.md so users know how to report vulnerabilities.",
        ),
        Finding(
            id="security.no_lockfile",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="Dependency manifest exists but no lockfile was found.",
            evidence="pyproject.toml present, lockfile missing",
            recommendation="Commit a lockfile or document reproducible dependency installation.",
        ),
        Finding(
            id="dependency.unpinned_python_dependency",
            category=Category.SECURITY_POSTURE,
            severity=Severity.MEDIUM,
            message="Python dependency declaration is not pinned to an exact version.",
            evidence="requests>=2",
            recommendation="Pin direct dependencies or rely on a committed lockfile and review dependency update policy.",
        ),
        Finding(
            id="hygiene.no_license",
            category=Category.PROJECT_HYGIENE,
            severity=Severity.MEDIUM,
            message="No license file was found.",
            evidence="LICENSE missing",
            recommendation="Add a license file so users can evaluate reuse permissions.",
        ),
    ]
    return ScanResult(
        target=Target(raw="sample://risky-install", kind="local", path=None),
        detected_files=DetectedFiles(
            readme="README.md",
            dependency_manifests=["pyproject.toml"],
        ),
        findings=findings,
        score=calculate_score(findings),
    )
