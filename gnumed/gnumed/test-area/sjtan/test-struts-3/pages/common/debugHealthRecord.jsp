<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>

<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>

<%@taglib uri="http://struts.apache.org/tags-html-el" prefix="html-el"%>

<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<html:base/>
    
       
       
<html>
<head><title>JSP Page</title></head>
<body>

<logic:iterate name="healthRecord" id="encounter" property="healthSummary.encounters"
 indexId="ienc" >
 <p>
   <bean:write name="encounter" property="started" format="dd/MM/yyyy hh:mm" />
             </b>   ,
                    <bean:write name="encounter" property="description" />
 </p>
 <logic:iterate name="encounter" property="narratives" id="narrative">
 <p>
      <%=encounter%>

    <bean:write name="narrative" property="narrative"/>
 </p>
 </logic:iterate>
</logic:iterate>
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

</body>
</html>
