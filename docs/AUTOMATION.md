# 자동 게시 운영 · 2026-10-30

사용자가 기존 CS 학습 자료의 자동화 실행을 승인했습니다. 검증 완료된 기존 100편을 순서대로 GitHub·Notion·GitHub Pages에 하루 신규 1편씩 게시합니다. 최초 공개된 글은 원래 ID·날짜·본문·URL을 보존합니다.

현재 단계: 실제 첫 추가 게시·검증 완료, Repository Variable `CS_AUTO_PUBLISH=true` 활성화 및 재조회 확인. 2026-10-30 기준 공개 2편, 미게시 98편입니다.

## 활성화 검증 결과

- 승인 정책 커밋 `e921d81`: 로컬 Python 테스트 76개, 기존 100편 원문 검사 통과.
- [CI 40899609101](https://github.com/js05157/cs-interview/actions/runs/40899609101)와 [dry-run 40899605320](https://github.com/js05157/cs-interview/actions/runs/40899605320) 성공.
- [실제 게시 40899711673](https://github.com/js05157/cs-interview/actions/runs/40899711673): publish/build/deploy/record 모두 성공. 신규 글은 기존 순서 2번 컨텍스트 스위칭 1편입니다. 첫 글 상태·본문·날짜·URL은 보존했습니다.
- [GitHub 원문](https://github.com/js05157/cs-interview/blob/master/Operating-System/Process/os-context-switch.md), [Notion](https://www.notion.so/40847f4c2c25817f82c6e33b7442fba3), [블로그](https://js05157.github.io/cs-interview/topics/os-context-switch/) 확인. 원문·README·Jekyll 원본·상태 일치, Notion의 기존 부모/분야/Process 계층과 다섯 절·질문 토글·청크 fingerprint 확인. 실제 블로그·CSS/JS·SVG·검색 인덱스·글 목록 HTTP 200.
- 같은 2026-10-30 날짜 선택은 `daily-limit`로 신규 게시 차단. 다음 한국 날짜의 선택은 원래 순서 3번이며 실제 추가 게시 없이 조회만 했습니다.
- 다음 예약 확인은 2026-10-30 10:30 KST지만 오늘 신규 글을 이미 게시해 건너뜁니다. 다음 신규 게시 대상 시점은 2026-10-31 10:30 KST입니다. 미래 예약의 실제 실행은 아직 관측하지 않았습니다.

## 범위와 일정

- 기존 `Daily CS publisher`의 매일 10:30, `Asia/Seoul` 예약을 사용합니다. 실행 지연·누락 가능성이 있으므로 정각 완료를 보장하지 않습니다.
- `config/publication_policy.json`에 고정된 기존 100개 주제만 허용합니다. 아직 공개하지 않은 ID 목록은 복사하지 않고 ID SHA-256 허용 목록을 사용합니다. 이는 암호화가 아니며 승인 범위를 고정하기 위한 방식입니다. 미래에 추가한 주제는 별도 승인·정책 갱신이 필요합니다.
- 같은 한국 날짜에 신규 1개까지만 처리합니다. 수동 실행도 그날의 신규 1개로 계산합니다. 미완료 플랫폼은 기존 ID·날짜로 먼저 복구합니다.
- 전체 대기열 완료 후 신규 게시를 중단합니다. OpenAI API·유료 서비스를 사용하지 않습니다.

## 실행과 중지

예약 게이트는 Repository Variable `CS_AUTO_PUBLISH=true`입니다. 중지는 Settings → Secrets and variables → Actions → Variables에서 값을 `false`로 바꿉니다. Secret이 아닌 Variable입니다. 워크플로 자체를 수정하거나 토큰 권한을 확대할 필요가 없습니다.

수동 확인은 Actions → Daily CS publisher → Run workflow → `dry-run`을 사용합니다. 실제 수동 게시·복구는 `publish`이며 같은 날짜의 신규 중복을 차단합니다. 실패 시 상태를 삭제하거나 다른 주제를 선택하지 말고 [운영 복구 절차](OPERATIONS.md)를 따릅니다. 수동 publish는 예약 게이트가 false여도 실행되므로 필요한 경우에만 사용합니다.

CONTENT_REPO_TOKEN은 비공개 원문 읽기 전용을 유지합니다. 공개 파일·상태 push는 워크플로의 GITHUB_TOKEN이 수행합니다. Notion은 기존 부모 페이지의 분야→세부분야→주제 계층을 사용하고 게시 전 인증·부모 ID/제목·활성 상태를 확인합니다.
