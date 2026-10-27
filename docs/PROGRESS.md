# 진행 상태 · 2026-10-27

## 완료·검증

- 기존 공개/비공개 저장소 접근과 양쪽 master 확인.
- VS Code에 열린 별도 manufacturing-alarm-rag 프로젝트는 변경하지 않음.
- 100개 주제의 지정 분야별 개수, 중복, 선행 순서 검증.
- 한국어 학습 문서 34개 작성(OS 10개 + Network 12개 + Database 12개). 사용자 학습·검토가 남아 있는 AI 초안.
- Java 14개/Python 6개 실행 예제와 PostgreSQL 17.11의 SQL 22개 블록 검증. 참고 URL 총 59개 도달 확인.
- GitHub 게시, Notion 변환·계층·재조회, 상태 관리, Jekyll 화면과 Actions 구현.
- 로컬 자동 테스트 34개 통과. 실제 콘텐츠 dry-run에서 공개 파일 무변경.
- 공식 GitHub Pages Action과 같은 Docker 이미지로 실제 Jekyll 빌드 성공. 기본 HTML 5개, 합성 글 포함 HTML 6개를 별도로 검증.
- 정적 리소스·baseurl·검색 JSON·canonical/Open Graph·표·코드 강조·Liquid 문자 보존 검사 통과.
- actionlint 1.7.12로 로컬 워크플로우 2개 정적 검사 통과.
- 실제 콘텐츠 dry-run 반복에서 같은 후보, 공개 파일 해시 동일, 게시 state 0개 확인. 34개 문서의 Notion 오프라인 변환 통과.
- CS_AUTO_PUBLISH 미설정으로 예약 비활성. Secret 3개는 모두 이름 존재 확인(값은 읽지 않음).
- 두 워크플로우가 master에 등록되었고 검토한 로컬 파일과 일치함을 확인. 로컬 master도 파일 손실 없이 fast-forward로 통합 완료.
- 실제 GitHub CI 성공: [run 40510804709](https://github.com/js05157/cs-interview/actions/runs/40510804709). 테스트 34개, Jekyll 빌드와 출력 검사 성공.
- 실제 Actions dry-run 성공: [run 40510890295](https://github.com/js05157/cs-interview/actions/runs/40510890295). 비공개 Secret checkout, 34개 테스트, 당시 22개 문서 검사, 후보 선택과 공개 파일 무변경 확인. publish/build/deploy/record는 모두 skipped.

## 남은 작업

- **학습 문서 66개 추가 작성**. private 체크포인트의 order 35부터 진행.
- 새 데이터베이스 배치까지 포함한 [Actions dry-run 40513929584](https://github.com/js05157/cs-interview/actions/runs/40513929584)도 성공. 34개 문서 검증과 공개 파일 무변경 확인. mode는 dry-run이며 실제 게시를 승인한 것이 아님.
- 개발용 Git 인증에는 workflow scope가 없으므로 앞으로 워크플로우를 변경할 때도 GitHub 웹 등록 방식을 사용. CONTENT_REPO_TOKEN 권한은 변경하지 않음.
- 실제 Notion API 인증·부모 공유와 운영 쓰기는 미검증.
- 샘플 1개 공개와 Pages 실제 배포는 미실행.
- 실제 게시와 예약 활성화 승인은 받지 않았으며 임의로 실행하지 않음.

## 첫 1건 게시 전 점검

- 실제 첫 원문을 격리된 로컬 샌드박스에 준비하고 Notion·배포는 mock으로 검사. 같은 날 신규 차단, 다음 날 다음 ID 선택, 미완료 우선 복구, Notion 성공 응답 유실의 기존 페이지 재사용을 확인.
- 실제 공개·비공개 파일 무변경을 검사했으며 GITHUB_TOKEN의 운영 push, Actions Notion 키의 인증·쓰기와 실제 Pages 배포는 여전히 미검증.
- github-pages environment의 master 허용과 Pages Source=workflow를 읽기 전용으로 재확인. CS_AUTO_PUBLISH는 미설정으로 유지.
- 상세 첫 게시 계획과 미확인 사항은 비공개 docs/FIRST_PUBLISH_PREFLIGHT.md와 JSON에 저장. 실제 게시 승인은 아직 없음.
- 비공개 manifests/remaining_generation_plan.json에 35~100번 66개의 5개 배치(16/14/14/10/12개)를 준비. 본문 수는 34개로 유지하며 게시 대기열을 35번으로 옮기지 않음.

## 다음 세션 재개

이 문서, ARCHITECTURE.md, OPERATIONS.md와 private의 README, docs/RESUME_PROMPT.md, manifests/generation_checkpoint.json을 읽습니다. 양쪽 remote와 git status를 확인한 뒤 계속 진행합니다.

워크플로우 등록과 기본 CI·dry-run은 검증 완료입니다. 최신 run 결과를 확인하고 private의 체크포인트부터 콘텐츠를 이어서 작성합니다. 원래 로컬 커밋은 `codex/pre-resume-workflows-20261027`에 보존했으며, 현재 master의 워크플로우는 원격과 일치하는 추적 파일입니다. `WORKFLOW_REGISTRATION.md`는 이후 변경 시 참고 절차입니다.

구체적인 검증 범위와 미확인 항목은 `VALIDATION_2026-10-27.md`에 기록했습니다. 합성 글 빌드 재현용 `python -m scripts.build_fixture --destination <새 임시 폴더>`는 비공개 콘텐츠 없이 테스트 소스만 작성합니다. 이 폴더를 공개 게시글로 복사하지 마세요.

```powershell
python -m unittest discover -s tests -v
python -m scripts.cli validate --private ../cs-content-private --initial
python -m scripts.cli prepare --private ../cs-content-private
```

본문 진행 상태의 기준은 비공개 체크포인트입니다. 100개 본문이 완성되었다고 보고하지 않습니다. 외부 연동을 검증하기 전에는 성공으로 기록하지 않습니다.
