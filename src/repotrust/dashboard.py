from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .evidence import EvidenceRow, evidence_rows
from .models import Finding, ScanResult


def print_command_header(
    *,
    console: Console,
    target: str,
    mode: str,
    report_format: str,
    locale: str = "en",
) -> None:
    if locale == "ko":
        console.print(
            Panel(
                f"[bold cyan]RepoTrust 한국어 모드[/bold cyan]\n"
                f"[dim]검사 대상[/dim] {target}\n"
                f"[dim]검사 방식[/dim] {_mode_label(mode, locale)}  "
                f"[dim]리포트 형식[/dim] {_format_label(report_format, locale)}",
                title="명령 모드",
                border_style="cyan",
            )
        )
        return
    console.print(
        Panel(
            f"[bold cyan]RepoTrust[/bold cyan]\n"
            f"[dim]target[/dim] {target}\n"
            f"[dim]mode[/dim] {mode}  [dim]format[/dim] {report_format}",
            title="COMMAND MODE",
            border_style="cyan",
        )
    )


def print_assessment_dashboard(
    *,
    console: Console,
    result: ScanResult,
    mode: str,
    verbose: bool,
    output_label: Path | None,
    locale: str = "en",
) -> None:
    console.print(
        Panel(
            _assessment_text(
                result=result,
                mode=mode,
                output_label=output_label,
                locale=locale,
            ),
            title=_text("assessment_title", locale),
            border_style=_risk_border_style(result.score.risk_label),
        )
    )
    console.print(_risk_breakdown_table(result, locale=locale))
    console.print(_evidence_table(result, locale=locale))
    console.print(_top_findings_table(result, locale=locale))
    console.print(
        Panel(
            _next_actions_text(result, output_label, locale=locale),
            title=_text("next_actions_title", locale),
            border_style="cyan",
        )
    )

    if verbose and result.findings:
        print_findings(console=console, result=result, locale=locale)


def print_legacy_summary(*, console: Console, result: ScanResult, verbose: bool) -> None:
    table = Table(title="RepoTrust Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("Target", result.target.raw)
    table.add_row("Score", f"{result.score.total}/{result.score.max_score}")
    table.add_row("Grade", result.score.grade)
    table.add_row("Risk", result.score.risk_label)
    table.add_row("Findings", str(len(result.findings)))
    console.print(table)

    if verbose and result.findings:
        print_findings(console=console, result=result)


def print_findings(*, console: Console, result: ScanResult, locale: str = "en") -> None:
    finding_table = Table(title=_text("findings_title", locale))
    finding_table.add_column(_text("severity_column", locale))
    finding_table.add_column("ID")
    finding_table.add_column(_text("message_column", locale))
    for finding in result.findings:
        finding_table.add_row(
            _severity_label(finding.severity.value, locale),
            finding.id,
            _message_text(finding.message, locale),
        )
    console.print(finding_table)


def _assessment_text(
    *,
    result: ScanResult,
    mode: str,
    output_label: Path | None,
    locale: str,
) -> str:
    output = str(output_label) if output_label is not None else _text("terminal_only", locale)
    assessment = result.assessment
    if locale == "ko":
        return (
            f"[bold]결론[/bold] {_verdict(result, locale)}\n"
            f"[bold]확실도[/bold] {_confidence_badge(assessment.confidence, locale)}  "
            f"[bold]검사 범위[/bold] {_coverage_badge(assessment.coverage, locale)}\n"
            f"[bold]점수[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
            f"[bold]등급[/bold] [bold]{result.score.grade}[/bold]  "
            f"[bold]위험도[/bold] {_risk_badge(result.score.risk_label, locale)}\n"
            f"[bold]발견 항목[/bold] {_finding_counts(result, locale)}\n\n"
            f"{_beginner_summary(result)}\n\n"
            f"[dim]검사 대상[/dim] {result.target.raw}\n"
            f"[dim]검사 방식[/dim] {_mode_label(mode, locale)}\n"
            f"[dim]결과 파일[/dim] {output}"
        )
    return (
        f"[bold]Verdict[/bold] {_verdict(result, locale)}  [dim]{assessment.verdict}[/dim]\n"
        f"[bold]Confidence[/bold] {_confidence_badge(assessment.confidence, locale)}  "
        f"[bold]Coverage[/bold] {_coverage_badge(assessment.coverage, locale)}\n"
        f"[bold]Score[/bold] [bold cyan]{result.score.total}/{result.score.max_score}[/bold cyan]  "
        f"[bold]Grade[/bold] [bold]{result.score.grade}[/bold]  "
        f"[bold]Risk[/bold] {_risk_badge(result.score.risk_label, locale)}\n"
        f"[bold]Findings[/bold] {_finding_counts(result, locale)}\n\n"
        f"{assessment.summary}\n\n"
        f"[dim]Target[/dim] {result.target.raw}\n"
        f"[dim]Mode[/dim] {mode}\n"
        f"[dim]Output[/dim] {output}"
    )


def _risk_breakdown_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=_text("risk_breakdown_title", locale), header_style="bold cyan")
    table.add_column(_text("area_column", locale))
    table.add_column(_text("score_column", locale), justify="right")
    table.add_column(_text("signal_column", locale))
    table.add_column(_text("read_column", locale))
    for category, score in result.score.categories.items():
        table.add_row(
            _category_label(category, locale),
            f"{score}/100",
            _score_bar(score),
            _score_label(score, locale),
        )
    return table


def _evidence_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=_text("evidence_title", locale), header_style="bold cyan")
    table.add_column(_text("signal_column", locale))
    table.add_column(_text("status_column", locale))
    table.add_column(_text("evidence_column", locale))
    for row in evidence_rows(result):
        table.add_row(_evidence_label(row.label, locale), _status_text(row, locale), row.value)
    return table


def _top_findings_table(result: ScanResult, *, locale: str) -> Table:
    table = Table(title=_text("top_findings_title", locale), header_style="bold cyan")
    table.add_column(_text("severity_column", locale))
    table.add_column("ID")
    table.add_column(_text("recommendation_column", locale))
    findings = sorted(result.findings, key=_finding_sort_key)[:5]
    if not findings:
        table.add_row("-", _text("no_findings", locale), _text("no_action_required", locale))
        return table
    for finding in findings:
        table.add_row(
            _severity_label(finding.severity.value, locale),
            finding.id,
            _recommendation_text(finding.recommendation, locale),
        )
    return table


def _next_actions_text(result: ScanResult, output_label: Path | None, *, locale: str) -> str:
    actions = _localized_actions(result, locale)
    if output_label is not None:
        if locale == "ko":
            actions.append(f"{output_label} 파일을 열어서 자세한 근거를 확인하세요.")
        else:
            actions.append(f"Open {output_label} for the full evidence trail.")
    else:
        actions.append(_text("save_html_action", locale))
    return "\n".join(f"{index}. {action}" for index, action in enumerate(actions, start=1))


def _finding_sort_key(finding: Finding) -> tuple[int, str]:
    severity_rank = {"high": 0, "medium": 1, "low": 2, "info": 3}
    return severity_rank.get(finding.severity.value, 9), finding.id


def _finding_counts(result: ScanResult, locale: str) -> str:
    counts = {"high": 0, "medium": 0, "low": 0, "info": 0}
    for finding in result.findings:
        counts[finding.severity.value] += 1
    return "  ".join(f"{_severity_label(name, locale)}:{count}" for name, count in counts.items())


def _score_bar(score: int) -> str:
    filled = max(0, min(10, round(score / 10)))
    empty = 10 - filled
    style = "green" if score >= 90 else "yellow" if score >= 70 else "red"
    return f"[{style}]{'█' * filled}{'░' * empty}[/{style}]"


def _score_label(score: int, locale: str) -> str:
    if score >= 90:
        return "좋음" if locale == "ko" else "clean"
    if score >= 70:
        return "확인 필요" if locale == "ko" else "review"
    return "주의" if locale == "ko" else "attention"


def _risk_badge(risk_label: str, locale: str) -> str:
    style = _risk_border_style(risk_label)
    label = _risk_label(risk_label) if locale == "ko" else risk_label.upper()
    return f"[bold {style}]{label}[/bold {style}]"


def _risk_border_style(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "red"
    if "moderate" in normalized:
        return "yellow"
    return "green"


def _verdict(result: ScanResult, locale: str) -> str:
    verdict = result.assessment.verdict
    if verdict == "do_not_install_before_review":
        if locale == "ko":
            return "[bold red]검토 전 설치 금지[/bold red]"
        return "[bold red]do not install before review[/bold red]"
    if verdict == "insufficient_evidence":
        if locale == "ko":
            return "[bold yellow]근거 부족[/bold yellow]"
        return "[bold yellow]insufficient evidence[/bold yellow]"
    if verdict == "usable_after_review":
        if locale == "ko":
            return "[bold yellow]검토 후 사용 가능[/bold yellow]"
        return "[bold yellow]usable after review[/bold yellow]"
    if locale == "ko":
        return "[bold green]현재 검사 기준으로 사용 가능[/bold green]"
    return "[bold green]usable by current checks[/bold green]"


def _confidence_badge(confidence: str, locale: str) -> str:
    style = "green" if confidence == "high" else "yellow" if confidence == "medium" else "red"
    label = _confidence_label(confidence) if locale == "ko" else confidence.upper()
    return f"[bold {style}]{label}[/bold {style}]"


def _coverage_badge(coverage: str, locale: str) -> str:
    style = "green" if coverage == "full" else "yellow" if coverage == "partial" else "red"
    label = _coverage_label(coverage) if locale == "ko" else coverage.upper()
    return f"[bold {style}]{label}[/bold {style}]"


def _status_text(row: EvidenceRow, locale: str) -> str:
    if row.status == "found":
        return "[green]있음[/green]" if locale == "ko" else "[green]found[/green]"
    if row.status == "unknown":
        return "[yellow]확인 못함[/yellow]" if locale == "ko" else "[yellow]unknown[/yellow]"
    return "[red]없음[/red]" if locale == "ko" else "[red]missing[/red]"


TEXT = {
    "en": {
        "assessment_title": "Trust Assessment",
        "risk_breakdown_title": "Risk Breakdown",
        "evidence_title": "Evidence",
        "top_findings_title": "Top Findings",
        "next_actions_title": "Next Actions",
        "findings_title": "Findings",
        "area_column": "Area",
        "score_column": "Score",
        "signal_column": "Signal",
        "read_column": "Read",
        "status_column": "Status",
        "evidence_column": "Evidence",
        "severity_column": "Severity",
        "recommendation_column": "Recommendation",
        "message_column": "Message",
        "terminal_only": "terminal only",
        "no_findings": "No findings",
        "no_action_required": "No action required by the current rule set.",
        "save_html_action": "Save an HTML report when you need a shareable review artifact.",
    },
    "ko": {
        "assessment_title": "신뢰도 검사 결과",
        "risk_breakdown_title": "어디가 괜찮고 어디를 봐야 하나",
        "evidence_title": "확인한 근거",
        "top_findings_title": "먼저 볼 문제",
        "next_actions_title": "다음에 할 일",
        "findings_title": "발견 항목",
        "area_column": "영역",
        "score_column": "점수",
        "signal_column": "확인 항목",
        "read_column": "읽는 법",
        "status_column": "상태",
        "evidence_column": "근거",
        "severity_column": "심각도",
        "recommendation_column": "추천 조치",
        "message_column": "설명",
        "terminal_only": "파일 저장 안 함",
        "no_findings": "큰 문제 없음",
        "no_action_required": "현재 규칙으로는 바로 고칠 항목이 없습니다.",
        "save_html_action": "공유하거나 나중에 보려면 HTML 리포트를 저장하세요.",
    },
}


def _text(key: str, locale: str) -> str:
    return TEXT.get(locale, TEXT["en"]).get(key, TEXT["en"][key])


def _beginner_summary(result: ScanResult) -> str:
    assessment = result.assessment
    if assessment.verdict == "do_not_install_before_review":
        return "지금 바로 설치하지 마세요. 먼저 빨간색 또는 노란색 항목을 확인해야 합니다."
    if assessment.verdict == "insufficient_evidence":
        return "아직 판단할 근거가 부족합니다. README, LICENSE, 보안 문서 같은 기본 파일을 더 확인하세요."
    if assessment.verdict == "usable_after_review":
        return "사용할 수는 있지만 먼저 아래 문제를 읽고 괜찮은지 확인하세요."
    return "현재 확인한 기준에서는 사용할 수 있어 보입니다. 그래도 중요한 프로젝트라면 아래 근거를 한 번 더 확인하세요."


def _localized_actions(result: ScanResult, locale: str) -> list[str]:
    if locale != "ko":
        return list(result.assessment.next_actions)
    if result.assessment.verdict == "do_not_install_before_review":
        return [
            "설치 명령을 바로 실행하지 마세요.",
            "심각도 높음 또는 보통 항목의 추천 조치를 먼저 확인하세요.",
        ]
    if result.assessment.verdict == "insufficient_evidence":
        return [
            "근거가 부족하므로 HTML 리포트를 저장해 빠진 항목을 확인하세요.",
            "GitHub URL이라면 네트워크나 API 제한 때문에 확인하지 못한 항목이 있는지 보세요.",
        ]
    if result.assessment.verdict == "usable_after_review":
        return [
            "아래 발견 항목을 읽고 내 프로젝트에 문제가 되는지 확인하세요.",
            "팀이나 친구에게 공유할 때는 HTML 리포트를 함께 보내세요.",
        ]
    return [
        "점수와 근거가 기대와 맞는지 확인하세요.",
        "중요한 프로젝트에 쓰기 전에는 HTML 리포트를 저장해 보관하세요.",
    ]


def _category_label(category: str, locale: str) -> str:
    if locale != "ko":
        return category
    return {
        "readme_quality": "README 설명",
        "install_safety": "설치 안전",
        "security_posture": "보안 준비",
        "project_hygiene": "프로젝트 관리",
    }.get(category, category)


def _severity_label(severity: str, locale: str) -> str:
    if locale != "ko":
        return severity.upper() if severity in {"high", "medium", "low", "info"} else severity
    return {
        "high": "높음",
        "medium": "보통",
        "low": "낮음",
        "info": "정보",
    }.get(severity, severity)


def _risk_label(risk_label: str) -> str:
    normalized = risk_label.lower()
    if "high" in normalized or "elevated" in normalized:
        return "위험 높음"
    if "moderate" in normalized:
        return "주의 필요"
    return "위험 낮음"


def _confidence_label(confidence: str) -> str:
    return {"high": "높음", "medium": "보통", "low": "낮음"}.get(confidence, confidence)


def _coverage_label(coverage: str) -> str:
    return {
        "full": "충분히 확인",
        "partial": "일부만 확인",
        "failed": "검사 실패",
        "metadata_only": "기본 정보만 확인",
    }.get(coverage, coverage)


def _mode_label(mode: str, locale: str) -> str:
    if locale != "ko":
        return mode
    return {
        "local": "로컬 폴더",
        "GitHub remote": "GitHub 원격 검사",
        "GitHub parse-only": "GitHub URL만 확인",
    }.get(mode, mode)


def _format_label(report_format: str, locale: str) -> str:
    if locale != "ko":
        return report_format
    return {
        "markdown": "터미널",
        "html": "HTML",
        "json": "JSON",
    }.get(report_format, report_format)


def _evidence_label(label: str, locale: str) -> str:
    if locale != "ko":
        return label
    return {
        "README": "README 설명서",
        "LICENSE": "라이선스",
        "SECURITY": "보안 안내",
        "CI workflows": "자동 검사 설정",
        "Dependency manifests": "의존성 목록",
        "Lockfiles": "잠금 파일",
        "Dependabot": "의존성 업데이트 설정",
    }.get(label, label)


def _recommendation_text(recommendation: str, locale: str) -> str:
    if locale != "ko":
        return recommendation
    return RECOMMENDATION_KO.get(recommendation, recommendation)


def _message_text(message: str, locale: str) -> str:
    if locale != "ko":
        return message
    risky_prefix = "README install instructions include a risky pattern: "
    if message.startswith(risky_prefix):
        pattern = message.removeprefix(risky_prefix).removesuffix(".")
        return f"README 설치 안내에 위험한 방식이 있습니다: {_risky_pattern_label(pattern)}."
    return MESSAGE_KO.get(message, message)


RECOMMENDATION_KO = {
    "Continue remote scan with repository contents and workflow metadata.": (
        "원격 저장소 내용과 자동 검사 정보를 계속 확인하세요."
    ),
    "Retry later or provide a GITHUB_TOKEN with sufficient rate limit.": (
        "나중에 다시 실행하거나 충분한 rate limit이 있는 GITHUB_TOKEN을 설정하세요."
    ),
    "Provide a GITHUB_TOKEN with repository read access or verify repository visibility.": (
        "읽기 권한이 있는 GITHUB_TOKEN을 설정하거나 저장소 공개 상태를 확인하세요."
    ),
    "Verify the owner/repo URL and repository visibility.": (
        "owner/repo URL이 맞는지, 저장소가 접근 가능한지 확인하세요."
    ),
    "Retry later or inspect GitHub API availability and repository permissions.": (
        "나중에 다시 시도하거나 GitHub API 상태와 저장소 권한을 확인하세요."
    ),
    "Treat the project as read-only unless a maintained fork or replacement is available.": (
        "관리되는 fork나 대체 프로젝트가 없다면 읽기 전용 참고용으로만 보세요."
    ),
    "Confirm where maintainers accept bug reports, security questions, and support requests before adopting the project.": (
        "사용하기 전에 버그 신고, 보안 문의, 지원 요청을 어디로 해야 하는지 확인하세요."
    ),
    "Retry later or verify repository permissions before treating missing remote signals as absent.": (
        "빠진 신호를 없다고 판단하기 전에 나중에 다시 시도하거나 저장소 권한을 확인하세요."
    ),
    "Retry remote scan later or scan a local checkout for full README and install safety analysis.": (
        "나중에 원격 검사를 다시 하거나 로컬로 clone해서 README와 설치 안전을 자세히 확인하세요."
    ),
    "Run repo-trust html/json/check without --parse-only, or scan a local checkout for file-level analysis.": (
        "--parse-only 없이 실행하거나 로컬 checkout을 검사해 파일 수준 근거를 확인하세요."
    ),
    "Pass a valid local repository path.": "올바른 로컬 저장소 경로를 입력하세요.",
    "Add a README with purpose, installation, usage, and support information.": (
        "목적, 설치, 사용법, 지원 정보를 담은 README를 추가하세요."
    ),
    "Expand the README with project purpose, install steps, examples, and troubleshooting notes.": (
        "README에 프로젝트 목적, 설치 단계, 예시, 문제 해결 방법을 더 자세히 적으세요."
    ),
    "Add a short overview near the top that explains the project purpose, target users, and expected use case.": (
        "README 위쪽에 프로젝트 목적, 대상 사용자, 사용 상황을 짧게 설명하세요."
    ),
    "Add an Installation or Setup section with supported install methods.": (
        "지원하는 설치 방법을 담은 Installation 또는 Setup 섹션을 추가하세요."
    ),
    "Add a Usage, Quickstart, or Examples section with copyable commands.": (
        "복사해서 실행할 수 있는 명령이 있는 Usage, Quickstart, Examples 섹션을 추가하세요."
    ),
    "Document how users should report issues, contribute, or find release notes.": (
        "문제 신고, 기여 방법, 릴리스 노트를 어디서 볼 수 있는지 문서화하세요."
    ),
    "Add documented install commands that avoid unaudited shell execution.": (
        "검토되지 않은 shell 실행을 피하는 설치 명령을 문서화하세요."
    ),
    "Provide explicit install commands so users and automation can review them before running.": (
        "사용자와 자동화가 실행 전에 검토할 수 있도록 설치 명령을 명확히 적으세요."
    ),
    "Prefer package-manager installs with pinned versions, checksums, or reviewed scripts.": (
        "버전 고정, checksum, 검토된 스크립트가 있는 패키지 관리자 설치를 우선하세요."
    ),
    "Add SECURITY.md with supported versions and vulnerability reporting instructions.": (
        "지원 버전과 취약점 신고 방법을 담은 SECURITY.md를 추가하세요."
    ),
    "Enable Dependabot or another dependency update workflow.": (
        "Dependabot 또는 다른 의존성 업데이트 자동화를 켜세요."
    ),
    "Add CI to run tests, linting, or security checks before changes are merged.": (
        "변경이 병합되기 전에 테스트, lint, 보안 검사를 실행하는 CI를 추가하세요."
    ),
    "Commit lockfiles where appropriate to improve reproducibility.": (
        "재현 가능한 설치를 위해 필요한 lockfile을 커밋하세요."
    ),
    "Add a license file so reuse terms are clear.": (
        "재사용 조건이 분명하도록 라이선스 파일을 추가하세요."
    ),
    "Add standard project metadata if this repository is installable software.": (
        "설치 가능한 소프트웨어라면 표준 프로젝트 metadata를 추가하세요."
    ),
}


MESSAGE_KO = {
    "GitHub repository metadata was collected.": "GitHub 저장소 기본 정보를 확인했습니다.",
    "GitHub API rate limit prevented remote scan completion.": (
        "GitHub API 사용량 제한 때문에 원격 검사를 끝내지 못했습니다."
    ),
    "GitHub API authentication or authorization failed.": (
        "GitHub API 인증 또는 권한 확인에 실패했습니다."
    ),
    "GitHub repository was not found or is not visible.": (
        "GitHub 저장소를 찾을 수 없거나 볼 권한이 없습니다."
    ),
    "GitHub API returned an unexpected error.": "GitHub API에서 예상하지 못한 오류가 났습니다.",
    "GitHub repository is archived.": "GitHub 저장소가 archived 상태입니다.",
    "GitHub issue tracking is disabled.": "GitHub issue 기능이 꺼져 있습니다.",
    "GitHub remote scan completed with partial metadata.": (
        "GitHub 원격 검사가 일부 정보만 확인한 상태로 끝났습니다."
    ),
    "README exists but its content could not be fetched for remote analysis.": (
        "README는 있지만 원격 분석을 위해 내용을 가져오지 못했습니다."
    ),
    "GitHub URL was parsed without remote metadata collection.": (
        "GitHub URL 형식만 확인했고 원격 정보는 가져오지 않았습니다."
    ),
    "The target local path does not exist or is not a directory.": (
        "입력한 로컬 경로가 없거나 폴더가 아닙니다."
    ),
    "README file is missing.": "README 파일이 없습니다.",
    "README is too short to establish usage confidence.": (
        "README가 너무 짧아서 사용법을 믿고 판단하기 어렵습니다."
    ),
    "README does not clearly explain what the project does.": (
        "README가 프로젝트가 무엇을 하는지 분명히 설명하지 않습니다."
    ),
    "README does not include an obvious installation section.": (
        "README에 설치 방법 섹션이 잘 보이지 않습니다."
    ),
    "README does not include an obvious usage or example section.": (
        "README에 사용법이나 예시 섹션이 잘 보이지 않습니다."
    ),
    "README does not mention contribution, support, changelog, or maintenance expectations.": (
        "README에 기여, 지원, 변경 기록, 유지보수 안내가 부족합니다."
    ),
    "Install safety cannot be audited because README is missing.": (
        "README가 없어서 설치 안전성을 확인할 수 없습니다."
    ),
    "README does not expose recognizable install commands.": (
        "README에서 알아볼 수 있는 설치 명령을 찾지 못했습니다."
    ),
    "No security policy file was found.": "보안 정책 파일을 찾지 못했습니다.",
    "No Dependabot configuration was found.": "Dependabot 설정을 찾지 못했습니다.",
    "No GitHub Actions workflows were found.": "GitHub Actions workflow를 찾지 못했습니다.",
    "Dependency manifests exist without a detected lockfile.": (
        "의존성 목록은 있지만 lockfile을 찾지 못했습니다."
    ),
    "No root license file was found.": "루트 라이선스 파일을 찾지 못했습니다.",
    "No recognized dependency manifest was found.": (
        "알아볼 수 있는 의존성 manifest를 찾지 못했습니다."
    ),
}


def _risky_pattern_label(label: str) -> str:
    return {
        "Shell pipe install": "shell pipe 설치",
        "Process substitution shell execution": "process substitution shell 실행",
        "Python inline execution": "Python inline 실행",
        "Direct VCS package install": "직접 VCS 패키지 설치",
    }.get(label, label)
