
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>
<html>
<head><title>JSP Page</title></head>
<body>
         <bean:define id="index" name="indexNarrative" scope="request" type="java.lang.Integer"/>
         
            <bean:define id="narrative" name="entryNarrative" scope="request"/>                   
<%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
<%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
                <%-- a numbered anchor id , for this item's entry --%>

          <div id="entryItem<%=index%>" 
                    style="display:<%=((index.intValue() ==0)?"block":"none")%>" 
                    >
            
            
        
                    <a name='linkNarrative<%=index%>'> </a>
                
                    <div id='entryIssue<%=index%>'>
                
               <%=index.intValue()+1%>
                
                        <table>
                            <tr>
                                <td>
                                    <bean:message key="health.issue"/>
                                </td>
                                <td>
                                    new
                                    <input type="checkbox" name="newHealthIssue<%=index%>" value=''
                                    onchange="changeHealthIssueEntry(this, <%=index%>);"
                                    />
                                </td>
                                <td>
                                    <div id="selectHealthIssue<%=index%>">
                                        <html-el:select styleId="selectHI${index}" name="narrative" property="episode.healthIssue.description" 
                                            onchange=""  
                                            >

                                            <html:option key="" value="">no issue selected</html:option>
                                            <html:optionsCollection name="healthRecord" 
                                            property="healthSummary.healthIssues" 
                                            label="description"  value="description" />

                                        </html-el:select>
                                    </div>   

                                    <div id="txtNewHealthIssue<%=index%>" 
                                        style="display:block" >
                                        <bean:message key="new.health.issue"/>
                                        <html-el:text styleId="txtNewHI${index}" disabled="true"  name="narrative" property="newHealthIssueName" />
               							<html-el:text styleId="txtNewHIStart${index}" disabled="true" name="narrative" property="healthIssueStartString" />
                                    </div>
               
               
                                </td> 
                                <td colspan='2' align=center id='episodeEntry<%=index%>'> <bean:message key="main.complaint" />
                                    <html-el:text  name="narrative" property="episode.description" size="40"  />
                                </td>
                            </tr>
                        </table>
                    </div>
                 
                    <table > 
                
                        <tr>
                            <td>
                                <bean:message key="narrative.notes" />
                                <bean:message key="narrative.soap"/>
                                <html-el:select styleId="soapCat${index}" name="narrative" property="soapCat" 
                                    onmouseout="if ( this.value =='o' ) {
                                    document.getElementById('vitals${index}').style.display='block'; 
                                    } else{
                                    document.getElementById('vitals${index}').style.display='none'; 
                                    }
                                    if ( this.value=='p') {
                                    document.getElementById('medications${index}').style.display='block';
                                    } else {
                                    document.getElementById('medications${index}').style.display='none';
                                    }
                                    "
                                    >
                                    <html:option key="s" value="s" >S</html:option>
                                    <html:option key="o" value="o">O</html:option>
                                    <html:option key="a" value="a">A</html:option>
                                    <html:option key="p" value="p">P</html:option>
                     
                                </html-el:select>
                            </td>
                            <td >
                                <bean:message key="narrative.clin_when" />
                                <html:text name="narrative" property="clinWhenString" size="30"/>       
                            </td>
                            <td> 
                                <bean:message key="rfe"/> <html:checkbox name="narrative" property="rfe"  value="false" />
                            </td> 
                            <td>
                                <bean:message key="aoe"/> <html:checkbox name="narrative" property="aoe"  value="false"/>
                            </td>
                        </tr>
                        <tr>
                            <td  >
                                <bean:message key="allergy"/> 
                                <html-el:checkbox styleId="isAllergy${index}" 
                                name="clinicalUpdateForm" property="encounter.allergy[${index}].marked" value="0"  
                            
                                onchange="if (this.checked) {
                                document.getElementById('allergyInput${index}').style.display='block'; 
                         
                                } else {  
                                document.getElementById('allergyInput${index}').style.display='none'; 
                                }"
                                onmouseover="
                                if (this.checked) {
                                document.getElementById('allergyInput${index}').style.display='block'; 
                         
                                } else {  
                                document.getElementById('allergyInput${index}').style.display='none'; 
                                }"
                                />
                            </td>
                            <td  colspan='4' >
                            
                                <div  id="allergyInput<%=index%>" 
                                    style='display:block' 
                                
                                    >
                                    <table><tr>
                                        <td>
                                            <bean:message key="allergy.definite"/>
                                            <html-el:checkbox name="clinicalUpdateForm" property="allergy[${index}].definite"
                                            />
                                        </td>  
                                        <td>
                                            <bean:message key="allergy.substance"/>
                                            <html-el:text name="clinicalUpdateForm" property="allergy[${index}].substance"
                                            onmouseover="if (document.getElementById('isAllergy${index}').checked)
                                            { document.getElementById('allergyInput${index}').style.display='block'; 
                         
                                            } else {  
                                            document.getElementById('allergyInput${index}').style.display='none'; 
                                            }" 
                                            />
                                        </td>
                                    </tr></table>
                                </div>
                            </td>
                        </tr>
                        <tr>
                            <td colspan='6'>
                                <div id="vitals<%=index%>" style='display: none'>
                                    <bean:define id="ix" value="<%=String.valueOf(index)%>"  toScope="request"/>
                                
                                    <jsp:include page="./vitals.jsp"/>
                                  
                                </div>
                            </td>     
                        </tr>
                     
                        <tr>
                            <td COLSPAN='6'>
                                <html-el:textarea  name="narrative" property="narrative"  rows="6" cols="80" 
                                onmouseover="if ( document.getElementById('soapCat${index}').value =='o' ) {
                                document.getElementById('vitals${index}').style.display='block'; 
                                } else
                                {
                                document.getElementById('vitals${index}').style.display='none'; 
                                }" />
                    
                            </td>
                        </tr>
                        <tr>
                            <td COLSPAN='6'>
                   
                                <div id="medications<%=index%>" style='display: none'>
                                
                                    <jsp:include page="./medicationEntry.jsp"/>
                                </div>
                            </td>
                        </tr>
                   
                    </table>
                    <sub>
                    <html:link anchor='submitEncounter' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
                    paramProperty="patientId" > to submit </html:link>
                     
                    <div id="submitEncounter" style="display:block" />
                        <table >
                            <tr>
                                <td>
                                    <html:submit altKey="change.clinical" ><bean:message key="change.clinical"/></html:submit>
                                </td>
                                <td>
                                    <html:reset altKey="reset" />
                                </td>
                            </tr>
                        </table>
                    </div>
                    </sub> 
                </div>
         
</body>
</html>
