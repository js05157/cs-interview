# 글 관리

## 직접 작성하는 글

[글 관리 화면](https://js05157.github.io/cs-interview/manage/)에서 제목·날짜·종류·태그·공개 여부와 Markdown을 작성합니다. 미리보기는 브라우저 안에서 동작하며 HTML과 javascript: 링크를 실행하지 않습니다. 저장은 GitHub 편집기로 이동한 후 GitHub 로그인이 확인된 계정이 커밋합니다. 프런트엔드는 PAT나 Actions Secret을 받지 않습니다. 이것은 별도 인증 서버를 둔 CMS가 아닌 GitHub 편집 동선입니다.

1. 원고 작성 → GitHub에서 저장 → master의 blog/_posts 파일명과 내용을 확인 → 커밋합니다. 긴 원고는 복사 안내 또는 Markdown 다운로드를 이용합니다. 저장 버튼만 누른 것으로 게시가 끝나지 않습니다.
2. 기존 일반 글은 목록의 수정 링크로 GitHub 편집기·미리보기를 엽니다. `content_type`은 `cs`, `development`, `project`, `ssafy`, `essay` 중 하나입니다. `ssafy` 글은 SSAFY 목록에 자동으로 포함됩니다.
3. 공개 중단은 front matter의 `published: false`로 설정합니다. 삭제는 GitHub의 삭제 화면에서 커밋합니다. Git 기록을 통해 되돌릴 수 있습니다. 공개 저장소이므로 비노출 원고도 소스와 과거 기록은 공개입니다. 비밀 초안은 저장하지 마세요.
4. 이미지 업로드는 blog/assets/uploads에 합니다. `![이미지 설명](/cs-interview/assets/uploads/example.png)`처럼 삽입합니다. 파일명에 공백을 피하고 alt를 작성합니다. GitHub의 본문 미리보기와 실제 Jekyll 렌더링은 일부 다를 수 있습니다.
5. CI 성공 확인 후 Actions → Daily CS publisher → Run workflow → master, mode=publish를 수동 실행하면 변경된 사이트를 배포합니다. `.publisher/site.json`의 입력 digest가 달라지면 **새 CS 주제를 선택하기 전에 site-update**로 처리합니다. 사이트 변경도 없고 기존 미완료도 없을 때는 첫 주제 제한 정책이 다음 CS 공개를 차단합니다. 예약 게이트는 켜지 않습니다.

일반 글에는 `topic_id`를 넣지 않습니다. 게시 엔진은 일반 글을 비공개 CS 큐에 추가하거나 Notion에 복제하지 않습니다. 삭제된 일반 글을 다시 생성하지 않습니다. 검색·RSS·사이트맵·종류별 목록은 실제 공개된 site.posts를 기준으로 빌드됩니다.

## 권한

/manage/ 자체는 공개된 원고 도구입니다. 접근을 숨기는 방식으로 보안을 구현하지 않습니다. 실제 master 저장·수정·삭제는 GitHub 서버의 로그인·저장소 쓰기 권한 검사로 보호됩니다. 비로그인 방문자는 GitHub 로그인 화면으로 이동하며 저장 권한이 없는 계정은 master를 직접 수정할 수 없습니다. 포크·PR 제안 권한과 원본 저장소 쓰기 권한은 다릅니다. 저장소에 다른 write/admin 협업자를 추가하면 그 사람도 편집할 수 있으므로 소유자만 운영하려면 GitHub Settings → Collaborators에서 추가 쓰기 권한을 주지 않습니다.

브라우저에 토큰·비밀번호를 입력하는 자체 폼은 없습니다. 새 OAuth 앱·인증 서버·유료 서비스 연결도 없습니다. CONTENT_REPO_TOKEN의 읽기 전용 권한은 그대로 유지합니다.

## CS 관리 글

CS 관리 글은 공개 파일을 직접 덮어쓰지 않습니다. 비공개 원문을 편집하고 **기존 글에 대한 명시적인 개정 계획**을 검토합니다. 현재 config/maintenance.json은 사용자 승인된 os-process-thread 한 건만 지정합니다. publication_policy.json의 허용 ID를 확대하지 않습니다.

개정 계획에는 `schema_version: 1`, `kind: revision`, 기존 `topic_id`, `from_hash`, 새 비공개 본문 `to_hash`, 기존 `notion_page_id`, 공개된 이전 본문의 `previous_body_path`를 기록합니다. 이전 본문은 공개된 내용만 백업합니다. 신규/미게시 본문을 공개 config나 백업에 넣지 않습니다.

```powershell
python -m scripts.cli validate --private ../cs-content-private
python -m scripts.cli prepare --private ../cs-content-private
```

미리보기에서 action=revision, 기존 ID인지 확인한 뒤 CI를 통과한 master에서 위의 수동 Actions publish를 실행합니다. Actions는 기존 Secret으로 인증·부모 제목/ID·계층과 동일 주제 페이지를 먼저 확인합니다. 빠진 계층이나 페이지를 새로 만드는 방식으로 개정하지 않습니다. 공개 원문·Jekyll·상태 hash를 함께 커밋한 후 기존 Notion 페이지의 내용만 조정합니다.

Notion의 이전 관리 토글은 원문 fingerprint뿐 아니라 본문·서식·중첩 블록을 대조합니다. 수동 변경을 발견하면 중단합니다. 새 토글을 추가하고 조회 검증한 다음 이전 관리 토글만 보관 처리합니다. 별도 수동 메모는 유지합니다. 응답 유실은 pending marker/block ID를 기록하고 다음 실행에서 조회합니다. 결과를 확인할 수 없으면 멈추며 새 주제를 선택하지 않습니다. 기존 URL·게시일·페이지 ID는 유지합니다.

중단 시 같은 workflow를 재실행해 동일 개정을 복구합니다. Notion의 401/403은 Secret 만료·페이지 공유·연결의 update 권한을 확인합니다. `*-uncertain-review-required`, `manual-edit-protected`는 실제 페이지를 대조해 검토해야 하며 state를 삭제하거나 ID를 초기화하지 않습니다. Git와 Notion 사이의 원자적 트랜잭션은 없으므로 동시 수동 편집은 피합니다.

### CS 공개 중단

현재 첫 글에는 실행하지 않습니다. 이후 특정 기존 글의 공개 중단을 승인받으면 그 시점의 hash·이전 본문·페이지 ID를 고정한 `kind: withdraw` 계획을 준비합니다. 같은 ID의 state에 `publication_status: withdrawn` tombstone을 남기고 Jekyll의 published=false와 README 노출 중단을 반영합니다. 공개 원문과 Git 기록은 보존되므로 기밀 삭제 기능이 아닙니다. Notion 상태·페이지는 유지하고 자동 삭제하지 않습니다. 큐에서 이 ID를 다시 새 글로 선택하거나 복구로 되살리지 않습니다. 재공개는 별도 검토가 필요합니다.

## 배포 영수증과 충돌

빌드 receipt에는 관리 글 hash와 `__site__` digest를 포함합니다. 배포 성공을 기록할 때 master의 입력과 다르면 완료로 표시하지 않고 중단합니다. 동시 원고 변경이 있었다면 최신 master에서 사이트를 다시 빌드·배포합니다. Git push는 fast-forward만 사용합니다. 파일 수동 변경을 force push나 상태 삭제로 우회하지 않습니다.

## 활동 데이터 갱신

`python -m scripts.activity --help`의 옵션으로 GitHub 공개 프로필 calendar snapshot을 갱신하고 CI 후 사이트를 수동 배포합니다. 홈은 출처와 기준 날짜를 표시합니다. 방문 시 외부 위젯에 접속하지 않으며, 가져오기에 실패하면 마지막 실제 snapshot을 유지합니다. 실시간 활동 또는 블로그 작성 횟수가 아닙니다.

API 근거: [Notion 이미지 블록](https://developers.notion.com/reference/block#image), [블록 갱신](https://developers.notion.com/reference/update-a-block). 도식은 직접 작성한 SVG이며 지원되는 직접 호스팅 HTTPS 이미지로 동기화합니다.
