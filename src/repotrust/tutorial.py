from __future__ import annotations


def render_tutorial(*, locale: str = "en") -> str:
    if locale == "ko":
        return _render_ko()
    return _render_en()


def _render_en() -> str:
    return """RepoTrust Beginner Tutorial

Goal: inspect a repository without running its install commands.

Step 1. Start with your local checkout:
  repo-trust html .
  open result/<folder>-YYYY-MM-DD.html

Step 2. Before copying README install commands:
  repo-trust safe-install .

Step 3. Save a machine-readable report for later comparison:
  repo-trust json .

Optional GitHub URL check without API keys:
  repo-trust check https://github.com/owner/repo

If you prefer menus:
  repo-trust
  Choose [L] local scan, [S] safe install, then [J] export JSON.
"""


def _render_ko() -> str:
    return """RepoTrust 초보자 튜토리얼

목표: 저장소의 설치 명령을 실행하지 않고 먼저 신뢰 근거를 확인합니다.

1단계. 로컬 checkout부터 검사하세요:
  repo-trust-kr html .
  open result/<폴더>-YYYY-MM-DD.html

2단계. README 설치 명령을 복사하기 전에 확인하세요:
  repo-trust-kr safe-install .

3단계. 나중에 비교할 JSON 리포트를 저장하세요:
  repo-trust-kr json .

API key 없이 GitHub URL만 빠르게 확인하려면:
  repo-trust-kr check https://github.com/owner/repo

메뉴가 더 편하면:
  repo-trust-kr
  [L] 로컬 검사, [S] 안전 설치, [J] JSON 저장 순서로 선택하세요.
"""
