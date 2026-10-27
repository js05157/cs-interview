# 워크플로우 웹 등록

2026-10-27 등록 완료: 두 파일이 master에 존재하고 검토본과 일치합니다. CI와 dry-run도 성공했습니다. 아래는 이후 워크플로우를 변경할 때의 참고 절차이며 지금 다시 등록할 필요는 없습니다.

현재 개발용 Git 인증에 workflow scope가 없어 자동 업로드가 불가능합니다. CONTENT_REPO_TOKEN은 비공개 저장소 읽기 전용으로 유지합니다. 권한을 확대하거나 업로드 토큰으로 재사용하지 않습니다.

기존 로컬 파일:

```text
C:\Users\js051\Documents\Codex\2026-10-27\files-pasted-by-the-user-cs\work\cs-interview\.github\workflows\ci.yml
C:\Users\js051\Documents\Codex\2026-10-27\files-pasted-by-the-user-cs\work\cs-interview\.github\workflows\publish.yml
```

1. [공개 저장소](https://github.com/js05157/cs-interview)의 Code 화면에서 브랜치 master를 선택합니다.
2. Add file → Create new file을 선택합니다.
3. 파일명에 `.github/workflows/ci.yml`을 입력하고 해당 로컬 파일 전체 내용을 붙여넣습니다. 코드 펜스는 추가하지 않습니다.
4. Commit changes에서 `ci: add publisher tests and Jekyll build`로 master에 저장합니다. 보호 브랜치면 새 브랜치/PR로 저장하고 병합합니다. 보호 규칙을 해제하지 않습니다.
5. 같은 방법으로 `.github/workflows/publish.yml`을 만들고 `ci: add guarded daily CS publisher`로 저장합니다.
6. Actions의 Validate publisher and Jekyll에서 테스트·빌드를 확인합니다. 이 CI는 배포하지 않습니다.
7. Daily CS publisher → Run workflow에서 branch=master, mode=dry-run을 실행합니다. publish 모드는 선택하지 않습니다.
8. gate와 dry-run만 수행되고 publish/build/deploy/record가 건너뛰어지는지 확인합니다.

CS_AUTO_PUBLISH는 미설정/false로 유지합니다. 워크플로우 등록과 dry-run은 실제 학습 문서 공개나 예약 활성화 승인이 아닙니다.

원래 로컬 커밋은 `codex/pre-resume-workflows-20261027` 브랜치에 보존했습니다. 등록된 원격 파일과 로컬 검토본의 일치를 확인한 뒤 master를 fast-forward로 통합했으며 현재 두 워크플로우는 정상 추적 중입니다. 이후 변경에도 fetch와 diff로 원격을 먼저 확인하세요.
