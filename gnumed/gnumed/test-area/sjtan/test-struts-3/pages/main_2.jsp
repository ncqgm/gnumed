<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>

<%@ taglib uri="/tags/struts-html" prefix="html" %>

<html>
<html:base/>
<head><title>JSP Page</title>

<LINK   TYPE="text/css" REL="stylesheet" href="./style.css" title="Style"/>    
 
</head>


    
<body>
<table width='100%'> 
    <tr>
        <td colspan='2'><h3><bean:message key="app.title"/></h3> </td>
    </tr>
    <tr>
    <td class='menu' colspan='2'>
        <html:link forward="loginLink">  <bean:message key="app.login"/>
                                    </html:link> |
        <html:link forward="aboutLink">  <bean:message key="app.about"/>
                                    </html:link> |
                              
        <html:link forward="adsLink"><bean:message key="app.ads"/></html:link> |
   <!-- 
        if use page instead of forward , will be from root of webapps path, and
        requires the current name of the webapp
  -->
    
    <html:link forward="dbtestLink"> <bean:message key="app.test.db"/></html:link> |
      <html:link action="/TestListNamesDisplay"> <bean:message key="app.list.context"/></html:link>
   
    </td>
     </tr>
     </table>
     <table width='100%'>
     <tr>
       <td   valign='top'> 
            <jsp:include page="/pages/clinicalEntry.jsp"/>
       </td> 
        
        <td valign='top' > 
       
            <jsp:include page="/pages/clinSummary.jsp"/> 
        </td>
   
  </tr>
  <tr >
  <td colspan='2' >
    <jsp:include page="/pages/pastNotes.jsp"/> 
  </td>
  </tr>
</table>

<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
      
       
</body>
 
</html>
