<%@ taglib uri="/tags/struts-logic" prefix="logic" %>
<logic:redirect forward="welcomeLink"/>

<%--

Redirect default requests to Welcome global ActionForward.
By using a redirect, the user-agent will change address to match the path of our Welcome ActionForward. 

--%>
