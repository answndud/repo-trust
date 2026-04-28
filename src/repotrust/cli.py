from __future__ import annotations

from datetime import date
from enum import Enum
from pathlib import Path
import sys
from typing import Annotated

import typer
from rich.console import Console

from . import __version__
from .config import ConfigError, RepoTrustConfig, load_config
from .console import ConsoleWorkflow, run_console_mode
from .dashboard import print_assessment_dashboard, print_command_header, print_legacy_summary
from .models import ScanResult
from .reports import render_report
from .scanner import ScanInputError, scan as scan_target
from .targets import parse_target

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


PRODUCT_HELP = {
    "root": {
        "en": """Usage: repo-trust [OPTIONS] COMMAND [ARGS]...

Inspect repository trust signals and write clear local reports.

Options:
  --version  Show the RepoTrust version and exit.
  --help     Choose English or Korean help and exit.

Commands:
  html   Write an HTML trust report.
  json   Write a JSON trust report.
  check  Inspect a target and print a terminal dashboard.

Console Mode:
  repo-trust      Open the English workflow console.
  repo-trust-kr   Open the Korean workflow console.
""",
        "ko": """사용법: repo-trust [옵션] 명령 [인자]...

저장소 신뢰 신호를 검사하고 읽기 쉬운 로컬 리포트를 만듭니다.

옵션:
  --version  RepoTrust 버전을 출력하고 종료합니다.
  --help     영어 또는 한국어 도움말을 선택해 봅니다.

명령:
  html   HTML 신뢰 리포트를 저장합니다.
  json   JSON 신뢰 리포트를 저장합니다.
  check  파일 저장 없이 터미널 대시보드로 검사합니다.

콘솔 모드:
  repo-trust      영어 workflow 콘솔을 엽니다.
  repo-trust-kr   한국어 workflow 콘솔을 엽니다.
""",
    },
    "html": {
        "en": """Usage: repo-trust html [OPTIONS] TARGET

Write an HTML trust report.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  -o, --output PATH  Custom output path. Defaults to result/<target>-YYYY-MM-DD.html.
  --config PATH      Load an explicit repotrust.toml policy file.
  --parse-only       For GitHub URLs, parse the URL without calling the GitHub API.
  --fail-under INT   Exit with code 1 if total score is below this value.
  -v, --verbose      Print findings in the terminal dashboard.
  --help             Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust html [옵션] 대상

HTML 신뢰 리포트를 저장합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  -o, --output PATH  저장 경로를 직접 지정합니다. 기본값은 result/<대상>-YYYY-MM-DD.html입니다.
  --config PATH      repotrust.toml 정책 파일을 직접 지정합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 파싱합니다.
  --fail-under INT   전체 점수가 이 값보다 낮으면 exit code 1로 종료합니다.
  -v, --verbose      터미널 대시보드에 finding을 자세히 출력합니다.
  --help             영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "json": {
        "en": """Usage: repo-trust json [OPTIONS] TARGET

Write a JSON trust report.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  -o, --output PATH  Custom output path. Defaults to result/<target>-YYYY-MM-DD.json.
  --config PATH      Load an explicit repotrust.toml policy file.
  --parse-only       For GitHub URLs, parse the URL without calling the GitHub API.
  --fail-under INT   Exit with code 1 if total score is below this value.
  -v, --verbose      Print findings in the terminal dashboard.
  --help             Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust json [옵션] 대상

JSON 신뢰 리포트를 저장합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  -o, --output PATH  저장 경로를 직접 지정합니다. 기본값은 result/<대상>-YYYY-MM-DD.json입니다.
  --config PATH      repotrust.toml 정책 파일을 직접 지정합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 파싱합니다.
  --fail-under INT   전체 점수가 이 값보다 낮으면 exit code 1로 종료합니다.
  -v, --verbose      터미널 대시보드에 finding을 자세히 출력합니다.
  --help             영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "check": {
        "en": """Usage: repo-trust check [OPTIONS] TARGET

Inspect a target and print a terminal dashboard.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  --config PATH      Load an explicit repotrust.toml policy file.
  --parse-only       For GitHub URLs, parse the URL without calling the GitHub API.
  --fail-under INT   Exit with code 1 if total score is below this value.
  -v, --verbose      Print findings in the terminal dashboard.
  --help             Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust check [옵션] 대상

파일을 저장하지 않고 터미널 대시보드로 검사합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  --config PATH      repotrust.toml 정책 파일을 직접 지정합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 파싱합니다.
  --fail-under INT   전체 점수가 이 값보다 낮으면 exit code 1로 종료합니다.
  -v, --verbose      터미널 대시보드에 finding을 자세히 출력합니다.
  --help             영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
}

HELP_OPTION_HELP = "Choose English or Korean help and exit."


class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"


def _help_callback(command: str):
    def callback(value: bool) -> bool:
        if value:
            _show_localized_help(command)
            raise typer.Exit()
        return value

    return callback


def _show_localized_help(command: str) -> None:
    typer.echo("Help language / 도움말 언어")
    typer.echo("1. English")
    typer.echo("2. 한국어")
    choice = typer.prompt("Select", default="1")
    locale = "ko" if choice.strip() == "2" else "en"
    typer.echo()
    typer.echo(_localized_help_text(command, locale))


def _localized_help_text(command: str, locale: str) -> str:
    command_help = PRODUCT_HELP.get(command, PRODUCT_HELP["root"])
    return command_help.get(locale, command_help["en"])


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
        target=target,
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
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
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
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.command("json", add_help_option=False)
@direct_kr_app.command("json", add_help_option=False)
def json_report(
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
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
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
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
    )


@direct_app.command("check", add_help_option=False)
@direct_kr_app.command("check", add_help_option=False)
def check(
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
    parse_only: Annotated[
        bool,
        typer.Option(
            "--parse-only",
            help="For GitHub URLs, parse the URL without calling the GitHub API.",
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
        parse_only=parse_only,
        fail_under=fail_under,
        verbose=verbose,
        terminal_only=True,
    )


def _run_product_scan(
    *,
    target: str,
    report_format: ReportFormat,
    output: Path | None,
    config: Path | None,
    parse_only: bool,
    fail_under: int | None,
    verbose: bool,
    terminal_only: bool = False,
) -> None:
    parsed_target = parse_target(target)
    if parse_only and parsed_target.kind != "github":
        raise typer.BadParameter(
            "--parse-only can only be used with GitHub URL targets.",
            param_hint="--parse-only",
        )

    remote = parsed_target.kind == "github" and not parse_only
    mode = _scan_mode(parsed_target.kind, remote)
    output_path = None if terminal_only else output or _default_output_path(target, report_format)

    print_command_header(
        console=status_console,
        target=target,
        mode=mode,
        report_format=report_format.value,
    )
    _run_scan(
        target=target,
        report_format=report_format,
        output=output_path,
        config=config,
        remote=remote,
        fail_under=fail_under,
        verbose=verbose,
        dashboard=True,
        output_label=output_path,
    )


def _run_console_shell(ctx: typer.Context, *, locale: str) -> None:
    run_console_mode(
        console=status_console,
        help_text=lambda: _localized_help_text("root", locale),
        version=__version__,
        run_workflow=_run_console_workflow,
        locale=locale,
    )


def _run_console_workflow(workflow: ConsoleWorkflow) -> None:
    _run_product_scan(
        target=workflow.target,
        report_format=ReportFormat(workflow.report_format),
        output=None,
        config=None,
        parse_only=workflow.parse_only,
        fail_under=None,
        verbose=workflow.verbose,
        terminal_only=workflow.terminal_only,
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
) -> None:
    normalized_format = report_format.value
    loaded_config = _load_cli_config(config)

    try:
        result = scan_target(target, weights=loaded_config.weights, remote=remote)
    except ScanInputError as exc:
        raise typer.BadParameter(str(exc), param_hint="--remote") from exc
    rendered = render_report(result, normalized_format)
    if output:
        output = _resolve_output_path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        status_console.print(f"Wrote {normalized_format} report to [bold]{output}[/bold]")
    else:
        if dashboard:
            status_console.print(rendered)
        else:
            sys.stdout.write(rendered)

    if dashboard:
        print_assessment_dashboard(
            console=status_console,
            result=result,
            mode=_scan_mode(result.target.kind, _is_remote_result(result)),
            verbose=verbose,
            output_label=output,
        )
    else:
        print_legacy_summary(console=status_console, result=result, verbose=verbose)

    effective_fail_under = fail_under if fail_under is not None else loaded_config.fail_under
    if effective_fail_under is not None and result.score.total < effective_fail_under:
        raise typer.Exit(code=1)


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


def _load_cli_config(config_path: Path | None) -> RepoTrustConfig:
    if config_path is None:
        return RepoTrustConfig()
    try:
        return load_config(config_path)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc), param_hint="--config") from exc


def _is_remote_result(result: ScanResult) -> bool:
    return any(finding.id.startswith("remote.") for finding in result.findings)
