# 검증 결과 · 2026-10-27

## 결과 구분

| 검사 | 결과 | 확인 범위 |
| --- | --- | --- |
| Python 단위·모의 통합 테스트 | 34개 통과 | 중복, 날짜 제한, 상태, Notion 재시도와 응답 유실, Pages receipt 등 |
| 워크플로우 정적 검사 | 2개 통과 | actionlint 1.7.12, YAML·표현식·Action 입력 등, shellcheck는 비활성 |
| 기본 사이트 실제 Jekyll 빌드 | 성공 | HTML 5개, 게시글 0개, 11개 출력 파일 |
| 합성 글 포함 Jekyll 빌드 | 성공 | HTML 6개, 합성 게시글 1개 |
| 출력 링크·정적 리소스 | 통과 | `/cs-interview/` 내부 링크, CSS·JS, 검색 JSON, RSS, sitemap, robots |
| 게시글 표현 | 통과 | 표, Rouge 코드 강조, Liquid 문자 보존, 관련 글 영역 |
| SEO 메타데이터 | 통과 | HTML별 canonical과 Open Graph URL 일치 |
| 실제 콘텐츠 로컬 dry-run | 통과 | 두 번 같은 후보 선택, 추적/미추적 공개 파일 해시 동일, state 게시 수 0 |
| 비공개 문서 Notion 오프라인 변환 | 22개 통과 | Markdown→블록과 요청 크기, Notion API 호출 없음 |
| GitHub Actions CI | 미실행 | 원격에 ci.yml 미등록 |
| GitHub Actions dry-run | 미실행 | 원격에 publish.yml 미등록 |
| CONTENT_REPO_TOKEN의 실제 읽기 인증 | 미검증 | Secret 이름은 등록 확인, 값 접근 없음 |
| Notion 실제 쓰기·Pages 실제 배포 | 미실행 | 사용자 승인 전 수행 금지 유지 |

## 빌드 환경

공식 `actions/jekyll-build-pages@v1`이 참조하는 이미지 `ghcr.io/actions/jekyll-build-pages:v1.0.13`을 로컬 Docker에서 사용했습니다. [공식 Action 정의](https://github.com/actions/jekyll-build-pages/blob/v1/action.yml)

확인한 이미지 digest:

```text
sha256:6791ebfd912185ed59bfb5fb102664fa872496b79f87ff8b9cfba292a7345041
```

원본 `blog/`는 읽기 전용으로 마운트하고 별도 임시 출력 폴더에 Jekyll을 빌드했습니다. 인증 토큰을 전달하지 않았으며 Pages 업로드·배포 명령을 실행하지 않았습니다. 합성 글은 비공개 학습 콘텐츠와 무관한 테스트 데이터입니다.

## 인증·설정

- 개발용 Git 인증의 현재 scope는 `repo`이며 `workflow`는 없습니다. 같은 업로드를 반복하거나 토큰 권한을 변경하지 않았습니다.
- 연결 GitHub 도구도 이전 작업에서 워크플로우 쓰기 403이 확인되었으므로 같은 실패를 반복하지 않았습니다.
- 공개·비공개 저장소는 모두 master이며 비공개 저장소의 `private=true`를 재확인했습니다.
- Repository Secret 이름 3개(`CONTENT_REPO_TOKEN`, `NOTION_API_KEY`, `NOTION_PARENT_PAGE_ID`)를 확인했습니다. 값은 읽거나 출력하지 않았습니다.
- `CS_AUTO_PUBLISH`는 미설정입니다. Pages의 `build_type=workflow`, github-pages environment 존재를 읽기 전용으로 확인했습니다. 환경에 배포 보호 규칙을 추가하거나 변경하지 않았습니다.
- 설정에 블로그 URL이 존재한다는 사실을 실제 배포 성공으로 해석하지 않습니다.

## 다음 확인

GitHub 웹에서 검토된 두 워크플로우를 master에 등록한 뒤, CI 로그와 dry-run을 확인해야 합니다. 단계는 `WORKFLOW_REGISTRATION.md`를 참고하세요. dry-run의 mode를 publish로 변경하지 않습니다.

로컬 테스트는 실제 Actions 실행의 대체 증거가 아닙니다. 특히 read-only Secret의 비공개 checkout 권한은 Actions dry-run 성공 이후에만 검증 완료로 기록합니다.
