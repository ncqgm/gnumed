<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>
 
  <bean:define id="identityId" name="healthRecord" property="healthSummary.identityId" />
    <%String contextPath=org.apache.struts.util.RequestUtils.serverURL(request)+
        request.getContextPath()+
        "/ClinicalEdit.do"+
        "?id="+identityId.toString();
        request.setAttribute("contextPath", contextPath); %>
    
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>

 
