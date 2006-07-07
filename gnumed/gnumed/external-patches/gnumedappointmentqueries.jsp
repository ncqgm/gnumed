<%
  String [][] dbQueries=new String[][] { 

    {"search_appt", "select count(appointment_no) AS n from appointment where appointment_date = ? and provider_no = ? and status !='C' and ((start_time>= ? and start_time<= ?) or (end_time>= ? and end_time<= ?) or (start_time<= ? and end_time>= ?) )" }, 

    {"search_demographiccust_alert", "select cust3 from demographiccust where demographic_no = ? " }, 

    {"search_demographic_statusroster", "select patient_status,roster_status from demographic where demographic_no = ? " }, 
    {"search_demographic_no", "select demographic_no from demographic where demographic_no = ?" },
    {"insert_demographic", "insert into demographic (  last_name, first_name, address, city, province, postal, phone," + 
	" phone2,  year_of_birth, month_of_birth, date_of_birth, sex,  hin, chart_no , " +
	" patient_status, roster_status, email, pin, provider_no , " +
	" pcn_indicator, eff_date, end_date, date_joined, hc_renew_date, " +
	" hc_type, family_doctor , ver ) values ( ?, ?, ?, ?, ? , ? , ? , ? , ? , ?, ? ,? , ? , ? , "+
	"  '', '' , '', '', '' , "+
	"  '', '0001-01-01' , '0001-01-01', '0001=01-01', '0001-01-01' , "+
	"  '','' , '' )"
	 },
    
    {"last_demographic_no", "select max(demographic_no) as demographic_no from demographic" },
    {"insert_oscar_no", "insert into dem.lnk_identity2ext_id (  external_id, id_identity,  fk_origin) "+
				" values( ?, ?, ( select pk from dem.enum_ext_id_types where name ="+ 
					"'oscar_demographic_no' ) )" } ,
    {"delete_oscar_no", "delete from dem.lnk_identity2ext_id where external_id = ? "+
	    						" and fk_origin = (select pk from dem.enum_ext_id_types where name ="+
	    												"'oscar_demographic_no' ) " }
	
  };
%>
