<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix="html-el"%>

 <html:base />

<html>
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
    <table >
        <tr>
            <td>
            <table width='50%'>
            <tr>
            <td  valign='top' > 
                <jsp:include page="/pages/clinicalEntry.jsp"/>
            </td>
        </tr>
            <tr>
                <td >
                    <jsp:include page="/pages/pastNotes.jsp"/> 
  
                </td>
            </tr>
        </table>   
       
        <td valign='top' width='40%'> 
            <jsp:include page="/pages/clinSummary.jsp"/> 
        </td>
        
        </tr>
    </table>
        
    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
      
       
</body>
 
</html>
