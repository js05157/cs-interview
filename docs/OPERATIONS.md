# 운영 안내

## 현재 상태와 승인 범위

첫 문서 os-process-thread 한 건의 실제 수동 게시·같은 글 카테고리 수정 재배포를 완료했습니다. 세 플랫폼 상태는 complete이며 실제 URL과 증거는 [FIRST_PUBLICATION_RESULT.md](FIRST_PUBLICATION_RESULT.md)를 참고하세요. 이후 다른 문서 게시와 예약 활성화는 승인되지 않았습니다.

CS_AUTO_PUBLISH는 2026-10-28 조회에서도 미설정·비활성입니다. config/publication_policy.json은 첫 ID만 허용하므로 날짜가 바뀌어도 두 번째 주제를 게시하지 않습니다. 새 운영 범위는 별도 사용자 승인 후 이 정책을 검토·수정해야 합니다.

## 기존 설정과 검증

공개 저장소 Settings → Secrets and variables → Actions → Repository secrets에 NOTION_API_KEY, NOTION_PARENT_PAGE_ID, CONTENT_REPO_TOKEN 이름이 등록되어 있습니다. 값은 읽거나 표시하지 않습니다.

- CONTENT_REPO_TOKEN: 비공개 저장소 읽기 인증을 실제 Actions checkout으로 확인. Contents:read 전용을 유지하고 다른 용도로 사용하지 않습니다.
- NOTION_API_KEY: 첫 승인 게시의 Actions users/me 인증과 실제 페이지 생성·본문 쓰기 성공으로 검증했습니다.
- NOTION_PARENT_PAGE_ID: 승인된 CS 기술 면접 공부의 ID·제목과 일치하고 활성 상태임을 Actions에서 확인했습니다.
- Pages: Source=GitHub Actions, master 배포 허용. 실제 deploy-pages 성공과 게시글·정적 리소스 HTTP 200, 브라우저 검색·카테고리 동작 확인.

Secret 값을 코드·채팅·로그·Git에 넣지 않습니다. 확인된 만료·권한 오류가 있을 때 해당 Secret을 수정하며 읽기 토큰의 권한을 확대하지 않습니다. workflow 등록 절차는 WORKFLOW_REGISTRATION.md를 참고하세요.

## 로컬 설치·검증

두 저장소를 같은 부모 디렉터리에 별도로 clone합니다. Python 3.11 이상을 사용합니다.

```powershell
git clone https://github.com/js05157/cs-interview.git
git clone https://github.com/js05157/cs-content-private.git
cd cs-interview
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m unittest discover -s tests -v
.venv/Scripts/python -m scripts.cli validate --private ../cs-content-private --initial
.venv/Scripts/python -m scripts.cli prepare --private ../cs-content-private
```

초기 100개 구성 검사에만 `--initial` 를 사용합니다. 100개를 넘어 확장한 뒤에는 생략하세요.

`prepare`의 기본 모드는 dry-run입니다. 본문·키를 표시하지 않고 후보 ID와 날짜·선택 이유만 반환합니다. 실제 변경을 수행하는 `--mode publish`는 승인 후에만 사용합니다. 일반 운영은 Actions에서 진행합니다.

## 첫 수동 검증

아래 첫 1건 검증은 완료했습니다. 중복 점검을 위해 실제 publish를 다시 실행하지 않습니다.

1. GitHub → Actions → Daily CS publisher → Run workflow를 엽니다.
2. branch는 master, mode는 기본 dry-run을 선택합니다. 읽기 토큰으로 비공개 checkout, 후보 검증, 공개 파일 무변경을 확인합니다. Notion에는 접속하지 않습니다.
3. 사용자가 실제 샘플 1개 공개를 명시적으로 승인한 후에만 mode=publish를 선택합니다.
4. 공개 Markdown·README, Notion 계층·본문, 블로그와 state의 플랫폼 상태를 확인합니다. 샘플은 그날 신규 1개로 계산됩니다.
5. 이 승인은 예약 활성화와 별개입니다. 예약도 승인한 경우에만 아래 설정을 적용합니다.

## 매일 예약 활성화

현재는 활성화하지 않습니다. 이후 추가 문서 게시와 예약 활성화를 별도로 승인받고 첫 ID 제한 정책을 함께 검토한 경우에만 Settings → Secrets and variables → Actions → Variables에 CS_AUTO_PUBLISH=true를 등록합니다. 기본은 미설정/false이며 중지하려면 false로 바꿉니다.

```yaml
schedule:
  - cron: '30 10 * * *'
    timezone: Asia/Seoul
```

시간대 지정은 현재 GitHub Actions의 지원 기능입니다. [GitHub 공식 변경 이력](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/)

실행 지연·누락 가능성이 있어 10:30 정각 시작이나 11시 전 완료를 보장하지 않습니다. master가 보호된 경우 Actions의 push 허용은 저장소 운영 정책에 따라 설정합니다. 강제 push로 우회하지 않습니다. github-pages environment의 배포 브랜치는 master로 제한하는 것을 권장합니다.

## 오류 복구

| 상황 | 재실행 동작 |
| --- | --- |
| Git push 전 실패 | 원격 미예약. 새 checkout에서 같은 후보 처리 |
| GitHub 성공 / Notion 실패 | 같은 ID 복구, 성공한 Markdown 재작성 없음 |
| Notion 성공 / state 저장 실패 | 계층·제목·GitHub 원문 링크로 기존 페이지 재발견 |
| 본문 추가 성공 / 응답 유실 | 동일 chunk fingerprint를 조회해 재사용 |
| Pages 빌드·배포 실패 | 같은 날짜와 permalink로 재배포, Notion 성공 유지 |
| Pages 성공 / state push 실패 | 같은 내용을 재배포하고 상태 기록 |
| 401/403 | 인증·부모 공유·권한·블록 한도를 확인, 무한 재시도 없음 |
| 429/529 | Retry-After를 따르는 제한적 재시도 |
| 다음 원본 없음 | 순서를 건너뛰지 않고 중단, 다음 배치 추가 필요 |
| 전체 대기열 완료 | 신규 게시 중단, 불필요한 Notion·Pages 재처리도 생략 |

원인을 수정하고 master에서 수동 publish를 다시 실행합니다. 미완료를 먼저 복구하므로 새 글로 계산하지 않습니다. 부분 실패의 원인과 본문을 확인하지 않고 state를 삭제하지 마세요.

`notion-*-uncertain-review-required`는 쓰기 결과를 API에서 확인하지 못했다는 뜻입니다. 원본 Notion 페이지·링크와 state를 확인합니다. 페이지가 있으면 공유 범위·이동 위치를 수정해 재발견하도록 합니다. **생성되지 않았음을 사람이 확인한 경우에만** 해당 notion_uncertain 키 또는 topic의 notion_pending_chunk를 제거하고 커밋한 뒤 다시 실행합니다. 다른 키와 완료 상태는 유지합니다.

공개 원문을 사람이 편집하면 자동으로 덮어쓰지 않습니다. 플랫폼 간 차이를 검토한 뒤 원문 hash, Jekyll 재생성, Notion 편집 정책을 명시해 수정해야 합니다. 이 버전에는 공개 본문 강제 동기화 편집 명령이 없습니다.

## 콘텐츠 확장

1. 기존 주제와 중복되지 않는 ID와 한·영 제목을 선택합니다.
2. template으로 본문을 작성하고 공식 링크·코드·선행 관계를 검증합니다.
3. 새 topic JSON을 준비합니다. publish_order는 추가 도구가 마지막 순서로 지정합니다.
4. 공개 프로젝트 폴더에서 아래 명령을 실행합니다. 이 명령의 publish는 **비공개 카탈로그 추가만** 수행하며 세 플랫폼에 글을 게시하지 않습니다.

```powershell
python -m scripts.cli add-topic --private ../cs-content-private --topic-file ../new-topic.json
python -m scripts.cli add-topic --private ../cs-content-private --topic-file ../new-topic.json --mode publish
python -m scripts.cli validate --private ../cs-content-private
```

비공개 manifest와 본문을 함께 커밋·push합니다. 새로운 분야는 config/publisher.json과 blog/_data/categories.yml에 표시 이름을 추가합니다. 게시 엔진 재구축은 필요하지 않습니다. 기존 공개 ID와 날짜는 유지합니다.

## 무료 범위와 서비스 제한

운영 중 AI 생성·API 요금은 없습니다. GitHub Actions·Pages와 Notion의 이용 가능한 범위에서 동작하지만 저장·실행·API 한도는 실제 계정과 현행 조건에 따릅니다. Actions 사용량과 보관 기간, 토큰 만료를 점검합니다.

Notion Free workspace는 멤버 구성에 따라 블록 한도가 다릅니다. 복수 멤버 무료 워크스페이스의 일부 내부 연결에는 생애 1,000블록 한도가 적용되며 삭제로 용량이 복구되지 않습니다. 단일 멤버 무료 워크스페이스는 이 한도 대상이 아닙니다. 100개 글을 수용할 구성을 확인하고 유료 전환을 자동 선택하지 않습니다. [Notion 공식 블록 한도](https://developers.notion.com/reference/workspace-block-limits)

재시도 정책 근거: [Notion 공식 요청 제한](https://developers.notion.com/reference/request-limits)
