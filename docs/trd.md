# TRD: RepoTrust 기술 설계

## 기술 선택

- 언어: Python.
- CLI: Typer.
- 터미널 출력: Rich.
- 모델: dataclasses.
- 테스트: pytest.
- 패키징: `pyproject.toml` 기반 pip-compatible 구조.

이 선택은 v1에서 빠른 구현, 낮은 진입 장벽, 단순한 배포를 우선한 결과다.

## 현재 명령

```bash
repotrust scan <target>
```

옵션:

- `--format markdown|json|html`
- `--output <path>`
- `--fail-under <score>`
- `--verbose`

## 데이터 흐름

1. `cli.py`가 인자와 옵션을 받는다.
2. `scanner.py`가 target을 분석하고 scan 흐름을 결정한다.
3. `targets.py`가 local path와 GitHub URL을 구분한다.
4. local path이면 `detection.py`가 파일 존재 여부를 찾는다.
5. `rules.py`가 finding을 만든다.
6. `scoring.py`가 finding을 category score와 total score로 변환한다.
7. `reports.py`가 `ScanResult`를 Markdown/JSON/HTML로 렌더링한다.

## 핵심 모델

- `Target`: 입력 target의 종류와 파싱 결과.
- `DetectedFiles`: README, LICENSE, SECURITY, workflow, manifest, lockfile 등 탐지 결과.
- `Finding`: `id`, `category`, `severity`, `message`, `evidence`, `recommendation`.
- `Score`: category별 점수, total, grade, risk label.
- `ScanResult`: target, detected files, findings, score, generated timestamp.

## 모듈 책임

- `cli.py`: CLI UX, stdout/stderr 분리, exit code.
- `scanner.py`: scan orchestration. 세부 rule을 직접 구현하지 않는다.
- `targets.py`: target parsing. 네트워크 접근 금지.
- `detection.py`: 파일 시스템 탐지. scoring 판단 금지.
- `rules.py`: finding 생성. report rendering 금지.
- `scoring.py`: 감점/가중치 계산. 파일 시스템 접근 금지.
- `reports.py`: `ScanResult` 렌더링만 담당. scan logic 금지.

## 스코어링

현재 weight:

- README Quality: 25%
- Install Safety: 30%
- Security Posture: 25%
- Project Hygiene: 20%

severity별 감점은 `scoring.py`에만 둔다. rule은 severity를 결정하고, 점수 계산은 scoring layer가 담당한다.

현재 severity 감점:

- `info`: 0
- `low`: 8
- `medium`: 18
- `high`: 35

현재 grade threshold:

- `A`: 90 이상
- `B`: 80 이상
- `C`: 70 이상
- `D`: 60 이상
- `F`: 60 미만

Finding ID는 JSON report 사용자에게 노출되는 안정적인 식별자다. 새 rule을 추가할 때 기존 ID의 의미를 바꾸지 말고, 의미가 달라지면 새 ID를 만든다.

## 출력 정책

- report 본문은 stdout 또는 `--output` 파일로 나간다.
- Rich summary와 상태 메시지는 stderr로 나간다.
- JSON 출력은 pipe 가능한 valid JSON이어야 한다.
- HTML은 단일 static file이며 서버가 필요 없어야 한다.

## JSON Report Contract

JSON report는 외부 도구와 CI에서 사용할 수 있는 안정적인 contract로 취급한다. v1 contract는 `schema_version: "1.0"`을 최상위에 포함한다.

최상위 key:

- `schema_version`: JSON report contract version.
- `target`: 입력 target과 파싱 결과.
- `detected_files`: repository file detection 결과.
- `findings`: finding 객체 배열.
- `score`: category score와 total score.
- `generated_at`: UTC ISO timestamp.

Finding key:

- `id`
- `category`
- `severity`
- `message`
- `evidence`
- `recommendation`

Score key:

- `categories`
- `total`
- `max_score`
- `grade`
- `risk_label`

JSON report를 stdout으로 출력할 때는 summary/table이 섞이면 안 된다. 상태 출력은 stderr에만 기록한다.

## v1 기술 제약

- GitHub URL은 파싱만 한다.
- clone, fetch, GitHub API call은 하지 않는다.
- dependency manifest를 읽더라도 실제 vulnerability lookup은 하지 않는다.
- README command parsing은 skeleton 수준의 regex heuristic이다.

## 확장 포인트

- remote scan을 추가할 때는 기본 동작으로 켜지 말고 explicit option으로 시작한다.
- 외부 API가 들어오면 source attribution과 failure mode를 finding으로 표현한다.
- policy config가 생기면 scoring과 rule enable/disable을 분리한다.
- HTML dashboard가 생겨도 CLI JSON schema를 먼저 안정화한다.
