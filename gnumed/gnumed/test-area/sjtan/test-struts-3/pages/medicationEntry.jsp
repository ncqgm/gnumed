
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
<table width='60%'>      
     <logic-el:iterate id="med"  name="clinicalUpdateForm" property="medications" 
            indexId="i" offset="${medIx}" length="${medsPerPlan}">
    <tr>        
    <td>
       <table border='1'>     
         <tr>
   <td>
        drug #<bean:write name="i"/>    
        
        
   </td>
   <td>
           name :
             <html-el:text styleId="brandName${i}" name="med" 
                    property="brandName" indexed="true"/>
         
          <a href="javascript: void('');" 
onclick="

var prefix=document.getElementById('brandName<%=i%>').value;
var popup=open(
'<%=request.getRequestURL().toString().substring(0, request.getRequestURL().lastIndexOf("/")+1)%>SearchDrug.do?<%=org.gnumed.testweb1.global.Constants.Request.MEDICATION_ENTRY_INDEX%>=<%=i%>&amp;<%=org.gnumed.testweb1.global.Constants.Request.DRUG_NAME_PREFIX%>='
+prefix, '', 'width=600, height=400');
">find Drug </a>

<%--
          <html-el:link styleId="searchDrug${i}" action="/SearchDrug" name="med"  property="searchParams"
           onfocus="this.href=this.href.substr(0, this.href.lastIndexOf('=')+1) + document.getElementById('brandName${i}').value;"     
            >
       Find Drug</html-el:link>
--%>
   </td>
   <td>
             form:
             <html-el:text name="med" property="form" styleId="formulation${i}" indexed="true"/>
   </td>
   <td>
             dose:
             <html:text name="med" property="dose"  indexed="true"/>
   </td>
   </tr>
   <tr >
   <td    colspan='4'  >
             presentation:
             <html-el:text name="med" property="presentation"  styleId="presentation${i}" indexed="true" size='50'  />
   </td>
   </tr>
   <tr  >
   <td    colspan='2' >
             direction:
             <html:text name="med" property="directions"  indexed="true" size='40'  />
   </td>
   <td>
        qty
        <html-el:text name="med" property="qty" styleId="qty${i}" indexed="true" size='3'/>
        
        rpts
        <html-el:text name="med" property="repeats" styleId="repeats${i}" indexed="true" size='3'/>
   </td>     
   </tr>
   </table>
   </td>
   </tr>
   
    </logic-el:iterate>
</table>
    