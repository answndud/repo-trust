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

