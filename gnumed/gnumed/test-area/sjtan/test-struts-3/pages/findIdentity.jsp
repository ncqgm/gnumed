<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>

<html>
<head><title>JSP Page</title></head>
<body>

<h3>
    <b><bean:message key="demo.find.identity"/> </b>
</h3>

<html:form  action="/FindIdentity" onsubmit="return validateFindIdentity(this);">


<table>
<tr>
<td>
<b><bean:message key="demo.givenname"/> </b>:</td><td> <html:text property="givenname" size="20" maxlength="32" />
</td>

    <td> <b><bean:message key="demo.surname"/> </b>: </td>
        <td> <html:text property="surname" size="20" maxlength="32" />
        
   <td><b><bean:message key="demo.birthdate"/></b>: </td> 
   <td> <html:text property="birthdate" size="20" maxlength="32" />
</td></tr>
</table>



<html:submit altKey="find.identity" ><bean:message key="find.identity"/></html:submit>
<html:reset altKey="reset" />
</html:form>


   <jsp:include page="./listIdentities.jsp"/>
    
</body>
</html>

