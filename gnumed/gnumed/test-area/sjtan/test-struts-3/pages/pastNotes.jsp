<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix="html-el"%>
<html:base/>
<html>
    <head><title>JSP Page</title></head>
    <body>
    
      
        <a name='pastNotes' >
        <h2>Past Notes</h2>
        </a>
        <table border='1'>
            <logic:iterate id="encounter"
            name="healthRecord"
            property="healthSummary.encounters"
            
            >
            <tr>
            <td>
                <h4>
                    <bean:write name="encounter" property="started" format="dd/MM/yyyy hh:mm" />
                </h4>
            </td>
            <td>
                <h5>
                    <bean:write name="encounter" property="description" />
                </h5>
                     
            </td></tr>
            <tr>
            
            <td colspan='2'>
            <sub>   <html:link
                        anchor="encounterTop"
                            action="ClinicalEdit.do"
                            paramId="id"
                            paramName="clinicalUpdateForm"
                            paramProperty="patientId"
                            > entry top </html:link></sub>
            <logic:iterate id="narrative" name="encounter" property="narratives"
                indexId="index">
                <div class='pastNotesNarrative<%=Integer.toString(index.intValue() % 2 )%>'>
                <table style='pastNotesNarrative<%=Integer.toString(index.intValue() % 2 )%>' >
        
                <tr>
                    <td>
        
                        <bean:define    id="itemId"
                        name="narrative" property="id"/> 
     
                        <a name="itemDetail<%=itemId%>">
                
                        <bean:write name="narrative" property="clin_when" format="dd/MM/yyyy hh:mm" />
                        </a>
                    </td>
       
                    <td>
                        <b>
                        <i>episode:</i>
                        <bean:write name="narrative" property="episode.description"/>
                        </b>
                    </td>   
                    <td>
                        <b>
                        <i>issue:</>
                        <bean:write  name="narrative" property="episode.healthIssue.description" />
                        </b>
                    </td>    
                </tr>
                <tr>
        
                    <td>
                        <b>
                        <bean:write name="narrative" property="soapCat"/>
                        </b>
                        
                    </td>
        
                    <td colspan='2'> 
                        <bean:write name="narrative" property="narrative"/>
                          <i><sub> 
                          <%--
                    <a href='<%=request.getAttribute("contextPath")%>#linkItemDetail<%=itemId%>'>to summary</a>
                          --%>
                       
                        <html-el:link
                        anchor="linkItemDetail${itemId}"
                            action="ClinicalEdit.do"
                            paramId="id"
                            paramName="clinicalUpdateForm"
                            paramProperty="patientId"
                            > to summary</html-el:link>
                       
                            
                          </sub> </i> 
                    </td>
                </tr>
                </table>
                </div>
            </logic:iterate>
               
            
            </tr>
            </logic:iterate>
        </table>
        <a name='lastEntry'/>
    </body>
</html>
