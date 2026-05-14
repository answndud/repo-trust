from __future__ import annotations

ConsoleLocale = str
ConsoleText = dict[str, object]

CONSOLE_TEXT: dict[str, ConsoleText] = {
    "en": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust",
        "tagline": "Offline-first trust checks before installing a repository.",
        "first_run_hint": "First run: [L] scan local repo -> [S] safe install -> [J] export JSON.",
        "mission_label": "Mission",
        "mission": (
            "Decide whether a repository is safe enough to install, depend on, "
            "or hand to an AI agent."
        ),
        "command_mode_label": "Command Mode",
        "command_mode": (
            "repo-trust html <target>   repo-trust safe-install <target>   "
            "repo-trust check <target>"
        ),
        "workflows_title": "Select action:",
        "key_column": "Key",
        "action_column": "Action",
        "use_when_column": "Use When",
        "output_column": "Output",
        "workflows": [
            ("G", "GitHub repo", "URL check without API by default", ""),
            ("L", "Local repo", "Full file-level local scan", ""),
            ("C", "Quick check", "Instant trust summary", ""),
            ("J", "Export JSON", "Save machine-readable report", ""),
            ("S", "Safe Install", "Advice before running install commands", ""),
            ("N", "Next Steps", "Prioritized action plan after a scan", ""),
            ("T", "Tutorial", "Copyable first-run commands", ""),
            ("P", "Samples", "Generate good/risky sample reports", ""),
        ],
        "controls_title": "Controls",
        "controls": "[R] Reports   [?] Help   [Q] Quit",
        "input_controls": "[B] Back",
        "recent_count": "Recent: {count} reports",
        "recent_reports_title": "Recent Reports",
        "recent_reports_open_hint": "Open helper: copy a path below, or run `open <path>` on macOS.",
        "no_saved_reports": (
            "No saved reports yet. HTML and JSON commands write to result/ by default."
        ),
        "no_reports_found": "No reports found in result/",
        "number_column": "No.",
        "path_column": "Path",
        "type_column": "Type",
        "json_report_type": "json report",
        "html_report_type": "html report",
        "compare_html_report_type": "compare html",
        "markdown_report_type": "markdown report",
        "select_prompt": "Press a key",
        "selected_github": "Selected: GitHub repository",
        "selected_local": "Selected: Local repository",
        "selected_check": "Selected: Quick check",
        "selected_json": "Selected: JSON export",
        "selected_safe_install": "Selected: Safe install advice",
        "selected_next_steps": "Selected: Next steps plan",
        "selected_tutorial": "Selected: Beginner tutorial",
        "selected_samples": "Selected: Sample report gallery",
        "processing_message": "Running analysis...",
        "session_closed": "Session closed.",
        "local_path_prompt": "Enter local repository path:",
        "github_url_prompt": "Enter GitHub URL:",
        "github_url_example": "Example: https://github.com/openai/openai-python",
        "any_target_prompt": "Enter repository target:",
        "default_hint": "default",
        "back_message": "Back to action selection.",
    },
    "ko": {
        "brand_title": "REPO-TRUST",
        "console_title": "RepoTrust",
        "tagline": "설치 전 저장소 신뢰도를 기본은 API 없이 점검합니다.",
        "first_run_hint": "처음이면: [L] 로컬 검사 -> [S] 안전 설치 -> [J] JSON 저장.",
        "mission_label": "목적",
        "mission": (
            "저장소를 설치하거나 의존성으로 추가하거나 AI agent에게 맡겨도 되는지 "
            "확인 가능한 근거로 판단합니다."
        ),
        "command_mode_label": "명령 모드",
        "command_mode": (
            "repo-trust html <대상>   repo-trust safe-install <대상>   "
            "repo-trust check <대상>"
        ),
        "workflows_title": "작업 선택:",
        "key_column": "번호",
        "action_column": "작업",
        "use_when_column": "언제 쓰나",
        "output_column": "결과",
        "workflows": [
            ("G", "GitHub 저장소", "기본은 API 없이 URL 확인", ""),
            ("L", "로컬 저장소", "파일 근거까지 로컬 검사", ""),
            ("C", "빠른 점검", "즉시 요약 보기", ""),
            ("J", "JSON 내보내기", "기계가 읽는 리포트 저장", ""),
            ("S", "안전 설치", "설치 전 다음 단계 안내", ""),
            ("N", "다음 조치", "검사 후 우선순위별 행동 계획", ""),
            ("T", "튜토리얼", "처음 따라 할 명령 보기", ""),
            ("P", "샘플", "좋은/위험 리포트 예시 생성", ""),
        ],
        "controls_title": "컨트롤",
        "controls": "[R] 리포트   [?] 도움말   [Q] 종료",
        "input_controls": "[B] 뒤로",
        "recent_count": "최근 리포트: {count}개",
        "recent_reports_title": "최근 리포트",
        "recent_reports_open_hint": "열기 안내: 아래 경로를 복사하거나 macOS에서는 `open <경로>`를 실행하세요.",
        "no_saved_reports": (
            "아직 저장된 리포트가 없습니다. HTML/JSON 명령은 기본적으로 result/에 저장됩니다."
        ),
        "no_reports_found": "result/에서 리포트를 찾지 못했습니다.",
        "number_column": "번호",
        "path_column": "경로",
        "type_column": "형식",
        "json_report_type": "JSON 리포트",
        "html_report_type": "HTML 리포트",
        "compare_html_report_type": "비교 HTML",
        "markdown_report_type": "Markdown 리포트",
        "select_prompt": "키를 누르세요",
        "selected_github": "선택됨: GitHub 저장소",
        "selected_local": "선택됨: 로컬 저장소",
        "selected_check": "선택됨: 빠른 점검",
        "selected_json": "선택됨: JSON 내보내기",
        "selected_safe_install": "선택됨: 안전 설치 안내",
        "selected_next_steps": "선택됨: 다음 조치 계획",
        "selected_tutorial": "선택됨: 초보자 튜토리얼",
        "selected_samples": "선택됨: 샘플 리포트 갤러리",
        "processing_message": "분석 중...",
        "session_closed": "세션을 종료했습니다.",
        "local_path_prompt": "로컬 저장소 경로 입력:",
        "github_url_prompt": "GitHub URL 입력:",
        "github_url_example": "예: https://github.com/openai/openai-python",
        "any_target_prompt": "검사할 대상 입력:",
        "default_hint": "기본값",
        "back_message": "작업 선택으로 돌아갑니다.",
    },
}


def console_text(locale: ConsoleLocale) -> ConsoleText:
    return CONSOLE_TEXT.get(locale, CONSOLE_TEXT["en"])
