# Command Mode 초보자 가이드

RepoTrust는 이제 Command Mode만 공식 사용 방식으로 제공합니다. 예전처럼 `repo-trust` 또는 `repo-trust-kr`만 입력해서 메뉴를 고르는 Console Mode는 제거됐습니다.

Command Mode는 할 일을 한 줄에 직접 적는 방식입니다.

```bash
repo-trust-kr check .
```

위 명령은 "현재 폴더를 검사해서 터미널에 결과를 보여줘"라는 뜻입니다. `repo-trust-kr`은 한국어 출력, `repo-trust`는 영어 출력을 기본으로 합니다.

## 처음 실행 순서

처음에는 아래 순서만 따라 하세요.

```bash
repo-trust-kr samples
repo-trust-kr check .
repo-trust-kr safe-install .
repo-trust-kr next-steps .
repo-trust-kr html .
```

각 명령의 의미는 다음과 같습니다.

| 순서 | 명령 | 언제 쓰나요 |
| --- | --- | --- |
| 1 | `repo-trust-kr samples` | 좋은 리포트와 위험 리포트가 어떻게 생겼는지 먼저 볼 때 |
| 2 | `repo-trust-kr check .` | 현재 폴더를 바로 검사해 터미널에서 판단할 때 |
| 3 | `repo-trust-kr safe-install .` | README 설치 명령을 실행하기 전에 위험한 설치 패턴이 있는지 볼 때 |
| 4 | `repo-trust-kr next-steps .` | finding이 나왔는데 무엇부터 해야 할지 모를 때 |
| 5 | `repo-trust-kr html .` | 브라우저에서 읽거나 공유할 HTML 리포트를 저장할 때 |

## 대상 쓰는 법

RepoTrust 명령의 마지막에는 보통 검사 대상을 씁니다.

```bash
repo-trust-kr check .
repo-trust-kr check ../some-project
repo-trust-kr check https://github.com/owner/repo
```

`.`은 현재 터미널이 있는 폴더입니다. 내가 검사하려는 저장소 안에서 터미널을 열었다면 `.`을 쓰면 됩니다.

`../some-project`처럼 폴더 경로를 넣으면 그 폴더를 검사합니다.

GitHub URL을 넣으면 기본적으로 API를 호출하지 않고 URL 형식만 확인합니다. 파일 수준 근거가 부족하므로 중요한 dependency 후보는 clone한 뒤 로컬 폴더로 검사하는 편이 좋습니다.

```bash
git clone https://github.com/owner/repo
cd repo
repo-trust-kr check .
```

## 현재 폴더 검사하기

현재 폴더를 빠르게 검사하려면 `check`를 사용합니다.

```bash
repo-trust-kr check .
```

이 명령은 파일을 저장하지 않고 터미널에만 결과를 보여줍니다. 점수, 판정, 목적별 판단, 다음 행동을 빠르게 보고 싶을 때 사용합니다.

## GitHub URL 검사하기

URL만 빠르게 확인하려면 GitHub URL을 그대로 넣습니다.

```bash
repo-trust-kr check https://github.com/openai/codex
```

기본 GitHub URL 검사는 clone도 하지 않고 GitHub API도 호출하지 않습니다. 그래서 "URL은 GitHub 저장소처럼 보이지만 파일 근거는 부족하다"는 판단이 나올 수 있습니다.

GitHub metadata까지 보고 싶을 때만 `--remote`를 붙입니다.

```bash
repo-trust-kr check https://github.com/openai/codex --remote
```

`--remote`는 read-only GitHub API를 사용하지만 범위가 고정되어 있습니다. 확인하는 것은 repository metadata, root contents, README content뿐입니다. Actions workflow, Dependabot 설정, release/tag freshness, commit activity, 중첩 `.github/SECURITY.md`까지 봐야 하면 저장소를 로컬로 checkout한 뒤 `repo-trust-kr check .`로 검사하세요. `--remote`는 rate limit이나 token 설정의 영향을 받을 수 있습니다.

## HTML 리포트 만들기

브라우저에서 읽을 리포트가 필요하면 `html`을 사용합니다.

```bash
repo-trust-kr html .
```

기본 저장 위치는 `result/<대상>-YYYY-MM-DD.html`입니다.

저장 위치를 직접 정하려면 `--output`을 사용합니다.

```bash
repo-trust-kr html . --output reports/current.html
```

HTML 리포트는 정적 evidence artifact입니다. Safe Install이나 Next Steps 같은 단계별 안내는 터미널 command로 따로 봅니다.

## JSON 리포트 만들기

자동화나 다른 도구 연동이 필요하면 `json`을 사용합니다.

```bash
repo-trust-kr json . --output reports/current.json
```

JSON은 기계가 읽는 계약입니다. `schema_version`, `target`, `detected_files`, `findings`, `score`, `assessment`, `generated_at`을 포함합니다.

나중에 저장된 JSON에서 다음 조치를 다시 볼 수 있습니다.

## 설치해도 되는지 보기

README의 설치 명령을 복사하기 전에 `safe-install`을 실행하세요.

```bash
repo-trust-kr safe-install .
```

이 명령은 설치 명령을 실행하지 않습니다. README와 manifest를 읽고, 위험한 설치 패턴이 있으면 멈추라고 안내합니다.

설치 시점에 실행될 수 있는 파일까지 함께 보고 싶으면 `--audit`을 붙입니다.

```bash
repo-trust-kr safe-install --audit .
```

`curl ... | sh`, `sudo npm install -g`, `python -c`, 직접 VCS 설치 같은 패턴이 보이면 설치 전에 코드를 먼저 검토해야 합니다.

## 다음 조치 보기

finding이 많아서 무엇부터 해야 할지 모르겠다면 `next-steps`를 사용합니다.

```bash
repo-trust-kr next-steps .
```

이미 저장한 JSON에서 이어서 보려면 `--from-json`을 사용합니다.

```bash
repo-trust-kr json . --output reports/current.json
repo-trust-kr next-steps --from-json reports/current.json
```

이 방식은 저장소를 다시 검사하지 않고 JSON 파일만 읽습니다.

## Finding ID 설명 보기

리포트에 `install.risky.uses_sudo` 같은 ID가 나오면 `explain`으로 뜻을 확인합니다.

```bash
repo-trust-kr explain install.risky.uses_sudo
```

`explain`은 저장소를 검사하지 않습니다. finding ID의 영역, 기본 심각도, 의미, 추천 조치를 보여줍니다.

## CI에서 실패 기준으로 쓰기

CI에서는 `gate`를 사용합니다.

```bash
repo-trust gate . --fail-under 80 --output reports/repotrust.json
```

점수가 기준보다 낮으면 exit code 1로 종료됩니다. GitHub Actions 예시는 `examples/github-actions-repotrust-gate.yml`을 참고하세요.

정책 파일을 쓰고 싶다면 `repotrust.toml`에는 현재 `[policy] fail_under`만 둡니다.

```toml
[policy]
fail_under = 80
```

## 샘플 리포트 만들어보기

처음에는 실제 저장소보다 샘플을 먼저 보는 편이 쉽습니다.

```bash
repo-trust-kr samples
```

생성 예시:

```text
result/sample-good-YYYY-MM-DD.html
result/sample-good-YYYY-MM-DD.json
result/sample-risky-YYYY-MM-DD.html
result/sample-risky-YYYY-MM-DD.json
```

good 샘플은 통과한 상태를 보여주고, risky 샘플은 설치 전에 멈춰야 하는 상황을 보여줍니다.

## 자주 헷갈리는 것

`.`은 현재 폴더입니다.

```bash
repo-trust-kr check .
```

다른 폴더를 검사하려면 경로를 씁니다.

```bash
repo-trust-kr check ../my-project
```

Monorepo의 일부 폴더만 검사하려면 `--subdir`을 씁니다.

```bash
repo-trust-kr check . --subdir packages/api
```

GitHub URL에 `--subdir`을 붙일 수는 없습니다. 하위 폴더를 정확히 검사하려면 clone한 뒤 로컬 폴더에 `--subdir`을 사용하세요.

`--output`은 저장 파일 경로입니다.

```bash
repo-trust-kr html . --output reports/current.html
repo-trust-kr json . --output reports/current.json
```

`--format`은 사용하지 않습니다. `repo-trust html`, `repo-trust json`, `repo-trust check`처럼 command를 직접 고르는 방식을 사용하세요.

## 좋은 예시와 나쁜 예시

좋은 예시:

```bash
repo-trust-kr check .
repo-trust-kr safe-install .
repo-trust-kr html . --output reports/current.html
repo-trust-kr json . --output reports/current.json
```

나쁜 예시:

```bash
repo-trust-kr
repo-trust-kr check https://github.com/owner/repo --subdir packages/api
repo-trust-kr html .
```

첫 번째는 더 이상 메뉴를 열지 않습니다. 사용할 command를 직접 적어야 합니다.

두 번째는 GitHub URL에 `--subdir`을 붙인 예입니다. 로컬 checkout에서만 사용하세요.

세 번째는 나쁜 명령은 아니지만, 저장 위치를 알아야 합니다. 파일 위치를 명확히 남기고 싶으면 `--output`을 붙이는 편이 좋습니다.
