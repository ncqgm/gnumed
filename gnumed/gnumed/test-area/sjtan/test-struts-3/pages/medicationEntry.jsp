
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean-el" prefix="bean-el"%>



<bean:define id="medsPerPlan" value="<%=String.valueOf(org.gnumed.testweb1.data.DataObjectFactory.MEDS_PER_ITEM)%>" />
        <bean:define id="medIx" 
            value="<%=String.valueOf((Integer.parseInt(request.getAttribute("ix").toString()) * Integer.parseInt(medsPerPlan)))%>"
        />
<table>      
     <logic-el:iterate id="med"  name="clinicalUpdateForm" property="medications" 
            indexId="i" offset="${medIx}" length="${medsPerPlan}">
         <tr>
   <td>
        drug #<bean:write name="i"/>    
   </td>
   <td>
        generic name :
             <html:text name="med" property="brandName" indexed="true"/>
   </td>
   <td>
             form:
             <html:text name="med" property="form"  indexed="true"/>
   </td>
   <td>
             dose:
             <html:text name="med" property="dose"  indexed="true"/>
   </td>
   </tr>
   <tr >
   <td    colspan='6'  >
             direction:
             <html:text name="med" property="directions"  indexed="true" size='50'  />
   </td>
   </tr>
   
   
    </logic-el:iterate>
</table>
    