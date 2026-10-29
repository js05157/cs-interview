# 다섯 절 CS 학습 문서·게시 연동 완료 · 2026-10-29

1. **문서 100/100개 개편 완료.** 정의·설명·적용 예시·정리·꼬리 질문을 사용하며 질문 201개에 각각 답변이 있습니다. 누락·중복 주제와 누락 답변은 0개입니다. 정의 2~3문장, 정리 3~5문장, 질문 2~4개·각 답변 2~4문장 검사를 통과했습니다. 기존 문서를 주제별로 재구성했으며 3~5분은 편집 목표이지 측정된 읽기 시간이 아닙니다.

2. **분야별 수:** OS 10, Network 12, Database 12, Data Structure 8, Algorithm 8, Java 14, Spring/JPA 14, Architecture 10, DevOps 6, Data Engineering 6입니다. 원본 ID·경로·제목·순서·카탈로그·대기열을 보존했습니다. 99개 기존 코드와 전체 참고 자료를 유지했고 첫 코드만 승인된 SharedCounter로 변경했습니다. 이전 코드·본문은 보존 태그와 이미 공개된 첫 글 백업에 있습니다.

3. **클릭 UI:** 안전한 Markdown의 H3 질문·답변을 공유 파서로 검증하고 렌더 버전 3에서만 details/summary로 생성합니다. 원본의 임의 HTML은 계속 거부합니다. 기본 닫힘, 질문별 독립 동작, 다시 클릭해 접기, 네이티브 키보드 접근성, 모바일·다크 CSS를 지원합니다. 답변의 코드·인라인 코드·링크는 변환 테스트로 검증했습니다.

4. **실제 블로그 UI:** 첫 글에서 기본 닫힘 → 두 질문 동시 열림 → 한 질문만 접힘, Enter·Space 동작을 확인했습니다. 390px 다크 화면의 가로 넘침 없음, 그림·코드 표시, 검색과 CS 글 필터를 확인했습니다. 브라우저 오류는 관찰되지 않았습니다. [실제 질문 화면](screenshots/first-questions-mobile.png)을 참고하세요.

5. **Notion:** 같은 파서가 관리 절 안의 질문별 Toggle을 만듭니다. 100편 오프라인 대조에서 201개 답변 블록의 순서·내용이 일치합니다. 실제 첫 페이지에는 관리 절 5개와 질문 Toggle 3개가 있고 본문·코드·그림·답변을 확인했습니다. 코드·링크가 포함된 답변은 로컬 변환 테스트, 동일 페이지 반복 개정과 응답 유실은 mock 복구 테스트로 확인했습니다. 실제 Notion에 검증용 추가 글을 만들지 않았습니다.

6. **첫 글 동기화:** 승인된 [개정 실행](https://github.com/js05157/cs-interview/actions/runs/40866762296)이 성공했습니다. GitHub·Notion·Pages 상태 모두 complete, 본문 hash는 `f0787b1fc712dbd586bad874784def093f6f2e9e8452babb88ed88b558066a7a`, render_version=3입니다. 이전 관리 chunk 7개만 archive하고 이전 revision metadata를 revision_history에 보존했습니다. [첫 개정 결과](FIRST_RESULT.json), [최종 읽기 전용 감사](FINAL_VERIFICATION.json)에 근거가 있습니다.

7. **SVG 26개:** 제목·설명·방향·용어·기술 경계와 XML 안전성을 재검토했습니다. 25개는 유지하고 첫 그림만 승인 샘플로 교체했습니다. 26개 모두 비공개 갤러리의 390px 다크 환경에서 본문 넘침 없이 확대된 가로 탐색이 가능함을 확인했습니다. 직접 작성한 그림이며 복사한 외부 그림·폰트·스크립트의 라이선스 의존성을 추가하지 않았습니다. 첫 그림만 공개하고 25개는 비공개에 유지했습니다.

8. **실행 검사:** Java 63개, Python 6개, Spring JUnit 14개, PostgreSQL 17.11 SQL 22개 통과. 문서·Spring 실행 소스 14/14 일치, 오류·실패·건너뜀 0. YAML 3개는 정적 검사, Docker 예제 1개는 실제 빌드·비루트·읽기 전용 실행 성공입니다. H2·MockMvc·인메모리 모델을 운영 DB 잠금·실제 로그인·분산 보장으로 일반화하지 않습니다. 공개 엔진 테스트 74개도 통과했습니다.

9. **Jekyll·CI·dry-run:** 공식 이미지로 100편을 네트워크 없는 비공개 로컬 빌드에만 넣어 HTML 109개, 질문·답변 201개, 대응 그림 26개, 강조 코드 블록 109개와 `/cs-interview/` 경로를 확인했습니다. 이 빌드는 배포하지 않았습니다. [CI 40868829633](https://github.com/js05157/cs-interview/actions/runs/40868829633)은 공개 첫 글의 실제 Jekyll 빌드를 통과했습니다. [전체 dry-run 40877986698](https://github.com/js05157/cs-interview/actions/runs/40877986698)은 private `434a8e2`의 100편 읽기·74개 테스트·validate·prepare·공개 파일 무변경에 성공했고 publish/build/deploy/record는 skipped입니다. 문서 저장 후의 최신 실행은 Actions 기록과 비공개 FIVE_INTEGRATION_RESULT.json에도 남깁니다.

10. **저장:** 엔진 코드 검증 커밋 `4a7d6d8`, 전체 비공개 콘텐츠 커밋 `434a8e2`. 이후 검증 보고·템플릿·체크포인트도 각 저장소에 커밋·푸시합니다. 최종 저장 커밋은 완료 응답의 링크를 기준으로 확인할 수 있습니다. 양쪽 `pre-five-section-20261029` 태그는 개편 전 보존 지점입니다. 미게시 본문·카탈로그·도식은 공개 Git이나 Actions 산출물에 넣지 않았습니다.

11. **식별자 보존:** `os-process-thread`, 최초 날짜 `2026-10-27`, 원문 `Operating-System/Process/os-process-thread.md`, post `blog/_posts/2026-10-27-os-process-thread.md`, permalink `/topics/os-process-thread/`, Notion ID `40647f4c-2c25-81b4-b2a3-dd1cdeb62644` 유지. `CS 기술 면접 공부 → 운영체제 → Process` 계층과 세 플랫폼 이력을 보존했습니다. 재조회에서 Notion 수정 시각·본문이 바뀌지 않았습니다.

12. **자동 게시 상태:** `CS_AUTO_PUBLISH`는 UNSET, 승인 목록은 첫 ID 하나입니다. 같은 게시 날짜는 daily-limit이며 다음 날의 새 후보도 승인 정책으로 차단됩니다. 불완전 상태 복구가 새 주제 선정에 우선하고 실제 추가 공개는 0건입니다. 활성화하려면 별도 사용자 승인 후 승인 목록·자격 증명 만료·Notion 공간 권한과 계정 한도·복구 상태·첫 예약 실행의 관측을 확인해야 합니다. 현재 완료가 신규 게시·예약 활성화 승인은 아닙니다.

실제 글: [GitHub](https://github.com/js05157/cs-interview/blob/master/Operating-System/Process/os-process-thread.md) · [블로그](https://js05157.github.io/cs-interview/topics/os-process-thread/) · [동일 Notion 페이지](https://www.notion.so/40647f4c2c2581b4b2a3dd1cdeb62644).
