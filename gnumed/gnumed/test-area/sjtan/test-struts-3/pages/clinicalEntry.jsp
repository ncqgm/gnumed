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
    
    <table>
    <tr valign='top'>
        <td >
    <jsp:include page="./encounter_2.jsp"/> 
        </td>
    </tr>    
    <tr>
        <td>
        <jsp:include page="./vaccinationEntry.jsp"/>
        </td>
    </tr>
    </table>
    </html:form>
 

