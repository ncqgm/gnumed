<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean-el" prefix="bean-el"%>
 <head><title>Search Drug</title>

    <LINK   TYPE="text/css" REL="stylesheet" href="./style.css" title="Style"/>    
 
</head> 
<body>
<h4>FIND A DRUG </H4>
Got to Search screen
 
<table>
<thead> <td>Generic Name</td> <td> BrandName</td><td>Description</td><td>Scheme</td><td>Qty</td><td>max Repeats</td>
</thead>

<script language='javascript1.4' >
    function setMedFields(selectIndex) {
       
    }
</script>


<logic:iterate id="drugRef" name="drugRefCandidates" indexId="index" >
    <tr>
        <td>
            <bean:write name="drugRef" property="ATC"/>
        </td>
        <td>
            <bean:write name="drugRef" property="brandName"/>
        </td>
        <td>
            <bean:write name="drugRef" property="description"/>
        </td>
        
        <td>
            <bean:write name="drugRef" property="scheme"/>
        </td>
        
        <td>
            
            <bean:write name="drugRef" property="subsidizedQuantity"/>
        </td>
        <td>
             <bean:write name="drugRef" property="subsidizedRepeats"/>
        </td>
        <td>
            <bean:define id="drugRef" toScope="request" name="drugRef" type="org.gnumed.testweb1.data.DrugRef"/>
            <a href="javascript:void('');" onclick='
            var i ="<%=session.getAttribute(org.gnumed.testweb1.global.Constants.Session.TARGET_MEDICATION_ENTRY_INDEX)%>";
            var brandName="<%=((org.gnumed.testweb1.data.DrugRef)request.getAttribute("drugRef")).getBrandName()%>";
            var description="<%=((org.gnumed.testweb1.data.DrugRef)request.getAttribute("drugRef")).getDescription()%>";
            var qty="<%=((org.gnumed.testweb1.data.DrugRef)request.getAttribute("drugRef")).getDefaultQuantity()%>";
            var repeats="<%=((org.gnumed.testweb1.data.DrugRef)request.getAttribute("drugRef")).getDefaultRepeats()%>";
            var formulation="<%=((org.gnumed.testweb1.data.DrugRef)request.getAttribute("drugRef")).getForm()%>";
            opener.document.getElementById("brandName"+i).value=brandName;
            opener.document.getElementById("presentation"+i).value=description;
            opener.document.getElementById("qty"+i).value=qty;
            opener.document.getElementById("repeats"+i).value=repeats;
             opener.document.getElementById("formulation"+i).value=formulation;
             window.close();
              '>   select  </a>
        </td>
            
     </tr>
</logic:iterate>
</table>        
        
        </body>