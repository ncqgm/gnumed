<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>
<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>
<%@ taglib uri="http://struts.apache.org/tags-logic" prefix="logic" %>
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
<p>
	Session attribute names : <%=request.getSession().getAttributeNames()%>
	
<% java.util.Enumeration en =  request.getSession().getAttributeNames();
while (en.hasMoreElements()) {
    out.println("<br>");
    String name = (String) en.nextElement();
    out.println(name + " " + request.getSession().getAttribute(name));
    }
%>

<%--
<%java.util.Enumeration ensv =session.getServletContext().getAttributeNames();
	out.println("<p>ServletContext attribute names are:");
  while (ensv.hasMoreElements()) {
    out.println("<br>");
    String name = (String) ensv.nextElement();
    out.println(name + " " + session.getServletContext().getAttribute(name));
    }
%>

<% java.util.Enumeration eni = config.getInitParameterNames();
    out.println("config.initParameters are:");
    while (eni.hasMoreElements()) {
        String name = (String) eni.nextElement();
        out.println( name + " : " + config.getInitParameter(name));
        }
    %>
    --%>
    
    <br>
    Your user principal name is :  <%=request.getUserPrincipal().getName()%>
</p>
Hello

 <html:link forward="success"  />
 
</body>
</html>