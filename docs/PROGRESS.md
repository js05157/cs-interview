# 진행 상태 · 2026-10-27

## 완료·검증

- 기존 공개/비공개 저장소 접근과 양쪽 master 확인.
- VS Code에 열린 별도 manufacturing-alarm-rag 프로젝트는 변경하지 않음.
- 100개 주제의 지정 분야별 개수, 중복, 선행 순서 검증.
- 한국어 학습 문서 22개 작성(기존 OS 10개 + Network 12개). 사용자 학습·검토가 남아 있는 AI 초안.
- 실행 예제 총 20개(Java 14/Python 6), 참고 URL 총 41개 도달 확인.
- GitHub 게시, Notion 변환·계층·재조회, 상태 관리, Jekyll 화면과 Actions 구현.
- 로컬 자동 테스트 34개 통과. 실제 콘텐츠 dry-run에서 공개 파일 무변경.
- 공식 GitHub Pages Action과 같은 Docker 이미지로 실제 Jekyll 빌드 성공. 기본 HTML 5개, 합성 글 포함 HTML 6개를 별도로 검증.
- 정적 리소스·baseurl·검색 JSON·canonical/Open Graph·표·코드 강조·Liquid 문자 보존 검사 통과.
- actionlint 1.7.12로 로컬 워크플로우 2개 정적 검사 통과.
- 실제 콘텐츠 dry-run 2회에서 같은 후보, 공개 파일 해시 동일, 게시 state 0개 확인. 22개 문서의 Notion 오프라인 변환 통과.
- CS_AUTO_PUBLISH 미설정으로 예약 비활성. Secret 3개는 모두 이름 존재 확인(값은 읽지 않음).

## 남은 작업

- **학습 문서 78개 추가 작성**. private 체크포인트의 order 23부터 진행.
- 개발용 Git 인증은 repo scope만 있고 workflow scope가 없어 워크플로우를 업로드할 수 없음. 기존 403 연결 도구와 같은 실패를 반복하지 않음.
- 원격 master에 ci.yml/publish.yml이 아직 없어 실제 GitHub CI와 Actions dry-run은 미실행. 로컬 빌드 결과로 대신 성공 처리하지 않음.
- CONTENT_REPO_TOKEN 등록은 확인됐지만 실제 Secret을 사용한 비공개 checkout은 Actions dry-run 후 확인 필요.
- 실제 Notion API 인증·부모 공유와 운영 쓰기는 미검증.
- 샘플 1개 공개와 Pages 실제 배포는 미실행.
- 실제 게시와 예약 활성화 승인은 받지 않았으며 임의로 실행하지 않음.

## 다음 세션 재개

이 문서, ARCHITECTURE.md, OPERATIONS.md와 private의 README, docs/RESUME_PROMPT.md, manifests/generation_checkpoint.json을 읽습니다. 양쪽 remote와 git status를 확인한 뒤 계속 진행합니다.

우선 `WORKFLOW_REGISTRATION.md`에 따라 두 파일을 GitHub 웹에서 master에 등록하고 CI·dry-run을 확인합니다. 로컬 `.github/workflows`는 미추적 상태이며, 원래 로컬 커밋은 `codex/pre-resume-workflows-20261027`에 보존했습니다. 이력 정렬 과정에서 파일은 삭제하지 않았습니다. 웹 등록 후에는 원격 변경을 먼저 비교·통합하세요.

구체적인 검증 범위와 미확인 항목은 `VALIDATION_2026-10-27.md`에 기록했습니다. 합성 글 빌드 재현용 `python -m scripts.build_fixture --destination <새 임시 폴더>`는 비공개 콘텐츠 없이 테스트 소스만 작성합니다. 이 폴더를 공개 게시글로 복사하지 마세요.

```powershell
python -m unittest discover -s tests -v
python -m scripts.cli validate --private ../cs-content-private --initial
python -m scripts.cli prepare --private ../cs-content-private
```

본문 진행 상태의 기준은 비공개 체크포인트입니다. 100개 본문이 완성되었다고 보고하지 않습니다. 외부 연동을 검증하기 전에는 성공으로 기록하지 않습니다.
