
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix='html-el'%>
<%--  See vaccination regarding indexed properties for <logic:iterate>
 1. need a indexed getter method on the bean.  2. the id attribute of logic:iterate must
be the name of the property targetted by the getter
e.g. getNarrative(index) ...  id='narrative'
--%>
<%--
<jsp:include page="./createContextPath.jsp"/>
    --%>
<h3> <bean:message key="encounter.entry.title"/> </h3>
    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
    <html:base/>
    <div class="errors">
        <html:errors/>
        
    </div>
    
    <a name="encounterTop"/>
    
    <jsp:include page="./patient_detail_block.jsp"/>
    
    
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
                    <logic:iterate id="encounterType" type="org.apache.commons.beanutils.BasicDynaBean" name="healthRecord" property="healthSummary.encounterTypes">
                    <option value='<%=encounterType.get("pk")%>' > <%=encounterType.get("description")%> </option>
                    </logic:iterate>
                </html:select>
            </td>
             
            </tr>
            
        </table>
        
        <table border='1' id='allNarrativeInput'>
        
        <logic:iterate id="narrative" name="clinicalUpdateForm" 
        property="encounter.narratives"   
         scope="request" indexId="index">
         <tr>
         <td>
          <a name='linkNarrative<%=index%>'> </a>
           <%=index.intValue()+1%>
         </td>
        <td>
           
            <table id='narrativeEntry<%=index%>' >
                <tr>
                
                <td  >
                 <logic:greaterThan name="index" value="0">
                    link
                    
                    <html-el:checkbox  name="narrative" property="linkedToPreviousEpisode" indexed="true" 
                     onchange="if (this.checked) { 
                            document.getElementById('healthIssueInput${index}').style.display='none';
                            
                            document.getElementById('clinNarrative${index}').style.display='block';
                            document.getElementById('episodeEntry${index}').style.display='none';
                            
                        
                            } else {
                                document.getElementById('healthIssueInput${index}').style.display='block';
                                document.getElementById('episodeEntry${index}').style.display='block';
                            
                            }
                           return true;
                          "/>
                 </logic:greaterThan>
                </td>
                <td>
                
                <table id='healthIssueInput<%=index%>' >
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
                
                  
                <html:select name="narrative" property="episode.healthIssue.description" indexed="true"
onchange=""  
>
                      <html:option key="" value="">no issue selected</html:option>
                      <html:optionsCollection name="healthRecord" property="healthSummary.healthIssues" label="description"  value="description" />
                      
                    </html:select>
                
                </div>
                
                
                <div id="txtNewHealthIssue<%=index%>" style="display:none" >
                    
                               :
                                <html:text name="narrative" property="newHealthIssueName" indexed="true"/>
                        
                
                </div>
                
                </td>
                </tr>
                <tr>
                </tr>
                </table>
                 
                 </td>
                <td>
                show 
                <input type='checkbox'  name="showNarrative<%=index%>" value='' 
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
             
                <table > 
                
                        <tr>
                        <td colspan='3' id='episodeEntry<%=index%>'> <bean:message key="main.complaint" />
                           <html:text  name="narrative" property="episode.description" indexed="true" size="40"  />
                        
                        </td>
                     </tr>  
                    <tr>
                        <td>
                            <bean:message key="narrative.notes" />
                        </td>
                        <td>
                            <bean:message key="narrative.soap"/>
                            <html-el:select styleId="soapCat${index}" name="narrative" property="soapCat" indexed="true" 
                                onchange="if ( this.value =='o' ) {
                                            document.getElementById('vitals${index}').style.display='block'; 
                                        } else
                                        {
                                            document.getElementById('vitals${index}').style.display='none'; 
                                        }" >
                            <html:option key="s" value="s" >S</html:option>
                             <html:option key="o" value="o">O</html:option>
                            <html:option key="a" value="a">A</html:option>
                            <html:option key="p" value="p">P</html:option>
                     
                            </html-el:select>
                        </td>
                         <td >
                         <bean:message key="narrative.clin_when" />
                         <html:text name="narrative" property="clinWhenString" size="30" indexed="true"/>       
                         </td>
                        <td> <bean:message key="rfe"/> <html:radio name="narrative" property="rfe" indexed="true" value="false" />
                        </td> 
                        <td><bean:message key="aoe"/> <html:radio name="narrative" property="aoe" indexed="true" value="false"/>
                        </td>
                        
                    </tr>
                    <tr>
                    
                    <td  >
                     <bean:message key="allergy"/> 
                    <html-el:checkbox styleId="isAllergy${index}" 
                    name="clinicalUpdateForm" property="allergy[${index}]"     
                    onchange="if (this.checked) {
                        document.getElementById('allergyInput${index}').style.display='block'; 
                         
                    } else {  
                        document.getElementById('allergyInput${index}').style.display='none'; 
                    }"  />
                    </td>
                    <td colspan='4' >
                    <div  id="allergyInput<%=index%>" style='display: none'>
                        <bean:message key="allergy.definite"/>
                        <html-el:checkbox name="clinicalUpdateForm" property="allergyEntry[${index}].definite"
                                 />
                                 
                           <bean:message key="allergy.substance"/>
                          <html-el:text name="clinicalUpdateForm" property="allergyEntry[${index}].substance"
                                 />
                           
                        
                    </div>
                    </td>
                    </tr>
                     <tr>
                     <td colspan='6'>
                     <div id="vitals<%=index%>" style='display: none'>
                        
                             
                     
                                <jsp:include page="./vitals.jsp"/>
                     </div>
                     
                    </td>     
                     </tr>
                     
                    <tr>
                    <td COLSPAN='6'>
                        <html-el:textarea  name="narrative" property="narrative"  rows="6" cols="80" indexed="true"
                        onmouseover="if ( document.getElementById('soapCat${index}').value =='o' ) {
                                            document.getElementById('vitals${index}').style.display='block'; 
                                        } else
                                        {
                                            document.getElementById('vitals${index}').style.display='none'; 
                                        }" />
                    
                    </td>
                    
                    <td><sub>
                   <html:link anchor='submitEncounter' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
        paramProperty="patientId" > to submit </html:link>
                   <%--
                    <a href='<%=request.getAttribute("contextPath")%>#submitEncounter'>
                     to submit
                     
                    </a>
                    --%>
                    <%--
                    <logic:redirect anchor="submitEncounter" page="encounter.jsp" >
                    to submit
                    </logic:redirect>
                  --%>
                    </sub></td>
                   
                        </tr>
                </table>
            </div>
                    
            </td>
            </tr>
        </logic:iterate>
        </table>
        <%--
        <table >
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
