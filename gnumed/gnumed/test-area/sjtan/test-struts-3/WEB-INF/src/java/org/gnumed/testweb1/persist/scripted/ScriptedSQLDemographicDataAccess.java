/*
 * ScriptedSQLDemographicDataAccess.java
 *
 * Created on June 21, 2004, 1:32 AM
 */

package org.gnumed.testweb1.persist.scripted;
import java.security.Principal;
import java.sql.Connection;
import java.sql.SQLException;

import javax.security.auth.login.FailedLoginException;
import javax.sql.DataSource;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.business.LoginInfo;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.persist.CredentialUsing;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.DataSourceUsing;
import org.gnumed.testweb1.persist.DemographicDataAccess;
import org.gnumed.testweb1.persist.LoginInfoUsing;
import org.gnumed.testweb1.persist.ThreadLocalCredentialUsing;

/**
 *
 * @author  sjtan
 */
public class ScriptedSQLDemographicDataAccess  implements DemographicDataAccess,  DataSourceUsing , CredentialUsing, LoginInfoUsing {
    private DataSource dataSource;
    static ThreadLocalCredentialUsing localCredential ;
    static {
        localCredential = new ThreadLocalCredentialUsing();
    }
    /**
     * Holds value of property demographicDetailSQL.
     */
    private DemographicDetailSQL demographicDetailSQL;
    
    Log log = LogFactory.getLog(this.getClass());
    private static ThreadLocal threadCredentialHolder = new ThreadLocal();
    
    /** Creates a new instance of ScriptedSQLDemographicDataAccess */
    public ScriptedSQLDemographicDataAccess() {
        
    }
    
    public DemographicDetail[] findDemographicDetail(
    DemographicDetail fragment)
    throws DataSourceException{
        checkDataSourceExists();
        Connection conn = null;
        try {
            DataSource src = getDataSource();
            //conn = src.getConnection();
            conn = src.getConnection();
            conn.rollback();
            
            Util.setSessionAuthentication(conn, (Principal) localCredential.getCredential());
            
            DemographicDetail[] details = this.demographicDetailSQL.findByExample(conn, fragment);
            return details;
        
        } catch (SQLException e2) {
            e2.printStackTrace();
            throw new DataSourceException("failed connection",e2);
            
        } finally {
            try {
                conn.close();
            }catch (Exception e) {
               log.error(e ); 
            }
        }
        
    }
    
    public DemographicDetail findDemographicDetailById(final Long id) throws DataSourceException{
        Connection conn = null;
        try {
            checkDataSourceExists();
            DataSource src = getDataSource();
            conn = src.getConnection();
            conn.rollback();
            Util.setSessionAuthentication(conn, (Principal) localCredential.getCredential());
            
            return demographicDetailSQL.findByPrimaryKey(conn, id);
           
        } catch (Exception e) {
            log.error(e.getLocalizedMessage());
            throw new DataSourceException(e);
        } finally {
            try {
            conn.close();
            } catch (Exception e) {
                log.error(e.getLocalizedMessage());
            throw new DataSourceException(e);
            }
        }
    }
    
    public DemographicDetail save(DemographicDetail detail)
    throws DataSourceException{
        Connection conn = null;
        try {
            
            checkDataSourceExists();
            
            DataSource src = getDataSource();
            conn = src.getConnection();
            conn.rollback();
            Util.setSessionAuthentication(conn, (Principal) localCredential.getCredential());
            
            DemographicDetail existingDetail = null;
            try {
               existingDetail=  demographicDetailSQL.findByPrimaryKey(conn,detail.getId());
            }catch (Exception e) {
                log.info(e);
            }
            
            if (detail.getId() == null || detail.getId().intValue() == 0 || existingDetail ==null ) {
                log.info("before insert");
                detail = demographicDetailSQL.insert(conn, detail);
                log.info("after normal insert");
            }
            
            
            else {
                log.info("before update");
                demographicDetailSQL.update(conn, detail);
                log.info("after update");
            }
            
            return detail;
        } catch (Exception e) {
            
            throw new DataSourceException(e);//Util.getStaceTraceN(e, 12 ));
            
        } finally {
            try {
                if (!conn.isClosed()) {
                    conn.close();
                }
                } catch (Exception e) {
                    log.error(e.getLocalizedMessage());
                
                }
        }
    }
    
    protected void checkDataSourceExists() throws NullPointerException {
        
        dataSource.getClass();
    }
    
    
    public DataSource getDataSource() {
        return dataSource;
    }
    
    public void setDataSource(DataSource ds) {
        dataSource = ds;
    }
    
    /**
     * Getter for property demographicDetailSQL.
     * @return Value of property demographicDetailSQL.
     */
    public DemographicDetailSQL getDemographicDetailSQL() {
        return this.demographicDetailSQL;
    }
    
    /**
     * Setter for property demographicDetailSQL.
     * @param demographicDetailSQL New value of property demographicDetailSQL.
     */
    public void setDemographicDetailSQL(DemographicDetailSQL demographicDetailSQL) {
        this.demographicDetailSQL = demographicDetailSQL;
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.persist.CredentialUsing#setCredential(java.lang.Object)
     */
    public void setCredential(Object o) {
        localCredential.setCredential(o);
        
    }

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.persist.DemographicDataAccess#newDemographicDetail()
     */
    public DemographicDetail newDemographicDetail() throws DataSourceException {
        try {
          
            DemographicDetail detail =  getDemographicDetailSQL().newDemographicDetail(getDataSource().getConnection());
            return detail;
        } catch (Exception e) {
            throw new DataSourceException(e);
        }
        
       
    }

   
    
}
