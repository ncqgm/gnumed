/*
 * DemographicDetailSQLUpdatesImpl1.java
 *
 * Created on June 20, 2004, 5:31 PM
 */

package org.gnumed.testweb1.persist.scripted.gnumed1;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
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



/**
 *
 * @author  sjtan
 *
 * POSSIBLE BUGS:
 *  insert address will insert the AU country code for the country field.
 */
public class DemographicDetailSQLImpl1 implements DemographicDetailSQL , DataObjectFactoryUsing, ResourceBundleUsing{
    
    final static String[] sqlToDetails = {
        "id, firstnames, lastnames, title, dob, gender, number, street, city, postcode, state, country," +
        "email, fax, homephone, workphone, mobile",
        "id, givenname, surname, title, birthdate, sex, streetno ,street, urb, postcode, state, countryCode, " +
        "email, fax, homePhone, workPhone, mobile"
        
    };
    static String publicHealthName ;
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
    
    /**
     * get the next id from the database
     * id generator ( sequence) for demographic detail.
     */
    private Long getNextId( Connection conn) throws SQLException {
        PreparedStatement stmtGetPk = conn.prepareStatement("select nextval('identity_id_seq')");
        stmtGetPk.execute();
        ResultSet rs = stmtGetPk.getResultSet();
        if (!rs.next())
            return null;
        log.debug( rs.getObject(1).getClass() + " is id's type");
        Long pk = (Long) rs.getObject(1);
        return pk;
        
        
    }
    
    /**
     * insert an identity row for this
     * demographic detail, generating
     * id for this demographic detail.
     * @param conn
     * @param detail
     * @throws SQLException
     * @return
     */
    private DemographicDetail insertIdentity(Connection conn, DemographicDetail detail)
    throws SQLException {
        if ( detail.getBirthdateValue() == null)
            throw new SQLException("Unable to Insert due to unparsed null birthdateValue");
        PreparedStatement stmtIdentity = conn.prepareStatement("insert into identity(id, title, dob , gender) values (?,  ? , ? , ?)");
        detail.setId(getNextId(conn));
        stmtIdentity.setObject(1, detail.getId());
        stmtIdentity.setString(2, detail.getTitle());
        stmtIdentity.setDate(3, new java.sql.Date(detail.getBirthdateValue().getTime()));
        stmtIdentity.setString(4, detail.getSex());
        stmtIdentity.execute();
        return detail;
        
    }
    
    /**
     * insert the names for this demographic record.
     */
    private void insertNames(Connection conn, DemographicDetail detail) throws SQLException {
        PreparedStatement stmtUpdateNames = conn.prepareStatement("update  names  set active = false where id_identity= ?");
        stmtUpdateNames.setLong(1, detail.getId().longValue());
        stmtUpdateNames.execute();
        
        PreparedStatement stmtNames = conn.prepareStatement("insert into names (id_identity, firstnames, lastnames , active) values( ? , ?, ?, true)");
        stmtNames.setLong(1, detail.getId().longValue());
        stmtNames.setString(2, detail.getGivenname());
        stmtNames.setString(3, detail.getSurname());
        stmtNames.execute();
        
    }
    
    
    private void insertAddress(Connection conn, DemographicDetail detail) throws SQLException {
        try{
            PreparedStatement stmtAddress = conn.prepareStatement(
            "insert into v_basic_address( number, street, city, postcode, state, country )" +
            "values ( ? , ? , ? , ?, ?, ?) ");
            stmtAddress.setString(1, detail.getStreetno());
            stmtAddress.setString(2, detail.getStreet());
            stmtAddress.setString(3, detail.getUrb().trim().toUpperCase());
            stmtAddress.setString(4, detail.getPostcode());
            stmtAddress.setString(5, detail.getState().trim().toUpperCase());
            // <DEBUG> This needs fixing
            stmtAddress.setString(6,detail.getCountryCode() == null ? "AU": detail.getCountryCode());
            StringBuffer sb = new StringBuffer();
            sb.append( detail.getStreetno()).append(" ").
            append( detail.getStreet()).append(" ").
            append( detail.getUrb()).append(" ").
            append( detail.getPostcode()).append(" ").
            append( detail.getState()).append(" ").
            append(detail.getCountryCode());
            
            log.info( " Inserted :" + detail.getStreetno() + " " +  sb.toString());
            stmtAddress.execute();
        } catch (Exception e) {
            throw new SQLException( bundle.getString("errors.insertAddress")+e.getMessage());
        }
        
        PreparedStatement getLastAddressId = conn.prepareStatement("select currval('address_id_seq')");
        getLastAddressId.execute();
        ResultSet rs = getLastAddressId.getResultSet();
        if (!rs.next())
            throw new SQLException("ResultSet for getLastAddressId returns no rows");
        Long addressId = (Long)rs.getObject(1);
        PreparedStatement stmtLinkAddress=conn.prepareStatement(
        "insert into lnk_person_org_address(id_identity, id_address, id_type ) " +
        "values (? , ? , ?)" );
        stmtLinkAddress.setObject(1, detail.getId());
        stmtLinkAddress.setObject(2, addressId );
        stmtLinkAddress.setInt(3, Constants.HOME_ADDRESS_TYPE );
        stmtLinkAddress.execute();
        
        
    }
    
    
    
    private void updateIdentity(Connection conn, DemographicDetail detail) throws DataSourceException, SQLException {
        PreparedStatement stmtIdentity = conn.prepareStatement("update identity  set title = ?, dob = ? , gender = ? where id = ?");
        stmtIdentity.setObject(4, detail.getId());
        stmtIdentity.setString(1, detail.getTitle());
        stmtIdentity.setDate(2, new java.sql.Date(detail.getBirthdateValue().getTime()));
        stmtIdentity.setString(3, detail.getSex());
        stmtIdentity.execute();
    }
    
    private void updateNames(Connection conn, DemographicDetail detail) throws DataSourceException, SQLException {
        Long[] existingIds = findIdsForNamesOf(conn, detail);
        log.info("Existing ids = " + existingIds);
        if (existingIds != null ) {
            
            for (int i = 0; i < existingIds.length; ++i) {
                if (existingIds[i].equals(detail.getId()))
                    return;
            }
        }
            /* if names had a many-to-many relationship to identity,
             * then they could be re=used. Instead, duplicates must
             * be inserted if not the same identity.
             */
        insertNames( conn, detail);
        
        
        
        
    }
    
    private void updateAddress(Connection conn, DemographicDetail detail) throws DataSourceException, SQLException {
        clearOldAddressLink(conn, detail, Constants.HOME_ADDRESS_TYPE);
        if ( addressExists( conn, detail) ) {
            createExistingAddressLink(conn, detail, Constants.HOME_ADDRESS_TYPE );
        } else {
            insertAddress(conn, detail);
        }
    }
    
    private void clearOldAddressLink( Connection conn, DemographicDetail detail, int addr_type)  throws SQLException{
        PreparedStatement stmt = conn.prepareStatement(
        "delete from lnk_person_org_address " +
        "where id_identity = ? and id_type = ?");
        stmt.setObject(1, detail.getId());
        stmt.setInt(2,  addr_type);
        stmt.execute();
    }
    
    private void createExistingAddressLink(Connection conn, DemographicDetail detail, int addr_type)  throws SQLException{
        PreparedStatement stmt = conn.prepareStatement(
        "insert into lnk_person_org_address ( id_identity, id_address, id_type )" +
        "values ( ?, ? , ?)");
        stmt.setObject(1, detail.getId());
        stmt.setObject(2, getExistingAddressId(conn, detail) );
        stmt.setInt(3, addr_type);
        stmt.execute();
    }
    
    private boolean addressExists(Connection conn, DemographicDetail detail) throws SQLException {
        Long id = getExistingAddressId(conn, detail);
        log.info("ADDRESS EXISTS: id = " + id);
        return id != null && id.longValue() != 0L;
    }
    
    private Long getExistingAddressId(Connection conn, DemographicDetail detail) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement(
        "select addr_id from v_basic_address v " +
        "where v.number = ? and v.street = ? " +
        "and v.city = ? and (v.postcode = ? or v.state = ?)");
        
        stmt.setString( 1,detail.getStreetno());
        stmt.setString( 2,detail.getStreet());
        stmt.setString( 3, detail.getUrb());
        stmt.setString( 4, detail.getPostcode());
        stmt.setString( 5, detail.getState());
        stmt.execute();
        
        ResultSet rs = stmt.getResultSet();
        
        if (rs.next()) {
            
            Long id = new Long(rs.getLong(1));
            log.info("ADDRESS_ID = "+ id);
            rs.close();
            return id;
        }
        return null;
        
        
    }
    
    private void insertContacts(Connection conn, DemographicDetail detail) throws SQLException {
        insertOrUpdateContacts( conn, getDataObjectFactory().createDemographicDetail(), detail);
    }
    
    private void updateContacts(Connection conn, DemographicDetail detail) throws SQLException, DataSourceException {
        DemographicDetail oldDetail = findByPrimaryKey(conn,detail.getId());
        insertOrUpdateContacts(conn, oldDetail, detail);
        
    }
    
    private void insertOrUpdateContacts( Connection conn, DemographicDetail oldDetail, DemographicDetail detail)
    throws SQLException {
        Map map = new HashMap();
        String [] contactFields = new String[] { "email", "fax","homePhone", "workPhone", "mobile" };
        
        for (int i = 0; i < contactFields.length; ++i) {
            String field = contactFields[i];
            try {
                
                if (
                BeanUtils.getSimpleProperty(detail,field) != null &&
                ! BeanUtils.getSimpleProperty(detail, field)
                .equals(BeanUtils.getSimpleProperty(oldDetail, field) ) ) {
                    map.put( field , new Integer(i + 1) );
                }
            } catch(Exception e) {
                log.error("error in comparing old vs new detail contacts", e);
                continue;
            }
            
        }
        
        PreparedStatement uniqueUrlAndType = conn.prepareStatement(
        "select id from comm_channel" +
        "            where url = ? and id_type = ?"
        );
        
        PreparedStatement insert = conn.prepareStatement(
        "insert into comm_channel( id, url, id_type) values (?,  ?, ?)"
        );
        
        PreparedStatement nextId = conn.prepareStatement(
        "select nextval('comm_channel_id_seq')" );
        
        PreparedStatement addLink = conn.prepareStatement(
        "insert into lnk_identity2comm_chan ( id_identity, id_comm) values ( ?, ?)"
        );
        
        PreparedStatement deleteOldLink = conn.prepareStatement(
        "delete from lnk_identity2comm_chan where id_identity = ? and id_comm = (" +
        "select c.id from comm_channel c join lnk_identity2comm_chan l2 " +
        "on (l2.id_comm = c.id) where c.id_type =  ?  and l2.id_identity = ? )"
        );
        
        
        
        Long id = detail.getId();
        
        Iterator i = map.keySet().iterator();
        while (i.hasNext()) {
            
            String type = (String) i.next();
            int id_type =     ((Integer)map.get(type)).intValue();
            String url = null;
            try {
                url = BeanUtils.getSimpleProperty(detail,type);
            } catch (Exception e) {
                throw new SQLException(e.getMessage());
            }
            
            if ( url == null || url.trim().length() == 0)
                continue;
            
            uniqueUrlAndType.setString( 1, url);
            uniqueUrlAndType.setInt( 2, id_type);
            uniqueUrlAndType.execute();
            ResultSet rs0 = uniqueUrlAndType.getResultSet();
            
            Long cid = null;
            if ( rs0.next()) {
                cid = new Long( rs0.getLong(1) );
            }
            
            
            deleteOldLink.setInt(2, id_type);
            deleteOldLink.setLong(1, id.longValue());
            deleteOldLink.setLong(3, id.longValue());
            
            deleteOldLink.execute();
            
            if ( cid == null ) {
                nextId.execute();
                
                ResultSet rs = nextId.getResultSet();
                if (!rs.next())
                    throw new SQLException("failed comm_channel sequencer");
                
                cid = new Long( rs.getLong(1) );
                
                insert.setLong(1, cid.longValue() );
                insert.setInt(3, id_type);
                
                
                insert.setString(2,url );
                insert.execute();
            }
            
            addLink.setLong(1, id.longValue());
            addLink.setLong(2, cid.longValue());
            addLink.execute();
            
        }
    }
    
    
    private void writeExtIds(Connection conn, DemographicDetail detail) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement(
        "insert into lnk_identity2ext_id (external_id, id_identity, fk_origin )" +
        "values (?, ?, (select pk from enum_ext_id_types where name = ?)   ) " );
        
        PreparedStatement stmt1 = conn.prepareStatement(
        "select external_id from lnk_identity2ext_id " +
        "where id_identity=? and " +
        "fk_origin = (select pk from enum_ext_id_types where name = ?)" );
        
        
        
        PreparedStatement stmt2 = conn.prepareStatement(
        "update lnk_identity2ext_id set external_id = ?    " +
        "where id_identity= ?  and " +
        "fk_origin = " +
        "(select pk from enum_ext_id_types where name = ?)" );
        
        PreparedStatement stmt3 = conn.prepareStatement(
        "delete from lnk_identity2ext_id where id_identity = ?" +
        "and fk_ origin = " +
        "(select pk from enum_ext_id_types where name = ?)" );
        
        
        setExtIdsStatementValues(stmt, stmt1, stmt2 , stmt3,  detail);
        
    }
    
    private void InsertOrUpdateExtIds( PreparedStatement stmt, Object[] params )
    throws SQLException {
        for (int i = 0 ; i < params.length; ++i ) {
            stmt.setObject(i + 1, params[i]);
        }
        log.info("before executing , params count = " + params.length  );
        stmt.execute();
    }
    
    private void setExtIdsStatementValues(
    PreparedStatement insert, PreparedStatement exists,
    PreparedStatement update,  PreparedStatement delete,
    DemographicDetail detail) throws SQLException {
        
        
        
        String[] extIdNames = new String[] { publicHealthName, veteransHealthName };
        String[] props = new String[] { "publicHealthIdWithExp", "veteransId" };
        for (int i = 0; i < extIdNames.length ; ++i ) {
            try {
                String new_ext_id = BeanUtils.getSimpleProperty(detail,  props[i] ) ;
                if (new_ext_id == null )
                    continue;
                new_ext_id = new_ext_id.trim();
                
                exists.setLong(1, detail.getId().longValue()  );
                exists.setString(2,extIdNames[i]);
                exists.execute();
                ResultSet rs = exists.getResultSet();
                if (rs.next()) {
                    String ext_id = rs.getString(1);
                    if (ext_id.equals( new_ext_id) ) {
                        continue;
                    }
                    if ( new_ext_id.length() == 0)
                        InsertOrUpdateExtIds( delete, new Object[] { detail.getId(), extIdNames[i] } );
                        
                        InsertOrUpdateExtIds( update,  new Object[] { new_ext_id,  detail.getId() ,  extIdNames[i] } );
                        
                } else {
                    if ( new_ext_id.length() != 0)
                        InsertOrUpdateExtIds( insert, new Object[] { new_ext_id,  detail.getId() ,  extIdNames[i] } );
                        
                }
            } catch (IllegalAccessException iae) {
                log.info("Check Resource entry for correct ext id type names" + detail,iae);
            } catch (java.lang.reflect.InvocationTargetException ite) {
                log.info("Check Resource entry for correct ext id type names" + detail,ite);
                
            } catch (java.lang.NoSuchMethodException nsme ) {
                log.info("Check Resource entry for correct ext id type names and " + detail, nsme);
                
                
            }
        }
        
        
    }
    
    /**
     * deletes a demographic detail from
     * the database
     * @param conn
     * @param detail the demographicDetail record
     * to delete. Its id will be
     * used to find the record.
     * @throws DataSourceException
     */
    
    public void delete(Connection conn, DemographicDetail detail) throws DataSourceException {
        
    }
    
    /**
     *
     * @param conn
     * @param detail
     * @throws SQLException
     * @return an array of id values
     * for name rows that
     * match the demographic record
     * lastname and firstname.
     */
    public Long[] findIdsForNamesOf( Connection conn, DemographicDetail detail) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement("select  id_identity from names where firstnames = ? and lastnames = ?");
        stmt.setString(1, detail.getGivenname());
        stmt.setString(2, detail.getSurname());
        stmt.execute();
        ResultSet rs = stmt.getResultSet();
        java.util.List l = new java.util.ArrayList();
        while (rs.next()) {
            l.add( new Long(rs.getLong(1)) );
        }
        rs.close();
        return (Long[]) l.toArray( new Long[0] );
        
        
    }
    
    /**
     * stores the demographic record
     * with a new id value.
     * @param conn
     * @param detail
     * @throws DataSourceException
     * @return a demographic record with
     * an id value.
     */
    public DemographicDetail insert(Connection conn, DemographicDetail detail) throws DataSourceException {
        try {
         //   conn.setAutoCommit(false);
            conn.commit();
            detail = insertIdentity(conn, detail);
            insertNames(conn, detail);
            
            if (detail.getStreet() != null
            && !detail.getStreet().trim().equals("")) {
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
            throw new  DataSourceException(e);
        }
        
    }
    
    /**
     * stores any changes in the demographic record.
     * @param conn
     * @param detail
     * @throws DataSourceException
     * @return
     */
    public void update(Connection conn, DemographicDetail detail) throws DataSourceException {
        try {
  //          conn.setAutoCommit(false);
            conn.commit();
            updateIdentity(conn, detail);
            updateNames( conn, detail);
            if (detail.getStreet() != null && detail.getStreet().trim().length() >0) {
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
            throw new  DataSourceException(e);
        }
    }
    
    
    
    /**
     * find a demographic record
     * by trying to match its fields.
     */
    public DemographicDetail[] findByExample(Connection conn, DemographicDetail detailFragment) throws DataSourceException {
        List l = null;
        try {
            PreparedStatement stmt = conn.prepareStatement(
            "select v.id,  firstnames, lastnames , dob, gender , number, street, city, postcode, state, country "+
            "from  v_basic_person v left  join v_home_address a on v.id=a.id  " +
            " where " +
            " strpos( upper(firstnames), upper( ? ) ) > 0 " +
            "and strpos(upper(lastnames), upper( ?  ) ) > 0"
            );
            stmt.setString(1, detailFragment.getGivenname() ==  null?"":detailFragment.getGivenname());
            stmt.setString(2, detailFragment.getSurname() == null ? "":detailFragment.getSurname());
            stmt.execute();
            ResultSet rs = stmt.getResultSet();
            
            l = new ArrayList();
            
            while (rs.next()) {
                
                DemographicDetail detail = getDataObjectFactory().createDemographicDetail();
                
                detail.setId(new Long(rs.getLong(1)));
                
                detail.setGivenname(rs.getString(2));
                detail.setSurname(rs.getString(3));
                DateFormat format = DateFormat.getDateInstance(DateFormat.SHORT);
                detail.setBirthdate(format.format(rs.getDate(4)) );
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
            log.error("inside detail collection loop" + e  );
            e.printStackTrace();
            throw new DataSourceException(e);
        }
        log.info("Got DemographicsDetails collection size = " + l.size());
        return (DemographicDetail[]) l.toArray( new DemographicDetail[0]);
    }
    
    
    
    
    /**
     * find a demographic record
     * by its id.
     */
    public DemographicDetail findByPrimaryKey(Connection conn, Long id) throws DataSourceException {
        try {
            PreparedStatement stmt = conn.prepareStatement(
            "select * from (select * from v_basic_person p " +
            "left join v_home_address a using (id) )" +
            "as person_address left join v_person_comms_flat " +
            "on (person_address.id =v_person_comms_flat.pk_identity) " +
            " where person_address.id = ?");
            stmt.setLong(1, id.longValue());
            stmt.execute();
            ResultSet rs = stmt.getResultSet();
            ResultSetDynaClass dynaClass = new ResultSetDynaClass(rs);
            Iterator i=dynaClass.iterator();
            if ( !i.hasNext())
                throw new DataSourceException("id not found");
            DynaBean bean = (DynaBean) i.next();
            
            Util.logBean(log, bean);
            
            DemographicDetail detail = getDataObjectFactory().createDemographicDetail();
            
            String[] sqlFields = sqlToDetails[0].split(",\\s*");
            String[] detailFields = sqlToDetails[1].split(",\\s*");
            
            
            for (int j = 0; j < sqlFields.length; ++j) {
                try {
                    log.info("detail:"+detailFields[j].trim() + " bean:"+sqlFields[j]
                    + " value = " +BeanUtils.getProperty(bean,  sqlFields[j].trim() ) );
                    BeanUtils.setProperty(
                    detail, detailFields[j].trim() ,
                    BeanUtils.getProperty(bean,  sqlFields[j].trim())
                    );
                    
                } catch( Exception iae ) {
                    log.error("error copying dynabean to demographicDetail", iae);
                }
            }
            
            getExternalIds(conn, detail);
            
            
            
            Util.logBean(log, detail);
            
            return detail;
            
        }catch (Exception e2) {
            e2.printStackTrace(System.err);
            throw new  DataSourceException(e2);
            
        }
    }
    
    protected void getExternalIds(Connection conn, DemographicDetail detail) throws SQLException {
        PreparedStatement stmt2 = conn.prepareStatement(
        "select l.id_identity as id , l.external_id , e.name from lnk_identity2ext_id l, enum_ext_id_types e " +
        "where l.id_identity = ?"
        + " and l.fk_origin = e.pk "
        );
        stmt2.setLong(1,  detail.getId().longValue());
        stmt2.execute();
        
        ResultSet rs= stmt2.getResultSet();
        
        
        
        while (rs.next()) {
            String name = rs.getString(3);
            if (bundle.getString("public.health.id.name").equals(name) ) {
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
        publicHealthName = bundle.getString("public.health.id.name");
        veteransHealthName = bundle.getString("veterans.health.id.name");
        //        java.util.Enumeration keys = bundle.getKeys();
        //        while (keys.hasMoreElements()) {
        //                String key = (String) keys.nextElement();
        //                log.info( "ResourceBundle.key = " + key + ":" + bundle.getString(key)  );
        //
        //        }
        //
        //        MessageResources mr =  PropertyMessageResourcesFactory.createFactory().createResources(this.resourceParameter);
        //        log.info("RESOURCE public.health.id.name IS " +mr.getMessage("public.health.id.name"));
    }
    
}
