<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<html>
<head><title>JSP Page</title></head>
<html:base/>
<html:xhtml/>

<body>

<div class='errors' >
<p>
<html:errors/>
</p>
</div>

<%-- A Common error, is to put a /> and close off the element form --%>
<html:form action="/Login" focus="username" onsubmit="return validateLoginForm(this);" >
<h4>                                                         
<bean:message key="login.prompt"/>
</h4>

<b>
<bean:message key="login.username"/> :
</b>
    <p>
        <html:text property="username" size="16" maxlength="32" />
    </p>
<b>
<bean:message key="login.password"/> :
</b>
<p>
    <html:password property="password" size="16" maxlength="32"/>
</p>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
<html:submit value="Submit" />
<html:reset />
</html:form>
</body>

<html:javascript formName="loginForm" scriptLanguage="javascript"
   dynamicJavascript="true" staticJavascript="false"/>

<script language='javascript1.1' src="./staticJavascript.jsp" />

</html>
