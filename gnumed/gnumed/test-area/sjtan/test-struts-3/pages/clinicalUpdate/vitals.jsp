
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix="html-el"%>
 <html>
<head><title>JSP Page</title></head>
<body>
 
<b><bean:message key="vitals"/></b> 
        <table width='100%' border='1'><tr> 
        <td colspan='2'>BP <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].systolic" size="3" maxlength="4"/>
        / <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].diastolic" size="2"  maxlength="4"/> mmHg
        </td><td>PR <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].pr" size="3"  maxlength="4"/>bpm
        </td>
        <td>rhythm <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].rhythm" size="12" maxlength="8"/>
        </td> 
        <td>T <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].temp" size="3" maxlength="4"/>c
        </td>
        <td>RR <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].rr" size="2" maxlength="4"/>bpm
        </td> 
        </tr>
        <tr>
        <td>ht <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].heightString" size="4"/>m
        </td>
        <td>wt <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].weightString" size="4"/>kg
        </td>
         
        <td>PEFR pre <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].prepefr" size="4"/>
        </td>
        <td>PEFR post <html-el:text name="clinicalUpdateForm" property="encounter.vital[${ix}].postpefr" size="4"/>
        </td>
        </tr></table>
        
</body>
</html>
