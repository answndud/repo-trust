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
  safe-install Print install advice without running install commands.
  next-steps Print a beginner action plan from scan findings.
  tutorial Print a beginner tutorial with copyable commands.
  samples Write built-in good/risky sample reports.
  init-policy Create starter CI policy files.
  gate   Write JSON and fail when policy requirements are not met.
  explain Explain a finding ID.
  compare Compare two JSON reports.

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
  safe-install 설치 명령을 실행하지 않고 안전한 다음 단계를 안내합니다.
  next-steps 검사 결과에서 초보자용 다음 조치 계획을 보여줍니다.
  tutorial 초보자가 처음 따라 할 명령을 보여줍니다.
  samples 좋은/위험 샘플 리포트를 생성합니다.
  init-policy CI 정책 시작 파일을 생성합니다.
  gate   JSON 리포트를 출력하고 정책 실패를 exit code로 표시합니다.
  explain finding ID의 의미와 추천 조치를 설명합니다.
  compare 두 JSON 리포트의 점수와 finding 변화를 비교합니다.

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
  --subdir PATH      Scan this relative subdirectory of a local target.
  --remote           For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only       For GitHub URLs, force URL-only mode without the GitHub API.
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
  --subdir PATH      로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote           GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
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
  --subdir PATH      Scan this relative subdirectory of a local target.
  --remote           For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only       For GitHub URLs, force URL-only mode without the GitHub API.
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
  --subdir PATH      로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote           GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
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
  --subdir PATH      Scan this relative subdirectory of a local target.
  --remote           For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only       For GitHub URLs, force URL-only mode without the GitHub API.
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
  --subdir PATH      로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote           GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
  --fail-under INT   전체 점수가 이 값보다 낮으면 exit code 1로 종료합니다.
  -v, --verbose      터미널 대시보드에 finding을 자세히 출력합니다.
  --help             영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "init-policy": {
        "en": """Usage: repo-trust init-policy [OPTIONS]

Create starter CI policy files.

Options:
  --dir PATH  Repository directory to write policy files into. Defaults to current directory.
  --force     Overwrite existing RepoTrust policy files.
  --help      Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust init-policy [옵션]

CI 정책 시작 파일을 생성합니다.

옵션:
  --dir PATH  정책 파일을 생성할 저장소 디렉터리입니다. 기본값은 현재 디렉터리입니다.
  --force     기존 RepoTrust 정책 파일을 덮어씁니다.
  --help      영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "audit-install": {
        "en": """Usage: repo-trust audit-install [OPTIONS] TARGET

Compatibility command for install-time execution auditing.
Prefer `repo-trust safe-install --audit TARGET` for new usage.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  --subdir PATH  Audit this relative subdirectory of a local target.
  --help  Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust audit-install [옵션] 대상

설치 시점 실행 표면 점검을 위한 호환 명령입니다.
새 사용법은 `repo-trust-kr safe-install --audit 대상`을 권장합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  --subdir PATH  로컬 대상의 상대 하위 디렉터리를 점검합니다.
  --help  영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "safe-install": {
        "en": """Usage: repo-trust safe-install [OPTIONS] TARGET

Print install advice without running repository install commands.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  --config PATH  Load an explicit repotrust.toml policy file.
  --subdir PATH  Scan this relative subdirectory of a local target.
  --remote       For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only   For GitHub URLs, force URL-only mode without the GitHub API.
  --audit        Also audit local install-time execution surfaces.
  --help         Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust safe-install [옵션] 대상

저장소 설치 명령을 실행하지 않고 안전한 다음 단계를 안내합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  --config PATH  repotrust.toml 정책 파일을 직접 지정합니다.
  --subdir PATH  로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote       GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only   GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
  --audit        로컬 설치 시점 실행 표면도 함께 점검합니다.
  --help         영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "next-steps": {
        "en": """Usage: repo-trust next-steps [OPTIONS] [TARGET]

Print a beginner action plan from scan findings.

Arguments:
  TARGET  Local path or GitHub URL to inspect. Omit when using --from-json.

Options:
  --from-json PATH  Read an existing RepoTrust JSON report without rescanning.
  --config PATH     Load an explicit repotrust.toml policy file.
  --subdir PATH     Scan this relative subdirectory of a local target.
  --remote          For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only      For GitHub URLs, force URL-only mode without the GitHub API.
  --help            Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust next-steps [옵션] [대상]

검사 결과에서 초보자용 다음 조치 계획을 보여줍니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다. --from-json을 쓸 때는 생략합니다.

옵션:
  --from-json PATH  저장된 RepoTrust JSON 리포트를 재스캔 없이 읽습니다.
  --config PATH     repotrust.toml 정책 파일을 직접 지정합니다.
  --subdir PATH     로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote          GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only      GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
  --help            영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "tutorial": {
        "en": """Usage: repo-trust tutorial [OPTIONS]

Print a beginner tutorial with copyable commands.

Options:
  --help  Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust tutorial [옵션]

초보자가 처음 따라 할 명령을 보여줍니다.

옵션:
  --help  영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "samples": {
        "en": """Usage: repo-trust samples [OPTIONS]

Write built-in good/risky sample reports.

Options:
  -o, --output-dir PATH  Directory for generated sample reports. Defaults to result/.
  --help  Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust samples [옵션]

좋은/위험 샘플 리포트를 생성합니다.

옵션:
  -o, --output-dir PATH  샘플 리포트를 저장할 디렉터리입니다. 기본값은 result/입니다.
  --help  영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "gate": {
        "en": """Usage: repo-trust gate [OPTIONS] TARGET

Write JSON and fail when policy requirements are not met.

Arguments:
  TARGET  Local path or GitHub URL to inspect.

Options:
  -o, --output PATH  Write JSON report to this file. Defaults to stdout.
  --config PATH      Load an explicit repotrust.toml policy file.
  --subdir PATH      Scan this relative subdirectory of a local target.
  --remote           For GitHub URLs, call the GitHub API for read-only metadata.
  --parse-only       For GitHub URLs, force URL-only mode without the GitHub API.
  --fail-under INT   Exit with code 1 if total score is below this value.
  --help             Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust gate [옵션] 대상

JSON 리포트를 출력하고 정책 요구사항을 만족하지 못하면 실패합니다.

인자:
  대상  검사할 로컬 경로 또는 GitHub URL입니다.

옵션:
  -o, --output PATH  JSON 리포트를 저장할 경로입니다. 기본값은 stdout입니다.
  --config PATH      repotrust.toml 정책 파일을 직접 지정합니다.
  --subdir PATH      로컬 대상의 상대 하위 디렉터리를 검사합니다.
  --remote           GitHub URL에서 GitHub API read-only metadata를 조회합니다.
  --parse-only       GitHub URL을 API 호출 없이 URL 형식만 확인합니다.
  --fail-under INT   전체 점수가 이 값보다 낮으면 exit code 1로 종료합니다.
  --help             영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "explain": {
        "en": """Usage: repo-trust explain [OPTIONS] FINDING_ID

Explain a RepoTrust finding ID.

Arguments:
  FINDING_ID  Finding ID such as install.risky.uses_sudo.

Options:
  --help  Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust explain [옵션] FINDING_ID

RepoTrust finding ID의 의미와 추천 조치를 설명합니다.

인자:
  FINDING_ID  install.risky.uses_sudo 같은 finding ID입니다.

옵션:
  --help  영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
    "compare": {
        "en": """Usage: repo-trust compare [OPTIONS] OLD_JSON NEW_JSON

Compare two RepoTrust JSON reports.

Arguments:
  OLD_JSON  Older RepoTrust JSON report.
  NEW_JSON  Newer RepoTrust JSON report.

Options:
  --format, -f  Comparison output format: text, markdown, or html.
  --output, -o  Write the comparison report to this file.
  --help  Choose English or Korean help and exit.
""",
        "ko": """사용법: repo-trust compare [옵션] OLD_JSON NEW_JSON

두 RepoTrust JSON 리포트의 점수와 finding 변화를 비교합니다.

인자:
  OLD_JSON  이전 RepoTrust JSON 리포트입니다.
  NEW_JSON  최신 RepoTrust JSON 리포트입니다.

옵션:
  --format, -f  비교 출력 형식입니다: text, markdown, html.
  --output, -o  비교 리포트를 이 파일에 저장합니다.
  --help  영어 또는 한국어 도움말을 선택해 봅니다.
""",
    },
}

HELP_OPTION_HELP = "Choose English or Korean help and exit."


def show_localized_help(command: str) -> None:
    typer.echo("┌──(repotrust㉿help)-[language]")
    typer.echo("│ 01 english")
    typer.echo("│ 02 한국어")
    choice = typer.prompt("└─$ help language", default="1")
    locale = "ko" if choice.strip() == "2" else "en"
    typer.echo()
    typer.echo(localized_help_text(command, locale))


def localized_help_text(command: str, locale: str) -> str:
    command_help = PRODUCT_HELP.get(command, PRODUCT_HELP["root"])
    return command_help.get(locale, command_help["en"])
