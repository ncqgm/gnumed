/*
 * DemographicDetailSQLUpdatesImpl1.java
 *
 * Created on June 20, 2004, 5:31 PM
 */

package org.gnumed.testweb1.persist.scripted.gnumed;

import java.io.UnsupportedEncodingException;
import java.lang.reflect.InvocationTargetException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.ResourceBundle;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.beanutils.DynaBean;
import org.apache.commons.beanutils.ResultSetDynaClass;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Constants;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.ResourceBundleUsing;
import org.gnumed.testweb1.persist.scripted.DemographicDetailSQL;
import org.omg.PortableServer.ID_UNIQUENESS_POLICY_ID;

import sun.util.logging.resources.logging;

/**
 * 
 * @author sjtan
 * 
 * POSSIBLE BUGS: insert address will insert the AU country code for the country
 * field.
 */
public class DemographicDetailSQLImpl1 implements DemographicDetailSQL,
		DataObjectFactoryUsing, ResourceBundleUsing {

	/*
	 * goal: 
	 * if postcode present, 
	 * 		if urb and postcode found then
	 * 			get id_urb from urb and postcode 
	 * 			if street and id_urb found then 
	 * 				link address with
	 * 				existing street
	 *  		else insert new street with id_urb link address with new
	 * 					street 
	 * 
	 *		else if street and postcode found 
	 *			link address with existing
	 * 			street 
	 * 		else find id_urb from urb and state and country 
	 * 			if id_urb exists
	 * 				insert new street/street postcode and id_urb
	 * 			    link address with new street
	 * 		else // not enough information error incorrect postcode or not enough
	 * 				info to find urb. 
	 * else //no postcode present 
	 * 	find id_urb from urb , state and country 
	 * 	if id_urb exists 
	 * 		if street and id_urb found then 
	 * 			link address with existing street 
	 * 		else insert new street with id_urb 
	 * 		link address with street
	 * 
	 * goals are : allocate a given postcode as street or urb postcode. find
	 * existing urbs, find existing streets.
	 * 
	 * class AddressUpdater { 
	 * -urb_id 
	 * -street_id 
	 * 
	 * AddressUpdate( Connection,  detail)
	 * 
	 * findUrbAndPostcode(urb, postcode) 
	 * findStreetAndIdUrb( streetName) 
	 * linkAddress(number, subunit ) 
	 * insertNewStreet(street)
	 * updateLatestIdStreet() 
	 * findStreetAndStreetPostcode() 
	 * linkAddress
	 * findIdUrbFromUrbNameStateAndCountry 
	 * insertNewStreet(street, streetPostcode) 
	 * linkAddress 
	 * 
	 * +processDetail
	 * }
	 *  
	 */
	public static abstract class AddressUpdater {
		int urb_id;

		int street_id;
		int address_id;

		Connection conn;
		PreparedStatement stmt;
		public abstract void processDetail(Connection conn,
				DemographicDetail detail) throws SQLException, UnsupportedEncodingException;

		public abstract boolean hasPostcode(DemographicDetail detail);

		abstract boolean findUrbAndPostcode(String urb, String postcode)
				throws SQLException, UnsupportedEncodingException;

		abstract boolean findStreet(String name) throws SQLException, UnsupportedEncodingException;

		abstract void linkAddressToStreet(String number, String subunit, String addendum) throws SQLException, UnsupportedEncodingException;

		abstract void insertNewStreet(String streetName, String suburb) throws SQLException, UnsupportedEncodingException;

		abstract boolean findStreetAndStreetPostcode(String streetName,
				String streetPostcode) throws SQLException, UnsupportedEncodingException;

		abstract boolean findIdUrbFromUrbStateCountry(String urb, String state,
				String country) throws SQLException, UnsupportedEncodingException;

		abstract void insertNewStreetWithPostcode(String streetName, String streetPostcode,
				String suburb) throws SQLException, UnsupportedEncodingException;
	}

	public static class AddressUpdater1 extends AddressUpdater {
		
	    static Log log = LogFactory.getLog(DemographicDetailSQLImpl1.AddressUpdater1.class);

        public void error(String msg) throws SQLException {
			throw new SQLException(msg);
		}
		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#processDetail(java.sql.Connection,
		 *      org.gnumed.testweb1.data.DemographicDetail)
		 */
		public void processDetail(Connection conn, DemographicDetail detail)
				throws UnsupportedEncodingException, SQLException {
			this.conn = conn;
			
			if (hasPostcode(detail)) {
				log.info("HAS POSTCODE");
				if (findUrbAndPostcode(detail.getUrb(), detail.getPostcode())) {
					log.info("found urb and postcode");
					if (findStreet(detail.getStreet())) {
					
						linkAddressToStreet(detail.getStreetno(), null, null);
				
					} else {
						
						insertNewStreet(detail.getStreet(), detail.getSuburb());
						linkAddressToStreet(detail.getStreetno(), null, null);
					
					}

				} else if (findStreetAndStreetPostcode(detail.getStreet(),
						detail.getPostcode())) {
				
						linkAddressToStreet(detail.getStreetno(), null, null);

				} else if ( 
					findIdUrbFromUrbStateCountry(detail.getUrb(), detail
					.getState(), detail.getCountryCode()) 
					) {
					
						insertNewStreetWithPostcode(detail.getStreet(), detail.getPostcode(),
							detail.getSuburb());
						linkAddressToStreet(detail.getStreetno(), null, null);
				} else {
					error("incorrect postcode or not enough info for finding urb");
				}
			} else { // no postcode
			    log.info("NO POSTCODE");
				if ( findIdUrbFromUrbStateCountry(detail.getUrb(), detail
						.getState(), detail.getCountryCode())) {
				    log.info("Found id_urb from urb , state, country");
					if (findStreet(detail.getStreet())) {
					    log.info("Found street");
						linkAddressToStreet(detail.getStreetno(), null, null);
						
					} else {
					    log.info("inserting street");
						insertNewStreet(detail.getStreet(), detail.getSuburb());
						linkAddressToStreet(detail.getStreetno(), null, null);
					}
				}
			}
			

		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#findUrbAndPostcode(java.lang.String,
		 *      java.lang.String)
		 */
		boolean findUrbAndPostcode(String urb, String postcode)
				throws UnsupportedEncodingException, SQLException {
			
		    stmt = conn.prepareStatement("select id from urb where name=? and postcode=?");
		    stmt.setString(1, Util.encode( urb) );
		    stmt.setString(2, postcode);
		    ResultSet rs = stmt.executeQuery();
		    if (rs.next()) {
		        urb_id = rs.getInt(1);
		        stmt.close();
		        return true;
		    }
		    stmt.close();
			return false;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#linkAddress(java.lang.String)
		 */
		void linkAddressToStreet(String number, String subunit, String addendum) throws UnsupportedEncodingException, SQLException {
		    if (!findAddress(number,subunit ,addendum)) {
		        stmt = conn.prepareStatement(
		                "insert into address( number, subunit, addendum, id_street)"
		                
		                +"values ( ? , ? , ?, ?)");
		        stmt.setString(1, number);
		        stmt.setString(2, Util.encode( subunit ));
		        stmt.setString(3, Util.encode(addendum));
		        stmt.setInt(4, street_id);
		        stmt.execute();
		        stmt.close();
		        stmt = conn.prepareStatement("select currval('address_id_seq')");
		        ResultSet rs = stmt.executeQuery();
		        address_id = 0;
		        if (rs.next())
		            address_id = rs.getInt(1);
		        else
		            throw new SQLException("address_id is zero after select currval('address_id_seq')");
		    }
		}
		
		
		boolean findAddress(String number, String subunit, String addendum) throws UnsupportedEncodingException, SQLException {
			log.info("trace "+number+" subunit"+subunit+" addendum"+addendum);
		    stmt = conn.prepareStatement("select id from address where number like ? " +
		    		"and subunit like ? and addendum like ? and id_street = ? ");
		    stmt.setString(1, number);
		    stmt.setString(2, Util.encode( subunit) );
		    stmt.setString(3, Util.encode( addendum) );
		    stmt.setInt(4, street_id);
		    ResultSet rs = stmt.executeQuery();
		    if ( rs.next() ) {
		        address_id = rs.getInt(1);
		        if (address_id > 0) {
		            stmt.close();
		        	return true;
		        }
		    } else {
		        log.info("No address id found for above");
		    }
		    stmt.close();
		    address_id = 0;
		    return false;
		}
	

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#findStreetAndStreetPostcode()
		 */
		boolean findStreetAndStreetPostcode(String streetName,
				String streetPostcode) throws UnsupportedEncodingException, SQLException {
//		  
		    stmt = conn.prepareStatement("select id from street where name=? and postcode=?");
		    stmt.setString(1, Util.encode(streetName) );
		    stmt.setString(2, streetPostcode);
		    ResultSet rs = stmt.executeQuery();
		    if (rs.next()) {
		        street_id = rs.getInt(1);
		        stmt.close();
		        return true;
		    }
		    stmt.close();
			return false;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#findIdUrbFromUrbStateCountry(java.lang.String,
		 *      java.lang.String, java.lang.String)
		 */
		boolean findIdUrbFromUrbStateCountry(String urb, String state,
				String country) throws UnsupportedEncodingException, SQLException {
		    stmt = conn.prepareStatement("select u.id from urb u, state s where u.id_state = s.id " +
		    		"and lower(u.name)=lower(?) and (s.name=? or s.code=?) and s.country = ?");
		    stmt.setString(1,   Util.encode(urb));
		    stmt.setString(2, Util.encode( state));
		    stmt.setString(3, Util.encode( state) );
		    stmt.setString(4, country);
		    ResultSet rs = stmt.executeQuery();
		    urb_id = 0;
		    if (rs.next()) {
		        urb_id = rs.getInt(1);
		    }	
		    
		    stmt.close();
			return urb_id != 0 ;
		}


		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#hasPostcode(org.gnumed.testweb1.data.DemographicDetail)
		 */
		public boolean hasPostcode(DemographicDetail detail) {
			return detail.getPostcode() != null && detail.getPostcode().trim().length() > 0;
		}

		/*
		 * (non-Javadoc)
		 * 
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#findStreet(java.lang.String)
		 */
		boolean findStreet(String name) throws UnsupportedEncodingException, SQLException {
		    stmt = conn.prepareStatement("select id from street where name=? and id_urb = ?");
		    stmt.setString(1,  Util.encode( name) );
		    stmt.setInt(2, urb_id);
		    ResultSet rs = stmt.executeQuery();
		    street_id = 0;
		    while (rs.next()) {
		        if (street_id  != 0) {
		            stmt.close();
		            return false;
		        }
		        street_id = rs.getInt(1);
		    }
		    stmt.close();
			return street_id != 0;
		}

		/* (non-Javadoc)
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#insertNewStreet(java.lang.String, java.lang.String, java.lang.String)
		 */
		void insertNewStreetWithPostcode(String streetName, String streetPostcode, String suburb) throws UnsupportedEncodingException, SQLException {
			// 
		    stmt = conn.prepareStatement("insert into street(name, postcode, suburb, id_urb) values(?, ? , ?, ?) ");
		   
		    stmt.setString(1, Util.encode( streetName) );
		    stmt.setString(2, streetPostcode);
		    stmt.setString(3, Util.encode( suburb) );
		    stmt.setInt(4, urb_id);
			stmt.execute();
			stmt = conn.prepareStatement("select currval('street_id_seq')");
			ResultSet rs = stmt.executeQuery();
		    street_id = 0;
		    while (rs.next()) {
		        street_id = rs.getInt(1);
		    }
		    stmt.close();
		}



		/* (non-Javadoc)
		 * @see org.gnumed.testweb1.persist.scripted.gnumed.DemographicDetailSQLImpl1.AddressUpdater#insertNewStreet(java.lang.String, java.lang.String)
		 */
		void insertNewStreet(String streetName, String suburb) throws UnsupportedEncodingException, SQLException {
			// 
		    insertNewStreetWithPostcode(streetName, "", suburb);
		}

	}


	private void insertAddress(Connection conn, DemographicDetail detail)
	throws SQLException {
	    try {
	        //            PreparedStatement stmtAddress = conn.prepareStatement(
	        //            "insert into v_basic_address( number, street, city, postcode,
	        // state, country )" +
	        //            "values ( ? , ? , ? , ?, ?, ?) ");
	        //            stmtAddress.setString(1, detail.getStreetno());
	        //            stmtAddress.setString(2, detail.getStreet());
	        //            stmtAddress.setString(3, detail.getUrb().trim().toUpperCase());
	        //            stmtAddress.setString(4, detail.getPostcode());
	        //            stmtAddress.setString(5, detail.getState().trim().toUpperCase());
	        //            // <DEBUG> This needs fixing
	        //            stmtAddress.setString(6,detail.getCountryCode() == null ? "AU":
	        // detail.getCountryCode());
	        //            StringBuffer sb = new StringBuffer();
	        //            sb.append( detail.getStreetno()).append(" ").
	        //            append( detail.getStreet()).append(" ").
	        //            append( detail.getUrb()).append(" ").
	        //            append( detail.getPostcode()).append(" ").
	        //            append( detail.getState()).append(" ").
	        //            append(detail.getCountryCode());
	        //            
	        //            log.info( " Inserted :" + detail.getStreetno() + " " +
	        // sb.toString());
	        //            stmtAddress.execute();
	        AddressUpdater updater = new AddressUpdater1();
	        updater.processDetail(conn, detail);
	        
	        PreparedStatement stmtLinkAddress = conn
	        .prepareStatement("insert into lnk_person_org_address(id_identity, id_address, id_type ) "
	                + "values (? , ? , ?)");
	        stmtLinkAddress.setObject(1, detail.getId());
	        stmtLinkAddress.setInt(2, updater.address_id);
	        stmtLinkAddress.setInt(3, Constants.HOME_ADDRESS_TYPE);
	        stmtLinkAddress.execute();
	        
	    } catch (Exception e) {
	        
	        //StringBuffer sb = Util.getStringStackTrace(e);
	        log.error("insert into lnk_person_org_address", e);
	        if (e instanceof SQLException )
	            throw (SQLException) e;
	        throw new SQLException(bundle.getString("errors.insertAddress")
	                +": " + e.getMessage());
	                		
	    }

		
	}


	

    /**
	 * @param detail
	 * @param conn
	 * @return
	 */
	private String getErrorUrbSelection(Connection conn,
			DemographicDetail detail) throws SQLException {
		// 

		PreparedStatement stmt = conn
				.prepareStatement("select "
						+ "suburb , urb.name, urb.postcode, country from street, urb, state "
						+ "where urb.id_state = state.id_state and street.id_urb = urb.id "
						+ " and ( strpos( urb.name, '?') = 1 or strpos(urb.postcode , '?') "
						+ " or (strpos( street.suburb, '?') = 1 or strpos( street.postcode, '?') = 1 ) ");
		String urb = detail.getUrb().length() > 0 ? detail.getUrb() : " ";
		String pcode = detail.getPostcode().length() > 0 ? detail.getPostcode()
				: " ";
		stmt.setString(1, urb);
		stmt.setString(2, pcode);
		stmt.setString(3, urb);
		stmt.setString(4, pcode);
		stmt.execute();
		ResultSet rs = stmt.getResultSet();
		StringBuffer sb = new StringBuffer();
		while (rs.next()) {
			sb.append("\n");
			sb.append(rs.getString(1)).append("/").append(rs.getString(2))
					.append("/").append(rs.getString(3)).append("/").append(
							rs.getString(4));
		}
		stmt.close();
		return sb.toString();
	}

	final static String[] sqlToDetailsNameAddress = {
			"id, firstnames, lastnames, title, dob, gender, number, street, city, postcode, state, country,"
					,
			"id, givenname, surname, title, birthdate, sex, streetno ,street, urb, postcode, state, countryCode, "
				

	};
	
	final static String[] sqlToDetailsAddressExtra1 = {
	        "suburb",
	        "suburb"
	};
	
	final static String[] sqlToDetailsComms = {
	        "email, fax, homephone, workphone, mobile",
	        "email, fax, homePhone, workPhone, mobile"
	};

	static String publicHealthName;

	static String veteransHealthName;

	protected ResourceBundle bundle;

	private String resourceParameter;

	private DataObjectFactory factory;

	private String[] privateHealthExtIdNames;

	/** Creates a new instance of DemographicDetailSQLUpdatesImpl1 */
	public DemographicDetailSQLImpl1() {

	}

	Log log = LogFactory.getLog(this.getClass());

	/**
	 * Holds value of property localExtIdNames.
	 */
	private String[] localExtIdNames;

    private String defaultEncoding = "LATIN6";

	/**
	 * get the next id from the database id generator ( sequence) for
	 * demographic detail.
	 */
	private Long getNextId(Connection conn) throws SQLException {
		PreparedStatement stmtGetPk = conn
				.prepareStatement("select nextval('identity_id_seq')");
		stmtGetPk.execute();
		ResultSet rs = stmtGetPk.getResultSet();
		if (!rs.next())
			return null;
		log.debug(rs.getObject(1).getClass() + " is id's type");
		Long pk = (Long) rs.getObject(1);
		return pk;

	}

	/**
	 * insert an identity row for this demographic detail, generating id for
	 * this demographic detail.
	 * 
	 * @param conn
	 * @param detail
	 * @return
	 * @throws SQLException
	 * @throws UnsupportedEncodingException
	 */
	private DemographicDetail insertIdentity(Connection conn,
			DemographicDetail detail) throws UnsupportedEncodingException, SQLException {
		if (detail.getBirthdateValue() == null)
			throw new SQLException(
					"Unable to Insert due to unparsed null birthdateValue");
		PreparedStatement stmtIdentity = conn
				.prepareStatement("insert into identity(id, title, dob , gender) values (?,  ? , ? , ?)");
		detail.setId(getNextId(conn));
		stmtIdentity.setObject(1, detail.getId());
		stmtIdentity.setString(2,Util.encode( detail.getTitle()));
		stmtIdentity.setDate(3, new java.sql.Date(detail.getBirthdateValue()
				.getTime()));
		stmtIdentity.setString(4, detail.getSex());
		stmtIdentity.execute();
		return detail;

	}

	/**
	 * insert the names for this demographic record.
	 * @throws SQLException
	 * @throws UnsupportedEncodingException
	 */
	private void insertNames(Connection conn, DemographicDetail detail)
			throws UnsupportedEncodingException, SQLException {
		PreparedStatement stmtUpdateNames = conn
				.prepareStatement("update  names  set active = false where id_identity= ?");
		stmtUpdateNames.setLong(1, detail.getId().longValue());
		stmtUpdateNames.execute();

		PreparedStatement stmtNames = conn
				.prepareStatement("insert into names (id_identity, firstnames, lastnames , active) values( ? , ?, ?, true)");
		stmtNames.setLong(1, detail.getId().longValue());
		stmtNames.setString(2, Util.encode( detail.getGivenname() ));
		stmtNames.setString(3, Util.encode( detail.getSurname()));
		stmtNames.execute();

	}

	private void updateIdentity(Connection conn, DemographicDetail detail)
			throws DataSourceException, UnsupportedEncodingException, SQLException {
		PreparedStatement stmtIdentity = conn
				.prepareStatement("update identity  set title = ?, dob = ? , gender = ? where id = ?");
		stmtIdentity.setObject(4, detail.getId());
		stmtIdentity.setString(1, Util.encode( detail.getTitle()));
		stmtIdentity.setDate(2, new java.sql.Date(detail.getBirthdateValue()
				.getTime()));
		stmtIdentity.setString(3, detail.getSex());
		stmtIdentity.execute();
	}

	private void updateNames(Connection conn, DemographicDetail detail)
			throws DataSourceException, UnsupportedEncodingException, SQLException {
		Long[] existingIds = findIdsForNamesOf(conn, detail);
		log.info("Existing ids = " + existingIds);
		if (existingIds != null) {

			for (int i = 0; i < existingIds.length; ++i) {
				if (existingIds[i].equals(detail.getId()))
					return;
			}
		}
		/*
		 * if names had a many-to-many relationship to identity, then they could
		 * be re=used. Instead, duplicates must be inserted if not the same
		 * identity.
		 */
		insertNames(conn, detail);

	}

	private void updateAddress(Connection conn, DemographicDetail detail)
			throws DataSourceException, UnsupportedEncodingException, SQLException {
		clearOldAddressLink(conn, detail, Constants.HOME_ADDRESS_TYPE);
		if (addressExists(conn, detail)) {
			createExistingAddressLink(conn, detail, Constants.HOME_ADDRESS_TYPE);
		} else {
			insertAddress(conn, detail);
		}
	}

	private void clearOldAddressLink(Connection conn, DemographicDetail detail,
			int addr_type) throws SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("delete from lnk_person_org_address "
						+ "where id_identity = ? and id_type = ?");
		stmt.setObject(1, detail.getId());
		stmt.setInt(2, addr_type);
		stmt.execute();
	}

	private void createExistingAddressLink(Connection conn,
			DemographicDetail detail, int addr_type) throws UnsupportedEncodingException, SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("insert into lnk_person_org_address ( id_identity, id_address, id_type )"
						+ "values ( ?, ? , ?)");
		stmt.setObject(1, detail.getId());
		stmt.setObject(2, getExistingAddressId(conn, detail));
		stmt.setInt(3, addr_type);
		stmt.execute();
	}

	private boolean addressExists(Connection conn, DemographicDetail detail)
			throws UnsupportedEncodingException, SQLException {
		Long id = getExistingAddressId(conn, detail);
		log.info("ADDRESS EXISTS: id = " + id);
		return id != null && id.longValue() != 0L;
	}

	private Long getExistingAddressId(Connection conn, DemographicDetail detail)
			throws UnsupportedEncodingException, SQLException {
	    String cond ;
	    if ( Util.nullIsBlank(detail.getPostcode()).length() == 0) {
	        cond = "'!' <> ? and '!' <> ? and st.code = ?";
	    } else {
	        if ( Util.nullIsBlank(detail.getState()).length() == 0) {
	    
	            cond = "'!'  <> ?";
	        } else {
	            cond = "st.code = ?";
	        }
	        
	        if (Util.nullIsBlank(detail.getSuburb()).length() == 0) {
	            cond = "'!' <> ? and u.postcode = ? and " + cond;
	        } else {
	            cond = "'!' <> ? and s.postcode = ? and " + cond;
	        }
	    }
	    
	    
	        PreparedStatement stmt = conn
				.prepareStatement("select v.id from address v , street s , urb u , state st "
						+ " where " +
						" v.id_street = s.id and s.id_urb = u.id" +
						" and v.number = ?" +
						" and  s.name  like  ? " +
						" and   s.suburb like ? " + 
						" and u.name   =  ?  and " + cond);

		stmt.setString(1, detail.getStreetno());
		stmt.setString(2, Util.encode(detail.getStreet()));
		stmt.setString(3,Util.encode( detail.getSuburb()));
		
		stmt.setString(4,Util.encode( detail.getUrb()));
		stmt.setString(5, detail.getPostcode());
		stmt.setString(6, detail.getPostcode());
		stmt.setString(7,Util.encode( detail.getState()) );
		
		stmt.execute();

		ResultSet rs = stmt.getResultSet();

		if (rs.next()) {

			Long id = new Long(rs.getLong(1));
			log.info("ADDRESS_ID = " + id);
			rs.close();
			return id;
		}
		return null;

	}

	private void insertContacts(Connection conn, DemographicDetail detail)
			throws SQLException {
		insertOrUpdateContacts(conn, getDataObjectFactory()
				.createDemographicDetail(), detail);
	}

	private void updateContacts(Connection conn, DemographicDetail detail)
			throws SQLException, DataSourceException {
		DemographicDetail oldDetail = findByPrimaryKey(conn, detail.getId());
		insertOrUpdateContacts(conn, oldDetail, detail);

	}

	private void insertOrUpdateContacts(Connection conn,
			DemographicDetail oldDetail, DemographicDetail detail)
			throws SQLException {
		Map map = new HashMap();
		String[] contactFields = new String[] { "email", "fax", "homePhone",
				"workPhone", "mobile" };

		for (int i = 0; i < contactFields.length; ++i) {
			String field = contactFields[i];
			try {

				if (BeanUtils.getSimpleProperty(detail, field) != null
						&& !BeanUtils.getSimpleProperty(detail, field).equals(
								BeanUtils.getSimpleProperty(oldDetail, field))) {
					map.put(field, new Integer(i + 1));
				}
			} catch (Exception e) {
				log.error("error in comparing old vs new detail contacts", e);
				continue;
			}

		}

//		PreparedStatement uniqueUrlAndType = conn
//				.prepareStatement("select id from lnk_identity2comm"
//						+ "            where url = ? and id_type = ?");

		PreparedStatement insert = conn
				.prepareStatement("insert into lnk_identity2comm(   id_identity, url, id_type) " +
						"values (  ?,  ?, ?)");

		PreparedStatement nextId = conn
				.prepareStatement("select nextval('lnk_identity2comm_id_seq')");

		// deprecated
//		PreparedStatement addLink = conn
//				.prepareStatement("insert into lnk_identity2comm_chan ( id_identity, id_comm) values ( ?, ?)");
//
//		PreparedStatement deleteOldLink = conn
//				.prepareStatement("delete from lnk_identity2comm_chan where id_identity = ? and id_comm = ("
//						+ "select c.id from lnk_identity2comm c join lnk_identity2comm_chan l2 "
//						+ "on (l2.id_comm = c.id) where c.id_type =  ?  and l2.id_identity = ? )");
		
		// update an old url of same type with same id_identity : THIS IS APPLICATION PAGE
		// specific
		
		PreparedStatement find = conn.prepareStatement("select * from lnk_identity2comm where id_identity=? and id_type=?");
		PreparedStatement update = conn.prepareStatement(
		        "update lnk_identity2comm set url = ? where id_identity = ? and id_type = ? ");
		
		Long id = detail.getId();

		Iterator i = map.keySet().iterator();
		while (i.hasNext()) {

			String type = (String) i.next();
			int id_type = ((Integer) map.get(type)).intValue();
			String url = null;
			try {
				url = BeanUtils.getSimpleProperty(detail, type);
			} catch (Exception e) {
				throw new SQLException(e.getMessage());
			}

			if (url == null || url.trim().length() == 0)
				continue;
//
//			uniqueUrlAndType.setString(1, url);
//			uniqueUrlAndType.setInt(2, id_type);
//			uniqueUrlAndType.execute();
//			ResultSet rs0 = uniqueUrlAndType.getResultSet();
//
//			Long cid = null;
//			if (rs0.next()) {
//				cid = new Long(rs0.getLong(1));
//			}
//
//			deleteOldLink.setInt(2, id_type);
//			deleteOldLink.setLong(1, id.longValue());
//			deleteOldLink.setLong(3, id.longValue());
//
//			deleteOldLink.execute();

			find.setLong(1,id.longValue()); 
			find.setInt(2, id_type);
			ResultSet rsf = find.executeQuery();
			if (rsf.next() ) {
			    update.setLong(2, id.longValue());
			    update.setString(1, url);
			    update.setInt(3, id_type);
			    update.execute();
			    
			} else {
			    insert.setLong(1, id.longValue());
			    insert.setString(2, url);
			    insert.setInt(3, id_type);
			    insert.execute();
			   
			}
			
			
//			
//			if (cid == null) {
//				nextId.execute();
//
//				ResultSet rs = nextId.getResultSet();
//				if (!rs.next())
//					throw new SQLException("failed lnk_identity2comm sequencer");
//
//				cid = new Long(rs.getLong(1));
//
//				insert.setLong(1, cid.longValue());
//				insert.setInt(3, id_type);
//
//				insert.setString(2, url);
//				insert.setLong(4, id.longValue());
//				insert.execute();
//			}
		}
		
	}

	private void writeExtIds(Connection conn, DemographicDetail detail)
			throws SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("insert into lnk_identity2ext_id (external_id, id_identity, fk_origin )"
						+ "values (?, ?, (select pk from enum_ext_id_types where name = ?)   ) ");

		PreparedStatement stmt1 = conn
				.prepareStatement("select external_id from lnk_identity2ext_id "
						+ "where id_identity=? and "
						+ "fk_origin = (select pk from enum_ext_id_types where name = ?)");

		PreparedStatement stmt2 = conn
				.prepareStatement("update lnk_identity2ext_id set external_id = ?    "
						+ "where id_identity= ?  and "
						+ "fk_origin = "
						+ "(select pk from enum_ext_id_types where name = ?)");

		PreparedStatement stmt3 = conn
				.prepareStatement("delete from lnk_identity2ext_id where id_identity = ?"
						+ "and fk_ origin = "
						+ "(select pk from enum_ext_id_types where name = ?)");

		setExtIdsStatementValues(stmt, stmt1, stmt2, stmt3, detail);

	}

	private void InsertOrUpdateExtIds(PreparedStatement stmt, Object[] params)
			throws SQLException {
		for (int i = 0; i < params.length; ++i) {
			stmt.setObject(i + 1, params[i]);
		}
		log.info("before executing , params count = " + params.length);
		stmt.execute();
	}

	private void setExtIdsStatementValues(PreparedStatement insert,
			PreparedStatement exists, PreparedStatement update,
			PreparedStatement delete, DemographicDetail detail)
			throws SQLException {

		String[] extIdNames = new String[] { bundle.getString("public.health.id.name"),
		 bundle.getString("veterans.health.id.name") };
		String[] props = new String[] { "publicHealthIdWithExp", "veteransId" };
		for (int i = 0; i < extIdNames.length; ++i) {
			try {
				String new_ext_id = BeanUtils.getSimpleProperty(detail,
						props[i]);
				if (new_ext_id == null)
					continue;
				new_ext_id = new_ext_id.trim();

				exists.setLong(1, detail.getId().longValue());
				exists.setString(2, extIdNames[i]);
				exists.execute();
				ResultSet rs = exists.getResultSet();
				if (rs.next()) {
					String ext_id = rs.getString(1);
					if (ext_id.equals(new_ext_id)) {
						continue;
					}
					if (new_ext_id.length() == 0)
						InsertOrUpdateExtIds(delete, new Object[] {
								detail.getId(), extIdNames[i] });

					InsertOrUpdateExtIds(update, new Object[] { new_ext_id,
							detail.getId(), extIdNames[i] });

				} else {
					if (new_ext_id.length() != 0)
						InsertOrUpdateExtIds(insert, new Object[] { new_ext_id,
								detail.getId(), extIdNames[i] });

				}
			} catch (IllegalAccessException iae) {
				log.info("Check Resource entry for correct ext id type names"
						+ detail, iae);
			} catch (java.lang.reflect.InvocationTargetException ite) {
				log.info("Check Resource entry for correct ext id type names"
						+ detail, ite);

			} catch (java.lang.NoSuchMethodException nsme) {
				log.info(
						"Check Resource entry for correct ext id type names and "
								+ detail, nsme);

			}
		}

	}

	/**
	 * deletes a demographic detail from the database
	 * 
	 * @param conn
	 * @param detail
	 *            the demographicDetail record to delete. Its id will be used to
	 *            find the record.
	 * @throws DataSourceException
	 */

	public void delete(Connection conn, DemographicDetail detail)
			throws DataSourceException {

	}

	/**
	 * 
	 * @param conn
	 * @param detail
	 * @throws SQLException
	 * @return an array of id values for name rows that match the demographic
	 *         record lastname and firstname.
	 */
	public Long[] findIdsForNamesOf(Connection conn, DemographicDetail detail)
			throws SQLException {
		PreparedStatement stmt = conn
				.prepareStatement("select  id_identity from names where firstnames = ? and lastnames = ?");
		stmt.setString(1, detail.getGivenname());
		stmt.setString(2, detail.getSurname());
		stmt.execute();
		ResultSet rs = stmt.getResultSet();
		java.util.List l = new java.util.ArrayList();
		while (rs.next()) {
			l.add(new Long(rs.getLong(1)));
		}
		rs.close();
		return (Long[]) l.toArray(new Long[0]);

	}

	/**
	 * stores the demographic record with a new id value.
	 * 
	 * @param conn
	 * @param detail
	 * @throws DataSourceException
	 * @return a demographic record with an id value.
	 */
	public DemographicDetail insert(Connection conn, DemographicDetail detail)
			throws DataSourceException {
		try {
		    
			//   conn.setAutoCommit(false);
			conn.commit();
			
			Util.setDefaultClientEncoding(conn);
			
			detail = insertIdentity(conn, detail);
			insertNames(conn, detail);
			detail.setStreet(Util.nullIsBlank(detail.getStreet()));
			if (!detail.getStreet().trim().equals("")) {
				insertAddress(conn, detail);
			}

			insertContacts(conn, detail);
			writeExtIds(conn, detail);

			conn.commit();
			//            conn.setAutoCommit(true);
			conn.close();
			return detail;
		} catch (Exception e) {
			try {
				conn.rollback();

				//                conn.setAutoCommit(true);
				conn.close();
			} catch (Exception e2) {
				throw new DataSourceException(e2);
			}
			throw new DataSourceException(e);
		}

	}

	/**
	 * stores any changes in the demographic record.
	 * 
	 * @param conn
	 * @param detail
	 * @throws DataSourceException
	 * @return
	 */
	public void update(Connection conn, DemographicDetail detail)
			throws DataSourceException {
		try {
			//          conn.setAutoCommit(false);
			conn.commit();
			Util.setDefaultClientEncoding(conn);
			updateIdentity(conn, detail);
			updateNames(conn, detail);
			detail.setStreet(Util.nullIsBlank(detail.getStreet()));
			if (!detail.getStreet().trim().equals("")) {
				updateAddress(conn, detail);
			}
			updateContacts(conn, detail);
			writeExtIds(conn, detail);
			conn.commit();
			//          conn.setAutoCommit(true);
			conn.close();

		} catch (Exception e) {
			DataSourceException de = new DataSourceException(e);
			try {
				conn.rollback();
				//              conn.setAutoCommit(true);
				conn.close();
			} catch (Exception e2) {
				e2.printStackTrace(System.err);
			}
			throw new DataSourceException(e);
		}
	}




    /**
	 * find a demographic record by trying to match its fields.
	 */
	public DemographicDetail[] findByExample(Connection conn,
			DemographicDetail detailFragment) throws DataSourceException {
		List l = null;
		try {
			PreparedStatement stmt = conn
					.prepareStatement("select v.id,  firstnames, lastnames , dob, gender , number, street, city, postcode, state, country "
							+ "from  v_basic_person v left  join (select * from lnk_person_org_address l, v_basic_address a where l.id_address= a.id) as la on v.id=la.id_identity  "
							+ " where "
							+ " strpos( upper(firstnames), upper( ? ) ) > 0 "
							+ "and strpos(upper(lastnames), upper( ?  ) ) > 0");
			stmt.setString(1, detailFragment.getGivenname() == null ? ""
					: detailFragment.getGivenname());
			stmt.setString(2, detailFragment.getSurname() == null ? ""
					: detailFragment.getSurname());
			stmt.execute();
			ResultSet rs = stmt.getResultSet();

			l = new ArrayList();

			while (rs.next()) {

				DemographicDetail detail = getDataObjectFactory()
						.createDemographicDetail();

				detail.setId(new Long(rs.getLong(1)));

				detail.setGivenname(rs.getString(2));
				detail.setSurname(rs.getString(3));
				DateFormat format = DateFormat
						.getDateInstance(DateFormat.SHORT);
				detail.setBirthdate(format.format(rs.getDate(4)));
				detail.setSex(rs.getString(5));

				detail.setStreetno(rs.getString(6));
				detail.setStreet(rs.getString(7));
				detail.setUrb(rs.getString(8));
				detail.setPostcode(rs.getString(9));
				detail.setState(rs.getString(10));
				detail.setCountryCode(rs.getString(11));
				getExternalIds(conn, detail);

				l.add(detail);

			}
		} catch (SQLException e) {
			log.error("inside detail collection loop" + e);
			e.printStackTrace();
			throw new DataSourceException(e);
		}
		log.info("Got DemographicsDetails collection size = " + l.size());
		return (DemographicDetail[]) l.toArray(new DemographicDetail[0]);
	}

	/**
	 * find a demographic record by its id.
	 */
	public DemographicDetail findByPrimaryKey(Connection conn, Long id)
			throws DataSourceException {
		try {
		    
		    DemographicDetail detail = getDataObjectFactory()
			.createDemographicDetail();
		    
			String selectDetailNamesAddress = "select * from v_basic_person p " +
			"left join lnk_person_org_address l on (p.id = l.id_identity) " +
			"left join v_basic_address a on (l.id_address = a.id) " +
		// can't access salaam to change view, so resort to application selection of comms.
		// "left join v_person_comms_flat vc on vc.id = p.id " +
			"where p.id= ? ";
            
			DynaBean bean = getDynaBeanFromSQL(conn, id, selectDetailNamesAddress);
			if (bean == null)
			    throw new DataSourceException("names not found for id =" + id.toString());
			
			transferDynaBeanToDetail(detail, bean, sqlToDetailsNameAddress[0], sqlToDetailsNameAddress[1]);

			// deals with street suburb field
			
			String selectAddressExtra1 = "select suburb " +
					"from street s," +
					"address a, lnk_person_org_address l where" +
					" l.id_address = a.id and " +
					" a.id_street = s.id and" +
					" l.id_identity = ?"
					;
			DynaBean beanExtra = getDynaBeanFromSQL(conn, id, selectAddressExtra1);
			if (bean != null)
			    transferDynaBeanToDetail(detail, beanExtra, 
			        sqlToDetailsAddressExtra1[0], sqlToDetailsAddressExtra1[1]);
			

			
			
			String selectComms = "select * from v_person_comms_flat where id =? ";
			
			try {
			    DynaBean beanComms = getDynaBeanFromSQL(conn, id, selectComms);
			    transferDynaBeanToDetail(detail, bean, sqlToDetailsComms[0], sqlToDetailsComms[1]);

			} catch (Exception e) {
			    getCommsAlternate(conn, id, detail);
			}
			
			getExternalIds(conn, detail);

			Util.logBean(log, detail);

			return detail;

		} catch (Exception e2) {
			e2.printStackTrace(System.err);
			throw new DataSourceException(e2);

		}
	}

	/**
     * @param conn
     * @param id
     * @param detail
     * @throws SQLException
     * @throws IllegalAccessException
     * @throws InvocationTargetException
     */
    private void getCommsAlternate(Connection conn, Long id, DemographicDetail detail) throws SQLException, IllegalAccessException, InvocationTargetException {
        log.info("Failed to get from view v_person_comms_flat : USING APPLICATION LOOP SELECT ");
        conn.rollback();
        PreparedStatement stmt = conn.prepareStatement(
                "select url from lnk_identity2comm " +
                "where id_type = ? and id_identity = ?");
        String[] fields = sqlToDetailsComms[1].split(",\\s*");
        for (int  i = 1; i < 6; ++i ) {
            stmt.setInt(1, i);
            stmt.setLong(2, id.longValue());
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                BeanUtils.setProperty(detail, fields[i-1], rs.getString(1));
              
            }
        }
        stmt.close();
    }




    /**
     * @param conn
     * @param id
     * @param selectDetailNamesAddress
     * @return
     * @throws SQLException
     * @throws DataSourceException
     * @throws Exception
     */
    private DynaBean getDynaBeanFromSQL(Connection conn, Long id, String selectDetailNamesAddress) throws SQLException, DataSourceException, Exception {
        PreparedStatement stmt = conn
        		.prepareStatement( 
        selectDetailNamesAddress );

        stmt.setLong(1, id.longValue());
        stmt.execute();
        ResultSet rs = stmt.getResultSet();
        ResultSetDynaClass dynaClass = new ResultSetDynaClass(rs);
        Iterator i = dynaClass.iterator();
        if (!i.hasNext())
        	return null;
        DynaBean bean = (DynaBean) i.next();

        Util.logBean(log, bean);
        return bean;
    }




    /**
     * @param detail
     * @param bean
     * @param sqlFieldNamesString
     * @param detailFieldNamesString
     */
    private void transferDynaBeanToDetail(DemographicDetail detail, DynaBean bean, String sqlFieldNamesString, String detailFieldNamesString) {
        String[] sqlFields = sqlFieldNamesString.split(",\\s*");
        String[] detailFields = detailFieldNamesString.split(",\\s*");

        for (int j = 0; j < sqlFields.length; ++j) {
        	try {
        		log.info("detail:" + detailFields[j].trim() + " bean:"
        				+ sqlFields[j] + " value = "
        				+ BeanUtils.getProperty(bean, sqlFields[j].trim()));
        		BeanUtils.setProperty(detail, detailFields[j].trim(),
        				BeanUtils.getProperty(bean, sqlFields[j].trim()));

        	} catch (Exception iae) {
        		log.error("error copying dynabean to demographicDetail"
        				+iae.getMessage() );
        	}
        }
    }




    protected void getExternalIds(Connection conn, DemographicDetail detail)
			throws SQLException {
		PreparedStatement stmt2 = conn
				.prepareStatement("select l.id_identity as id , l.external_id , e.name from lnk_identity2ext_id l, enum_ext_id_types e "
						+ "where l.id_identity = ?"
						+ " and l.fk_origin = e.pk ");
		stmt2.setLong(1, detail.getId().longValue());
		stmt2.execute();

		ResultSet rs = stmt2.getResultSet();

		while (rs.next()) {
			String name = rs.getString(3);
			if (bundle.getString("public.health.id.name").equals(name)) {
				detail.setPublicHealthIdWithExp(rs.getString(2));
				continue;
			}
			if (bundle.getString("veterans.health.id.name").equals(name)) {
				detail.setVeteransId(rs.getString(2));
				continue;
			}
		}

	}

	public DataObjectFactory getDataObjectFactory() {
		log.info(this + "Returning reference to " + factory);
		return factory;
	}

	public void setDataObjectFactory(DataObjectFactory dataObjectFactory) {
		this.factory = dataObjectFactory;
		log.info(this + " Got a  " + factory);
	}

	public ResourceBundle getResourceBundle() {
		return bundle;
	}

	public void setResourceBundle(ResourceBundle bundle) {
		this.bundle = bundle;
		
		//        java.util.Enumeration keys = bundle.getKeys();
		//        while (keys.hasMoreElements()) {
		//                String key = (String) keys.nextElement();
		//                log.info( "ResourceBundle.key = " + key + ":" + bundle.getString(key)
		// );
		//
		//        }
		//
		//        MessageResources mr =
		// PropertyMessageResourcesFactory.createFactory().createResources(this.resourceParameter);
		//        log.info("RESOURCE public.health.id.name IS "
		// +mr.getMessage("public.health.id.name"));
	}

}