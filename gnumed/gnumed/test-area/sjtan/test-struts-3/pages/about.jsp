<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-tiles" prefix="tiles"%>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>

<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<html>
<head><title>JSP Page</title></head>
<body>



Country <%=java.util.Locale.getDefault().getDisplayCountry()%>
Languge <%=java.util.Locale.getDefault().getDisplayLanguage()%>

Variant <%=java.util.Locale.getDefault().getDisplayVariant()%>

Name <%=java.util.Locale.getDefault().getDisplayName()%>

<b>
<bean:message key="about.stuff"/>
</b>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

</body>
</html>
