
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic-el" prefix="logic-el"%>
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
    
    


    <script language='javascript1.4'>

      function showEntry(checkbox, index) {
        var entry =document.getElementById("entryItem"+new String(index) );
        var linkBoxes = document.getElementById("links"  + new String(index+1) );
       if (checkbox.checked) {
                    entry.style.display='block';
                    if (linkBoxes != null) linkBoxes.style.display='block';
        } else {
                    entry.style.display='none';
                    if (linkBoxes != null) linkBoxes.style.display='none';
        }
      }
      
      

      function showEntryIssue(checkbox, index) {
        if (checkbox.checked) {
         document.getElementById("linkBox"+new String(index) ).checked = 0;
        document.getElementById("entryIssue"+new String(index) ).style.display='block';
        } else {
        document.getElementById("entryIssue"+new String(index)).style.display='none';
        }

      }

      function changeHealthIssueEntry( checkbox, index) {
        var select = "selectHealthIssue" + new String(index);
        var textNewIssue = "txtNewHealthIssue"+ new String(index);

        if (checkbox.checked) 
        {   
            document.getElementById(select).value='';
            document.getElementById(select).selectedIndex='0';
            document.getElementById(select).style.display='none';
            document.getElementById(textNewIssue).style.display='block';
            } else {
            document.getElementById(select).style.display='block'; 
            document.getElementById(textNewIssue).style.display='none';
        }
        return true;
      }

    </script>
     
<h3> <bean:message key="encounter.entry.title"/> </h3>
    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
    <html:base/>
    <div class="errors">
        <html:errors/>
        
    </div>
    
    <a name="encounterTop"/>
    
    <jsp:include page="./patient_detail_block.jsp"/>
    <%-- The Model used for this jsp are:
         healthRecord and clinicalUpdateForm as session level attribute objects.

         The Structure of healthRecord is 

         healthRecord
            healthSummary
                encounterTypes
                healthIssues   ...

         clinicalUpdateForm
            encounter
                started
                location
                *narratives
                    episode
                        healthIssue
            *allergyEntry
           
         clinicalUpdateForm is used to pass back the form data. Blank objects exist
         at relevant levels for filling in by the form.
         ( A issue is how to tell an unused blank object from one where some fields are allowed
         to be not filled in, the former not being used during database update. )
    --%>

             
    
        <bean:message key="current.encounter"/>


    <%-- EDITS THE ENCOUNTER TIME--%>

        <bean:message key="encounter.time"/>
        <br/>
        <bean:write name="clinicalUpdateForm" property="encounter.started"/>

    <%-- EDITS THE ENCOUNTER LOCATION: 
    use the information stored in healthRecord.healthSummary.encounterTypes list of
    apache DynaBean objects converted from a result set of selecting the encounter_type
    table.--%>

    
    
        <bean:message key="encounter.location"/>
        <html:select  name="clinicalUpdateForm" property="encounter.location" >
            <logic:iterate id="encounterType" type="org.apache.commons.beanutils.BasicDynaBean" name="healthRecord" property="healthSummary.encounterTypes">
                <option value='<%=encounterType.get("pk")%>' > <%=encounterType.get("description")%> </option>
            </logic:iterate>
        </html:select>
                 
             
        
        <div id='allNarrativeInput' >
        
        <%-- iterate through all the clinicalUpdateForm.encounter.narratives objects,
        each being called narrative 
        --%>
        <logic:iterate 
            id="narrative" 
            name="clinicalUpdateForm" 
            property="encounter.narratives"   
            scope="request" indexId="index"
            >
        
            <br>
             
            <div id='links<%=index%>' style='display:<%=((index.intValue()==1 )? "block": "none")%>'>
                link
                <html-el:checkbox styleId="linkBox${index}" name="narrative" property="linkedToPreviousEpisode" indexed="true" 
                onchange="showEntry(this, ${index});
                          if (this.checked) {
                                document.getElementById('checkIssue${index}').checked=0;
                                document.getElementById('entryIssue${index}').style.display='none';
                           }     
                          
                "
                value="0"
                />
                new episode
                <input type="checkbox"  id="checkIssue<%=index%>"
                onchange="showEntry(this, <%=index%>); showEntryIssue(this, <%=index%>);
                "
                value="0"
                />
            </div>   
           
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
                    <html:select name="narrative" property="episode.healthIssue.description" indexed="true"
                        onchange=""  
                        >

                        <html:option key="" value="">no issue selected</html:option>
                        <html:optionsCollection name="healthRecord" 
                        property="healthSummary.healthIssues" 
                        label="description"  value="description" />

                    </html:select>
                </div>   

                <div id="txtNewHealthIssue<%=index%>" 
                    style="display:none" >
                    <html:text name="narrative" property="newHealthIssueName" indexed="true"/>
                </div>
               
               
                   </td> 
                   <td colspan='2' align=center id='episodeEntry<%=index%>'> <bean:message key="main.complaint" />
                        <html:text  name="narrative" property="episode.description" indexed="true" size="40"  />
                   </td>
                </tr>
               </table>
              </div>
                 
                <table > 
                
                    <tr>
                   
                    <bean:message key="narrative.notes" />
                    <bean:message key="narrative.soap"/>
                    <html-el:select styleId="soapCat${index}" name="narrative" property="soapCat" indexed="true" 
                        onchange="if ( this.value =='o' ) {
                        document.getElementById('vitals${index}').style.display='block'; 
                        } else{
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
                    <td> 
                        <bean:message key="rfe"/> <html:radio name="narrative" property="rfe" indexed="true" value="false" />
                    </td> 
                    <td>
                        <bean:message key="aoe"/> <html:radio name="narrative" property="aoe" indexed="true" value="false"/>
                    </td>
                    </tr>
                    <tr>
                        <td  >
                            <bean:message key="allergy"/> 
                            <html-el:checkbox styleId="isAllergy${index}" 
                            name="clinicalUpdateForm" property="encounter.allergy[${index}].entered"     
                            onchange="if (this.checked) {
                            document.getElementById('allergyInput${index}').style.display='block'; 
                         
                            } else {  
                            document.getElementById('allergyInput${index}').style.display='none'; 
                            }"  />
                        </td>
                        <td  colspan='4' >
                            <div  id="allergyInput<%=index%>" style='display:none'>
                                <table><tr>
                                <td>
                                    <bean:message key="allergy.definite"/>
                                    <html-el:checkbox name="clinicalUpdateForm" property="allergy[${index}].definite"
                                    />
                                </td>  
                                <td>
                                    <bean:message key="allergy.substance"/>
                                    <html-el:text name="clinicalUpdateForm" property="allergy[${index}].substance"
                                    />
                               </td>
                               </tr></table>
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
                      
                    </sub></td>
                   
                    </tr>
                </table>
                
            </div>
         
            <%-- only show the linked checkbox if not the first entry --%>  
             
            <%-- This checkbox updates the narrative.linkedToPreviousEpisode property,
            narrative is actually a EntryClinNarrative object , and has presentation 
            related fields but its class is derived from ClinNarrativeImpl.
                
            if the linked checkbox is checked, then HIDE all the entry fields for 
            clinical issue and clinical episode description, because this item is 
            linked to the previous item's episode. 
            --%>
                
               
                     
            
        </logic:iterate>
        
        </div>
        <hr>
        
        
<html:javascript formName="clinicalUpdateForm"
   dynamicJavascript="true" staticJavascript="false"/> 
