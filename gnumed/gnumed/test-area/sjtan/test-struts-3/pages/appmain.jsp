<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>

<html>
<head><title>JSP Page</title></head>
<body>

    <html:base/>
    <div class='errors'>
        <p><b>
        <html:errors/></b></p>
    </div>

    <br></br>

    <html:link action="/GetDemoEntry"> <bean:message key="new.patient"></bean:message></html:link>
    |
    <html:link action="/GetLogin"> <bean:message key="app.login"></bean:message></html:link>
    |
    <html:link action="/GetLogin"> <bean:message key="app.login"></bean:message></html:link>

    <p>

    <jsp:include page="./findIdentity.jsp" />
    </p>

    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
   
   
</body>

</html>
