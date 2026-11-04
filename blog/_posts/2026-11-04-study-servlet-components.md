---
title: 'Front Controller·Filter·Listener: 요청 처리 공통화'
date: 2026-11-04 00:00:00 +0900
content_type: ssafy
series: Java 웹 기초
series_order: 2
series_total: 5
notion_url: https://www.notion.so/40e47f4c2c2581129665d7be02d770af
tags: [Java, Servlet, Filter, Listener]
permalink: /study/servlet-components/
description: Front Controller의 분기, 필터 체인, 리스너 이벤트, Servlet 공유 상태를 구분합니다.
---

요청마다 Servlet을 하나씩 만들면 같은 로깅·인코딩·오류 처리 코드가 반복됩니다. **Front Controller는 요청의 진입점을 모으고, Filter는 공통 처리를 연결하며, Listener는 생명주기 이벤트에 반응합니다.** 세 가지는 적용하는 시점이 다릅니다.

## 1. Front Controller가 요청을 구분하는 방법

Front Controller는 여러 요청을 먼저 받아 적절한 업무 처리로 분배하는 Servlet입니다. 모든 업무를 거대한 메서드 하나로 작성하라는 뜻은 아닙니다. 입력 확인과 전달을 진입점에서 맡고 업무 규칙은 Service 등에 나눕니다.

| 구분 방식 | 예 | 확인할 값 |
| --- | --- | --- |
| 작업 파라미터 | `/main?action=list` | `getParameter("action")` |
| 경로 매핑 | `/member/*` → `/member/list` | `getPathInfo()`의 `/list` |
| 확장자 매핑 | `*.do` → `/list.do` | `getServletPath()` |

폼의 `action` 속성은 전송할 URL입니다. 서버에서 읽을 `action` 파라미터와 다릅니다. 파라미터 방식에서는 다음처럼 hidden 입력을 넣을 수 있습니다.

```html
<form action="/learn/main" method="post">
  <input type="hidden" name="action" value="join">
  <input name="name">
  <button type="submit">등록</button>
</form>
```

`/main/*` 같은 경로 매핑과 `*.do` 같은 확장자 매핑을 임의로 `/main/*.do` 형태로 합치지 않습니다. Servlet 매핑 우선순위는 일반적으로 **정확한 경로 → 가장 긴 경로 매핑 → 확장자 → 기본 매핑**입니다. 기본 매핑 `/`와 광범위 경로 매핑 `/*`는 같지 않습니다. 무분별한 `/*`는 JSP·정적 자원까지 가로챌 수 있습니다.

```java
String action = req.getParameter("action");
if (action == null || action.isBlank()) action = "index";
switch (action) {
    case "index" -> showIndex(req, resp);
    case "list" -> showMembers(req, resp);
    default -> resp.sendError(404);
}
```

이 코드는 **분기 구조를 보여주는 의사코드**입니다. 실제로는 GET·POST 허용 여부도 나누고, 각 처리 메서드에 입력 검증·응답 정책을 둡니다. action이 없다고 예외가 나거나, 알 수 없는 action에 무조건 성공 응답을 주지 않도록 합니다.

## 2. Filter Chain은 들어갈 때와 나올 때를 감싼다

```text
요청 → Filter A 전처리 → Filter B 전처리 → Servlet/JSP
응답 ← Filter A 후처리 ← Filter B 후처리 ← 처리 결과
```

`chain.doFilter()`가 다음 필터 또는 최종 대상으로 진행시키는 지점입니다. 호출하지 않으면 뒤의 처리는 실행되지 않으므로 인증 실패처럼 요청을 차단할 수 있습니다. 호출 뒤의 코드는 아래 처리가 돌아온 다음 실행됩니다.

```java
@WebFilter(urlPatterns="/*", dispatcherTypes=DispatcherType.REQUEST)
public class TraceFilter extends HttpFilter {
    @Override protected void doFilter(HttpServletRequest req,
            HttpServletResponse resp, FilterChain chain)
            throws IOException, ServletException {
        resp.setHeader("X-Learning-Filter", "applied");
        long start = System.nanoTime();
        try { chain.doFilter(req, resp); }
        finally {
            getServletContext().log("request elapsed(ns)="
                    + (System.nanoTime() - start));
        }
    }
}
```

예제는 응답 헤더와 경과 시간으로 필터 적용을 관찰합니다. 비밀번호나 세션 ID를 로그에 남기지 않습니다. `finally`를 쓰면 하위 처리에서 예외가 발생해도 정리·기록 코드를 실행할 수 있습니다. 이미 응답이 커밋되었다면 뒤에서 redirect·헤더 변경을 시도할 수 없습니다. **chain 호출이 끝났다고 모든 응답이 반드시 커밋된 것은 아니며 실제 상태를 확인해야 합니다.**

### URL뿐 아니라 DispatcherType도 확인하기

| 타입 | 실행 계기 |
| --- | --- |
| REQUEST | 브라우저 등 클라이언트가 보낸 요청 |
| FORWARD | `RequestDispatcher.forward()` |
| INCLUDE | 실행 중 다른 자원을 포함 |
| ERROR | 컨테이너의 오류 페이지 처리 |
| ASYNC | 비동기 처리의 dispatch |

기본 REQUEST 필터가 forward에도 다시 실행된다고 가정하면 안 됩니다. 반대로 REQUEST와 FORWARD를 둘 다 켜면 내부 이동에서 한 번 더 실행될 수 있습니다. 순서가 중요한 필터는 애너테이션 발견 순서에 의존하지 말고 명시적으로 구성합니다. 등록을 애너테이션과 XML 양쪽에서 중복해서 하지 않는지도 확인합니다.

## 3. 입력 치환 필터만으로 XSS를 막을 수 있을까?

사용자 입력의 `<`를 `&lt;`로 바꾸는 실습은 요청 wrapper의 역할을 이해하는 데는 도움이 됩니다. 하지만 HTML 본문·속성·JavaScript·URL은 서로 다른 문맥이므로 단순 문자열 치환을 범용 보안 대책으로 사용하면 안 됩니다.

- 입력은 형식·길이·허용값을 검증합니다.
- 화면 출력은 문맥에 맞게 인코딩합니다. HTML 텍스트에서는 JSP의 `c:out`을 사용할 수 있습니다.
- 사용자 입력을 JavaScript 코드나 URL에 직접 이어 붙이는 방식은 피합니다.
- HTML을 허용하는 기능은 별도의 안전한 정화 정책이 필요합니다.

`HttpServletRequestWrapper`를 쓸 때도 `getParameter()`만 바꾸면 배열·Map·JSON 등 다른 입력 경로가 그대로 남습니다. 필터가 있다는 사실과 안전한 출력이라는 결론을 구분해야 합니다.

## 4. Listener는 요청 라우터가 아니라 이벤트 관찰자

Listener는 애플리케이션·요청·세션의 생성과 종료, 속성 변경 같은 이벤트에 반응합니다. `ServletContextListener`는 애플리케이션 시작·종료 시 공유 자원을 준비하고 정리하는 데 사용합니다.

```java
@WebListener
public class AppListener implements ServletContextListener {
    @Override public void contextInitialized(ServletContextEvent event) {
        event.getServletContext().log("application started");
    }
    @Override public void contextDestroyed(ServletContextEvent event) {
        event.getServletContext().log("application stopped");
    }
}
```

이는 시작·종료 훅의 형태를 보여주는 짧은 예입니다. 실제 자원을 생성했다면 종료 때 그 자원도 닫아야 합니다. 파일을 읽는 데 실패했다고 무조건 빈 데이터로 바꾸면 손상된 파일을 덮어쓸 수 있으므로 초기화 오류 정책도 필요합니다.

| 상황 | 먼저 떠올릴 요소 |
| --- | --- |
| URL·action에 따라 업무 분배 | Front Controller |
| 여러 경로의 인증·인코딩·로깅 | Filter |
| 애플리케이션 시작·종료 작업 | Listener |

## 5. Servlet의 공유 상태와 동시성

Servlet의 필드에 `currentUser`나 요청별 파라미터를 넣으면 서로 다른 사용자의 요청이 같은 값을 공유할 수 있습니다. 필드가 있다는 이유만으로 항상 오류인 것은 아니지만, **변경 가능한 상태를 공유한다면 동시성 정책이 필요합니다.** 불변 서비스 참조와 사용자별 가변 데이터를 구분합니다.

```java
// 공유 재고에서 이 둘은 별도 동작입니다.
if (stock > 0) {
    stock--;
}
```

재고가 1일 때 두 요청이 모두 조건을 통과할 수 있습니다. `volatile`만 붙여도 검사와 감소가 하나의 원자적 작업이 되지는 않습니다. 적절한 락·원자적 연산·DB의 조건부 갱신 등을 상황에 맞게 사용합니다. 메서드 전체를 동기화하면 요청이 직렬화되어 병목이 될 수 있고, 여러 서버에 분산된 재고까지 같은 JVM의 락으로 보호할 수는 없습니다.

공유 List를 복사해 읽기 전용으로 반환해도 내부 Member 객체까지 불변이 되는 것은 아닙니다. 복사와 갱신이 같은 동기화 규칙을 지키는지, 얕은 복사로 충분한지를 따로 봐야 합니다.

## 실행 확인과 복습

[검증 프로젝트](https://github.com/js05157/cs-interview/tree/master/examples/web-learning)의 `appliesRequestFilter` 테스트는 실제 HTTP 응답에서 `X-Learning-Filter: applied`를 검사합니다. 코드의 전체 import·서버 등록은 프로젝트에 있습니다. Front Controller 분기·Listener 예시는 설명용이며 별도의 운영 부하 시험을 수행했다는 뜻은 아닙니다.

- 필터에서 인증 실패 후 `sendRedirect()`만 호출하고 계속 chain을 실행하면? **보호하려던 대상까지 실행될 수 있습니다.** 응답 후 `return`으로 처리를 종료해야 합니다.
- JSP forward 때 필터 로그가 두 번 찍히면? **매핑의 DispatcherType을 확인합니다.** REQUEST와 FORWARD 모두 적용되었을 수 있습니다.
- 연결 풀이 있다고 모든 업무 데이터가 동시성 안전해질까요? **아닙니다.** 연결 수 제한과 재고 갱신의 원자성은 다른 문제입니다.

## 자료와 다음 학습

제공된 `02_servlet` PDF 31쪽의 Front Controller(5–10쪽), Filter·wrapper(12–20쪽), Listener(22–24쪽), 공유 상태(26–29쪽)를 정리했습니다. 준비·구분·다음 수업 안내를 제외한 개념과 실습 의도를 포함했습니다.

- [Jakarta Servlet 6.1 명세](https://jakarta.ee/specifications/servlet/6.1/jakarta-servlet-spec-6.1.pdf)
- 이전: [Servlet 기초](/cs-interview/study/servlet-basics/)
- 다음: [JSP와 MVC](/cs-interview/study/jsp-mvc/)
