/*
 * ScriptedSQLDemographicDataAccess.java
 *
 * Created on June 21, 2004, 1:32 AM
 */

package org.gnumed.testweb1.persist.scripted;
import java.sql.Connection;
import java.sql.SQLException;

import javax.sql.DataSource;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.persist.DataSourceUsing;
import org.gnumed.testweb1.persist.DemographicDataAccess;

/**
 *
 * @author  sjtan
 */
public class ScriptedSQLDemographicDataAccess implements DemographicDataAccess,  DataSourceUsing {
    private DataSource dataSource;
    
    /**
     * Holds value of property demographicDetailSQL.
     */
    private DemographicDetailSQL demographicDetailSQL;
    
    Log log = LogFactory.getLog(this.getClass());
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
            conn = src.getConnection();
            DemographicDetail[] details = this.demographicDetailSQL.findByExample(conn, fragment);
            return details;
        } catch (SQLException sqle) {
            log.error(sqle + ":" + sqle.getLocalizedMessage());
            
            throw new DataSourceException(sqle);
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
        try {
            
            checkDataSourceExists();
            
            DataSource src = getDataSource();
            Connection con = src.getConnection();
            
            if (detail.getId() == null || detail.getId().intValue() == 0) {
                log.info("before insert");
                detail = demographicDetailSQL.insert(con, detail);
                log.info("after normal insert");
            }
            
            
            else {
                log.info("before update");
                demographicDetailSQL.update(con, detail);
                log.info("after update");
            }
            
            return detail;
        } catch (Exception e) {
            
            throw new DataSourceException(Util.getStaceTraceN(e, 12 ));
            
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
    
   
    
}
