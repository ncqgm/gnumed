<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix="html-el"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-logic-el" prefix="logic-el"%>
<html:base/>
<html>
    <head><title>JSP Page</title></head>
    <body>
     
        <a name='pastNotes' >
        <h2>Past Notes</h2>
        </a>
            <logic:iterate id="encounter"
            name="healthRecord"
            property="healthSummary.encounters"
            
            >
            
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
            <b>
            <bean:define id="lastHealthIssueName" value="" type="java.lang.String"/>
            <bean:define id="lastEpisodeName" value=""  type="java.lang.String"/>
            <table>
            <logic:iterate id="narrative" 
                name="encounter" property="narratives"
                indexId="index">
                <div class='pastNotesNarrative<%=Integer.toString(index.intValue() % 2 )%>'>
                    <table style='pastNotesNarrative<%=Integer.toString(index.intValue() % 2 )%>' >
        
                        <tr>
                                
                             <bean:define    id="itemId"
                                name="narrative" property="id"/> 
                                <td  colspan='5' >
                                                            
                                <a name="itemDetail<%=itemId%>"/>
                                
                                <logic:notEqual name="narrative" property="episode.healthIssue.description" value="<%=lastHealthIssueName%>">
                                
                                    <b>
                                    <i>issue:</>
                                    <bean:write  name="narrative" property="episode.healthIssue.description" />
                                    </b>
                                <bean:define id="lastHealthIssueName" name="narrative" property="episode.healthIssue.description" type="java.lang.String"/>
                                </logic:notEqual>
                                 
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
        
                        <td>
                            <b>
                            <bean:write name="narrative" property="soapCat"/>
                            </b>
                        </td>
        
                        <td colspan='5'   align='left'> 
                            <bean:write name="narrative" property="narrative"  />
                        </td>
                        
                        </tr>
                    </table>
                </div>
            </logic:iterate>
                       
                <hr>
            </logic:iterate>
            
        <a name='lastEntry'/>
     
    </body>
</html>
