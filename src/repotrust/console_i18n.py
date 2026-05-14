from __future__ import annotations

ConsoleLocale = str
ConsoleText = dict[str, object]

CONSOLE_TEXT: dict[str, ConsoleText] = {
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
        ],
        "controls_title": "컨트롤",
        "controls": "[?] 도움말   [Q] 종료",
        "input_controls": "[B] 뒤로",
        "select_prompt": "키를 누르세요",
        "selected_github": "선택됨: GitHub 저장소",
        "selected_local": "선택됨: 로컬 저장소",
        "selected_check": "선택됨: 빠른 점검",
        "selected_json": "선택됨: JSON 내보내기",
        "selected_safe_install": "선택됨: 안전 설치 안내",
        "selected_next_steps": "선택됨: 다음 조치 계획",
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
    return CONSOLE_TEXT["ko"]
