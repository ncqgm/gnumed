<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>

<%@ taglib uri="/tags/struts-html" prefix="html" %>
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
     <hr/>
    <jsp:include page="./intraLinksClinicalEdit.jsp"/> 
    <table width='100%'>
    <tr>
        <td valign='top'>
        <table >
        <tr valign='top'>
        <td valign='top'>
            <input type="button" value='entry'
                onclick='
                    var e = document.getElementById("clinicalEntry");
                    var p = document.getElementById("pastNotes");
                    e.style.display="block";
                    p.style.display="none";
                    '/>
                    |
            <input type="button" value='past notes'
                onclick='
                    var e = document.getElementById("clinicalEntry");
                    var p = document.getElementById("pastNotes");
                    e.style.display="none";
                    p.style.display="block";
                    '/>        
            </td>
           </tr> 
        
            <tr>
            <td  valign='top' > 
            <div id="clinicalEntry">
                <tiles:insert name="leftTop"/>
                
            </div>    
            <div id="pastNotes" style='display:none'>
                 <tiles:insert name="leftBottom"/>
            </div>
            </td>
        </tr>
            
        </table>   
       
        <td valign='top' width='40%'> 
        <table>
        <tr><td>
           <tiles:insert name="rightTop"/>
        </td></tr>
         <tr><td>
           <tiles:insert name="rightBottom"/>
        </td></tr>
        </table>
        </td>
        
        </tr>
    </table> 
      
       
</body>
 
</html>
