<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean-el" prefix="bean-el"%>
<html>
<head>
    <title>Summary</title>

<body>
<a name="clinicalSummary" ></a>
    <h4>Summary</h4>  
  <jsp:include page="./patient_detail_block.jsp"/>   
  <jsp:include page="./relative_url_javascript.jsp"/>  
    <h5>Problem List</h5>
    <table border='1' cellpadding='2'e>
    <logic:iterate   id="healthIssue" 
            name="healthRecord" 
            property="healthSummary.healthIssues"
            indexId="index" >
            <bean:define id="tableCol" value="<%=Integer.toString(index.intValue() % 3) %>" />
            <logic:equal name="tableCol" value="0">
            <tr>
            </logic:equal>
            <td>
            <bean:write name="healthIssue" property="description" />
            </td>
           <logic:equal name="tableCol" value="2">
            </tr>
            </logic:equal>
            
    </logic:iterate>
    <logic:notEqual name='tableCol' value='2'>
    </tr>
    </logic:notEqual>
    
    </table>
     
    
    <h5>Allergies </h5>
     <table  border='1'>
  <%--   <thead><td><b>Substance</b></td> <td><b>is definite</b></td> <td> <b>description</b> </td> </thead>
    --%>
    <logic:iterate   id="allergy" 
            name="healthRecord" 
            property="healthSummary.allergys"
             >
            <tr>
            <td>
            <bean:write name="allergy" property="substance"/>
            </td>
            <td>
            <logic:equal name="allergy" property="definite" value="true">
            definite
            </logic:equal>
            <logic:equal name="allergy" property="definite" value="false">
            not definite
            </logic:equal>
             </td>
            <td>
            <small>
            <bean:write name="allergy" property="narrative" />
            </small>
            </td>
            </tr>
    </logic:iterate>
    </table>
    
    <h5>Vaccinations </h5>
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
    

    <h5>Clinical Episode</h5>
    <jsp:include page="./createContextPath.jsp"/>
      
 
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
                     <a name="linkItemDetail<%=itemId%>"/>    
                     <a href="<%=request.getAttribute("contextPath")%>#itemDetail<%=itemId%>">
                    <%=(itemIndex.intValue()+1)%> 
                </a> |
            </nested:iterate>
            </td>
            </tr>
    </logic:iterate>
    </table>
    
     
</body>
</html>
    