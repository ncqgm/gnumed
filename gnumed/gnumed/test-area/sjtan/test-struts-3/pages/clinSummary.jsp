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
<a name="clinicalSummary" ></a>
    <h2>Summary</h2>  
  <jsp:include page="./patient_detail_block.jsp"/>   
  <jsp:include page="./relative_url_javascript.jsp"/>  
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
    

    <h3>Clinical Episode</h3>
    
    <bean:define id="identityId" name="healthRecord" property="healthSummary.identityId" />
    <%String contextPath=org.apache.struts.util.RequestUtils.serverURL(request)+"/"
        +request.getContextPath()+"/"+"ClinicalEdit.do?id="+identityId.toString();
        request.setAttribute("contextPath", contextPath); %>
  
    <a   href="<%=request.getAttribute("contextPath")%>#pastNotes"> past notes </a>
         
    <table>
     <logic:iterate   id="episode" 
            name="healthRecord" 
            property="healthSummary.clinEpisodes"
            indexId="index"
            >
            <tr>
            <td>
             
            <bean:write name="episode" property="modified_when" format="dd/MM/yyyy hh:mm" />
            
            </td>
            <td><b>
            <bean:write name="episode" property="description" />
            </b>
            : issue is 
            <bean:write name="episode" property="healthIssue.description"/>
            </td>
            <td>
            <a name='#episodeSummary<%=index%>'/>
            items :
            <nested:iterate id="item" name="episode"
                property="rootItems"
                        
                        indexId="itemIndex"  >
                   <bean:define    id="itemId"
                        name="item" property="id"/> 
                         
                     <a href="<%=contextPath%>#itemDetail<%=itemId%>">
                    <%=(itemIndex.intValue()+1)%> 
                </a> |
            </nested:iterate>
            </td>
            </tr>
    </logic:iterate>
    </table>
    
     
</body>
</html>
    