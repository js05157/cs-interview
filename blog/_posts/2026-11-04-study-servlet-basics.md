---
title: 'Servlet 기초: 웹 요청에서 Java 응답까지'
date: 2026-11-04 00:00:00 +0900
content_type: ssafy
series: Java 웹 기초
series_order: 1
series_total: 5
notion_url: https://www.notion.so/40e47f4c2c258169a387d49b1402bcaf
tags: [Java, Servlet, Maven, HTTP]
permalink: /study/servlet-basics/
description: 컨테이너·Context·URL 매핑·Maven·Servlet 생명주기와 요청·응답을 하나의 흐름으로 이해합니다.
---

브라우저가 `/learn/add?a=2&b=3`을 요청하면 누가 Java 코드를 실행할까요? 이 글은 **요청 주소를 해석하고, 컨테이너가 Servlet을 호출하고, 결과를 HTTP 응답으로 보내는 과정**을 따라갑니다.

## 1. 웹 프로그램의 역할부터 나누기

프런트엔드는 화면과 사용자 상호작용을 담당하고 백엔드는 요청의 의미를 해석해 업무 처리를 수행합니다. DB는 저장을 담당합니다. 웹 서버는 정적 파일 제공과 프록시 역할을, WAS는 애플리케이션 실행을 담당하는 식으로 역할을 나눌 수 있습니다.

| 구분 | 핵심 역할 | 예 |
| --- | --- | --- |
| 화면·표현 | 사용자의 입력과 결과 표시 | HTML, CSS, JavaScript |
| 애플리케이션 | 입력 검증과 업무 규칙 | Servlet, Service |
| 데이터 | 영속 저장과 조회 | DAO, DB |

세 계층은 **역할 구분**입니다. 반드시 서로 다른 물리 서버 세 대가 필요하지는 않습니다. 작은 실습에서는 Tomcat이 정적 파일과 Java 요청을 함께 처리합니다. 또 Tomcat은 Servlet/JSP 컨테이너이며 Jakarta EE의 모든 기능을 제공하는 서버와 동일하지는 않습니다.

## 2. Tomcat·Container·Context의 관계

컨테이너는 Servlet의 생성·초기화·호출·종료를 관리하는 실행 환경입니다. 하나의 Tomcat에는 여러 웹 애플리케이션을 올릴 수 있고, 각 애플리케이션에는 별도의 `ServletContext`가 있습니다.

```text
GET http://localhost:8080/learn/add?a=2&b=3
             └ 서버·포트 ┘└Context┘└매핑┘└파라미터┘

Tomcat → /learn 애플리케이션 → /add 매핑 → AddServlet.doGet()
                                               ↓
브라우저 ← HTTP 상태·헤더·본문 ← HttpServletResponse
```

`/learn`은 배포된 애플리케이션의 Context 경로이고 `/add`는 그 안의 Servlet 매핑입니다. 소스 패키지 이름은 URL과 직접적인 관계가 없습니다. 개발 포트 8080도 관례이며 고정 규칙은 아닙니다.

## 3. 개발 환경과 프로젝트 구조

수업 자료는 Tomcat 11 계열을 사용합니다. Tomcat 11은 Java 17 이상, Servlet 6.1, JSP 4.0, EL 6.0 조합입니다. 오래된 `javax.servlet.*` 예제와 현재의 `jakarta.servlet.*` 예제를 무작정 섞으면 컴파일·실행 오류가 생깁니다. [Tomcat 공식 호환표](https://tomcat.apache.org/whichversion.html)

```text
src/main/java/          Java 클래스
src/main/resources/     클래스패스 리소스
src/main/webapp/        HTML·CSS·JavaScript·JSP
  WEB-INF/web.xml      배포 설정
  WEB-INF/views/       직접 URL 접근을 막을 JSP
src/test/java/          테스트
pom.xml                의존성·컴파일 설정
target/                빌드 산출물
```

IDE에서는 웹 개발 플러그인, Tomcat 런타임, 프로젝트의 JDK와 웹 모듈 버전, 실제 배포 Context를 순서대로 확인합니다. 브라우저에 404가 보이면 코드부터 고치기 전에 **서버 기동 → 애플리케이션 배포 → Context → 매핑**을 점검합니다. 경고를 없애려고 외부 XML 다운로드를 무조건 허용하기보다 필요한 스키마와 접근 대상을 확인합니다.

### Maven이 해결하는 문제

Maven은 라이브러리 버전과 빌드 방법을 `pom.xml`로 공유합니다. `groupId:artifactId:version`이 의존성의 좌표입니다. 일반적인 외부 Tomcat 배포 프로젝트는 `war`로 패키징하며, 서버가 제공하는 Servlet API는 보통 `provided` 범위를 사용합니다.

```xml
<dependency>
  <groupId>jakarta.servlet</groupId>
  <artifactId>jakarta.servlet-api</artifactId>
  <version>6.1.0</version>
  <scope>provided</scope>
</dependency>
```

`provided`는 컴파일할 때는 필요하지만 WAR에 서버 API 구현을 중복해서 넣지 않겠다는 뜻입니다. 이 시리즈의 실행 검증 프로젝트는 재현을 쉽게 하려고 **내장 Tomcat 테스트**를 사용하므로 별도의 Tomcat 구현 의존성이 있습니다. 외부 서버 배포용 POM과 혼동하지 않습니다.

## 4. URL 매핑과 경로의 기준

Servlet은 `HttpServlet`을 상속하고 `doGet`, `doPost` 등을 재정의합니다. 등록은 `@WebServlet` 또는 `web.xml`로 할 수 있습니다. 같은 URL을 서로 다른 Servlet에 중복 등록하면 배포 오류가 날 수 있습니다.

| 사용 위치 | `/`가 가리키는 기준 | `/learn`에 배포한 예 |
| --- | --- | --- |
| 브라우저의 링크·폼 | origin 루트 | `/learn/add` |
| `@WebServlet` 매핑 | 해당 웹 애플리케이션 | `/add` |
| `request.getRequestDispatcher` | `/`로 시작하면 Context 루트 | `/WEB-INF/views/result.jsp` |
| `sendRedirect`에 전달한 `/path` | 브라우저가 해석하는 origin 루트 | Context를 붙여 `/learn/path` |

브라우저 기준 경로는 보통 `request.getContextPath()`를 이용해 조합합니다. 앞에 `/`가 없는 상대 경로는 현재 URL에 따라 달라집니다. **“Servlet에서 쓰는 모든 `/`는 Context 기준”으로 외우면 redirect에서 틀리기 쉽습니다.**

## 5. Servlet 생명주기와 동시 요청

1. 컨테이너가 등록 정보와 URL을 확인합니다.
2. 아직 준비되지 않았다면 객체를 만들고 `init()`을 호출합니다. `loadOnStartup` 설정으로 기동 시 준비할 수도 있습니다.
3. 요청마다 `service()`가 HTTP 메서드를 확인하고 `doGet()`·`doPost()` 등으로 연결합니다.
4. 애플리케이션 종료·재배포 때 `destroy()`로 자원을 정리합니다.

초기화가 끝나기 전에 해당 인스턴스가 요청을 처리하지 않습니다. 종료 과정의 요청 대기에는 컨테이너의 시간 제한도 있으므로 “요청이 남아 있으면 무조건 영원히 종료하지 않는다”는 뜻은 아닙니다.

일반적으로 등록된 Servlet 인스턴스 하나가 여러 요청을 처리합니다. 요청마다 사용자 값을 인스턴스 필드에 저장하면 서로 덮어쓸 수 있습니다. 입력값과 계산 중간값은 지역 변수·request 속성에 두고, 공유 데이터의 동시성은 별도로 설계합니다.

## 6. 요청에서 읽고 응답에 쓰기

| 요청 API | 무엇을 읽는가 |
| --- | --- |
| `getMethod()` | GET·POST 등 요청 메서드 |
| `getParameter(name)` | 파라미터 하나의 문자열 값 |
| `getParameterValues(name)` | 체크박스 등 같은 이름의 여러 값 |
| `getHeader(name)` | 요청 헤더 |
| `setAttribute`·`getAttribute` | 서버가 처리 중 저장한 객체 |

폼·쿼리 파라미터는 문자열입니다. 숫자는 변환·범위 검증이 필요하고 값이 없으면 `null`일 수 있습니다. JSON 본문이 자동으로 `getParameter()`에 들어오는 것은 아닙니다. 파라미터 전체를 로그에 남기면 비밀번호 등이 유출될 수 있습니다.

응답은 상태 코드, 헤더, 본문으로 구성됩니다. `setContentType()`은 형식을, `charset`은 문자 해석 방법을 전달합니다. **`getWriter()`를 얻기 전에** 문자 인코딩을 설정합니다. 폼 POST의 요청 인코딩 역시 파라미터를 읽기 전에 설정합니다.

### 직접 실행하는 더하기 예제

```java
@WebServlet("/add")
public class AddServlet extends HttpServlet {
    @Override protected void doGet(HttpServletRequest req,
                                   HttpServletResponse resp) throws IOException {
        resp.setContentType("text/plain;charset=UTF-8");
        try {
            int a = Integer.parseInt(req.getParameter("a"));
            int b = Integer.parseInt(req.getParameter("b"));
            resp.getWriter().print(Math.addExact(a, b));
        } catch (NumberFormatException | ArithmeticException e) {
            resp.sendError(400, "두 정수를 확인하세요.");
        }
    }
}
```

`GET /learn/add?a=2&b=3`은 `200`과 본문 `5`를 반환합니다. `a=no`, 필수값 누락, 정수 범위 초과는 `400`으로 처리합니다. 이 Servlet은 `doPost()`를 구현하지 않았으므로 POST는 `405`입니다. 전체 import와 실행 방법은 [검증 프로젝트](https://github.com/js05157/cs-interview/tree/master/examples/web-learning)에 있습니다.

GET은 조회, POST는 제출에 주로 사용하지만 **POST라고 데이터가 암호화되지는 않습니다.** 인증 정보는 HTTPS로 보호해야 합니다. 멱등성은 같은 요청을 반복했을 때 의도한 서버 상태 변화가 같다는 뜻이며, 응답 문자열까지 항상 같다는 뜻은 아닙니다.

| 상태 | 이 단계에서의 의미 |
| --- | --- |
| 200·201 | 처리 성공·리소스 생성 |
| 302·303 | 다른 주소로 이동하도록 응답 |
| 400·401·403 | 잘못된 요청·인증 필요/실패·권한 부족 |
| 404·405 | 대상 없음·허용하지 않는 메서드 |
| 500 | 서버 내부 오류 |

## 정리와 복습

Servlet은 컨테이너가 HTTP 요청을 Java 호출로 연결하는 진입점입니다. URL의 Context와 매핑을 구분하고 입력을 검증한 뒤 상태·형식·본문을 응답합니다. 객체 생명주기는 컨테이너가 관리하지만 공유 필드의 동시성까지 자동으로 해결해 주지는 않습니다.

- `/learn/add`의 `/learn`을 Servlet 매핑에도 써 버리면 어떤 주소가 될까요? **Context와 매핑을 중복하게 됩니다.** 실제 배포 경로와 등록 정보를 따로 확인해야 합니다.
- 같은 이름의 체크박스가 여러 개면 왜 `getParameterValues()`가 필요할까요? **하나의 문자열로는 전체 선택값을 얻을 수 없기 때문입니다.**
- `getWriter()` 뒤에 UTF-8을 지정하면 왜 늦을 수 있을까요? **이미 Writer의 인코딩이 결정되었을 수 있기 때문입니다.**

## 자료와 다음 학습

제공된 `01_servlet` PDF 45쪽 중 환경·구조(4–18쪽), Maven(20–25쪽), Servlet·HTTP·실습(27–43쪽)을 학습 흐름으로 재구성했습니다. 표지·구분·다음 수업 안내는 개념 본문에서 제외했습니다. 예제는 정리본을 위해 새로 작성했습니다.

- [Jakarta Servlet 6.1](https://jakarta.ee/specifications/servlet/6.1/)
- [Tomcat 버전과 Java·API 호환표](https://tomcat.apache.org/whichversion.html)
- 다음: [Front Controller·Filter·Listener](/cs-interview/study/servlet-components/)
