# ADR: RepoTrust 주요 결정 기록

이 문서는 프로젝트를 오래 쉬었다가 다시 시작할 때 "왜 이렇게 했는지"를 빠르게 복구하기 위한 결정 기록이다.

## ADR-001: v1은 CLI와 파일 리포트로 시작한다

상태: Accepted

결정:

- v1은 `repotrust scan <target>` CLI를 중심으로 만든다.
- 출력은 Markdown, JSON, static HTML을 지원한다.
- GitHub App과 웹 대시보드는 뒤로 미룬다.

이유:

- 신뢰 평가 rule과 score 모델이 먼저 안정화되어야 한다.
- CLI는 테스트와 CI 통합이 쉽고, agent가 사용하기 좋다.
- dashboard부터 만들면 평가 기준보다 UI 구현이 먼저 커질 위험이 있다.

## ADR-002: GitHub URL은 파싱만 하고 clone/API 호출은 하지 않는다

상태: Accepted

결정:

- `https://github.com/owner/repo` 형태는 target metadata로 파싱한다.
- remote repository를 자동 clone하거나 GitHub API를 호출하지 않는다.
- 대신 "remote scan not enabled" finding을 낸다.

이유:

- 사용자가 scan 명령을 실행했을 때 네트워크 부작용이 없어야 한다.
- rate limit, auth, private repo, API 실패 처리를 v1에서 다루지 않는다.
- 로컬 스캔 품질을 먼저 안정화한다.

## ADR-003: explainable heuristic scoring을 사용한다

상태: Accepted

결정:

- 총점은 category별 점수의 weighted sum으로 계산한다.
- 모든 주요 감점은 finding으로 설명한다.
- finding은 evidence와 recommendation을 포함한다.

이유:

- RepoTrust의 목적은 "점수"보다 "왜 신뢰하거나 조심해야 하는지" 설명하는 것이다.
- 사용자가 CI policy나 수동 검토에서 finding ID를 기준으로 판단할 수 있다.
- black-box score는 신뢰 도구 자체의 신뢰도를 떨어뜨린다.

## ADR-004: core model은 dataclasses로 시작한다

상태: Accepted

결정:

- `Finding`, `Score`, `Target`, `DetectedFiles`, `ScanResult`는 dataclasses로 구현한다.
- Pydantic은 아직 도입하지 않는다.

이유:

- 현재 입력 검증 요구가 단순하다.
- dependency를 최소화하고 구조를 읽기 쉽게 유지한다.
- 외부 config, remote API response, schema validation이 커지면 재검토한다.

## ADR-005: AGENTS.md는 짧게 유지하고 자세한 맥락은 docs/로 분리한다

상태: Accepted

결정:

- 루트 `AGENTS.md`는 프로젝트 목적, 문서 맵, 작업 원칙, 검증 원칙, 금지사항만 담는다.
- PRD/TRD/ADR/domain/testing/workflow 문서는 `docs/`에 둔다.

이유:

- Codex가 매번 읽는 entrypoint가 길어지면 중요한 작업 맥락을 압박한다.
- 오래 쉬었다가 돌아올 때는 상세 문서를 선택적으로 읽는 편이 낫다.
- OpenAI Codex 문서와 Harness engineering 글의 권장 방향과 맞다.

## ADR-006: skills/MCP/subagents는 지금 만들지 않는다

상태: Accepted

결정:

- repo-local skills는 아직 만들지 않는다.
- project-scoped MCP config도 만들지 않는다.
- subagents 사용을 전제한 작업 구조도 만들지 않는다.

이유:

- 현재 프로젝트는 작고 반복 workflow가 아직 명확하지 않다.
- v1은 외부 도구 연결 없이도 구현/검증 가능하다.
- 복잡한 하네스는 필요가 생겼을 때 추가한다.

재검토 조건:

- 동일한 release/report review 작업을 반복하게 될 때 skills 고려.
- GitHub API, vulnerability DB, browser inspection이 필수화될 때 MCP 고려.
- 대규모 rule expansion이나 보안/문서/CLI 병렬 리뷰가 자주 필요할 때 subagents 고려.

## ADR-007: Finding ID는 public-ish contract로 취급한다

상태: Accepted

결정:

- Finding ID는 사용자가 JSON report를 비교하거나 CI policy를 만들 때 사용할 수 있는 안정적인 식별자로 취급한다.
- 기존 ID의 의미를 조용히 바꾸지 않는다.
- rule 의미가 바뀌면 기존 ID를 재사용하지 않고 새 ID를 만든다.
- severity나 message를 조정할 수는 있지만, 의미가 유지되는 경우에만 같은 ID를 유지한다.

이유:

- RepoTrust의 핵심 가치는 설명 가능한 finding이다.
- ID가 흔들리면 자동화와 리포트 비교가 어려워진다.
- rule이 늘어날수록 ID 안정성이 JSON contract만큼 중요해진다.

## ADR-008: 설정 파일 v1은 `repotrust.toml`로 설계한다

상태: Accepted

결정:

- 설정 파일 v1은 repository root의 `repotrust.toml`을 기본 파일명으로 설계한다.
- 구현 시 명시적 `--config <path>` 옵션을 먼저 지원하고, 자동 탐지는 그 다음 단계로 둔다.
- v1 설정 항목은 `policy.fail_under`와 네 개 category weight로 제한한다.
- CLI flag가 config 값보다 우선한다.
- rule enable/disable, severity override, remote credential 설정은 v1 config에서 제외한다.

이유:

- TOML은 Python 프로젝트 사용자가 이해하기 쉽고, Python 3.11+에서는 `tomllib`로 읽을 수 있다.
- threshold와 category weight는 CI/조직 정책에 가장 직접적으로 필요한 최소 설정이다.
- rule별 override까지 처음부터 열면 scoring contract와 finding 안정성이 복잡해진다.
- 명시적 `--config`를 먼저 지원하면 자동 탐지의 예측 불가능성을 피할 수 있다.

재검토 조건:

- Python 3.10 지원을 유지하면서 TOML 파서 fallback이 필요할 때.
- 조직별 policy inheritance가 필요해질 때.
- rule disable/override 요구가 반복적으로 생길 때.

## ADR-009: Legacy remote GitHub scan은 명시적 `--remote`로만 설계한다

상태: Accepted for legacy `repotrust scan`; product CLI는 ADR-010을 따른다.

결정:

- 기본 `repotrust scan <github-url>` 동작은 계속 URL 파싱만 수행한다.
- 네트워크를 사용하는 GitHub API scan은 `--remote`를 명시했을 때만 수행한다.
- remote scan은 clone을 사용하지 않고 GitHub REST API의 read-only metadata만 사용한다.
- 인증은 선택 사항이며, 구현 시 `GITHUB_TOKEN` 환경 변수를 우선 사용한다.
- API 실패, 인증 실패, rate limit, partial scan은 모두 finding으로 표현한다.
- remote scan 구현은 CLI v1 완성 범위 밖이며, v1에서는 설계까지만 완료한다.

이유:

- scan 명령이 암묵적으로 네트워크를 사용하면 예측 가능성과 재현성이 떨어진다.
- clone 없이 metadata를 조회하면 설치 전 신뢰 판단이라는 제품 목적에 맞다.
- API 실패를 파일 부재로 오해하면 점수 신뢰도가 떨어진다.
- v1은 local scan과 report contract를 안정화하는 데 집중해야 한다.

## ADR-010: Product CLI는 GitHub URL remote scan을 기본값으로 둔다

상태: Accepted

결정:

- 공식 사용자 CLI는 `repo-trust html/json/check <target>` command group으로 제공한다.
- `repo-trust html/json/check <github-url>`은 GitHub REST API read-only metadata 조회를 기본으로 실행한다.
- 네트워크 없는 URL 파싱은 `--parse-only`로 명시한다.
- `repotrust scan`은 legacy compatibility를 위해 기존 `--remote` opt-in contract를 유지한다.
- HTML/JSON product commands는 기본적으로 `result/<target>-YYYY-MM-DD.<ext>`에 저장한다.

이유:

- 사용자용 GitHub URL 리포트 명령에서 매번 `--remote --format ... --output ...`을 붙이는 흐름은 제품 CLI처럼 보이지 않는다.
- `html`, `json`, `check` 명령은 사용자가 원하는 산출물을 먼저 표현하므로 README와 help가 단순해진다.
- legacy 명령은 자동화와 기존 테스트 contract를 깨지 않으면서 새 UX로 이동할 시간을 제공한다.

재검토 조건:

- 사용자가 GitHub URL scan을 기본 기대 동작으로 요구할 때.
- API rate limit이나 private repo 지원 요구가 커질 때.
- GitHub App 또는 웹 대시보드 개발을 시작할 때.

## ADR-010: Remote metadata는 score와 evidence를 분리한다

상태: Accepted

결정:

- Remote metadata 중 archived 상태처럼 명확한 maintenance risk는 score-deducting finding으로 둘 수 있다.
- fork/private/default branch/stars/language/size/created date 같은 정보는 v0.1.x에서는 evidence-only context로 시작한다.
- release/tag freshness는 바로 고감점하지 않고, no release practice와 release가 중요하지 않은 project type을 구분할 수 있을 때 낮은 severity부터 도입한다.
- API 실패나 권한 부족으로 알 수 없는 상태는 missing signal로 변환하지 않고 remote failure 또는 partial finding으로 유지한다.
- contributor profile 분석은 source attribution, privacy, impersonation risk가 설계될 때까지 보류한다.

이유:

- Remote API metadata는 해석 맥락이 없으면 쉽게 과잉 점수화된다.
- star count나 fork 여부는 popularity/context signal이지 안전성 자체가 아니다.
- unknown 상태를 absence로 처리하면 RepoTrust 점수 신뢰도가 떨어진다.

재검토 조건:

- 조직 policy config에서 evidence-only metadata를 score에 반영하고 싶다는 요구가 생길 때.
- package ecosystem별 release practice를 구분할 수 있을 때.
- remote scan이 GitHub App 또는 dashboard로 확장될 때.
