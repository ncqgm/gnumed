<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<html>
<head><title>JSP Page</title></head>
<body>

<%java.util.Enumeration en1;
int[] scopes = new int[] {PageContext.PAGE_SCOPE, PageContext.REQUEST_SCOPE,
PageContext.SESSION_SCOPE, PageContext.APPLICATION_SCOPE};
String[] scopeNames = new String[] { "page", "request", "session", "application" };

for (int ik = 0; ik < scopes.length; ++ik) {
    
     
    out.println("<br>" + scopeNames[ik] + " Scope:<br>");
    en1 = pageContext.getAttributeNamesInScope(scopes[ik]);
    while(en1.hasMoreElements()) {
        String s = (String)en1.nextElement();
        Object name = null;
        switch (ik) {
            case 0: name =  pageContext.getAttribute(s);break;
            case 1: name =  request.getAttribute(s);break;
            case 2: name = session.getAttribute(s);break;
            case 3: name = application.getAttribute(s);break;
            default:break;
            }
        out.println(s + " : " + name +"<br>");
    }
}
%>
 

</body>
</html>
