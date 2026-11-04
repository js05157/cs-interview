<%@ page contentType="text/plain;charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<c:set var="flag" value="P" scope="page" />
<c:set var="flag" value="R" scope="request" />
<c:set var="flag" value="S" scope="session" />
before=${flag}, request=${requestScope.flag}, sum=${'1'+'2'}
<c:remove var="flag" />
after=${empty pageScope.flag and empty requestScope.flag and empty sessionScope.flag}
