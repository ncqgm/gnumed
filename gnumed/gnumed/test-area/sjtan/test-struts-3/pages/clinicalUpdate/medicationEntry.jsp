
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>



<bean:define id="medsPerPlan" value="<%=String.valueOf(org.gnumed.testweb1.data.DataObjectFactory.MEDS_PER_ITEM)%>" />
        <bean:define id="medIx" 
            value="<%=String.valueOf((Integer.parseInt(request.getAttribute("ix").toString()) * Integer.parseInt(medsPerPlan)))%>"
        />
<table width='60%'>      
     <logic-el:iterate id="medication"   
            name="clinicalUpdateForm" property="encounter.medications" 
            indexId="i" offset="${medIx}" length="${medsPerPlan}">
    <tr>        
    <td>
       <table border='1'>     
         <tr>
   <td>
        drug #<bean:write name="i"/>    
        
        
   </td>
   <td  >
           <html-el:hidden styleId="drugDB_origin${i}" 
                    name="medication" property="DB_origin" indexed="true"/>
                    
           <html-el:hidden styleId="drugDB_drug_id${i}"
                    name="medication" property="DB_drug_id" indexed="true"/>
                                                  
            name :
         
            <html-el:text styleId="brandName${i}" name="medication" 
                    property="brandName" indexed="true" />
           
   </td>
    <td>
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
   <td  >
             form:
             <html-el:text name="medication" property="form" 
                                styleId="formulation${i}" indexed="true" size="5"/>
   </td>
     <td>
             dose:
             <html:text name="medication" property="dose"  indexed="true" size="4"/>
   </td>
   <td>
   
           unit:
           <html-el:text name="medication" property="amountUnit"  
                            styleId="amountUnit${i}" indexed="true" size="4" readonly="true" />
    </td>
 
   <td>
            freq:
            <html:text name="medication" property="periodString"  indexed="true" size="8"/>
   			prn
  			 <html:checkbox name="medication" property="PRN"  indexed="true" />
  	 </td>
   </tr>
   <tr >
   <td    colspan='4'  >
    generic:        
            <html-el:text  styleId="genericName${i}" name="medication" 
                    property="genericName" indexed="true"  readonly="true" size="50"/>
   </td>
   <td colspan='5'>
         presentation:
             <html-el:text name="medication" property="presentation"  styleId="presentation${i}" indexed="true" size='50'  />
   </td>
   </tr>
   <tr  >
   <td    colspan='3' >
             direction:
             <html:text name="medication" property="directions"  indexed="true" size='40'  />
   </td>
   <td>
        qty
        <html-el:text name="medication" property="qty" styleId="qty${i}" indexed="true" size='3'/>
   </td>
  <td>
        rpts
        <html-el:text name="medication" property="repeats" styleId="repeats${i}" indexed="true" size='3'/>
   </td >     
   <td colspan='2'>atc code:
    <html-el:text name="medication" property="ATC_code" styleId="ATC_code${i}" indexed="true" size='8' readonly='true'/>
   </td>
   </tr>
   </table>
   </td>
   </tr>
   
    </logic-el:iterate>
</table>
    