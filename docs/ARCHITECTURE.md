# 현재 개편 구조 · 2026-10-29

개인 블로그 UI와 GitHub 글 관리 동선, 기존 CS 글 개정·공개 중단 및 사이트 전용 배포를 추가했습니다. 상세 계약은 [글 관리](CONTENT_MANAGEMENT.md), 실제 검증은 [개편 진행](redesign/PROGRESS.md)을 확인합니다.

- 직접 작성한 글은 blog/_posts의 content_type/published로 관리하며 topic_id가 없습니다. CS 큐·Notion 동기화에 넣지 않습니다. 글 종류는 cs/development/project/ssafy/essay입니다.
- 기존 글 개정은 config/maintenance.json의 이전·새 hash, 이전 공개 본문, 같은 Notion 페이지 ID를 고정해 수행합니다. ID/게시일/URL은 유지합니다. 수동 변경 블록은 보호하고 새 chunk 검증 후 이전 관리 chunk만 archive합니다. 상태 삭제로 복구하지 않습니다.
- 공개 중단된 CS ID는 state에 withdrawn tombstone을 남깁니다. 일반 글 삭제/비노출과 CS tombstone 모두 자동 재생성을 하지 않으며 Notion을 자동 삭제하지 않습니다.
- .publisher/site.json은 blog 입력 digest와 배포 기록을 보관합니다. 신규 CS 선택 전에 변경된 사이트를 topic_id 없는 site-update로 처리합니다. receipt의 __site__와 현재 입력을 대조한 후 성공을 기록합니다. 같은 텍스트의 Windows/Linux 줄바꿈과 정렬을 정규화합니다.
- 미게시 SVG는 private assets에 유지하며 선택된 ID의 cs-asset: 한 개만 검증·공개 URL로 변환합니다. source_content_hash와 실제 공개 content_hash·자산 hash를 구분합니다. 일반 원고 이미지는 공개 assets/uploads를 사용합니다.
- 아래 초기 게시 파이프라인의 권한 분리·중복 방지·동일 ID 복구·비공개 읽기 원칙을 유지합니다. 예약 게이트와 첫 ID 승인 정책은 확대하지 않았습니다.

# 구조와 복구 모델

공개 저장소는 `js05157/cs-interview`, 기본 브랜치는 `master`입니다. 비공개 저장소 `js05157/cs-content-private`도 실제 조회에서 `private=true`, `master`를 확인했습니다.

## 데이터 흐름

```text
Codex 초기 작성 → private/pending + manifests + generation_checkpoint
                     ↓ CONTENT_REPO_TOKEN (Contents: read)
Daily CS publisher → 대상·승인 정책 검사 → 필요한 Notion 사전 인증·목적지·계층 생성 확인
                     ↓ 사전 점검 성공
                 공개 Markdown + README + Jekyll post + state
                     ↓ GITHUB_TOKEN으로 먼저 commit/push
                 Notion 조회·조정 → 상태 checkpoint commit
                     ↓ 독립적으로 진행
                 Jekyll build → 산출물 검사 → Pages artifact → Pages deploy
                     ↓ deploy 결과와 빌드에 포함한 hash 목록
                 상태 checkpoint commit
```

Actions에서 비공개 checkout은 지원되는 workspace 하위 임시 경로에 받은 뒤 즉시 `$RUNNER_TEMP/cs-private`로 이동합니다. 그 경로는 Git 커밋 대상과 Jekyll source에 포함되지 않습니다. 비공개 저장소에 쓰는 API·push는 없습니다. 초기 콘텐츠를 저장하는 개발 단계의 사용자 Git 인증과 운영용 읽기 토큰은 별개입니다.

## 파일과 데이터 모델

- private `manifests/topics.json`: 고유 ID, 한·영 제목, 분야, 세부분야, 난이도, 우선순위, 선행 ID, 게시 순서, 원본/목표 경로.
- private `manifests/publish_queue.json`: ID 순서. 다음 원본이 없으면 건너뛰지 않고 중단합니다.
- private `manifests/generation_checkpoint.json`: 작성 개수, 배치 검증 결과, 다음 주제.
- public `.publisher/state.json`: 공개된 ID별 플랫폼 상태, URL, 날짜, 본문 hash 및 Notion 계층 캐시·불확실한 쓰기 의도. API 키와 미게시 본문은 없습니다.
- public `blog/_data/publisher.json`: 공개 게시 개수와 Notion 부모 URL만 제공합니다.

본문 hash는 UTF-8 텍스트의 줄바꿈을 LF로 정규화한 SHA-256입니다. 플랫폼별 성공 상태는 `complete`, 아직 처리하지 않은 경우 `pending`, 확인된 실패는 `failed`입니다. 오류 메시지는 분류 코드만 저장하며 API 원문이나 인증 정보를 기록하지 않습니다.

## 하루 1개와 멱등성

1. 미완료 게시가 있으면 가장 오래된 문서부터 복구합니다. 완료 전에는 다른 신규 주제를 선택하지 않습니다.
2. 신규 예약은 실제 실행 시점의 한국 날짜로 고정합니다. UTC 자정과 구분하며, 이전 날짜로 억지로 소급하지 않습니다.
3. 현재 승인 정책은 첫 ID만 허용합니다. 첫 게시 prepare는 Actions에서 Notion 인증·부모 ID/제목·활성 상태를 확인하고 실제 분야/세부분야 계층을 생성하거나 재사용합니다. 이 사전 점검이 실패하면 학습 원문은 공개하지 않습니다. 공개 원문·블로그 원문·상태·목차를 함께 push한 뒤에만 Notion 주제 본문을 생성합니다. push 실패 시 주제 본문 쓰기는 시작하지 않습니다.
4. 같은 날짜의 기록이 있으면 신규 문서를 선택하지 않습니다. 복구는 기존 ID와 날짜를 유지합니다.
5. 기존 파일이나 다른 글의 permalink를 발견하면 덮어쓰지 않고 중단합니다. 공개 후 사람이 본문을 수정한 경우에도 hash 불일치를 감지해 검토를 요구합니다.
6. Actions 전체 concurrency group과 로컬 배타적 잠금을 사용합니다. 별도 실행자가 경쟁하면 원격 Git의 fast-forward 검사로 두 번째 신규 push를 거부합니다. 강제 push와 자동 재배치는 없습니다.

Git 파일 준비 중 로컬 작업이 중단돼도 원격에 push하기 전이면 주제 본문의 외부 게시를 시작하지 않습니다. 사전 점검에서 만든 계층은 재사용합니다. 새 checkout으로 재시도하며, 원격 커밋 자체는 생성됐으나 클라이언트가 응답을 잃으면 다음 실행이 원격 상태에서 복구합니다.

## Notion의 불확실한 쓰기

분야/세부분야 페이지를 부모의 child_page 목록에서 확인하고, 제목이 중복이면 중단합니다. 주제 페이지는 같은 제목과 원문 GitHub 링크를 함께 확인합니다. 같은 이름의 수동 페이지는 보호합니다.

페이지 생성에는 원문과 블로그 링크를 함께 넣어 상태 기록이 유실돼도 기존 페이지를 찾습니다. 본문은 설명형 문서의 도입과 H2 섹션을 결정적인 토글 chunk로 나누고 제목, 문단, 목록, 코드, 인라인 서식과 표를 보존합니다. 각 토글의 제목 링크에는 결정적인 chunk fingerprint가 있어 추가 응답이 유실돼도 이미 반영된 섹션을 재사용합니다. API의 rich_text 2,000자 제한 등을 고려해 텍스트를 나눕니다.

429/529는 Retry-After에 따라 제한적으로 재시도합니다. GET의 일시적인 서버 오류도 재시도합니다. POST/PATCH의 5xx·네트워크 단절은 **무작정 재전송하지 않습니다**. 의도와 pending chunk를 저장하고 다음 실행에서 기존 결과를 조회합니다. 이미 확인되면 계속 진행하고 여전히 결과를 확인할 수 없으면 검토가 필요하다는 상태로 멈춥니다. 안전한 4xx 거절은 의도를 제거해 설정 수정 후 다시 처리할 수 있습니다.

Notion에는 Git과 결합된 원자적 트랜잭션이나 이 구현이 사용할 서버 측 idempotency key가 없습니다. 따라서 정확히 한 번을 수학적으로 보장한다고 주장하지 않습니다. 충돌·불확실성에서 정지하는 방식을 사용합니다. API 저장과 상태 push가 모두 불확실한 극단적인 상황은 운영자가 확인해야 합니다. 수동으로 토글을 삭제하거나 링크를 바꾸면 자동 복구 계약을 깨뜨릴 수 있습니다.

## Pages 상태

Jekyll 빌드는 `blog/`만 읽습니다. 별도 build job은 예약된 공개 커밋 SHA를 checkout합니다. 공개 원문·블로그 원문을 대조한 ID/hash receipt를 해당 실행에서 보관하고, 공식 deploy-pages 성공 이후 receipt에 포함된 문서만 완료 처리합니다. deploy가 실패해도 Notion의 성공은 유지합니다. 상태 push만 실패하면 재실행 시 같은 글을 재배포하여 복구할 수 있습니다.

봇의 `GITHUB_TOKEN` 커밋이 다른 push 워크플로우를 실행할 것이라고 가정하지 않으며, 게시 워크플로우 안에서 build/deploy를 직접 연결합니다. [GitHub Pages 사용자 정의 워크플로우](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

## 블로그 테마 선택

[Chirpy 공식 설치 안내](https://chirpy.cotes.page/posts/getting-started/)를 검토했습니다. 기존 공개 저장소와 공식 Jekyll 빌드 Action을 유지하고 프런트엔드 번들러·테마 초기화 의존성을 줄이기 위해 작은 커스텀 Liquid 레이아웃과 CSS/JS를 선택했습니다. 무료이며 외부 유료 서비스가 없습니다. 외부 웹 폰트 요청 없이 시스템 글꼴로 표시합니다.

라이트/다크, 네 메뉴, 검색 JSON, 접힌 목차, 글 종류 필터, 프로젝트·SSAFY 목록, Rouge 강조·코드 복사, SVG 확대, RSS/sitemap/robots/canonical/Open Graph를 구성합니다. CS 세부 카테고리는 내부 메타데이터로 유지합니다. 실제 글이 없을 때는 준비 상태를 표시하며 경력과 프로젝트를 만들어 넣지 않습니다.

## 보안 경계

- publish는 schedule 또는 master의 명시적 workflow_dispatch만 지원합니다. 외부 PR에 Secrets를 전달하지 않습니다.
- CI는 공개 소스만 사용하며 read 권한, persist-credentials=false로 실행합니다.
- dry-run job은 contents:read이며 Notion Secret을 전달하지 않고 파일도 수정하지 않습니다.
- 코드/문서 커밋은 contents:write job, 배포는 pages:write/id-token:write job으로 분리합니다.
- source 경로와 symlink 탈출, 중복 ID/제목/경로/순서, 잘못된 선행 관계를 검사합니다.
- raw HTML은 검토 대상으로 거부합니다. Jekyll의 Liquid는 원문을 raw 구간으로 감싸 문자 그대로 보존합니다.
- 게시 작업은 생성기를 호출하지 않으며 AI API 관련 의존성도 없습니다.

## 첫 실제 연동 검증

2026-10-28 기준 공개 주제는 첫 문서 1개, 세 플랫폼 상태는 complete입니다. 카테고리 키를 별도 변수로 조회하도록 수정했고 실제 분야별 글 목록과 검색 목록을 빌드 검사에서 대조합니다. 상세 실행·복구 근거는 FIRST_PUBLICATION_RESULT.md를 참고하세요.
