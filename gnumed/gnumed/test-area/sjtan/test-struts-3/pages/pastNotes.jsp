<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>

<html>
<head><title>JSP Page</title></head>
<body>

<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
<a href='<%=request.getAttribute("contextPath")%>#clinicalSummary'>Back To Summary </a>
<a name='pastNotes' >
     <h2>Past Notes</h2>
     </a>
    <table border='1'>
    <logic:iterate id="encounter"
                name="healthRecord"
            property="healthSummary.encounters"
              >
    <tr>
    <td>
    <h4>
    <bean:write name="encounter" property="started" format="dd/mm/yyyy hh:mm"/>
    </h4>
    </td>
    <td>
    <h5>
    <bean:write name="encounter" property="description" />
    </h5>
    </td></tr>
        <tr>
        <td colspan='2'>
        <table>
        <logic:iterate id="narrative" name="encounter" property="narratives"
                    indexId="index">
        <tr>
        <td>
        
                <bean:define    id="itemId"
                        name="narrative" property="id"/> 
     
                <a name="itemDetail<%=itemId%>">
                
        <bean:write name="narrative" property="clin_when" format="dd/M/yyyy hh:mm:ss" />
        </a>
        </td>
       
            <td>
                <bean:write name="narrative" property="episode.description"/>
            </td>   
        </tr>
        <tr>
        
        <td>
        <b>
        <bean:write name="narrative" property="soapCat"/>
        </b>
        </td>
        
        <td> 
        <bean:write name="narrative" property="narrative"/>
        </td>
        </tr>
        </logic:iterate>
        </table>
    </tr>
    </logic:iterate>
    </table>
</body>
</html>
