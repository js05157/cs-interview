# 작업 재개

먼저 docs/PROGRESS.md, docs/ARCHITECTURE.md, docs/OPERATIONS.md를 읽으세요.

- 기본 브랜치는 master입니다. 기존 수동 작성 파일을 보호하세요.
- 별도 비공개 저장소 js05157/cs-content-private의 체크포인트를 읽고 콘텐츠 작업을 이어 가세요.
- 공개 저장소에 pending/, 비공개 manifest, 미게시 학습 본문을 복사하지 마세요.
- OpenAI/LLM API, OPENAI_API_KEY를 사용하지 않습니다.
- 사용자의 명시적인 승인 전에는 실제 publish 실행, Notion 쓰기, Pages 배포, CS_AUTO_PUBLISH=true 설정을 하지 마세요.
- 구현 코드 저장과 읽기 전용 검증, 비공개 콘텐츠 작성은 진행할 수 있습니다.
- 테스트: python -m unittest discover -s tests -v
- 콘텐츠 검증: python -m scripts.cli validate --private ../cs-content-private
- 안전한 미리보기: python -m scripts.cli prepare --private ../cs-content-private
- 실제 확인하지 않은 서비스 연동과 콘텐츠 품질 검토를 완료라고 기록하지 마세요.
