<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>

<html>
<html:base/>


<head>
<title>Starting Page</title>
<LINK   TYPE='text/css'  REL='stylesheet' href='style.css'/>     
</head>
<body>

    <div class='errors'>
        <p><b>
        <html:errors/></b></p>
    </div>

    <br></br>

    <html:link action="/GetDemoEntry"> <bean:message key="new.patient"></bean:message></html:link>
    |
    <jsp:include page="./findIdentity.jsp" />
    </p>

    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
   
   
</body>

</html>
