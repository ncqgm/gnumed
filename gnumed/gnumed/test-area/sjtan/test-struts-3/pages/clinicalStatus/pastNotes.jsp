<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>

<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>

<%@taglib uri="http://struts.apache.org/tags-html-el" prefix="html-el"%>

<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<html:base/>
    
        <a name='pastNotes'>
        <h2>Past Notes</h2>
        </a>
       
        <table>
            <logic:iterate id="encounter"
            name="healthRecord"
            property="healthSummary.encounters"
            indexId="encounterIndex"
            
            >
            <%-- debugging --%>
           <%-- <bean:write name="encounter"/> --%>
            <%--  <bean:write name="encounter" property="narratives"/> --%>
            
            
            <bean:size id="nEpisodes" name="encounter" property="narratives"/>
            
            <%--
            # of episodes = <bean:write name="nEpisodes"/>
            --%>
             
            <logic:greaterThan name="nEpisodes" value="0" >
             
            <tr>
            <td>
              <b>
                    <bean:write name="encounter" property="started" format="dd/MM/yyyy hh:mm" />
             </b>   ,
                    <bean:write name="encounter" property="description" />
            <%--
            <small>   
                <html:link
                    anchor="encounterTop"
                    action="ClinicalEdit.do"
                    paramId="id"
                    paramName="clinicalUpdateForm"
                    paramProperty="patientId"
                    > entry top 
                </html:link>
            </small>
            --%>
           
           
            <bean:define id="lastHealthIssueName" value="" type="java.lang.String"/>
            <bean:define id="lastEpisodeName" value=""  type="java.lang.String"/>
        
            
            <table style='pastNotesNarrative<%=Integer.toString(encounterIndex.intValue() % 2 )%>' >
        <%--
           <%=encounter.toString()%>
           --%>
           
            <logic:iterate id="narrative" 
                name="encounter" property="narratives" 
                indexId="index">


            <%--       <%=narrative.toString()%> 
               implements comparable = <%=(new Boolean( narrative instanceof Comparable) )%>

               --%>
                        <div class='pastNotesNarrative<%=Integer.toString(index.intValue() % 2 )%>'>
                   
                       
                                
                             <bean:define    id="itemId"
                                name="narrative" property="id"/> 
                                 <td  colspan='5' >
                                                            
                                <a name="itemDetail<%=itemId%>"/>
                                
                              <logic:notEqual name="narrative" property="episode.healthIssue.description" value="<%=lastHealthIssueName%>">
                                
                                   <td>
                                    <b>
                                         <i>issue:</>
                                        <bean:write  name="narrative" property="episode.healthIssue.description" />
                                    </b>
                                         <bean:define id="lastHealthIssueName" name="narrative" property="episode.healthIssue.description" type="java.lang.String"/>
                                    <td>
                                </tr>
                             
                               </logic:notEqual>
                               
                                <%-- version = 0.1 , episode description existed.    
                                <logic:notEqual name="narrative" property="episode.description" value="<%=lastEpisodeName%>">
                                 
                                    <b>
                                    <i> /episode:</i>
                                    <bean:write name="narrative" property="episode.description" />
                                    </b>
                                <bean:define id="lastEpisodeName" name="narrative" property="episode.description" type="java.lang.String" />
                                   <logic:notPresent parameter="print">
                                        <i><sub> 
                                            <html-el:link
                                            anchor="linkItemDetail${itemId}"
                                            action="ClinicalEdit.do"
                                            paramId="id"
                                            paramName="clinicalUpdateForm"
                                            paramProperty="patientId"
                                            > to summary</html-el:link>
                                        </sub> </i> 
                                   </logic:notPresent>
                                     </td>
                                
                                </logic:notEqual>
                                 
                            </tr> 
                           
                        <tr>
                        --%>
                       <tr>
                        <td>
                            <b>
                            <bean:write name="narrative" property="soapCat"/>
                            </b>
                        </td>
                                
                        <td colspan='5'   align='left'> 
                            <bean:write name="narrative" property="narrative"  />
                        </td>
                       
                        </tr>
                   
                </div>
                
            </logic:iterate>
                </table>
            </td>
            </tr> 
            
          
            </logic:greaterThan>

            </logic:iterate>

        </table>
          
        <a name='lastEntry'/>
    