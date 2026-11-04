# Java 웹 기초 실행 예제

[학습 목차](https://js05157.github.io/cs-interview/study/)의 5편을 위해 새로 작성한 예제입니다. 강의 실습 ZIP·원본 PDF 없이 독립 실행합니다. 외부 Tomcat 배포용 WAR가 아니라 테스트 안에서 시작하고 종료하는 내장 Tomcat 프로젝트입니다.

Java 17 이상과 Maven이 필요합니다.

```shell
cd examples/web-learning
mvn test
```

고정 검증 조합은 JDK17, Tomcat11.0.27(Servlet6.1/JSP4.0/EL6), JSTL API3.0.2/구현3.0.1, JUnit5.12.2입니다. 의존성은 최초 실행 때 Maven이 다운로드합니다. 테스트는 127.0.0.1의 임의 포트만 열고 종료 시 서버를 닫습니다.

`WebLearningTest`의 8개 테스트:

- 더하기 GET의 결과 5, 잘못된 값·범위 초과 400, 미지원 POST 405.
- 요청 필터의 응답 헤더.
- JSP 실제 컴파일·JSTL 목록·request 속성과 HTML escaping.
- EL scope 검색, 숫자 변환, c:remove scope 생략 시 전체 영역 제거.
- WEB-INF 직접 요청 차단과 사용자 정의 404 상태 유지.
- 쿠키는 현재 요청에 없고 다음 요청에 오며 동일 Path로 삭제 가능.
- 로그인 303·세션 프로필·로그아웃 후 401.
- 잘못된 비밀번호로 로그인되지 않음.

Servlet·필터는 테스트가 직접 등록해 실행 대상을 고정합니다. 동일 클래스를 별도 WAR에 배포할 때 애너테이션과 프로그램 등록을 중복하지 않습니다. `target/`은 Git에 저장하지 않습니다.

`learner/demo-only`는 로컬 학습용 고정 입력입니다. 운영 비밀번호 저장·해싱·CSRF·HTTPS·브라우저 SameSite 정책·분산 세션·부하 시험은 구현하거나 검증하지 않았습니다. Controller/Listener 구조, 장바구니, 500 페이지 등 본문의 일부 설명 코드는 원리 설명이며 이 8개 테스트의 실행 범위와 구분합니다. 정리본의 코드에는 해당 차이를 표시했습니다.
