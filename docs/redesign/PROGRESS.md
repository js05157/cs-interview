# 개편 진행 기록 · 2026-10-29

- 보존 태그: public pre-personal-blog-20261028, private pre-editorial-redesign-20261028. 기존 공개 state·첫 ID/날짜/URL/Notion ID·정책·워크플로우는 개정 적용 전까지 동일하게 유지했습니다.
- 개인 소개 홈, 네 메뉴, 실제 GitHub 활동 snapshot, 최근 글, 빈 프로젝트/SSAFY 목록, 글 종류 필터, 검색, 접힌 목차, 코드 복사, SVG 확대, 라이트/다크, GitHub 글 관리 동선을 구현했습니다. 프로젝트 내용은 사용자의 ‘나중에 추가’ 선택에 따라 넣지 않았습니다.
- 실제 로컬 Jekyll 3.10 빌드 성공. 생성 HTML 10개, 글 1개, /cs-interview/ 내부 자산·링크·SEO/RSS/사이트맵 검사 통과. 첫 글 개정 fixture도 별도 실제 빌드했습니다.
- 브라우저 기본 데스크톱/390px 모바일 홈, 검색 결과, 작성 미리보기의 HTML·javascript: 비실행, Markdown 다운로드, 첫 샘플 SVG 표시·확대를 확인했습니다. 실행하지 않은 기능은 별도로 남깁니다.
- Python 60개 테스트: 기존 48개 + 개정/사이트 영수증/공개 중단 관련 12개. 기존 첫 글과 신규 일반 원고를 분리합니다. Notion append/archive 응답 유실, 수동 메모 보존, 수동 편집 차단, 페이지 재생성 금지와 동일 ID 복구를 mock 검증했습니다.
- 첫 샘플은 비공개 원문에서 편집하고 기존 Java 코드를 그대로 유지해 JDK17로 재실행했습니다. 원본은 공개 보존 태그/공개 첫 본문 백업에도 있습니다. private의 나머지 99개는 첫 샘플 연동 검증 전 편집하지 않았습니다.
- config/maintenance.json은 기존 os-process-thread 개정만 지정합니다. .publisher/site.json과 __site__ 배포 digest가 사이트만 배포하는 경로를 제공합니다. workflow 권한은 확대하지 않고 기존 workflow 호출을 호환했습니다.
- 2026-10-29 현재 비공개 저장소 private=true, Secret 이름 3개 존재, Pages source=workflow, CS_AUTO_PUBLISH 미설정. 토큰 값은 읽거나 출력하지 않았습니다. 운영 CONTENT_REPO_TOKEN의 권한을 변경하지 않았습니다.

## 다음 작업

1. 현재 코드 CI 및 실제 Actions dry-run 확인. 첫 개정 수동 실행 전에 CI 성공 SHA·첫 ID 정책·비활성 게이트를 확인합니다.
2. 기존 Notion 페이지 같은 ID 수정·같은 URL 사이트 배포, 실제 본문/도식/코드/표 대조. 실패하면 같은 개정만 복구합니다.
3. 첫 샘플 통합 검증 후 비공개 나머지 99개를 맥락 검토하여 배치 편집하고 코드/출처/ID 보존과 체크포인트를 저장합니다.
4. 모바일/데스크톱 최종 화면·권한 동선·일반 글 fixture·dry-run과 영수증 상태 확인. 미확인 결과를 성공으로 기록하지 않습니다.

운영 방법은 ../CONTENT_MANAGEMENT.md를 참고하세요. 완료한 UI 구현과 실제 배포 완료는 구분합니다.
