---
title: 'JSP와 MVC: 데이터를 화면으로 전달하기'
date: 2026-11-04 00:00:00 +0900
content_type: ssafy
series: Java 웹 기초
series_order: 3
series_total: 5
notion_url: https://www.notion.so/40e47f4c2c2581dcbfb4def81e21733b
tags: [Java, JSP, MVC, Forward, Redirect]
permalink: /study/jsp-mvc/
description: JSP의 Servlet 변환, 내장 객체와 scope, parameter·attribute, MVC와 화면 이동을 정리합니다.
---

Servlet에서 긴 HTML 문자열을 만들면 화면과 업무 코드가 서로 얽힙니다. JSP는 HTML 중심으로 화면을 작성하는 기술입니다. **JSP도 서버에서 Servlet으로 변환되어 실행되며, 브라우저에는 실행 결과인 HTML이 전달됩니다.**

## 1. JSP가 실행되는 과정

```text
JSP 소스 → Servlet Java 소스로 번역 → 컴파일 → 생성·초기화 → 요청 처리
                                                   jspInit()    _jspService()
                                                   종료 시 jspDestroy()
```

최초 접근이나 변경 감지 시 번역·컴파일이 필요할 수 있습니다. 이후에는 생성된 Servlet을 재사용합니다. 사전 컴파일도 가능하므로 매 요청마다 JSP 전체를 새로 컴파일한다고 이해하지 않습니다. IDE·Tomcat 작업 디렉터리의 생성된 `*_jsp.java`를 보면 화면 코드가 어떻게 바뀌는지 확인할 수 있습니다.

## 2. JSP 문법을 Java의 어느 위치로 바꾸는가

| 문법 | 역할 | 변환되는 위치·특징 |
| --- | --- | --- |
| `<%@ page ... %>` | 인코딩·import·오류 등 번역 정보 | 컨테이너가 읽는 지시자 |
| `<% ... %>` | 스크립틀릿 | 주로 `_jspService()` 내부 |
| `<%= ... %>` | 식의 값을 출력 | 출력 호출로 변환, 자동 HTML escaping 아님 |
| `<%! ... %>` | 필드·메서드 선언 | Servlet 클래스 멤버 |
| `<%-- ... --%>` | JSP 주석 | 응답 HTML에 포함하지 않음 |
| `<!-- ... -->` | HTML 주석 | 응답에 남아 소스 보기로 확인 가능 |

선언부의 가변 필드는 여러 요청이 공유할 수 있으므로 요청별 상태를 보관하면 안 됩니다. JSP 주석에도 비밀번호를 넣지 않는 것이 좋지만 특히 **HTML 주석은 비밀 저장소가 아닙니다.**

```html
<%@ page contentType="text/html;charset=UTF-8"
         pageEncoding="UTF-8" session="false" %>
```

`pageEncoding`은 JSP 소스 해석, `contentType`의 charset은 응답 해석과 관련됩니다. 기본값에 의존하지 않고 둘 다 UTF-8로 맞춥니다. 모든 JSP 파일에 page 지시자가 문법상 필수인 것은 아니며 설정·정적 include로 정보를 공유할 수도 있습니다. 페이지의 내용과 설정이 충돌하지 않게 관리하는 것이 핵심입니다. [JSP 4.0 명세](https://jakarta.ee/specifications/pages/4.0/jakarta-server-pages-spec-4.0.html)

## 3. 내장 객체와 네 가지 scope

JSP는 `request`, `response`, `out`, `pageContext`, `session`, `application`, `config`, `page` 같은 객체를 제공합니다. `exception`은 `isErrorPage="true"`인 오류 페이지에서 사용할 수 있습니다. `session="false"`이면 session 내장 객체를 사용할 수 없습니다.

| scope | 데이터를 공유하는 범위 | 적합한 데이터 |
| --- | --- | --- |
| page | 현재 JSP 페이지 실행 | 화면 안의 임시 값 |
| request | 한 요청의 처리·forward | 조회 결과, 검증 오류 |
| session | 같은 서버 세션의 여러 요청 | 로그인 상태, 장바구니 |
| application | 웹 애플리케이션 전반 | 공유 설정·공유 자원 |

넓은 scope가 더 좋은 것은 아닙니다. 조회 결과를 application에 두면 사용자끼리 섞일 수 있고, session에 계속 쌓으면 메모리와 오래된 값 문제가 생깁니다. 서버 세션은 브라우저 종료 통지만으로 즉시 삭제되는 구조가 아니므로 종료·만료를 구분해야 합니다.

## 4. Parameter와 Attribute는 출처와 자료형이 다르다

| 비교 | Parameter | Attribute |
| --- | --- | --- |
| 주로 누가 만드는가 | 클라이언트 요청 | 서버 처리 코드 |
| 조회 | `getParameter()` | `getAttribute()` |
| 값 | 문자열·문자열 배열 | Java 객체 |
| 원본 API로 변경 | 전용 setter 없음 | `setAttribute`, `removeAttribute` |
| 예 | 검색어·입력 숫자 | 검색 결과 List·오류 메시지 |

컨트롤러는 문자열을 검증·변환하고 Model을 호출합니다. 화면에 필요한 결과 객체를 request 속성으로 전달하면 JSP가 업무 처리를 반복할 필요가 없습니다.

## 5. Model 1과 Model 2

Model 1에서는 JSP가 요청 제어와 화면 생성을 함께 맡는 경우가 많습니다. 시작은 간단하지만 기능이 늘면 업무·화면 코드가 섞입니다. Model 2는 Servlet을 Controller로, JSP를 View로 분리합니다.

```text
브라우저 → Controller: 입력 검증·업무 호출·응답 선택
                 ↕
              Model: Service → 필요할 때 DAO
                 ↓ 결과 객체
            request.setAttribute(...)
                 ↓ forward
               View: JSP → HTML → 브라우저
```

Model은 DB 테이블만을 의미하지 않습니다. 업무 규칙·서비스·화면에 전달할 데이터도 포함합니다. JSP가 직접 DAO를 호출하거나 Service가 HTTP 응답을 출력하면 경계가 다시 흐려집니다.

### 데이터 전달을 관찰하는 예제

```java
req.setAttribute("message", "요청에서 전달한 값");
req.setAttribute("members", List.of(
    new Member("Ada"), new Member("<script>demo</script>")));
req.getRequestDispatcher("/WEB-INF/views/members.jsp").forward(req, resp);
```

JSP에서는 `${requestScope.message}`와 `${requestScope.members}`를 사용합니다. `Member`는 `getName()`을 제공하는 간단한 객체입니다. 구체적인 화면은 다음 EL/JSTL 글에서 다룹니다. `WEB-INF` 아래의 JSP는 직접 URL 요청으로 접근할 수 없지만 Controller의 forward로는 사용할 수 있습니다.

## 6. Forward와 Redirect를 요청 수로 비교하기

| 비교 | Forward | Redirect |
| --- | --- | --- |
| 동작 | 컨테이너 내부에서 다른 대상으로 전달 | 응답의 Location을 받은 브라우저가 다시 요청 |
| 브라우저가 보내는 요청 | 기존 요청 1번 | 처음 요청 + 후속 요청 |
| 주소창 | 일반적으로 유지 | 이동 주소로 변경 |
| request 속성 | 공유 | 자동 전달되지 않음 |
| 대표 사용 | 조회 결과·입력 오류 화면 | 작업 성공 후 목록·메인 이동 |

```java
// 같은 요청의 결과 화면
req.getRequestDispatcher("/WEB-INF/views/result.jsp").forward(req, resp);
return;

// 별도의 새 요청으로 이동
resp.sendRedirect(req.getContextPath() + "/members");
return;
```

위 코드는 두 가지 선택지를 비교한 것입니다. 한 요청에서 둘을 연속 실행하는 코드가 아닙니다. redirect 호출이 Java 메서드를 자동으로 끝내 주지는 않으므로 이후 처리를 실행하지 않도록 합니다. 응답이 이미 커밋되면 forward할 수 없습니다. 외부 URL을 사용자 입력으로 무조건 받아 redirect하면 오픈 리다이렉트 문제가 생길 수 있습니다.

## 7. PRG와 입력 오류의 처리

POST 성공 뒤 결과 JSP로만 forward하면 새로고침이 POST 재전송으로 이어질 수 있습니다. PRG는 **POST 처리 → Redirect 응답 → GET 결과 조회**로 바꿔 새로고침 시 GET을 반복하게 합니다. POST 뒤 GET 이동 의도를 명확히 하려면 303 응답을 사용할 수 있습니다.

반대로 검증 실패 시에는 request에 오류와 입력값을 넣고 입력 화면으로 forward하면 편합니다. 비밀번호처럼 민감한 값은 다시 채우지 않습니다. 일회성 성공 알림을 session에 보관했다면 읽은 뒤 지워 오래된 알림이 반복되지 않게 합니다.

PRG만으로 중복 결제·중복 등록을 모두 막을 수는 없습니다. 응답 유실과 재시도는 여전히 가능하므로 중요한 변경에는 고유 제약이나 멱등성 처리가 별도로 필요합니다.

## 실행 확인과 복습

로컬 검증 프로젝트는 실제 Tomcat에서 JSP를 컴파일하고 request 메시지·목록을 HTML로 출력합니다. `WEB-INF` 직접 요청의 404와 사용자 입력의 escaping도 검사합니다. 단순 문자열 치환으로 JSP 실행을 흉내 낸 검사가 아닙니다.

- redirect 후 request의 List가 사라지는 이유는? **다른 HTTP 요청이기 때문입니다.** 식별자를 새 요청에 전달해 다시 조회하거나 적절한 별도 상태 관리가 필요합니다.
- `<%! int count; %>`는 요청마다 초기화될까요? **아닙니다.** 생성된 Servlet의 필드이므로 공유 상태가 될 수 있습니다.
- JSP를 WEB-INF에 두면 인증이 자동으로 해결될까요? **아닙니다.** 직접 View 접근을 막는 설계이며 Controller의 권한 검사는 별도로 필요합니다.

## 자료와 다음 학습

제공된 `03_jsp` PDF 34쪽의 번역·문법(4–12쪽), 내장 객체·scope(13–18쪽), MVC(20–23쪽), 화면 이동(24–27쪽), 구구단 정상·오류 흐름(29–32쪽)을 연결했습니다. 실습 의존 파일 대신 독립 재현 예제를 제공합니다.

- [JSP 4.0 명세](https://jakarta.ee/specifications/pages/4.0/jakarta-server-pages-spec-4.0.html)
- [응답·redirect API](https://jakarta.ee/specifications/servlet/6.1/apidocs/jakarta.servlet/jakarta/servlet/http/HttpServletResponse.html)
- 이전: [Servlet 공통 처리](/cs-interview/study/servlet-components/)
- 다음: [EL과 JSTL](/cs-interview/study/el-jstl/)
