<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<html>
<html>
<head><title>Clin Entry</title></head>
<body>
<html:base/>   
    <html:form action="/SaveClinical"> 
  <a name='submitEncounter' />
    <div id="submitEncounter" style="display:block" />
        <table >
            <tr>
            <td>
                <html:submit altKey="change.clinical" ><bean:message key="change.clinical"/></html:submit>
            </td>
            <td>
                <html:reset altKey="reset" />
            </td>
            </tr>
        </table>
    </div>
    <table>
    <tr valign='top'>
        <td >
    <jsp:include page="./encounter_2.jsp"/> 
        </td>
    <tr>
        <td>
        <jsp:include page="./vaccinationEntry.jsp"/>
        </td>
    </tr>
    </table>
    </html:form>

</body>
</html>

