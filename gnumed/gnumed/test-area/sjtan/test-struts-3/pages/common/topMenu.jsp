<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>

<%@ taglib uri="/tags/struts-html" prefix="html" %>

<table width='100%'> 
    <tr>
        <td colspan='2'><h3><bean:message key="app.title"/></h3> </td>
    </tr>
    <tr>
        <td class='menu' colspan='2'>
            
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
    