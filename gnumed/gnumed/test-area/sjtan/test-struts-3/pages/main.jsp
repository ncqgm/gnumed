<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles"%>
<%@ taglib uri="/tags/struts-bean" prefix="bean" %>

<%@ taglib uri="/tags/struts-html" prefix="html" %>

<html>
<html:base/>
<head><title>JSP Page</title>
    <LINK   TYPE='text/css'  REL='stylesheet' href='style.css'/>     
</head>
<!--
<STYLE type="text/css" >
    h1,h2,h3 { background-color:#A47 }
        b   { color : #555}
       BODY { background-color: #AAA }
    </STYLE>
    -->

    
<body>
    <table width='100%'> 
     
        <tr>
            <td class='menu' colspan='2'>
                <jsp:include page="./topMenu.jsp"/>
            </td>
        </tr>
     
        <tr>
            <td width='85%'> 
                <tiles:insert name="content"/> 
            </td> 
        
            <td> 
                <tiles:insert name="support"/>
            </td>
   
        </tr>
        
    </table>

    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

</body>
</html>
