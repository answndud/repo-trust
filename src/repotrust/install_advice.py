from __future__ import annotations

from .models import Category, Finding, ScanResult, Severity


def render_safe_install_advice(result: ScanResult, *, locale: str = "en") -> str:
    """Render a terminal-friendly install plan without executing anything."""
    if locale == "ko":
        return _render_ko(result)
    return _render_en(result)


def _render_en(result: ScanResult) -> str:
    profile = result.assessment.profiles["install"]
    install_findings = _install_findings(result)
    high_findings = [
        finding for finding in install_findings if finding.severity == Severity.HIGH
    ]

    lines = [
        "RepoTrust Safe Install Advice",
        "",
        f"Target: {result.target.raw}",
        f"Install verdict: {profile.verdict}",
        f"Confidence: {result.assessment.confidence} ({result.assessment.coverage})",
        "",
        "Before you run anything:",
        "- Confirm the command came from the repository README or trusted release notes.",
        "- Prefer the isolated pattern below over global, sudo, or shell-pipe installs.",
        "- If any high-risk evidence appears, stop and review the HTML report first.",
        "",
    ]

    if high_findings:
        lines.extend(
            [
                "Do not run the README install commands yet.",
                "",
                "High-risk install evidence:",
            ]
        )
        for finding in high_findings:
            lines.append(f"- {finding.id}: {finding.evidence}")
        lines.extend(["", "Safer next steps:"])
        lines.extend(f"- {action}" for action in profile.next_actions)
        lines.append(
            "- Generate an HTML report with `repo-trust html <target>` "
            "and review every install finding."
        )
        lines.append(
            "- If you must inspect behavior, use a disposable virtual machine, "
            "container, or fresh virtual environment."
        )
    elif result.assessment.coverage in {"failed", "metadata_only"}:
        lines.extend(
            [
                profile.summary,
                "",
                "RepoTrust does not have enough file evidence to recommend an install command.",
                "",
                "Safer next steps:",
                "- Scan a local checkout for README and manifest evidence.",
                "- For GitHub URLs, use `--remote` only when you explicitly want read-only GitHub metadata.",
                "- Do not copy install commands from the repository until README install evidence is available.",
            ]
        )
    else:
        lines.extend([profile.summary, ""])
        lines.extend(["Safer install pattern:"])
        lines.extend(f"- {command}" for command in _safe_commands(result, locale="en"))
        if install_findings:
            lines.extend(["", "Install findings to review:"])
            for finding in install_findings:
                lines.append(f"- {finding.id}: {finding.evidence}")
        lines.extend(["", "Next steps:"])
        lines.extend(f"- {action}" for action in profile.next_actions)

    return "\n".join(lines).rstrip() + "\n"


def _render_ko(result: ScanResult) -> str:
    profile = result.assessment.profiles["install"]
    install_findings = _install_findings(result)
    high_findings = [
        finding for finding in install_findings if finding.severity == Severity.HIGH
    ]

    lines = [
        "RepoTrust 안전 설치 안내",
        "",
        f"대상: {result.target.raw}",
        f"설치 판단: {profile.verdict}",
        f"신뢰도: {result.assessment.confidence} ({result.assessment.coverage})",
        "",
        "실행 전 체크리스트:",
        "- 명령이 저장소 README나 신뢰할 수 있는 release notes에서 나온 것인지 확인하세요.",
        "- 전역 설치, sudo, shell pipe보다 아래의 격리된 설치 패턴을 우선하세요.",
        "- 고위험 근거가 보이면 멈추고 HTML 리포트를 먼저 확인하세요.",
        "",
    ]

    if high_findings:
        lines.extend(
            [
                "아직 README 설치 명령을 실행하지 마세요.",
                "",
                "고위험 설치 근거:",
            ]
        )
        for finding in high_findings:
            lines.append(f"- {finding.id}: {finding.evidence}")
        lines.extend(["", "더 안전한 다음 단계:"])
        lines.extend(f"- {_ko_action(action)}" for action in profile.next_actions)
        lines.append("- `repo-trust-kr html <대상>`으로 HTML 리포트를 만들고 install finding을 모두 확인하세요.")
        lines.append("- 꼭 동작을 확인해야 한다면 새 가상환경, 컨테이너, 일회용 VM에서만 실행하세요.")
    elif result.assessment.coverage in {"failed", "metadata_only"}:
        lines.extend(
            [
                _ko_profile_summary(profile.summary),
                "",
                "설치 명령을 추천하기에는 파일 근거가 부족합니다.",
                "",
                "더 안전한 다음 단계:",
                "- 로컬로 checkout한 저장소를 검사해 README와 manifest 근거를 확인하세요.",
                "- GitHub URL은 read-only metadata 조회가 필요할 때만 `--remote`를 명시하세요.",
                "- README 설치 근거가 확인되기 전에는 저장소의 설치 명령을 복사 실행하지 마세요.",
            ]
        )
    else:
        lines.extend([_ko_profile_summary(profile.summary), ""])
        lines.extend(["더 안전한 설치 패턴:"])
        lines.extend(f"- {command}" for command in _safe_commands(result, locale="ko"))
        if install_findings:
            lines.extend(["", "검토할 설치 finding:"])
            for finding in install_findings:
                lines.append(f"- {finding.id}: {finding.evidence}")
        lines.extend(["", "다음 단계:"])
        lines.extend(f"- {_ko_action(action)}" for action in profile.next_actions)

    return "\n".join(lines).rstrip() + "\n"


def _install_findings(result: ScanResult) -> list[Finding]:
    return sorted(
        (
            finding
            for finding in result.findings
            if finding.category == Category.INSTALL_SAFETY
        ),
        key=lambda finding: (
            {
                Severity.HIGH: 0,
                Severity.MEDIUM: 1,
                Severity.LOW: 2,
                Severity.INFO: 3,
            }[finding.severity],
            finding.id,
        ),
    )


def _safe_commands(result: ScanResult, *, locale: str) -> list[str]:
    manifests = set(result.detected_files.dependency_manifests)
    lockfiles = set(result.detected_files.lockfiles)
    commands: list[str] = []

    if manifests & {"pyproject.toml", "requirements.txt", "requirements-dev.txt"}:
        commands.append("python3 -m venv .venv")
        commands.append(".venv/bin/python -m pip install --upgrade pip")
        if "requirements.txt" in manifests:
            commands.append(".venv/bin/python -m pip install -r requirements.txt")
        else:
            commands.append(".venv/bin/python -m pip install -e .")

    if "package.json" in manifests:
        if lockfiles & {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
            commands.append("npm ci --ignore-scripts")
        else:
            commands.append("npm install --ignore-scripts")

    if "go.mod" in manifests:
        commands.append("go test ./...")

    if commands:
        return commands

    if locale == "ko":
        return ["표준 manifest를 찾지 못했습니다. 먼저 HTML 리포트와 README 설치 섹션을 직접 확인하세요."]
    return [
        "No standard manifest was found. Review the HTML report and README install "
        "section before installing."
    ]


def _ko_profile_summary(summary: str) -> str:
    return {
        "Do not run the documented install commands before reviewing the high-risk install evidence.": (
            "고위험 설치 근거를 검토하기 전에는 문서의 설치 명령을 실행하지 마세요."
        ),
        "Install may be possible, but install-related findings should be reviewed first.": (
            "설치가 가능할 수 있지만, 설치 관련 finding을 먼저 검토해야 합니다."
        ),
        "Current checks did not find install-specific blockers.": (
            "현재 검사 기준에서는 설치를 막는 install-specific finding을 찾지 못했습니다."
        ),
        "RepoTrust did not collect enough file evidence to judge install safety.": (
            "RepoTrust가 설치 안전성을 판단할 파일 근거를 충분히 수집하지 못했습니다."
        ),
    }.get(summary, summary)


def _ko_action(action: str) -> str:
    return {
        "Do not run README install commands until the high-risk command path is replaced or reviewed in isolation.": (
            "고위험 명령 경로가 대체되거나 격리 환경에서 검토되기 전까지 README 설치 명령을 실행하지 마세요."
        ),
        "Prefer a package-manager install with pinned versions, checksums, or reviewed source.": (
            "고정 버전, checksum, 검토된 source를 사용하는 package-manager 설치를 우선하세요."
        ),
        "Review install findings before running commands on a host machine.": (
            "실사용 환경에서 명령을 실행하기 전에 install finding을 먼저 검토하세요."
        ),
        "Use a throwaway environment when install behavior is unclear.": (
            "설치 동작이 불명확하면 일회용 환경에서만 확인하세요."
        ),
        "Review the actual install command before running it in your environment.": (
            "내 환경에서 실행하기 전에 실제 설치 명령을 다시 확인하세요."
        ),
    }.get(action, action)
