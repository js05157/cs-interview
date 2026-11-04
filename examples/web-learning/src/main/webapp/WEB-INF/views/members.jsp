<%@ page contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" session="false" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<!doctype html><html lang="ko"><meta charset="utf-8"><title>학습 목록</title><body>
<p id="message"><c:out value="${requestScope.message}" /></p>
<c:choose><c:when test="${empty requestScope.members}">목록이 없습니다.</c:when>
<c:otherwise><ul><c:forEach items="${requestScope.members}" var="member" varStatus="status">
<li>${status.count}. <c:out value="${member.name}" /></li>
</c:forEach></ul></c:otherwise></c:choose>
</body></html>
