# 진행 상태 · 2026-10-27

## 완료·검증

- 기존 공개/비공개 저장소 접근과 양쪽 master 확인.
- VS Code에 열린 별도 manufacturing-alarm-rag 프로젝트는 변경하지 않음.
- 100개 주제의 지정 분야별 개수, 중복, 선행 순서 검증.
- 한국어 학습 문서 10개 작성. 사용자 학습·검토가 남아 있는 AI 초안.
- 실행 예제 9개(Java 5/Python 4), 참고 URL 21개 도달 확인.
- GitHub 게시, Notion 변환·계층·재조회, 상태 관리, Jekyll 화면과 Actions 구현.
- 로컬 자동 테스트 34개 통과. 실제 콘텐츠 dry-run에서 공개 파일 무변경.
- CS_AUTO_PUBLISH 미설정으로 예약 비활성. Notion Secret 2개는 이름만 확인.

## 남은 작업

- **학습 문서 90개 추가 작성**. private 체크포인트의 order 11부터 진행.
- CONTENT_REPO_TOKEN은 최초 조회에서 누락. 사용자가 기존 read-only 토큰을 등록할 예정.
- GitHub CI의 실제 Jekyll 빌드·HTML 검사 결과 확인 대기.
- 실제 Notion API 인증·부모 공유와 운영 쓰기는 미검증.
- 샘플 1개 공개와 Pages 실제 배포는 미실행.
- 실제 게시와 예약 활성화 승인은 받지 않았으며 임의로 실행하지 않음.

## 다음 세션 재개

이 문서, ARCHITECTURE.md, OPERATIONS.md와 private의 README, docs/RESUME_PROMPT.md, manifests/generation_checkpoint.json을 읽습니다. 양쪽 remote와 git status를 확인한 뒤 계속 진행합니다.

```powershell
python -m unittest discover -s tests -v
python -m scripts.cli validate --private ../cs-content-private --initial
python -m scripts.cli prepare --private ../cs-content-private
```

본문 진행 상태의 기준은 비공개 체크포인트입니다. 100개 본문이 완성되었다고 보고하지 않습니다. 외부 연동을 검증하기 전에는 성공으로 기록하지 않습니다.
