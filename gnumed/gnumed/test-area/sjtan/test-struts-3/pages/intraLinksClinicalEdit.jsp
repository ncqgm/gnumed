<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>

<%@taglib uri="http://jakarta.apache.org/struts/tags-html" prefix="html"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-logic" prefix="logic"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-nested" prefix="nested"%>
<%@taglib uri="http://jakarta.apache.org/struts/tags-html-el" prefix='html-el'%>

<html:link anchor='encounterTop' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
        paramProperty="patientId" > to encounter entry </html:link> |

 <html:link anchor='pastNotes' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
    paramProperty="patientId" >
    to past notes </html:link> |        
<html:link anchor='lastEntry' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
        paramProperty="patientId" > to past notes/last entry </html:link> |
       
    
    <html:link anchor='episodeList' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
    paramProperty="patientId" >
    to episode list </html:link>
    |
        
    <html:link anchor='episodeListLast' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
    paramProperty="patientId" >
   end of episode list</html:link>
   |
   <html:link anchor='submitEncounter' action='ClinicalEdit.do' paramId="id" paramName="clinicalUpdateForm"
    paramProperty="patientId" >
   to Submit</html:link>