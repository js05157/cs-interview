# 첫 문서 실제 게시 검증 결과 · 2026-10-28

사용자가 승인한 `os-process-thread`(프로세스와 스레드) 한 건만 게시했습니다. 최초 게시 날짜는 한국 기준 2026-10-27이며, 2026-10-28 카테고리 수정 재배포에서도 날짜·ID·URL과 본문 hash를 유지했습니다. 추가 문서 게시와 예약 활성화는 하지 않았습니다.

## 실제 URL과 결과

| 플랫폼 | 결과 | 실제 URL |
| --- | --- | --- |
| GitHub | 성공 | [프로세스와 스레드](https://github.com/js05157/cs-interview/blob/master/Operating-System/Process/os-process-thread.md) |
| Notion | 성공 | [프로세스와 스레드](https://www.notion.so/40647f4c2c2581b4b2a3dd1cdeb62644) |
| GitHub Pages | 성공 | [블로그 게시글](https://js05157.github.io/cs-interview/topics/os-process-thread/) |

## Actions 사전 점검

최초 [수동 게시 실행 40520128773](https://github.com/js05157/cs-interview/actions/runs/40520128773)의 prepare 단계에서 다음을 확인한 뒤 학습 Markdown을 공개했습니다.

- Actions에 전달된 NOTION_API_KEY로 users/me 인증 성공.
- NOTION_PARENT_PAGE_ID가 승인된 **CS 기술 면접 공부**의 ID·제목과 일치하고 활성 상태임을 확인.
- 실제 목적지 `운영체제 → Process` 페이지 2개 생성 성공으로 콘텐츠 생성 권한 확인.
- 사전 점검의 키·개인 정보는 출력하지 않음. CONTENT_REPO_TOKEN은 비공개 읽기에만 사용하고 권한 변경 없음.

## 게시 결과 검증

- 공개 Markdown: `Operating-System/Process/os-process-thread.md`. 비공개 원본과 전체 텍스트·SHA-256 일치.
- Jekyll 글: `blog/_posts/2026-10-27-os-process-thread.md`. 원문·front matter·permalink 일치.
- README: 총 1개, 운영체제 1개. 최근 게시와 분야별 목록에 동일 문서·정확한 링크 반영.
- Notion: `CS 기술 면접 공부 → 운영체제 → Process → 프로세스와 스레드`. 연결 도구로 본문을 다시 읽어 원본의 파싱 결과와 대조. 10개 절, Java 코드 1개, 표 1개, 목록·링크·인라인 코드와 chunk fingerprint가 모두 일치.
- 실제 Jekyll 빌드: HTML 6개, 게시글 1개. `/cs-interview/` 경로와 정적 리소스 검사 통과.
- 실제 블로그·홈·학습 아카이브·About·Projects·CSS·JavaScript·검색 JSON·RSS·sitemap·robots HTTP 200 확인.
- 실제 브라우저: CSS 적용, JavaScript 목차 생성, 운영체제 1개 표시, 카테고리 목록에서 글 이동, `프로세스` 검색 결과 표시 성공. 오류·경고 로그 없음.
- `.publisher/state.json`: ID는 첫 문서 1개뿐이며 github_status/notion_status/blog_status가 모두 complete. Notion 불확실한 쓰기 목록은 비어 있고 세 URL·게시 날짜·본문 hash가 일치.

## 발견한 문제와 같은 문서 복구

처음 배포한 화면에서 Jekyll의 중첩 Liquid 키 조회가 카테고리를 찾지 못해 운영체제 수가 0으로 표시되고 아카이브 글이 빠졌습니다. 키를 먼저 변수에 대입하도록 레이아웃·홈·아카이브를 수정했습니다. 산출물 검증에도 검색 목록과 실제 분야별 글 목록의 일치 검사를 추가했습니다.

[수정 CI 40521085551](https://github.com/js05157/cs-interview/actions/runs/40521085551)는 Python 테스트 46개와 실제 글을 포함한 Jekyll 빌드를 통과했습니다. 첫 글의 blog_status를 재빌드 대기로 기록한 뒤 [복구 실행 40604831780](https://github.com/js05157/cs-interview/actions/runs/40604831780)이 같은 ID를 recover로 선택해 재배포했습니다. needs_notion=false로 Notion은 재생성하지 않았고, 새 Markdown·새 주제도 만들지 않았습니다. build/deploy/record가 모두 성공했습니다.

## 중복 방지와 현재 승인 범위

- 실제 완료 상태를 대상으로 게시 날짜를 2026-10-27로 지정한 읽기 전용 선택 결과는 `action=daily-limit`, `topic_id=null`입니다. 파일 hash가 바뀌지 않았으며 중복 검증을 위한 실제 publish는 실행하지 않았습니다.
- 다음 날짜의 후보도 첫 ID만 허용하는 `config/publication_policy.json`에서 거부됩니다. 날짜가 바뀐 복구 실행에서도 기존 첫 글만 복구한 것을 확인했습니다.
- CS_AUTO_PUBLISH는 여전히 **미설정·비활성**입니다. 완료 후 불필요한 수동 publish를 다시 실행하지 않습니다.

## 남은 작업과 재개

비공개 본문은 **34개 작성 / 66개 남음**, 다음 작성 순서는 **35번 ds-array-list**입니다. `manifests/remaining_generation_plan.json`에 16/14/14/10/12개 단위의 배치를 준비했습니다. 이번 검증에서는 추가 본문을 생성하지 않았습니다. 작성 체크포인트와 게시 대기열은 별개이며, 공개 게시 상태는 1개입니다.

이번 첫 게시를 위해 사용자가 추가 설정할 항목은 없습니다. 이후 다른 문서 게시와 예약 활성화는 별도 승인이 필요합니다. Notion은 연결 도구 재조회로 검증했으며 네이티브 앱에서 모든 토글을 직접 펼쳐 확인한 것은 아닙니다. 브라우저 상호작용 검증은 데스크톱 내장 브라우저에서 수행했습니다.
