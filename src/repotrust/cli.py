from __future__ import annotations

import json
from datetime import date
from enum import Enum
from pathlib import Path
import sys
from typing import Annotated

import typer
from rich.console import Console

from . import __version__
from .compare_reports import CompareFormat, render_compare_reports
from .config import (
    VERDICT_RANK,
    ConfigError,
    RepoTrustConfig,
    apply_config_policy,
    load_config,
)
from .console import ConsoleWorkflow, run_console_mode
from .dashboard import print_assessment_dashboard, print_command_header, print_legacy_summary
from .finding_catalog import get_finding_reference
from .help_i18n import HELP_OPTION_HELP, localized_help_text, show_localized_help
from .init_policy import init_policy_files
from .install_audit import audit_install, render_install_audit
from .install_advice import render_safe_install_advice
from .models import Category, DetectedFiles, Finding, ScanResult, Score, Severity, Target
from .next_steps import render_next_steps
from .reports import render_report
from .sample_gallery import render_sample_gallery_summary, write_sample_gallery
from .scanner import ScanInputError, scan as scan_target
from .targets import parse_target
from .tutorial import render_tutorial

app = typer.Typer(
    help="Evaluate repository trust signals and generate reports.",
    invoke_without_command=True,
)
direct_app = typer.Typer(
    help="Inspect repository trust signals and write clear local reports.",
    add_completion=False,
    add_help_option=False,
    invoke_without_command=True,
)
direct_kr_app = typer.Typer(
    help="Inspect repository trust signals and write clear local reports.",
    add_completion=False,
    add_help_option=False,
    invoke_without_command=True,
)
status_console = Console(stderr=True)


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


def _help_callback(command: str):
    def callback(value: bool) -> bool:
        if value:
            show_localized_help(command)
            raise typer.Exit()
        return value

    return callback


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Evaluate repository trust signals and generate reports."""
    if version:
        typer.echo(f"repotrust {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command()
def scan(
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to scan.")],
    report_format: Annotated[
        ReportFormat,
        typer.Option(
            "--format",
            "-f",
            help="Report format: markdown, json, or html.",
        ),
    ] = ReportFormat.MARKDOWN,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write the report to this file."),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    remote: Annotated[
        bool,
        typer.Option("--remote", help="Use GitHub API remote scan for GitHub URL targets."),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal summary."),
    ] = False,
) -> None:
    """Scan a repository target."""
    _run_scan(
        target=_target_with_subdir(target, subdir),
        report_format=report_format,
        output=output,
        config=config,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.callback()
def product_main(
    ctx: typer.Context,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("root"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Inspect repository trust signals and write clear local reports."""
    if version:
        typer.echo(f"repo-trust {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_console_shell(ctx, locale="en")
        raise typer.Exit()


@direct_kr_app.callback()
def product_kr_main(
    ctx: typer.Context,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("root"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the RepoTrust version and exit.",
        ),
    ] = False,
) -> None:
    """Inspect repository trust signals and write clear local reports."""
    if version:
        typer.echo(f"repo-trust-kr {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        _run_console_shell(ctx, locale="ko")
        raise typer.Exit()


@direct_app.command("html", add_help_option=False)
@direct_kr_app.command("html", add_help_option=False)
def html_report(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("html"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Custom output path. Defaults to result/<target>-YYYY-MM-DD.html.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = False,
) -> None:
    """Write an HTML trust report."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.HTML,
        output=output,
        config=config,
        subdir=subdir,
        parse_only=parse_only,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
        locale=_product_locale(ctx),
    )


@direct_app.command("json", add_help_option=False)
@direct_kr_app.command("json", add_help_option=False)
def json_report(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("json"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Custom output path. Defaults to result/<target>-YYYY-MM-DD.json.",
        ),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = False,
) -> None:
    """Write a JSON trust report."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.JSON,
        output=output,
        config=config,
        subdir=subdir,
        parse_only=parse_only,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
        locale=_product_locale(ctx),
    )


@direct_app.command("check", add_help_option=False)
@direct_kr_app.command("check", add_help_option=False)
def check(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("check"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print findings in the terminal dashboard."),
    ] = True,
) -> None:
    """Inspect a target and print a terminal dashboard."""
    _run_product_scan(
        target=target,
        report_format=ReportFormat.MARKDOWN,
        output=None,
        config=config,
        subdir=subdir,
        parse_only=parse_only,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
        terminal_only=True,
        locale=_product_locale(ctx),
    )


@direct_app.command("tutorial", add_help_option=False)
@direct_kr_app.command("tutorial", add_help_option=False)
def tutorial(
    ctx: typer.Context,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("tutorial"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Print a beginner tutorial with copyable commands."""
    typer.echo(render_tutorial(locale=_product_locale(ctx)), nl=False)


@direct_app.command("samples", add_help_option=False)
@direct_kr_app.command("samples", add_help_option=False)
def samples(
    ctx: typer.Context,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("samples"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-o", help="Directory for generated sample reports."),
    ] = Path("result"),
) -> None:
    """Write built-in good/risky sample reports."""
    paths = write_sample_gallery(output_dir)
    status_console.print(
        render_sample_gallery_summary(paths, locale=_product_locale(ctx)),
        markup=False,
    )


@direct_app.command("init-policy", add_help_option=False)
@direct_kr_app.command("init-policy", add_help_option=False)
def init_policy(
    ctx: typer.Context,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("init-policy"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    directory: Annotated[
        Path,
        typer.Option("--dir", help="Repository directory to write policy files into."),
    ] = Path("."),
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing RepoTrust policy files."),
    ] = False,
) -> None:
    """Create starter CI policy files without overwriting by default."""
    result = init_policy_files(directory, version=__version__, force=force)
    locale = _product_locale(ctx)
    if locale == "ko":
        for path in result.written:
            status_console.print(f"생성: [bold]{path}[/bold]")
        for path in result.skipped:
            status_console.print(f"건너뜀: [bold]{path}[/bold] 이미 존재합니다. 덮어쓰려면 --force를 사용하세요.")
        if result.written:
            status_console.print("다음 단계: repotrust.toml 정책을 검토한 뒤 pull_request gate로 사용하세요.")
        return

    for path in result.written:
        status_console.print(f"Created [bold]{path}[/bold]")
    for path in result.skipped:
        status_console.print(f"Skipped [bold]{path}[/bold] because it already exists. Use --force to overwrite.")
    if result.written:
        status_console.print("Next step: review repotrust.toml before making the workflow a required gate.")


@direct_app.command("audit-install", add_help_option=False)
@direct_kr_app.command("audit-install", add_help_option=False)
def audit_install_command(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("audit-install"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Audit this relative subdirectory of a local target."),
    ] = None,
) -> None:
    """Audit install-time execution surfaces without running commands."""
    audit = audit_install(_target_with_subdir(target, subdir))
    typer.echo(render_install_audit(audit, locale=_product_locale(ctx)), nl=False)


@direct_app.command("safe-install", add_help_option=False)
@direct_kr_app.command("safe-install", add_help_option=False)
def safe_install(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("safe-install"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
) -> None:
    """Print install advice without running repository install commands."""
    target = _target_with_subdir(target, subdir)
    parsed_target = parse_target(target)
    remote_scan = _resolve_product_remote(
        parsed_target_kind=parsed_target.kind,
        parse_only=parse_only,
        remote=remote,
    )
    result = _scan_result(target=target, config=config, remote=remote_scan)
    typer.echo(render_safe_install_advice(result, locale=_product_locale(ctx)), nl=False)


@direct_app.command("next-steps", add_help_option=False)
@direct_kr_app.command("next-steps", add_help_option=False)
def next_steps(
    ctx: typer.Context,
    target: Annotated[
        str | None,
        typer.Argument(help="Local path or GitHub URL to inspect."),
    ] = None,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("next-steps"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    from_json: Annotated[
        Path | None,
        typer.Option("--from-json", help="Read an existing RepoTrust JSON report without rescanning."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
) -> None:
    """Print a beginner action plan from the scan findings."""
    if target is None and from_json is None:
        raise typer.BadParameter("Pass TARGET or --from-json REPORT.json.")
    if target is not None and from_json is not None:
        raise typer.BadParameter("TARGET cannot be combined with --from-json.")
    if subdir is not None and from_json is not None:
        raise typer.BadParameter("--subdir cannot be combined with --from-json.")
    if from_json is not None:
        try:
            result = _scan_result_from_report_json(_load_report_json(from_json))
        except ValueError as exc:
            status_console.print(str(exc))
            raise typer.Exit(code=1) from exc
        typer.echo(render_next_steps(result, locale=_product_locale(ctx)), nl=False)
        return

    assert target is not None
    target = _target_with_subdir(target, subdir)
    parsed_target = parse_target(target)
    remote_scan = _resolve_product_remote(
        parsed_target_kind=parsed_target.kind,
        parse_only=parse_only,
        remote=remote,
    )
    result = _scan_result(target=target, config=config, remote=remote_scan)
    typer.echo(render_next_steps(result, locale=_product_locale(ctx)), nl=False)


@direct_app.command("gate", add_help_option=False)
@direct_kr_app.command("gate", add_help_option=False)
def gate(
    ctx: typer.Context,
    target: Annotated[str, typer.Argument(help="Local path or GitHub URL to inspect.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("gate"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write JSON report to this file."),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Load an explicit repotrust.toml policy file."),
    ] = None,
    subdir: Annotated[
        Path | None,
        typer.Option("--subdir", help="Scan this relative subdirectory of a local target."),
    ] = None,
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, force URL-only mode without calling the GitHub API.",
        ),
    ] = False,
    remote: Annotated[
        bool,
        typer.Option(
            "--remote",
            help="For GitHub URLs, call the GitHub API for read-only repository metadata.",
        ),
    ] = False,
    fail_under: Annotated[
        int | None,
        typer.Option("--fail-under", help="Exit with code 1 if total score is below this value."),
    ] = None,
) -> None:
    """Write JSON and fail when the configured policy gate fails."""
    target = _target_with_subdir(target, subdir)
    parsed_target = parse_target(target)
    remote_scan = _resolve_product_remote(
        parsed_target_kind=parsed_target.kind,
        parse_only=parse_only,
        remote=remote,
    )

    _run_scan(
        target=target,
        report_format=ReportFormat.JSON,
        output=output,
        config=config,
        remote=remote_scan,
        fail_under=fail_under,
        verbose=False,
        dashboard=False,
        dashboard_locale=_product_locale(ctx),
    )


@direct_app.command("explain", add_help_option=False)
@direct_kr_app.command("explain", add_help_option=False)
def explain(
    ctx: typer.Context,
    finding_id: Annotated[str, typer.Argument(help="Finding ID to explain.")],
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("explain"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Explain a RepoTrust finding ID."""
    reference = get_finding_reference(finding_id)
    locale = _product_locale(ctx)
    if reference is None:
        examples = [
            "install.risky.uses_sudo",
            "security.no_policy",
            "target.github_not_fetched",
        ]
        status_console.print(
            f"Unknown finding ID: [bold]{finding_id}[/]\n"
            "Run [bold]repo-trust explain --help[/bold] for usage, or try one of:\n"
            + "\n".join(f"- {example}" for example in examples)
        )
        raise typer.Exit(code=1)

    if locale == "ko":
        typer.echo(f"Finding: {reference.id}")
        typer.echo(f"제목: {reference.title}")
        typer.echo(f"영역: {reference.category.value}")
        typer.echo(f"기본 심각도: {reference.severity.value}")
        typer.echo(f"의미: {reference.explanation}")
        typer.echo(f"추천 조치: {reference.action}")
        return

    typer.echo(f"Finding: {reference.id}")
    typer.echo(f"Title: {reference.title}")
    typer.echo(f"Category: {reference.category.value}")
    typer.echo(f"Default severity: {reference.severity.value}")
    typer.echo(f"Meaning: {reference.explanation}")
    typer.echo(f"Recommended action: {reference.action}")


@direct_app.command("compare", add_help_option=False)
@direct_kr_app.command("compare", add_help_option=False)
def compare(
    ctx: typer.Context,
    old_report: Annotated[Path, typer.Argument(help="Older RepoTrust JSON report.")],
    new_report: Annotated[Path, typer.Argument(help="Newer RepoTrust JSON report.")],
    output_format: Annotated[
        CompareFormat,
        typer.Option(
            "--format",
            "-f",
            help="Comparison output format: text, markdown, or html.",
        ),
    ] = CompareFormat.TEXT,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Write the comparison report to this file."),
    ] = None,
    help_requested: Annotated[
        bool,
        typer.Option(
            "--help",
            callback=_help_callback("compare"),
            help=HELP_OPTION_HELP,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Compare two RepoTrust JSON reports."""
    locale = _product_locale(ctx)
    try:
        old_data = _load_report_json(old_report)
        new_data = _load_report_json(new_report)
    except ValueError as exc:
        status_console.print(str(exc))
        raise typer.Exit(code=1) from exc

    rendered = render_compare_reports(
        old_data,
        new_data,
        output_format=output_format,
        locale=locale,
    )
    if output:
        output_path = _resolve_output_path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        if locale == "ko":
            status_console.print(
                f"{output_format.value} 비교 리포트를 [bold]{output_path}[/bold]에 저장했습니다."
            )
        else:
            status_console.print(
                f"Wrote {output_format.value} comparison report to [bold]{output_path}[/bold]"
            )
        return

    typer.echo(rendered)


def _run_product_scan(
    *,
    target: str,
    report_format: ReportFormat,
    output: Path | None,
    config: Path | None,
    subdir: Path | None = None,
    parse_only: bool,
    remote: bool,
    fail_under: int | None,
    verbose: bool,
    terminal_only: bool = False,
    locale: str = "en",
) -> None:
    target = _target_with_subdir(target, subdir)
    parsed_target = parse_target(target)
    remote_scan = _resolve_product_remote(
        parsed_target_kind=parsed_target.kind,
        parse_only=parse_only,
        remote=remote,
    )

    mode = _scan_mode(parsed_target.kind, remote_scan)
    output_path = None if terminal_only else output or _default_output_path(target, report_format)

    _run_scan(
        target=target,
        report_format=report_format,
        output=output_path,
        config=config,
        remote=remote_scan,
        fail_under=fail_under,
        verbose=verbose,
        dashboard=True,
        output_label=output_path,
        dashboard_locale=locale,
    )


def _run_console_shell(ctx: typer.Context, *, locale: str) -> None:
    run_console_mode(
        console=status_console,
        help_text=lambda: localized_help_text("root", locale),
        version=__version__,
        run_workflow=_run_console_workflow,
        locale=locale,
    )


def _run_console_workflow(workflow: ConsoleWorkflow) -> None:
    if workflow.workflow_kind == "safe_install":
        _run_console_safe_install_workflow(workflow)
        return
    if workflow.workflow_kind == "next_steps":
        _run_console_next_steps_workflow(workflow)
        return
    if workflow.workflow_kind == "tutorial":
        status_console.print(render_tutorial(locale=workflow.locale), markup=False)
        return
    if workflow.workflow_kind == "samples":
        paths = write_sample_gallery(Path("result"))
        status_console.print(
            render_sample_gallery_summary(paths, locale=workflow.locale),
            markup=False,
        )
        return

    _run_product_scan(
        target=workflow.target,
        report_format=ReportFormat(workflow.report_format),
        output=None,
        config=None,
        parse_only=workflow.parse_only,
        remote=workflow.remote,
        fail_under=None,
        verbose=workflow.verbose,
        terminal_only=workflow.terminal_only,
        locale=workflow.locale,
    )


def _run_console_safe_install_workflow(workflow: ConsoleWorkflow) -> None:
    result = _scan_result(
        target=workflow.target,
        config=None,
        remote=workflow.remote,
    )
    status_console.print(
        render_safe_install_advice(result, locale=workflow.locale),
        end="",
        markup=False,
    )


def _run_console_next_steps_workflow(workflow: ConsoleWorkflow) -> None:
    result = _scan_result(
        target=workflow.target,
        config=None,
        remote=workflow.remote,
    )
    status_console.print(
        render_next_steps(result, locale=workflow.locale),
        end="",
        markup=False,
    )


def _run_scan(
    *,
    target: str,
    report_format: ReportFormat,
    output: Path | None,
    config: Path | None,
    remote: bool,
    fail_under: int | None,
    verbose: bool,
    dashboard: bool = False,
    output_label: Path | None = None,
    dashboard_locale: str = "en",
) -> None:
    normalized_format = report_format.value
    loaded_config = _load_cli_config(config)
    result = _scan_result_with_config(target=target, config=loaded_config, remote=remote)
    rendered = render_report(result, normalized_format)
    if output:
        output = _resolve_output_path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        if dashboard_locale == "ko" and not dashboard:
            status_console.print(
                f"{normalized_format} 리포트를 [bold]{output}[/bold]에 저장했습니다."
            )
        elif not dashboard:
            status_console.print(f"Wrote {normalized_format} report to [bold]{output}[/bold]")
    else:
        if not dashboard:
            sys.stdout.write(rendered)

    if dashboard:
        print_assessment_dashboard(
            console=status_console,
            result=result,
            mode=_scan_mode(result.target.kind, _is_remote_result(result)),
            verbose=verbose,
            output_label=output,
            locale=dashboard_locale,
        )
    else:
        print_legacy_summary(console=status_console, result=result, verbose=verbose)

    failures = _policy_failures(result, loaded_config, fail_under)
    if failures:
        status_console.print("[bold red]Policy gate failed[/bold red]")
        for failure in failures:
            status_console.print(f"- {failure}")
        raise typer.Exit(code=1)


def _scan_result(
    *,
    target: str,
    config: Path | None,
    remote: bool,
) -> ScanResult:
    loaded_config = _load_cli_config(config)
    return _scan_result_with_config(target=target, config=loaded_config, remote=remote)


def _scan_result_with_config(
    *,
    target: str,
    config: RepoTrustConfig,
    remote: bool,
) -> ScanResult:
    try:
        result = scan_target(target, weights=config.weights, remote=remote)
    except ScanInputError as exc:
        raise typer.BadParameter(str(exc), param_hint="--remote") from exc
    return apply_config_policy(result, config)


def _resolve_output_path(output: Path, today: date | None = None) -> Path:
    if output.is_absolute() or output.parent != Path("."):
        return output
    output_date = today or date.today()
    dated_name = f"{output.stem}-{output_date.isoformat()}{output.suffix}"
    return Path("result") / dated_name


def _default_output_path(
    target: str,
    report_format: ReportFormat,
    today: date | None = None,
) -> Path:
    output_date = today or date.today()
    filename = f"{_target_slug(target)}-{output_date.isoformat()}.{_format_extension(report_format)}"
    return Path("result") / filename


def _target_slug(target: str) -> str:
    parsed_target = parse_target(target)
    if parsed_target.kind == "github" and parsed_target.repo:
        return _safe_slug(parsed_target.repo)

    path = Path(parsed_target.path or parsed_target.raw).expanduser()
    name = path.resolve().name if path.name in {"", "."} else path.name
    return _safe_slug(name or "repository")


def _safe_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "repository"


def _target_with_subdir(target: str, subdir: Path | None) -> str:
    if subdir is None:
        return target

    parsed_target = parse_target(target)
    if parsed_target.kind != "local":
        raise typer.BadParameter(
            "--subdir can only be used with local path targets.",
            param_hint="--subdir",
        )
    if subdir.is_absolute() or ".." in subdir.parts:
        raise typer.BadParameter(
            "--subdir must be a relative path inside the local target.",
            param_hint="--subdir",
        )

    base_path = Path(parsed_target.path or parsed_target.raw).expanduser()
    return str(base_path / subdir)


def _format_extension(report_format: ReportFormat) -> str:
    if report_format == ReportFormat.HTML:
        return "html"
    if report_format == ReportFormat.JSON:
        return "json"
    return "md"


def _scan_mode(kind: str, remote: bool) -> str:
    if kind == "github" and remote:
        return "GitHub remote"
    if kind == "github":
        return "GitHub parse-only"
    return "local"


def _resolve_product_remote(
    *,
    parsed_target_kind: str,
    parse_only: bool,
    remote: bool,
) -> bool:
    if parse_only and remote:
        raise typer.BadParameter(
            "--parse-only cannot be combined with --remote.",
            param_hint="--parse-only",
        )
    if parse_only and parsed_target_kind != "github":
        raise typer.BadParameter(
            "--parse-only can only be used with GitHub URL targets.",
            param_hint="--parse-only",
        )
    if remote and parsed_target_kind != "github":
        raise typer.BadParameter(
            "--remote can only be used with GitHub URL targets.",
            param_hint="--remote",
        )
    return parsed_target_kind == "github" and remote


def _load_cli_config(config_path: Path | None) -> RepoTrustConfig:
    if config_path is None:
        return RepoTrustConfig()
    try:
        return load_config(config_path)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc), param_hint="--config") from exc


def _policy_failures(
    result: ScanResult,
    config: RepoTrustConfig,
    fail_under: int | None,
) -> list[str]:
    failures: list[str] = []
    effective_fail_under = fail_under if fail_under is not None else config.fail_under
    if effective_fail_under is not None and result.score.total < effective_fail_under:
        failures.append(
            f"score {result.score.total} is below required minimum {effective_fail_under}"
        )

    for profile, min_verdict in config.profile_min_verdicts.items():
        actual_verdict = result.assessment.profiles[profile].verdict
        if VERDICT_RANK[actual_verdict] < VERDICT_RANK[min_verdict]:
            failures.append(
                f"profile {profile} verdict {actual_verdict} is below required {min_verdict}"
            )
    return failures


def _is_remote_result(result: ScanResult) -> bool:
    return any(finding.id.startswith("remote.") for finding in result.findings)


def _product_locale(ctx: typer.Context) -> str:
    return "ko" if ctx.command_path.split()[0].endswith("-kr") else "en"


def _load_report_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Could not read report: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON report: {path}") from exc

    required = {"schema_version", "score", "assessment", "findings"}
    if not isinstance(data, dict) or not required <= data.keys():
        raise ValueError(f"Not a RepoTrust JSON report: {path}")
    if not isinstance(data.get("score"), dict) or not isinstance(data.get("assessment"), dict):
        raise ValueError(f"Invalid RepoTrust JSON report shape: {path}")
    if not isinstance(data.get("findings"), list):
        raise ValueError(f"Invalid RepoTrust findings list: {path}")
    return data


def _scan_result_from_report_json(data: dict) -> ScanResult:
    try:
        target_data = data["target"]
        detected_data = data["detected_files"]
        score_data = data["score"]
        findings_data = data["findings"]
        generated_at = data["generated_at"]
    except KeyError as exc:
        raise ValueError(f"Invalid RepoTrust JSON report shape: missing {exc.args[0]}") from exc

    return ScanResult(
        target=Target(**target_data),
        detected_files=DetectedFiles(**detected_data),
        findings=[
            Finding(
                id=finding["id"],
                category=Category(finding["category"]),
                severity=Severity(finding["severity"]),
                message=finding["message"],
                evidence=finding["evidence"],
                recommendation=finding["recommendation"],
            )
            for finding in findings_data
        ],
        score=Score(**score_data),
        generated_at=generated_at,
    )
