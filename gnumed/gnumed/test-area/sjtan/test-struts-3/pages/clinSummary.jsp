<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>

<html>
<head>
    <title>Summary</title>

<body>
    <h2>Summary</h2>  
  
  <jsp:include page="./patient_detail_block.jsp"/>   
    
    <h3>Problem List</h3>
    <table>
    <logic:iterate   id="healthIssue" 
            name="healthRecord" 
            property="healthSummary.healthIssues"
             >
            <tr>
            <td>
            <bean:write name="healthIssue" property="description" />
            </td>
            </tr>
    </logic:iterate>
    </table>
    <h3>Clinical Episode</h3>
     <table>
    <logic:iterate   id="episode" 
            name="healthRecord" 
            property="healthSummary.clinEpisodes"
            >
            <tr>
            <td>
            <dt:format pattern="dd/mm/yy">
            <bean:write name="episode" property="modified_when" format="dd/mm/yyyy hh:mm" />
            </dt:format>
            </td>
            <td><b>
            <bean:write name="episode" property="description" />
            </b>
            : issue is 
            <bean:write name="episode" property="healthIssue.description"/>
            </td>
            </tr>
    </logic:iterate>
    </table>
    
    <h3>Allergies </h3>
     <table cellpadding='4' border='1'>
     <thead><td><b>Substance</b></td> <td><b>is definite</b></td> <td> <b>description</b> </td> </thead>
    <logic:iterate   id="allergy" 
            name="healthRecord" 
            property="healthSummary.allergys"
             >
            <tr>
            <td>
            <bean:write name="allergy" property="substance"/>
            </td>
            <td>
            <bean:write name="allergy" property="definite"/>
            </td>
            <td>
            <bean:write name="allergy" property="narrative" />
            </td>
            </tr>
    </logic:iterate>
    </table>
    
    <h3>Vaccinations </h3>
     <logic:present name="vaccines" scope="session">
    
    
    <table>
    <logic:iterate id="vaccination"
                name="healthRecord"
            property="healthSummary.vaccinations"
             >
    <tr>
    <td>
    <bean:write name="vaccination" property="dateGivenString"/>
    </td>
    <td>
    <bean:write name="vaccination" property="vaccine.tradeName" />
    </td>
    <td>
    <bean:write name="vaccination" property="site" />
    </td>
    <td>
    <bean:write name="vaccination" property="batchNo" />
    </td>
    
    </tr>
    
    </logic:iterate>    
    </table>
    
     </logic:present>
     
     <h2>Past Notes</h2>
     
    <table border='1'>
    <logic:iterate id="encounter"
                name="healthRecord"
            property="healthSummary.encounters"
              >
    <tr>
    <td>
    <h4>
    <bean:write name="encounter" property="started" format="dd/mm/yyyy hh:mm"/>
    </h4>
    </td>
    <td>
    <h5>
    <bean:write name="encounter" property="description" />
    </h5>
    </td></tr>
        <tr>
        <td colspan='2'>
        <table>
        
        <logic:iterate id="clin_narrative" name="encounter" property="narratives">
        <tr>
            <td>
                <bean:write name="clin_narrative" property="clin_when" format="dd/mm/yyyy hh:mm"/>
            </td>
            <td>
             <b>issue </b>
             <bean:write name="clin_narrative" property="episode.healthIssue.description"/>
            </td>
        </tr>
        <tr>
        <td> 
        <table><tr>
       
        <td>
        <b>
        
        <bean:write name="clin_narrative" property="soapCat"/>
        </b></td>
        </tr><tr><td>
            
                <bean:write name="clin_narrative" property="episode.description"/>
        
        </td></tr></table>    
        </td>
       
        
        <td> 
        <bean:write name="clin_narrative" property="narrative"/>
        </td>
        </tr>
        </logic:iterate>
        </table>
    </tr>
    </logic:iterate>
    </table>
</body>
</html>
    