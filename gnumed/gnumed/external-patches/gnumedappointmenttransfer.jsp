
<% 
  boolean isGnumed = oscarVariables.getProperty("is_gnumed_demographics").equals("true");
  int oscar_no = 0;
 %>
 <%
  if (isGnumed && !bFirstDisp ) {
  	
  // retrieve the oscar_no if it exists , into oscar_no variable
  if (isGnumed && request.getParameter("oscar_no") != null && !"".equals(request.getParameter("oscar_no")) ) {
	oscar_no = Integer.parseInt(request.getParameter("oscar_no"));
	//check if it is till in the database
	ResultSet rs1 = apptMainBean.queryResults(oscar_no, "search_demographic_no");
	System.out.println("after search demographic no");
	if (!rs1.next()) {  
		// obsolete oscar_no
		apptMainBean.setAltHandler("gnumed");	
		apptMainBean.queryExecuteUpdate(new String[] { Integer.toString(oscar_no)  }, "delete_oscar_no");
		apptMainBean.resetToDefaultHandler();
		oscar_no = 0;

	}
  }
  // if oscar_no is not on request, then demographic is unprocessed, so insert it into oscar_mcmaster db.
  if (isGnumed &&	request.getParameter("demographic_no")!=null  
	&& oscar_no==0  ) {

	  out.println("<b>oscar number was zero</b>");
		apptMainBean.queryExecuteUpdate( 
		new String[] { 
			request.getParameter("lastname")  ,
			request.getParameter("firstname")  ,
			request.getParameter("address")  ,
			request.getParameter("city")  ,
			request.getParameter("province")  ,
			request.getParameter("postal")  ,
			request.getParameter("phone")  ,
			request.getParameter("phone2")  ,
			request.getParameter("year_of_birth")  ,
			request.getParameter("month_of_birth")  ,
			request.getParameter("date_of_birth")  ,
			request.getParameter("sex")  ,
			request.getParameter("hin")  ,
			request.getParameter("chart_no")   } ,
		        "insert_demographic" 
		);
		
		// after inserting into oscar db, retrieve the latest demographic number (? does mysql have sequences)
		// since this is non- transactional, there could be a failure here. 
		// perhaps use  getResultSet() immediately after update, or getGeneratedKeys(), but this may not
		// be implemented
		ResultSet rs2 = apptMainBean.queryResults( "last_demographic_no");
		if ( rs2.next() ) {
			// a last_demographic_no was retrieved, so switch back to gnumed db to insert the
			// new oscar external id against the pk_identity
			apptMainBean.setAltHandler("gnumed");
			
			int pk_identity = Integer.parseInt(request.getParameter("demographic_no"));	
			
			oscar_no = rs2.getInt("demographic_no");
			
			apptMainBean.queryExecuteUpdate( new  String[]{ Integer.toString(oscar_no) },  pk_identity , "insert_oscar_no" );
			apptMainBean.resetToDefaultHandler();

		}
  
  }
 }
	

 %>

