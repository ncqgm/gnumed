<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>

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

   
</body>

</html>
