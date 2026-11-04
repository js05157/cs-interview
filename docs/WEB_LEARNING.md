# Java 웹 기초 학습 정리 · 2026-11-04

사용자가 최종 지정한 Servlet 2개·JSP·EL/JSTL·세션/쿠키 PDF 5개(184쪽)를 바탕으로 독립적인 학습 노트 5편을 작성했습니다. 프로젝트·DB PDF는 제외했습니다. 원본 PDF·OCR·강의 이미지를 공개 저장소에 넣지 않고 설명과 예제를 새로 작성했습니다.

- [학습 목차](https://js05157.github.io/cs-interview/study/)
- [Notion 학습](https://www.notion.so/40e47f4c2c25814b8ba6c26db9498bd5)
- [실행 예제](../examples/web-learning/README.md)

정리 순서는 Servlet 기초 → Front Controller/Filter/Listener → JSP/MVC → EL/JSTL → 쿠키/세션입니다. 개발 환경·요청 흐름·비교표·짧은 코드·주의사항·복습 질문과 원본 페이지 범위를 각 글에 담았습니다. 쿠키 기본 Path, 브라우저 종료와 서버 세션, c:remove scope 생략, XSS/CSRF의 보장 범위처럼 단순화하면 틀리는 부분은 공식 API·명세와 대조해 보완했습니다.

표시 메뉴와 Notion 허브는 ‘학습’입니다. 웹의 `/study/`가 학습 목차이며 과거 `/ssafy/`는 여기로 이동합니다. 내부 `content_type: ssafy`는 기존 글·관리 도구와의 호환을 위해 유지하지만 사용자 화면에는 ‘학습’으로 표시합니다. 기존 `/learning/`의 CS 분류 이동은 유지합니다.

로컬 Maven 내장 Tomcat11.0.27의 8개 테스트로 실제 HTTP·JSP/JSTL·쿠키·로그인과 404를 확인했습니다. 모든 본문 코드가 독립 실행 프로그램이라는 뜻은 아니며 의사코드·설정 조각·보안 범위는 본문과 예제 README에 표시했습니다. 기존 Python85개 테스트, 공식 Jekyll의 HTML33개/게시글12개(CS7+학습5), 검색·분야·학습 목차·baseurl 검사를 통과했습니다. 390px 다크 화면에서 5편의 본문 넘침 없이 코드27블록·표17개가 표시되는 것을 확인했습니다.

Notion은 ‘학습’ 허브 아래 5개의 하위 페이지에 저장하고 각 절·코드27블록의 내용을 대조했습니다. 웹에서 Notion으로, Notion에서 웹으로 이어 읽을 수 있습니다. CS 원문100개·원래 큐·분야 회전·하루 신규 CS1편·게시 기록7편과 자동 활성 설정은 변경하지 않습니다. 배포는 topic_id 없는 site-update로만 진행합니다.
