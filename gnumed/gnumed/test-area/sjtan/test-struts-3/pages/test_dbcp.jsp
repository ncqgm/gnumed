<%@page contentType="text/html"%>
<%@page pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/sql" prefix="sql" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://jakarta.apache.org/struts/tags-bean" prefix="bean" %>

<sql:query var="rs" scope="session" dataSource="jdbc/gnumed" >
select * from names
</sql:query>

<html>
  <head>
    <title>DB Test</title>
  </head>
  <body>

  <h2>Results</h2>
  
<c:forEach var="row" begin="0" items="${rs.rowsByIndex}">
    
    Foo  ${row.lastnames}  <br/>
    Bar  ${row.firstnames} <br/>
</c:forEach>

  </body>
</html>