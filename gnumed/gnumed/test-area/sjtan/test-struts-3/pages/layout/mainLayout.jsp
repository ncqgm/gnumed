<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-tiles" prefix="tiles"%>
<%@ taglib uri="http://struts.apache.org/tags-bean" prefix="bean" %>

<%@ taglib uri="http://struts.apache.org/tags-html" prefix="html" %>

<html>
<html:base/>
<head><title>JSP Page</title>
    
    <LINK   TYPE='text/css'  REL='stylesheet' href='../style.css'/>     
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
            <tiles:insert name="menu1"/> | 
            <tiles:insert name="menu2"/>
                
            </td>
        </tr>
     
        <tr>
            <td width='85%'> 
                <table>
                <tr>
                  <td>
                   <tiles:insert name="content"/>
                  </td>
                </tr>
                <tr>
                    <td>
                        <tiles:insert name="content2"/>
                    </td>
                </tr>
                  <tr>
                    <td>
                        <tiles:insert name="content3"/>
                    </td>
                </tr>
                </table>
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
