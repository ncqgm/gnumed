<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@ taglib uri="/tags/struts-bean" prefix="bean" %>
<%@ taglib uri="/tags/struts-html" prefix="html" %>
<%@ taglib uri="/tags/struts-logic" prefix="logic" %>
<html>
<body>

Country <%=java.util.Locale.getDefault().getDisplayCountry()%>
Languge <%=java.util.Locale.getDefault().getDisplayLanguage()%>

Variant <%=java.util.Locale.getDefault().getDisplayVariant()%>

Name <%=java.util.Locale.getDefault().getDisplayName()%>

<p>
Language code   :<%=java.util.Locale.getDefault().getLanguage()%>
Country code   :<%=java.util.Locale.getDefault().getCountry()%>
</p>
Hello.
</body>
</html>