from __future__ import annotations

import typer

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


def show_localized_help(command: str) -> None:
    typer.echo("help language / 도움말 언어")
    typer.echo("01 english")
    typer.echo("02 한국어")
    choice = typer.prompt("select>", default="1")
    locale = "ko" if choice.strip() == "2" else "en"
    typer.echo()
    typer.echo(localized_help_text(command, locale))


def localized_help_text(command: str, locale: str) -> str:
    command_help = PRODUCT_HELP.get(command, PRODUCT_HELP["root"])
    return command_help.get(locale, command_help["en"])
