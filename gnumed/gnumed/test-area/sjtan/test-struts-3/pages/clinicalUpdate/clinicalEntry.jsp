<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
 
 
<html:base/>   
    <html:form action="/SaveClinical"  > 
  <a name='submitEncounter' />
    <html:link page="./encounterEpisodeBased.jsp">test 2</html:link>
    <jsp:include page="./encounter_2.jsp"/> 
    
        <jsp:include page="./vaccinationEntry.jsp"/>
   
    </html:form>
 

