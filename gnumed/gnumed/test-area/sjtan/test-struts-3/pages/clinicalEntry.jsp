<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<html>
<html>
<head><title>Clin Entry</title></head>
<body>

<html:base/>
<div class='errors'>
<p><b>
<html:errors/>
</b></p>
</div>

 
    <html:form action="/SaveClinical"> 


            <jsp:include page="./encounter.jsp"/> 


            <jsp:include page="./vaccinationEntry.jsp"/>
 <%--
 --%>   
        <table>
            <td>
                <html:submit altKey="change.clinical" ><bean:message key="change.clinical"/></html:submit>
            </td>
            <td>
                <html:reset altKey="reset" />
            </td>
            </tr>
        </table>

    </html:form>

</body>
</html>
