<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>


<html>
<head><title>Print Record</title></head>
<body>

<b><bean:message key="patient.details"/></b>
<jsp:include page="./patient_detail_block.jsp"/>
<jsp:include page="./clinSummary.jsp"/>
<jsp:include page="./pastNotes.jsp"/>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

</body>
</html>
