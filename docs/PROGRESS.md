# PROGRESS

지금 진행 중인 상태만 기록한다. 작업이 완료되면 최종 상태와 검증 결과를 `docs/COMPLETED.md`로 옮기고 이 문서에서는 제거한다.

## 운영 규칙

- 의미 있는 구현, 수정, 검증 후 현재 상태를 갱신한다.
- 작업이 중단될 때는 미완료 상태, blocker, 다음 액션을 남긴다.
- 검증 명령과 결과를 `최근 검증`에 남긴다.
- 완료된 작업은 이 문서에 유지하지 않는다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.

## 현재 작업

v0.2.6 GitHub Release publish 승인 대기.

## 개발 상태 요약

v0.2.6 release candidate는 로컬 검증과 clean wheel smoke를 통과했다. 남은 작업은 GitHub Release publish뿐이며 push/tag/release 생성이 필요한 live external write라 명시 승인이 필요하다.

## Blocker

push/tag/GitHub Release 생성 명시 승인 필요.

## 최근 검증

시작 전 기준: `a7317b3 Add safe install pre-run checklist`, 전체 테스트 `149 passed`.
`git diff --check && .venv/bin/python -m pytest -q`는 `149 passed`였다.
`.venv/bin/python -m build --outdir /tmp/repotrust-release-v0.2.6/dist`는 wheel/sdist를 생성했다.
Clean wheel install smoke에서 세 entrypoint version `0.2.6`, safe-install checklist, Console `[S] 안전 설치`, risky fixture JSON 생성, `json.tool` 검증이 성공했다.
Self-scan JSON은 score `98`, grade `A`, high confidence, full coverage, medium/high finding 0개였다.

## 다음 액션

사용자가 publish를 명시 승인하면 release prep commit push, CI 확인, tag/release publish를 진행한다.
