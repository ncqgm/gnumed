<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-tiles" prefix="tiles"%>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>

<html>

<h3><bean:message key="app.support"/> </h3>
<b> <bean:message key="nosupport"/> </b>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
<!--
<a href="./development_notes.jsp"><bean:message key="app.development_notes"/> </a>
-->
<html:link forward="development">
<bean:message key="app.development_notes"/>
</html:link> 
</html>
