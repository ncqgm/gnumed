
<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>
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
        sel = document.getElementById("selectHI" + new String(index))
        txt = document.getElementById("txtNewHI" + new String(index))
        txt2 = document.getElementById("txtNewHIStart" + new String(index))
        if (checkbox.checked)  {
        sel.value=''
        sel.selectedIndex=0
        sel.disabled = true
        txt.disabled = false
        txt2.disabled = false
        } else {
            
        sel.disabled = false
        txt.disabled= true
        txt2.disabled = true
        }
        
     
        }
      
    </script>
   
     <!-- working script in mozilla for display/hide of elements example
      
       
    function changeHealthIssueEntry( checkbox, index) {
         var select = "selectHealthIssue" + new String(index)
        var textNewIssue = "txtNewHealthIssue"+ new String(index)
          if (checkbox.checked)  {   
            document.getElementById(select).style.display='none';
            document.getElementById(select).value='';
            document.getElementById(select).selectedIndex='0';
             
            document.getElementById(textNewIssue).style.display='block'; 
            } else {
             document.getElementById(select).style.display='block'; 
               document.getElementById(textNewIssue).style.display='none';
			
        }
        
     
      }
    -->
   
   <!--
       <script language='text/javascript'>
      function changeHealthIssueEntry( checkbox, index) {
        var select = "selectHI" + new String(index)
        var textNewIssue = "txtNewHI"+ new String(index)
        if (checkbox.checked) 
        {   
             document.getElementById(select).disabled=true
             
              } else {
               document.getElementById(select).disabled=false
        }
		
       
      }

    </script>
    -->
  
    <!--
     var sel = document.getElementById(select);
     var txt = document.getElementById(textNewIssue);
       if (checkbox.checked) {
			txt.disabled=false;
		
			document.getElementById(select).value='';
			document.getElementById(select).selectedIndex=0;
			document.getElementById(select).disabled=true;
			
			
						
		} else {
			document.getElementById(select).disabled=false;
			txt.value = ''
			txt.disabled=true;
		}
     
    -->
<h3> <bean:message key="encounter.entry.title"/> </h3>
    <%-- <jsp:useBean id="beanInstanceName" scope="session" class="beanPackage.BeanClassName" /> --%>
    <%-- <jsp:getProperty name="beanInstanceName"  property="propertyName" /> --%>
    <html:base/>
    <div class="errors">
        <html:errors />
        
        <%--
        <jsp:include page="/pages/common/debugAttributes.jsp"/>
       	--%>
        
       	
        
        <%if (request.getAttribute(org.apache.struts.Globals.ERROR_KEY) !=null)
            out.println( request.getAttribute(org.apache.struts.Globals.ERROR_KEY) );%>
     </div>
   
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
                indexId="index"
                >
        
             
                <div id='links<%=index%>' style='display:<%=((index.intValue()==1 )? "block": "none")%>'>
                    link
                    <html-el:checkbox 
                    name="narrative" 
                    property="linkedToPreviousEpisode" 
                    indexed="true" 
                    styleId="linkBox${index}" 
                    onclick="showEntry(this, ${index});
                    if (this.checked) {
                    document.getElementById('checkIssue${index}').checked=0;
                    document.getElementById('entryIssue${index}').style.display='none';
                    }     
                          
                    "
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
                                        <html-el:select styleId="selectHI${index}" name="narrative" property="episode.healthIssue.description" indexed="true"
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
                                        <html-el:text styleId="txtNewHI${index}" disabled="true"  name="narrative" property="newHealthIssueName" indexed="true"/>
               							<html-el:text styleId="txtNewHIStart${index}" disabled="true" name="narrative" property="healthIssueStartString" indexed="true"/>
                                    </div>
               
               
                                </td> 
                                <td colspan='2' align=center id='episodeEntry<%=index%>'> <bean:message key="main.complaint" />
                                    <html-el:text  name="narrative" property="episode.description" indexed="true" size="40"  />
                                </td>
                            </tr>
                        </table>
                    </div>
                 
                    <table > 
                
                        <tr>
                            <td>
                                <bean:message key="narrative.notes" />
                                <bean:message key="narrative.soap"/>
                                <html-el:select styleId="soapCat${index}" name="narrative" property="soapCat" indexed="true" 
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
                                <html-el:textarea  name="narrative" property="narrative"  rows="6" cols="80" indexed="true"
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
       
 
<html:javascript formName="clinicalUpdateForm"
   dynamicJavascript="true" staticJavascript="false"/> 

