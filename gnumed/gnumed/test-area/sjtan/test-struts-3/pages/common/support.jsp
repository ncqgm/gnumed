<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<html>

<h3><bean:message key="app.support"/> </h3>
<b> <bean:message key="nosupport"/> </b>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
<a href="./development_notes.jsp"><bean:message key="app.development_notes"/> </a>

</html>
