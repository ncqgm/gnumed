<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<html>
<head><title>JSP Page</title></head>
<body>

<%@taglib uri="http://struts.apache.org/tags-html" prefix="html"%>
<%@taglib uri="http://struts.apache.org/tags-bean" prefix="bean"%>
<%@taglib uri="http://struts.apache.org/tags-logic" prefix="logic"%>
<%@taglib uri="http://struts.apache.org/tags-logic-el" prefix="logic-el"%>
<%@taglib uri="http://struts.apache.org/tags-nested" prefix="nested"%>
<%@taglib uri="http://struts.apache.org/tags-html-el" prefix='html-el'%>
<%@taglib uri="http://struts.apache.org/tags-bean-el" prefix="bean-el"%>

<% String[] titles = new String[] {"episode 1", "episode 2", "episode 3" };
   java.util.List titleList = java.util.Arrays.asList(titles);
    session.setAttribute("titleList", titleList);%>
 
<!-- the last index used for clinical episodes -->   
<bean:define id="last" value="<%=Integer.toString(titleList.size()-1)%>"/>

<logic:iterate id="title" name="titleList" indexId="j">

<!-- if j > 0, then display else don't display the division -->
<div id='episodeDiv<%=j%>' 
    <logic:greaterThan name="j" value="0">
        style='display:none'
    </logic:greaterThan>

    <logic:equal name="j" value="0">
        style ='display:block'
    </logic:equal>
>

<h2>
    <bean:write name="title"  />
</h2>

notes
<textarea  id='notes' rows='10' cols='60' >
</textarea>

<!-- display a button to show next episode except for last indexed episode -->
<div id='addEpisodeDiv<%=j%>'
    <logic:lessThan name="j" value="<%=last%>">
        style='display:block'
    </logic:lessThan>
    <logic:equal name="j" value="<%=last%>">
        style='display:none'
    </logic:equal>
    >
    
    <button onclick="javascript:
                var x=document.getElementById('episodeDiv<%=j.intValue()+1%>');
                x.style.display='block' 
                "
                >add episode </button>
    </div>
    
    <hr>
    
</div>    
</logic:iterate>

</body>
</html>
