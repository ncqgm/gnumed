<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>

<%@taglib uri="http://struts.apache.org/tags-html-el" prefix="html-el"%>
<html>
<head><title>JSP Page</title></head>
<body>


    <h5>Clinical Episode</h5>
  
        <a name="episodeList"/>
  
    <table border='1'>
        <logic:iterate   id="episode" 
            name="healthRecord" 
            property="healthSummary.clinEpisodes"
            indexId="index"
            >
	    <bean:size id="sizeItems" name="episode" property="rootItems"/>
	    <logic:greaterThan name="sizeItems" value="0">
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
 
                    <html-el:link anchor="itemDetail${itemId}"
                        action="ClinicalEdit.do" 
                        paramId="id" 
                        paramName="clinicalUpdateForm" paramProperty="patientId">
                    <%=(itemIndex.intValue() + 1)%>
                    </html-el:link>
             
                </nested:iterate>
            </td>
            </tr>
	    </logic:greaterThan>
        </logic:iterate>
    </table>
    <a name="episodeListLast"/>
</body>
</html>
