<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix="html-el"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<html>
<head><title>List Identities</title></head>
<body>
    <html:base/>
    <div class='errors'>
        <p><b>
        <html:errors/></b></p>
    </div>

 <p>
   
    <logic:present name="demographicDetails" scope="session">
   <!--  
    <b> Got a details of size  <bean:write name="demographicDetails" /> </b>
    -->
    <table>
    <logic:iterate  id="detail" name="demographicDetails" >
   <tr>
   
   <!--
     <td><html:link action="/ClinicalEdit" paramId="id" paramName="detail" paramProperty="id">
        <bean:message key="clinical.edit"/>
    </html:link>
    
    </td>
    -->
    <td>
    <html-el:link  
        href="javascript: void('');" 
        onclick="
            var id=${detail.id};
            var popup=open('/gnumed-test-war/ClinicalEdit.do?id='+id,
            '', 'width=900, height=800, scrollbars=yes');
            popup.moveTo(50,50);
            "
            >
        <bean:message key="clinical.edit"/>
   
    </html-el:link>
    
    </td>
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
    </logic:iterate>
    </table>
    
    </logic:present>
</p>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

</body>
</html>
