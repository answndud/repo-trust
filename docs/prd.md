# PRD: RepoTrust

## 한 줄 요약

RepoTrust는 오픈소스 저장소를 설치하거나 dependency로 채택하기 전에, 문서 품질과 설치 위험, 보안 신호, 프로젝트 위생 상태를 빠르게 점검해 설명 가능한 리포트를 만드는 CLI 도구다.

## 문제

개발자는 GitHub 저장소를 사용할 때 다음 질문에 자주 부딪힌다.

- 이 repo를 믿고 설치해도 되는가?
- README에 있는 명령어를 그대로 실행해도 되는가?
- AI agent에게 이 repo 설치를 맡겨도 되는가?
- 회사/개인 프로젝트에 dependency로 넣어도 되는가?
- README만 보고 따라 해도 충분한가?

현재는 이런 판단을 사람이 README, install command, LICENSE, CI, 보안 정책, dependency manifest를 흩어서 읽으며 감으로 판단하는 경우가 많다. RepoTrust는 이 판단을 자동화하되, 최종 결론을 강요하지 않고 근거와 불확실성을 함께 보여준다.

## 목표 사용자

- 새로운 오픈소스 패키지를 검토하는 개인 개발자.
- AI coding agent에게 설치/실행 작업을 맡기기 전에 위험 명령을 확인하고 싶은 사용자.
- 회사 프로젝트에 dependency를 추가하기 전 최소 신뢰 신호를 확인하려는 팀.
- 오픈소스 maintainer로서 자신의 저장소 문서/보안 상태를 점검하려는 사람.

## v1 baseline 범위

v0.1.0 baseline에 포함한다:

- `repotrust scan <target>` CLI.
- target은 로컬 경로 또는 GitHub URL.
- 로컬 경로 분석:
  - README 존재와 기본 품질.
  - README install command 위험 패턴.
  - `SECURITY.md`, CI workflow, Dependabot, lockfile, dependency manifest 존재.
  - LICENSE와 기본 프로젝트 metadata 존재.
- GitHub URL 분석:
  - URL 파싱만 수행.
  - clone/API 호출은 하지 않음.
  - remote scan 미지원 finding을 표시.
- Markdown, JSON, static HTML 리포트.
- explainable heuristic 기반 RepoTrust Score.

포함하지 않는다:

- GitHub App.
- 웹 대시보드.
- remote clone.
- GitHub API 호출.
- 실제 취약점 DB 조회.
- contributor profile 분석.
- release/tag freshness 분석.

## 현재 구현 상태

v0.1.0 이후 post-v1 작업으로 explicit remote scan이 추가됐다:

- 공식 사용자 CLI는 `repo-trust html/json/check/safe-install <target>` command group이다.
- `repo-trust`만 실행하면 interactive launcher가 열려 로컬 검사, GitHub URL 검사, HTML/JSON 저장, 빠른 터미널 확인을 선택할 수 있다.
- `repo-trust html/json/check/safe-install/gate <github-url>`은 기본적으로 네트워크 없이 URL만 파싱한다.
- `repo-trust html/json/check/safe-install/gate <github-url> --remote`는 GitHub REST API read-only metadata를 조회한다.
- `repo-trust html/json/check/safe-install/gate <github-url> --parse-only`는 호환성 옵션이며 기본값과 같은 URL-only 동작을 강제한다.
- legacy `repotrust scan <github-url>`은 계속 parse-only로 유지하고, `--remote`를 명시했을 때만 remote scan을 실행한다.
- Remote scan은 clone하지 않으며 repository metadata, root contents, README content, Dependabot config, GitHub Actions workflow metadata, package-managed repository의 release/tag freshness를 기존 `ScanResult`와 report contract에 연결한다.
- Remote metadata scoring은 보수적으로 유지한다. Archived repository, disabled issue tracking, 오래된 release/tag처럼 명확하고 낮은 강도의 maintenance/support signal만 점수화하고, fork/private/stars/default branch/language/size 같은 context metadata는 점수화하지 않는다.
- `repotrust.toml`은 명시적 `--config`로만 로드되며 score threshold, profile gate, finding disable, severity override, category weight를 지원한다.
- `repo-trust gate`는 CI에서 JSON report를 보존하면서 score/profile policy 실패를 exit code로 표현한다.

## 성공 기준

- 처음 보는 저장소를 로컬 checkout으로 스캔했을 때 1초 내외로 리포트를 생성한다.
- 사용자는 총점뿐 아니라 감점 이유와 권장 조치를 바로 볼 수 있다.
- JSON report는 CI나 다른 도구에서 재사용 가능하다.
- README install command의 명백한 고위험 패턴을 놓치지 않는다.
- 로컬에서 확인할 수 없는 정보는 추측하지 않고 "아직 확인하지 않음"으로 남긴다.

## 제품 원칙

- "안전하다/위험하다"를 단정하기보다 "확인 가능한 신뢰 신호"를 보여준다.
- 감점은 항상 finding으로 설명한다.
- AI agent가 읽고 실행하기 쉬운 출력 구조를 유지한다.
- 작은 로컬 CLI 기반을 먼저 안정화한 뒤 remote scan과 dashboard를 확장한다.

## 향후 확장 아이디어

- `repo-trust html/json/check/safe-install` 기반의 product CLI UX 고도화.
- dependency vulnerability source 연동.
- 중앙/상속형 조직 policy config.
- maintainer activity 점수.
- HTML 리포트 고도화 또는 웹 대시보드.
