from __future__ import annotations

ConsoleLocale = str
ConsoleText = dict[str, object]

CONSOLE_TEXT: dict[str, ConsoleText] = {
    "en": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust Console",
        "tagline": "Repository trust intelligence for dependencies, agents, and audits",
        "mission_label": "Mission",
        "mission": (
            "Decide whether a repository is safe enough to install, depend on, "
            "or hand to an AI agent."
        ),
        "command_mode_label": "Command Mode",
        "command_mode": (
            "repo-trust html <target>   repo-trust json <target>   repo-trust check <target>"
        ),
        "workflows_title": "Workflows",
        "key_column": "Key",
        "action_column": "Action",
        "use_when_column": "Use When",
        "output_column": "Output",
        "workflows": [
            ("1", "Scan local repository", "You already have a checkout", "HTML report"),
            ("2", "Scan GitHub URL", "You want a browser-readable remote report", "HTML report"),
            ("3", "Export GitHub URL", "You need automation-friendly data", "JSON report"),
            ("4", "Quick check", "You want a terminal assessment now", "Dashboard"),
            ("5", "List recent reports", "You want to find prior scan artifacts", "File list"),
            ("6", "Command reference", "You want flags and direct commands", "Help"),
            ("q", "Quit", "No scan", "Exit"),
        ],
        "recent_reports_title": "Recent Reports",
        "no_saved_reports": (
            "No saved reports yet. HTML and JSON commands write to result/ by default."
        ),
        "no_reports_found": "No reports found in result/",
        "number_column": "No.",
        "path_column": "Path",
        "type_column": "Type",
        "select_prompt": "select>",
        "session_closed": "Session closed.",
        "local_path_prompt": "target.local>",
        "github_url_prompt": "target.github>",
        "any_target_prompt": "target>",
    },
    "ko": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust 한국어 콘솔",
        "tagline": "dependency, agent, audit를 위한 저장소 신뢰도 점검 도구",
        "mission_label": "목적",
        "mission": (
            "저장소를 설치하거나 의존성으로 추가하거나 AI agent에게 맡겨도 되는지 "
            "확인 가능한 근거로 판단합니다."
        ),
        "command_mode_label": "명령 모드",
        "command_mode": (
            "repo-trust html <대상>   repo-trust json <대상>   repo-trust check <대상>"
        ),
        "workflows_title": "워크플로우",
        "key_column": "번호",
        "action_column": "작업",
        "use_when_column": "언제 쓰나",
        "output_column": "결과",
        "workflows": [
            ("1", "로컬 저장소 검사", "이미 clone한 폴더가 있을 때", "HTML 리포트"),
            ("2", "GitHub URL 검사", "브라우저용 원격 리포트가 필요할 때", "HTML 리포트"),
            ("3", "GitHub URL 내보내기", "자동화용 데이터가 필요할 때", "JSON 리포트"),
            ("4", "빠른 점검", "터미널에서 바로 판단할 때", "대시보드"),
            ("5", "최근 리포트 목록", "이전 결과 파일을 찾을 때", "파일 목록"),
            ("6", "명령어 도움말", "직접 명령과 옵션을 확인할 때", "도움말"),
            ("q", "종료", "검사하지 않음", "종료"),
        ],
        "recent_reports_title": "최근 리포트",
        "no_saved_reports": (
            "아직 저장된 리포트가 없습니다. HTML/JSON 명령은 기본적으로 result/에 저장됩니다."
        ),
        "no_reports_found": "result/에서 리포트를 찾지 못했습니다.",
        "number_column": "번호",
        "path_column": "경로",
        "type_column": "형식",
        "select_prompt": "선택>",
        "session_closed": "세션을 종료했습니다.",
        "local_path_prompt": "로컬 경로>",
        "github_url_prompt": "GitHub URL>",
        "any_target_prompt": "대상>",
    },
}


def console_text(locale: ConsoleLocale) -> ConsoleText:
    return CONSOLE_TEXT.get(locale, CONSOLE_TEXT["en"])
