<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
 
 
<html:base/>   
    <html:form action="/SaveClinical" > 
  <a name='submitEncounter' />
   
    <jsp:include page="./encounter_2.jsp"/> 
    
        <jsp:include page="./vaccinationEntry.jsp"/>
   
    </html:form>
 

