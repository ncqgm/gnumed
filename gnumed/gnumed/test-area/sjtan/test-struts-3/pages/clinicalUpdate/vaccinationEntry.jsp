
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>

<%-- DEVELOPMENT NOTE: HOWTO get vaccination update to work. 
    
    1.The ClinicalUpdateForm class
    must have a Vaccination getVaccination(int index)
    for struts to properly update a contained vaccination object.
    
    2. The id attribute of the logic:iterate tag must also be the property name 
        (vaccination for getVaccination(index) ).
    
    3. There may be a bug, put the form itself may need to have the getVaccination(int index)
method. 

    " Vaccination[] getVaccination(int index); "  will be usable as a readonly 
    method. So will " List getVaccination(int index); "
--%>

<h2> <bean:message key="vacc.entry.heading"/> </h2>
  
    <logic:present name="vaccines" scope="session">
        <b> Got to here </b>
        <%--
        <html:form action="/SaveClinical"  >    
         <html:text property="test"/> 
--%>
        <%-- <html:text property="vaccinations"/> --%>

            <table border='1'>
                <tr>
                <td>
                <bean:message key="vacc.entry.prompt"/>
                </td>
                </tr>
                
                <logic:iterate id="vaccination" name="clinicalUpdateForm" property="vaccinations">
           
                    <tr>
                    
                    
                    <td>
                        <bean:message key="vacc.date.given"/>
                        <html:text name="vaccination" property="dateGivenString" indexed="true" size="8"/>
                    </td>
                    <td>
                    <table>
                    <tr>
                    <td><b><bean:message key="vaccine"/> </b>:</td>
                    <td >
                   
                    <html:select name="vaccination" property="vaccineGiven" indexed="true"  >
                      <html:option key=" " value="0"/>
                      <html:optionsCollection name="vaccines" label="descriptiveName" value="id" />
                      
                    </html:select>
                    </td>
                    </tr>
                    <tr>
                    <td colspan='2'>
                        <bean:message key="vacc.batch.no"/>
                        <html:text name="vaccination" property="batchNo" indexed="true" size="6"/>
                    
                        <bean:message key="vacc.site.given"/>
                        <html:text name="vaccination" property="site" indexed="true" size="6"/>
                    </td>
                   </tr>
                    </table>
                    </td>
                    </tr>
                </logic:iterate>
            </table>     
        <%--
<html:submit altKey="change.clinical" ><bean:message key="change.clinical"/></html:submit>
            <html:reset altKey="reset" />
        </html:form>
   --%>  
    </logic:present>


<%--
<html:javascript formName="clinicalUpdateForm"
   dynamicJavascript="true" staticJavascript="false"/> 
--%>
<script  src="./staticJavascript.jsp"></script>

