<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>

<%@ taglib uri="/tags/struts-html" prefix="html" %>

<html>
<html:base/>
<head><title>JSP Page</title>
<LINK   TYPE='text/css'  REL='stylesheet' href='style.css'/>     
</head>

<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

<tiles:insert name="content"/>
<jsp:include page="./intraLinksClinicalEdit.jsp"/>
</body>
</html>
