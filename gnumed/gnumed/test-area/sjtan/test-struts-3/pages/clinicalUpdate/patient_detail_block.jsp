
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>

<html>
<head><title>JSP Page</title></head>
<body>
   
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
  <b>
  <u>
    <table>
        
        <tr>

        <td><b> <bean:write name="detail" property="id"/> </b> </td>
        <td colspan='4'>
            <html:link action="/DemographicEdit" paramId="id" paramName="detail" paramProperty="id">
                <bean:write name="detail" property="surname"/>, <bean:write name="detail" property="givenname" /> 
            </html:link>
        </td>
        <td colspan='2'> <bean:message key="demo.born"/> <bean:write name="detail" property="birthdate" />
        </td>
        <td colspan='8'> <bean:write name="detail" property="streetno"/>, 
            <bean:write name="detail" property="street"/>, <bean:write name="detail" property="urb"/>, 
            <bean:write name="detail" property="state"/>, <bean:write name="detail" property="postcode" />.
        </td>   
        <td>
            <bean:message key="demo.publicHealthId"/> :
            <bean:write name="detail" property="publicHealthId"/> 
            <bean:message key="demo.publicHealthIdExp"/> :
            <bean:write name="detail" property="publicHealthIdExp"/>
        </td>
        </tr>
    </table>
    </u>
    </b>
</body>
</html>
