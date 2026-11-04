---
title: '쿠키와 세션: 로그인·장바구니·오류 처리'
date: 2026-11-04 00:00:00 +0900
content_type: ssafy
series: Java 웹 기초
series_order: 5
series_total: 5
notion_url: https://www.notion.so/40e47f4c2c2581a48c15edd7badf85f4
tags: [Java, Cookie, Session, Security]
permalink: /study/session-cookie/
description: 쿠키 왕복, 서버 세션의 수명, 로그인·로그아웃, 접근 검사와 오류 페이지를 연결합니다.
---

HTTP 요청은 그 자체로 이전 요청의 로그인 결과를 기억하지 않습니다. **쿠키는 브라우저가 보관해 조건에 맞는 요청에 돌려주는 값이고, 서버 세션은 그 식별자에 연결한 상태를 서버 쪽에서 관리하는 방식입니다.** 로그인 성공 한 번과 이후 요청에서의 로그인 확인은 별도 과정입니다.

## 1. 쿠키가 왕복해야 상태를 이어갈 수 있다

```text
1. 브라우저 ── 첫 요청 ──────────────→ 서버
2. 브라우저 ← Set-Cookie: recent=4 ─── 서버
3. 브라우저: 쿠키 저장
4. 브라우저 ── Cookie: recent=4 ──────→ 서버의 다음 요청
```

Servlet의 `response.addCookie()`는 **응답**에 쿠키를 추가합니다. 현재 `request.getCookies()`를 즉시 바꾸지 않습니다. 쿠키를 설정하고 같은 요청을 JSP로 forward해도 새 쿠키가 현재 request에 생기는 것은 아닙니다. 다음 요청을 받아야 브라우저의 반환값을 확인할 수 있습니다.

## 2. 이름만 같으면 같은 쿠키일까?

쿠키는 이름뿐 아니라 domain·path 같은 저장·전송 범위도 함께 봐야 합니다. 같은 이름의 쿠키가 서로 다른 경로로 존재할 수 있습니다. 요청의 Cookie 헤더만으로는 원래 Set-Cookie의 모든 속성을 알 수 없습니다.

| 속성 | 의미 | 자주 하는 실수 |
| --- | --- | --- |
| Path | 전송할 경로 범위 | 다른 path로 삭제 쿠키를 보냄 |
| Domain | 적용할 호스트 범위 | 불필요하게 넓게 공유 |
| Max-Age | 유지 시간 | Java API와 HTTP 헤더의 음수 의미를 혼동 |
| Secure | 보안 연결에서 전송 | 쿠키 내용 자체를 암호화한다고 생각 |
| HttpOnly | JS의 직접 읽기 제한 | XSS 전체가 해결된다고 생각 |
| SameSite | cross-site 요청의 쿠키 제한 | 모든 CSRF를 완전히 막는다고 생각 |

Path를 생략하면 브라우저는 **쿠키를 설정한 요청 경로로 기본 경로를 계산**합니다. 항상 애플리케이션 Context가 되는 것은 아닙니다. `/learn/status/set`에서 설정한 쿠키가 `/learn/member`에 오지 않는다면 Path부터 확인합니다. 쿠키는 포트로 분리되는 저장소도 아닙니다. [Set-Cookie의 경로 규칙](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)

### Java의 maxAge와 실제 헤더를 구분하기

- `Cookie#setMaxAge(양수)`는 초 단위 지속 시간을 설정합니다.
- Java에서 음수는 보통 지속 시간을 명시하지 않는 세션 쿠키 의미입니다.
- `setMaxAge(0)`을 같은 이름·domain·path로 전송하면 삭제를 요청합니다.
- HTTP `Max-Age` 헤더 자체의 0 이하 값은 즉시 만료 의미입니다. Java의 음수 설정과 그대로 같은 의미로 외우지 않습니다.

세션 쿠키도 브라우저의 세션 복원 기능으로 살아날 수 있습니다. “브라우저를 닫으면 반드시 모두 사라진다”는 가정에 보안을 맡기지 않습니다.

## 3. 쿠키 예제와 실제 관찰

```java
Cookie recent = new Cookie("recent", "4");
recent.setPath(req.getContextPath().isEmpty() ? "/" : req.getContextPath());
recent.setMaxAge(90);
recent.setHttpOnly(true);
recent.setAttribute("SameSite", "Lax");
// HTTPS 운영 환경에서는 Secure도 true로 설정합니다.
resp.addCookie(recent);
```

한글·공백 등의 값을 저장하려면 허용되는 형태로 인코딩하고 읽을 때 같은 규칙으로 디코딩합니다. 인코딩은 암호화가 아닙니다. 비밀번호·신뢰해야 할 권한 값을 그대로 쿠키에 담지 않습니다. 최근 구구단·화면 설정처럼 변조되어도 보안 판단에 쓰지 않을 작은 값이 실습 대상으로 적절합니다.

로컬 HTTP 테스트에서는 Secure를 켜지 않습니다. 실제 쿠키 왕복 테스트는 처음 `/cookie/set`에서 요청 쿠키가 `absent`, 다음 `/cookie/check`에서 `4`, 같은 Path로 삭제한 뒤 `absent`가 되는 것을 검사합니다. 브라우저의 모든 SameSite 정책이나 HTTPS 전송을 이 테스트로 검증했다는 뜻은 아닙니다.

## 4. SameSite·HttpOnly는 방어의 일부

| SameSite | 일반적인 의미 |
| --- | --- |
| Strict | cross-site에서 쿠키 전송을 강하게 제한 |
| Lax | 일부 최상위의 안전한 탐색 등에는 허용 |
| None | cross-site 사용 허용을 요청하며 Secure 필요 |

site와 origin은 다릅니다. 브라우저의 third-party cookie 제한 등도 별도로 적용될 수 있습니다. 로그인 쿠키에 HttpOnly·Secure·적절한 SameSite를 구성하고, 상태 변경 요청에는 CSRF 토큰·Origin 검증 같은 대책을 함께 검토합니다. `HttpOnly`가 있어도 XSS가 사용자를 대신해 요청하는 위험까지 없어지지는 않습니다.

## 5. 세션 ID와 서버 상태의 관계

```text
브라우저: JSESSIONID=임의의 식별자
               │ Cookie로 전달
               ▼
서버 세션 저장소: 식별자 → { loginUser, cart, ... }
```

기본 이름은 보통 `JSESSIONID`이며 설정으로 바꿀 수 있습니다. 쿠키 외에 URL 재작성 같은 추적 방법도 있지만 인증 식별자를 URL에 노출하는 방식은 피하는 것이 좋습니다. 브라우저 탭마다 독립 세션이 자동으로 생기는 것도 아닙니다. 같은 쿠키 저장소를 쓰는 탭은 대체로 같은 세션을 공유합니다.

| API | 동작 |
| --- | --- |
| `getSession()` | 세션이 없으면 생성 |
| `getSession(false)` | 없으면 null, 새로 만들지 않음 |
| `setAttribute`·`getAttribute` | 상태 저장·조회 |
| `removeAttribute` | 속성 하나 제거 |
| `invalidate()` | 세션 전체 무효화 |
| `changeSessionId()` | 현재 세션의 식별자를 교체 |

브라우저 종료가 서버 세션의 즉시 삭제를 보장하지 않습니다. 서버는 로그아웃의 invalidate, 유휴 시간 초과, 서버 정책 등으로 세션을 종료합니다. `setMaxInactiveInterval(1200)`은 **초 단위 20분**, web.xml의 `<session-timeout>20</session-timeout>`은 **분 단위**입니다. [HttpSession API](https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/http/HttpSession.html)

## 6. 로그인·로그아웃과 접근 검사

로그인 성공 시 사용자 확인 → 세션 생성/조회 → ID 교체 → 필요한 사용자 정보 저장 → redirect 순으로 처리할 수 있습니다. 실패하면 성공 세션을 만들지 않고 입력 화면에 일반적인 오류를 표시합니다. 세션에는 비밀번호 대신 최소한의 사용자 식별 정보를 둡니다.

```java
// 인증에 성공한 뒤 실행하는 부분입니다.
HttpSession session = req.getSession();
req.changeSessionId();
session.setMaxInactiveInterval(1200);
session.setAttribute("loginUser", authenticatedUserId);
resp.setStatus(303);
resp.setHeader("Location", req.getContextPath() + "/auth/profile");
return;
```

보호된 경로의 Filter에서는 `getSession(false)`로 검사할 수 있습니다. 로그인 페이지·정적 자원까지 막아 무한 redirect가 생기지 않게 범위를 정합니다. 로그인했다는 사실과 해당 작업을 할 권한이 있다는 사실은 별도로 확인합니다.

```java
HttpSession session = req.getSession(false);
if (session == null || session.getAttribute("loginUser") == null) {
    resp.sendRedirect(req.getContextPath() + "/login");
    return;
}
chain.doFilter(req, resp);
```

로그아웃은 기존 세션이 있을 때 `invalidate()`합니다. 로그인 속성 하나를 지우는 것과 달리 장바구니 등 나머지 세션 데이터도 함께 무효화됩니다. 실제 서비스에서는 POST와 CSRF 방어, 식별자 쿠키 정리, 민감 응답의 캐시 정책도 함께 다룹니다.

## 7. 장바구니는 세션에 둘 수 있지만 공유를 생각해야 한다

실습의 흐름은 **GET 화면 → POST 항목 추가 → 세션 cart 수정 → redirect → GET 화면 재조회**입니다. 구매·비우기도 상태 변경이므로 GET 링크로 실행하지 않습니다. 장바구니만 비우려면 `removeAttribute("cart")`, 로그아웃이라면 세션 전체 무효화가 목적에 맞을 수 있습니다.

한 사용자의 여러 탭·요청이 동시에 cart를 수정할 수 있으므로 세션에 넣었다고 내부 List의 복합 연산이 자동으로 안전해지지는 않습니다. 장바구니에 들어간 가격·권한 같은 값을 그대로 신뢰해 결제하지 않고 서버에서 다시 검증해야 합니다. 이 정리본은 세션 활용 원리를 설명하며 실제 구매·결제 기능은 구현하지 않습니다.

## 8. 404·500과 오류 페이지

예상할 수 있는 입력 오류는 구체적인 검증 메시지로 처리하고, 예기치 않은 내부 오류는 서버 로그와 사용자 안내를 분리합니다. 스택 트레이스·SQL·파일 경로·비밀번호를 사용자에게 그대로 보여주지 않습니다.

```xml
<error-page>
  <error-code>404</error-code>
  <location>/WEB-INF/views/not-found.jsp</location>
</error-page>
<error-page>
  <error-code>500</error-code>
  <location>/WEB-INF/views/server-error.jsp</location>
</error-page>
```

위 XML은 두 오류 코드의 설정 예입니다. 검증 프로젝트에는 404 화면만 포함하고 실제 404 상태 유지를 확인합니다. `forward()`로 오류 화면만 출력하면 상태가 여전히 200일 수 있습니다. `sendError(404)`와 오류 페이지 매핑 또는 명시적인 상태 설정을 함께 고려합니다. ERROR dispatch를 관찰하려면 필터에 `DispatcherType.ERROR`가 필요합니다.

## 실행 확인과 복습

[실행 프로젝트](https://github.com/js05157/cs-interview/tree/master/examples/web-learning)는 로컬용 고정 계정으로 로그인 실패 401 → 로그인 성공 303 → 세션으로 프로필 조회 → 로그아웃 → 다시 401을 실제 HTTP로 검사합니다. 고정 비밀번호는 오직 재현용이며 비밀번호 저장·해싱이나 운영 인증을 구현한 예제가 아닙니다.

- 쿠키를 추가하고 forward한 화면에서 왜 새 쿠키가 안 보일까요? **아직 브라우저가 다음 요청으로 돌려주지 않았기 때문입니다.**
- 브라우저를 닫았는데 서버 메모리의 세션은 왜 남아 있을까요? **종료 통지와 서버의 만료 처리는 별개이기 때문입니다.**
- 장바구니 List는 session에 넣으면 안전할까요? **저장 범위와 동시성은 별개입니다.** 동시 수정 정책이 필요합니다.

## 자료와 이어 읽기

제공된 `05_sessioncookie` PDF 35쪽의 쿠키(4–14쪽), 세션과 로그인(16–25쪽), 오류 처리(27–30쪽), 장바구니 부록(33–34쪽)을 정리했습니다. 브라우저 종료·기본 Path·SameSite의 단순화된 표현은 API·브라우저 문서의 조건을 덧붙였습니다.

- [Cookie API](https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/http/Cookie.html)
- [HttpSession API](https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/http/HttpSession.html)
- [HTTP 쿠키 가이드](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- 이전: [EL과 JSTL](/cs-interview/study/el-jstl/)
- [학습 목차](/cs-interview/study/)
