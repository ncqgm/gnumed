
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>

<%--  See vaccination regarding indexed properties for <logic:iterate>
 1. need a indexed getter method on the bean.  2. the id attribute of logic:iterate must
be the name of the property targetted by the getter
e.g. getNarrative(index) ...  id='narrative'
--%>
<html>
<head>
    <title>Encounter </title>
 
</head>
<body>
<h3> <bean:message key="encounter.entry.title"/> </h3>
    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
    <html:base/>
    <div class="errors">
        <html:errors/>
        
    </div>
    
    
    
    <jsp:include page="./patient_detail_block.jsp"/>
    
    
    <div id="testdiv" class="testdiv0" style='visibility:hidden;'>
    <h2>THis should be hidden </h2>
    </div>
    <%--
    <html:form action="/SaveClinical">
--%>
        <table>
            
           
            <tr>
            <td>
                <bean:message key="current.encounter"/>
            </td>
            
            <td>
                <bean:message key="encounter.time"/>
                <bean:write name="clinicalUpdateForm" property="encounter.started"/>
            </td>
            <td>
                <bean:message key="encounter.location"/>
                <html:select  name="clinicalUpdateForm" property="encounter.location" >
                    <html:option value="1">consulting room </html:option>
                    <html:option value="2">nursing home </html:option>
                </html:select>
            </td>
             
            </tr>
            
        </table>
        <h4><bean:message key="vitals"/></h4> 
        <table width='80%' border='1'><tr> 
        <td colspan='2'>BP <html:text name="clinicalUpdateForm" property="encounter.vitals.systolic" size="3" maxlength="4"/>
        / <html:text name="clinicalUpdateForm" property="encounter.vitals.diastolic" size="2"  maxlength="4"/> mmHg
        </td><td>PR <html:text name="clinicalUpdateForm" property="encounter.vitals.pr" size="3"  maxlength="4"/>bpm
        </td>
        <td>rhythm <html:text name="clinicalUpdateForm" property="encounter.vitals.rhytm" size="12" maxlength="8"/>
        </td></tr>
        <tr>
        <td>T <html:text name="clinicalUpdateForm" property="encounter.vitals.temp" size="3" maxlength="4"/>c
        </td>
        <td>RR <html:text name="clinicalUpdateForm" property="encounter.vitals.rr" size="2" maxlength="4"/>kg
        </td> 
        <td>ht <html:text name="clinicalUpdateForm" property="encounter.vitals.height" size="4"/>m
        </td>
        <td>wt <html:text name="clinicalUpdateForm" property="encounter.vitals.height" size="4"/>kg
        </td>
        </tr>
        <tr><td colspan='2'/>
        <td>PEFR pre <html:text name="clinicalUpdateForm" property="encounter.vitals.prepefr" size="4"/>
        </td>
        <td>PEFR post <html:text name="clinicalUpdateForm" property="encounter.vitals.postpefr" size="4"/>
        </td>
        </tr></table>
        
  
        <logic:iterate id="narrative" name="clinicalUpdateForm" 
        property="encounter.narratives"   
         scope="request" indexId="index">
            <a name='linkNarrative<%=index%>'> </a>
            Narrative <%=index%>
            <table>
                <tr>
                
                <td>
                    <bean:message key="health.issue"/>
                </td>
                
                <td> ( <bean:message key="new.health.issue"/>
                    <input type="checkbox" name="newHealthIssue<%=index%>" value=''
                onchange="if (this.checked) 
                            { 
                                document.getElementById('sel<%=index%>').value='';
                                document.getElementById('sel<%=index%>').selectedIndex='0';
                                document.getElementById('sel<%=index%>').style.display='none';
                                document.getElementById('txtNewHealthIssue<%=index%>').style.display='block';
                            } else {
                                document.getElementById('sel<%=index%>').style.display='block'; 
                                document.getElementById('txtNewHealthIssue<%=index%>').style.display='none';
                            }
                            return true;"
                 value='1' title='create health issue'/> ) </td>               
                <td>
                <div id="sel<%=index%>">
                
                  
                <html:select name="narrative" property="healthIssueName" indexed="true"  >
                      <html:option key="" value="">no issue selected</html:option>
                      <html:optionsCollection name="healthRecord" property="healthSummary.healthIssues" label="description"  value="description" />
                      
                    </html:select>
                
                </div>
                
                
                <div id="txtNewHealthIssue<%=index%>" style="display:none" >
                    
                               :
                                <html:text name="narrative" property="newHealthIssueName" indexed="true"/>
                        
                
                </div>
                
                </td>
                   
                
                <td>
                show 
                <input type='checkbox' name="showNarrative<%=index%>" value='' 
                    onchange="
                    if (this.checked) {
                        document.getElementById('clinNarrative<%=index%>').style.display='block'; 
                        return true; 
                    } else {  
                        document.getElementById('clinNarrative<%=index%>').style.display='none'; 
                        return true;
                    } "
                    />
                </td>
                    
                </tr>    
                
            </table>
                
            <div id='clinNarrative<%=index%>' style='display:<%=(String)((index.intValue() == 0)? "block":"none")%>'  >   
              
                <table> 
                        <tr>
                        <td colspan='3' > <bean:message key="main.complaint" />
                           <html:text  name="narrative" property="episode.description" indexed="true" size="40"  />
                        
                        </td>
                     </tr>  
                    <tr>
                        <td>
                            <bean:message key="narrative.notes" />
                        </td>
                        <td>
                            <html:select name="narrative" property="soapCat" indexed="true" >
                            <html:option key="s" value="s" >S</html:option>
                             <html:option key="o" value="o">O</html:option>
                            <html:option key="a" value="a">A</html:option>
                            <html:option key="p" value="p">P</html:option>
                     
                            </html:select>
                        </td>
                                
                        <td> <bean:message key="rfe"/> <html:radio name="narrative" property="rfe" indexed="true" value="false" />
                        </td> 
                        <td><bean:message key="aoe"/> <html:radio name="narrative" property="aoe" indexed="true" value="false"/>
                        </td>
                               
                    </tr>
                    <tr>
                    <td COLSPAN='5'>
                        <html:textarea  name="narrative" property="narrative"  rows="6" cols="80" indexed="true" />
                    
                    </td>
                    </tr>
                </table>
            </div>
                    
            
        </logic:iterate>
        <%--
        <table>
            <td>
                <html:submit altKey="change.clinical" ><bean:message key="change.clinical"/></html:submit>
            </td>
            <td>
                <html:reset altKey="reset" />
            </td>
            </tr>
        </table>

    </html:form>
--%>

<html:javascript formName="clinicalUpdateForm"
   dynamicJavascript="true" staticJavascript="false"/> 


</body>
</html>
