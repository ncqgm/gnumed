<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix='html-el'%>
 <html>
<head><title>JSP Page</title></head>
<body>
 
<b><bean:message key="vitals"/></b> 
        <table width='100%' border='1'><tr> 
        <td colspan='2'>BP <html:text name="clinicalUpdateForm" property="encounter.vitals.systolic" size="3" maxlength="4"/>
        / <html:text name="clinicalUpdateForm" property="encounter.vitals.diastolic" size="2"  maxlength="4"/> mmHg
        </td><td>PR <html:text name="clinicalUpdateForm" property="encounter.vitals.pr" size="3"  maxlength="4"/>bpm
        </td>
        <td>rhythm <html:text name="clinicalUpdateForm" property="encounter.vitals.rhytm" size="12" maxlength="8"/>
        </td> 
        <td>T <html:text name="clinicalUpdateForm" property="encounter.vitals.temp" size="3" maxlength="4"/>c
        </td>
        <td>RR <html:text name="clinicalUpdateForm" property="encounter.vitals.rr" size="2" maxlength="4"/>kg
        </td> 
        </tr>
        <tr>
        <td>ht <html:text name="clinicalUpdateForm" property="encounter.vitals.height" size="4"/>m
        </td>
        <td>wt <html:text name="clinicalUpdateForm" property="encounter.vitals.height" size="4"/>kg
        </td>
         
        <td>PEFR pre <html:text name="clinicalUpdateForm" property="encounter.vitals.prepefr" size="4"/>
        </td>
        <td>PEFR post <html:text name="clinicalUpdateForm" property="encounter.vitals.postpefr" size="4"/>
        </td>
        </tr></table>
        
</body>
</html>
