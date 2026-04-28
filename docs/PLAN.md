# PLAN

앞으로 할 active 작업만 기록한다. 완료된 작업은 이 문서에 남기지 않고 `docs/COMPLETED.md`로 옮긴다.

## 운영 규칙

- 새 기능, 우선순위 변경, 범위 변경은 구현 전에 이 문서에 먼저 반영한다.
- 작업 항목은 `In Progress` 또는 `Pending` 중 하나에만 둔다.
- 각 작업에는 완료 기준을 적는다.
- 완료된 작업은 `docs/COMPLETED.md`로 archive한 뒤 이 문서에서 삭제한다.
- 모든 active 작업이 끝나면 상태 섹션에는 `현재 active 작업 없음`만 남긴다.
- 프로젝트가 아직 완성 전이면 다음 개발 계획을 우선순위 순서로 다시 채운다.

## 현재 목표

오픈소스 공개 준비를 마친 뒤 GitHub에 push하고, post-v1 작업을 Ralph-style 반복 루프로 진행한다.

## 현재 우선순위

1. 변경 사항을 검증하고 GitHub `main`에 push한다.
2. Remote GitHub scan MVP부터 작은 작업 단위로 반복 구현한다.

## In Progress

현재 active 작업 없음

## Pending

### 1. GitHub main push

- 작업: 공개 준비 변경을 커밋하고 `origin/main`에 push한다.
- 완료 기준:
  - 워크트리가 clean 상태다.
  - `git push origin main`이 성공한다.

### 2. Ralph-style post-v1 loop 세팅

- 작업: RepoTrust 방식의 반복 작업 루프를 하네스에 반영한다.
- 완료 기준:
  - 작은 story 단위, 검증 루틴, 완료 archive, 다음 story 승격 규칙이 문서화된다.
  - external Ralph 구현을 그대로 복사하지 않고 현재 `PLAN/PROGRESS/COMPLETED` 흐름에 맞춘다.

### 3. Remote GitHub scan MVP

- 작업: `repotrust scan <github-url> --remote` MVP를 구현한다.
- 완료 기준:
  - clone 없이 GitHub REST API read-only metadata를 조회한다.
  - auth/rate-limit/not-found/API error가 finding으로 표현된다.
  - tests는 mocked HTTP/fake transport를 사용하고 실제 네트워크를 요구하지 않는다.

## 다음 실행 순서

1. GitHub push를 진행한다.
2. Ralph-style loop 규칙을 문서화한다.
3. `Remote GitHub scan MVP`를 작은 story로 쪼개 구현한다.
