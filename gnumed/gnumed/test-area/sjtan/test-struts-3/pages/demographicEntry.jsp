<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<html>
<html>
<head><title>JSP Page</title></head>
<body>

<html:base/>
<div class='errors'>
<p><b>
<html:errors/>
</b></p>
</div>


<%-- A Common error, is to put a /> and close off the element form --%>
<html:form action="/SaveDemographic" focus="title" onsubmit="validateDemographicForm(this);" >
<h4>    
<bean:message key="demo.prompt"/>  
<h5>
id : <html:text property="id" readonly="true" size="10"/>
</h5>
</h4>
<p>
<table><tr>
<td>
<b><bean:message key="demo.title"/> </b>:</td><td> <html:text property="title" size="8" maxlength="32" />
</td>
<td>
<b><bean:message key="demo.givenname"/> </b>:</td><td> <html:text property="givenname" size="20" maxlength="32" />
</td>
<td>
   <b><bean:message key="demo.surname"/> </b>: </td><td> <html:text property="surname" size="20" maxlength="32" />
</td></tr>


<tr>
   <td>
   <b><bean:message key="demo.sex"/> </b>:</td>
        <td> 
        <html:select property="sex"  size="2">
                <html:option value="m"><bean:message key="demo.sex.male"/></html:option>
                <html:option value="f"><bean:message key="demo.sex.female"/></html:option>
        </html:select>
   </td>
   <td>
    <b><bean:message key="demo.birthdate"/> </b>:</td><td> <html:text property="birthdate" size="12" maxlength="32" />
   </td>
</tr>

<tr>
  <td>  <b><bean:message key="demo.streetno"/> </b>:</td><td> <html:text property="streetno" size="12" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.street"/> </b>:</td><td> <html:text property="street" size="20" maxlength="32" /></td>
</tr>
<tr>
  <td>  <b><bean:message key="demo.urb"/> </b>:</td><td> <html:text property="urb" size="20" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.postcode"/> </b>: </td><td><html:text property="postcode" size="12" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.state"/> </b>:</td><td> <html:text property="state" size="10" maxlength="32" /> 
     <b><bean:message key="demo.countryCode"/> </b>:</td><td> <html:text property="countryCode" size="2" maxlength="2" /></td>

</tr>
 <tr>
  <td>  <b><bean:message key="demo.homePhone"/> </b>:</td><td> <html:text property="homePhone" size="12" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.workPhone"/> </b>:</td><td> <html:text property="workPhone" size="12" maxlength="32" /></td>
 </tr>
 <tr>
  <td > <b><bean:message key="demo.email"/> </b>:</td><td colspan="2"> <html:text property="email" size="32" maxlength="64" /></td>
  <td>  <b><bean:message key="demo.mobile"/> </b>:</td><td> <html:text property="mobile" size="16" maxlength="32" /></td>
</tr>
<tr> 
  <td>   <b><bean:message key="demo.publicHealthId"/> </b>:</td><td> <html:text property="publicHealthId" size="16" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.publicHealthIdExp"/> </b>:</td><td> <html:text property="publicHealthIdExp" size="8" maxlength="32" /></td>
  <td>  <b><bean:message key="demo.veteransId"/> </b>: </td><td><html:text property="veteransId" size="16" maxlength="32" /></td>
  </tr>         
 </table>
     
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
<html:submit value="Submit" />
<html:reset altKey="reset" />
</html:form>



</body>

<html:javascript formName="demographicForm"
   dynamicJavascript="true" staticJavascript="false"/> 

<script  src="./staticJavascript.jsp"></script>
</html>
