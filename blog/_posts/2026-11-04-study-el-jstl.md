---
title: 'EL과 JSTL: 스크립틀릿 없이 화면 만들기'
date: 2026-11-04 00:00:00 +0900
content_type: ssafy
series: Java 웹 기초
series_order: 4
series_total: 5
notion_url: https://www.notion.so/40e47f4c2c25814b9526d5c0fffc07df
tags: [Java, JSP, EL, JSTL]
permalink: /study/el-jstl/
description: EL의 속성 검색과 연산, JSTL의 변수·조건·반복, include와 PRG를 화면 예제로 이해합니다.
---

Controller가 데이터를 준비했다면 JSP는 그 데이터를 읽어 화면을 만들면 됩니다. **EL은 값을 읽고 계산하는 표현식이고, JSTL은 조건·반복 같은 화면 작업을 태그로 표현하는 라이브러리입니다.** 업무 처리를 JSP로 옮기는 기술은 아닙니다.

## 1. EL은 어디에서 값을 찾을까?

`${name}`은 일반 Java 지역 변수 `name`을 읽는 문법이 아닙니다. 기본적으로 이름이 같은 속성을 **page → request → session → application** 순으로 검색합니다. 여러 scope에 같은 이름이 있으면 먼저 찾은 값이 보입니다.

```html
${name}
${requestScope.name}
${sessionScope.loginUser}
${param.keyword}
${paramValues.interests[0]}
${header['User-Agent']}
${cookie.recent.value}
${pageContext.request.contextPath}
```

`param`은 파라미터의 단일 값, `paramValues`는 여러 값, `cookie`는 이름으로 찾은 Cookie 객체를 제공합니다. request 속성과 파라미터의 이름이 같아도 출처는 다릅니다. 의도한 영역이 분명하면 `${requestScope.members}`처럼 scope를 쓰는 편이 읽기 쉽습니다.

없는 값을 단순 출력하면 빈 문자열처럼 보일 수 있습니다. 그렇다고 내부 값이 언제나 빈 문자열인 것은 아니며, 연산·메서드 호출에서의 변환과 오류는 따로 봐야 합니다.

## 2. 점·대괄호와 JavaBean 프로퍼티

`${member.name}`은 보통 JavaBean의 `getName()`을 읽습니다. private 필드를 직접 여는 문법이 아닙니다. Map은 키로, 배열·List는 인덱스로 접근합니다.

| 식 | 읽는 대상 |
| --- | --- |
| `${member.name}` | Bean의 name 프로퍼티 |
| `${member['name']}` | 같은 프로퍼티 또는 Map 키 |
| `${members[0].name}` | 첫 요소의 name |
| `${header['User-Agent']}` | 하이픈이 들어간 헤더 이름 |

`${header.User-Agent}`처럼 쓰면 하이픈이 연산자로 해석될 수 있습니다. 일반 JavaBean에는 getter가 필요하지만 모든 객체에 setter가 항상 필수인 것은 아닙니다. 읽기 전용 Bean도 가능하고, Java record 접근은 사용 중인 EL 버전의 record 지원 여부를 확인합니다. 이 시리즈의 검증 예제는 버전 차이를 줄이기 위해 `getName()`을 사용합니다.

## 3. EL 연산에서 Java와 다른 부분

| 목적 | 표현 예 | 주의 |
| --- | --- | --- |
| 비교 | `${count ge 1}`, `${state eq 'READY'}` | 숫자·문자열 변환 규칙 확인 |
| 논리 | `${not empty members and allowed}` | 빈 값과 권한 조건을 구분 |
| 선택 | `${empty name ? '방문자' : name}` | 출력 escaping은 별개 |
| 산술 | `${'1' + '2'}` | 문자열 결합이 아니라 숫자로 변환해 3 |
| 존재 확인 | `${empty members}` | null·빈 문자열·빈 배열·빈 Collection·빈 Map 등 |

숫자 0이나 문자열의 공백 한 칸이 무조건 empty인 것은 아닙니다. `+`로 문자열을 이어 붙이려고 하거나 변환할 수 없는 문자열을 계산하면 오류가 날 수 있습니다. JSP의 `${...}`와 JavaScript 템플릿 문자열의 `${...}`도 충돌할 수 있으므로 클라이언트 템플릿은 외부 JS로 분리하는 등 평가 위치를 명확히 합니다.

EL은 자동으로 HTML을 안전하게 바꾸지 않습니다. 사용자 입력을 HTML 텍스트로 표시할 때는 `c:out`처럼 escaping을 수행하는 출력을 사용합니다.

## 4. JSTL 준비와 라이브러리 구분

현재 Jakarta Tags 계열에서는 API와 구현 라이브러리가 필요합니다. 오래된 `javax` 기반 JSTL을 현재 Jakarta Servlet 환경에 무작정 섞지 않습니다. 검증 프로젝트는 다음 조합을 고정했습니다.

```xml
<dependency>
  <groupId>jakarta.servlet.jsp.jstl</groupId>
  <artifactId>jakarta.servlet.jsp.jstl-api</artifactId>
  <version>3.0.2</version>
</dependency>
<dependency>
  <groupId>org.glassfish.web</groupId>
  <artifactId>jakarta.servlet.jsp.jstl</artifactId>
  <version>3.0.1</version>
</dependency>
```

JSP에서 사용할 core 태그 라이브러리를 선언합니다.

```html
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
```

URI는 태그 라이브러리의 식별자입니다. 매 요청마다 이 주소에서 코드를 다운로드하라는 뜻이 아닙니다. core 외에 formatting(`fmt`), functions(`fn`) 등이 있습니다. DB 작업을 JSP의 SQL 태그로 처리하기보다 Controller·Service·DAO에 두는 것이 MVC의 역할 분리에 맞습니다.

## 5. 변수·조건·반복 태그

| 태그 | 역할 | 기억할 점 |
| --- | --- | --- |
| `c:set` | scope에 속성 저장 | scope 생략 시 page |
| `c:remove` | 속성 제거 | scope 생략 시 모든 scope에서 해당 이름 제거 |
| `c:if` | 조건이 참일 때 출력 | else는 없음 |
| `c:choose`·`when`·`otherwise` | 여러 갈래 조건 | 처음 맞는 when 사용 |
| `c:forEach` | 목록·횟수 반복 | index는 0부터, count는 1부터 |
| `c:out` | 값 출력 | 기본 XML/HTML escaping, 모든 출력 문맥의 보안 해결책은 아님 |

**`c:set`과 `c:remove`의 scope 생략을 같은 규칙으로 외우면 안 됩니다.** 제거할 영역이 분명하면 명시합니다. [Jakarta Tags 3.0 명세, c:remove](https://jakarta.ee/specifications/tags/3.0/jakarta-tags-spec-3.0.pdf)

```html
<c:set var="label" value="학습 중" scope="request" />
<c:if test="${not empty requestScope.label}">
  <c:out value="${requestScope.label}" />
</c:if>
<c:remove var="label" scope="request" />
```

## 6. 실제 목록 화면 만들기

앞 글의 Controller는 `members`에 Ada와 `<script>demo</script>`라는 이름을 담아 request 속성으로 전달했습니다. 아래 JSP는 빈 목록을 분기하고, 목록이 있으면 순서대로 출력합니다.

```html
<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" session="false" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<p><c:out value="${requestScope.message}" /></p>
<c:choose>
  <c:when test="${empty requestScope.members}">목록이 없습니다.</c:when>
  <c:otherwise>
    <ul>
      <c:forEach items="${requestScope.members}" var="member" varStatus="status">
        <li>${status.count}. <c:out value="${member.name}" /></li>
      </c:forEach>
    </ul>
  </c:otherwise>
</c:choose>
```

서버가 반환한 HTML에는 `1. Ada`, `2. &lt;script&gt;demo&lt;/script&gt;`가 들어갑니다. 두 번째 이름은 스크립트가 아니라 텍스트로 표시됩니다. 로컬 실제 Tomcat 테스트는 JSP 컴파일·JSTL 실행·응답 문자열을 확인합니다. `c:remove`의 전체 scope 제거와 EL의 `'1' + '2'`도 별도 JSP에서 검사합니다.

실제 회원 관리라면 DAO가 조회 결과를 반환하고 Controller가 request에 넣는 흐름입니다. 원본 List를 복사해 반환하더라도 객체 내부의 가변 필드까지 독립된 복사본이 되는 것은 아닙니다. 예제 이름은 화면 설명을 위한 가상 데이터입니다.

## 7. 페이지 모듈화: 정적 include와 실행 중 include

```html
<%@ include file="/WEB-INF/fragments/header.jspf" %>
```

include 지시자는 번역 단계에서 파일 내용을 합칩니다. 합쳐진 선언·지역 변수·지시자들이 충돌할 수 있으므로 공통 파일의 역할을 작게 유지합니다. fragment에 완성된 `<html>`·`<body>`를 중복해서 넣으면 문서 구조가 잘못될 수 있습니다.

반면 `<jsp:include page="..." />`는 요청 처리 중 포함 대상의 실행 결과를 합치는 방식입니다. “include면 항상 같은 Java 소스 하나가 된다”로 일반화하지 않습니다. 정적 include의 `/`는 웹 애플리케이션 기준이고, HTML 링크의 `/`는 브라우저의 origin 기준입니다.

공통 헤더의 로그인 표시와 메뉴를 재사용할 수 있지만 View에서 회원을 등록하거나 파일을 저장하지는 않습니다. 등록 성공 시 PRG, 검증 실패 시 request 오류를 담아 forward한다는 앞 글의 흐름과 연결합니다.

## 정리와 복습

EL은 서버가 준비한 값을 찾고 JSTL은 화면의 조건·반복을 표현합니다. 데이터 준비와 업무 판단은 Controller·Model에 남기면 화면을 읽기 쉬워집니다. scope 검색 순서와 출력 escaping을 함께 이해해야 같은 이름의 값이 덮이거나 입력이 HTML로 실행되는 실수를 줄일 수 있습니다.

- session과 request에 같은 `name`이 있으면 `${name}`은? **page에 같은 이름이 없다면 request 값을 먼저 찾습니다.** scope를 명시하면 의도가 분명합니다.
- `c:remove`에서 scope를 빼면 page만 지울까요? **아닙니다.** 같은 이름을 전체 scope에서 제거하므로 영역을 명시하는 것이 안전합니다.
- `c:out`을 쓰면 사용자 입력을 JavaScript 문자열에 넣어도 안전할까요? **아닙니다.** HTML 텍스트 escaping과 JavaScript 문맥의 안전한 처리는 다릅니다.

## 자료와 다음 학습

제공된 `04_el_jstl` PDF 39쪽의 MVC·회원가입·PRG(4–11쪽), EL(13–19쪽), JSTL(21–28쪽), include(30–33쪽), 회원 목록 흐름(35–37쪽)을 정리했습니다. 프로젝트·DB 별도 PDF는 사용하지 않았습니다.

- [Jakarta Tags 3.0 명세](https://jakarta.ee/specifications/tags/3.0/jakarta-tags-spec-3.0.pdf)
- [JSP 4.0 명세](https://jakarta.ee/specifications/pages/4.0/jakarta-server-pages-spec-4.0.html)
- 이전: [JSP와 MVC](/cs-interview/study/jsp-mvc/)
- 다음: [쿠키와 세션](/cs-interview/study/session-cookie/)
