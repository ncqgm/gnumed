/*
 * DemographicDetailSQLUpdates.java
 *
 * Created on June 20, 2004, 5:26 PM
 */

package org.gnumed.testweb1.persist.scripted;

import java.sql.Connection;

import org.gnumed.testweb1.data.DemographicDetail;
import org.gnumed.testweb1.persist.DataSourceException;
/**
 *
 * @author  sjtan
 */
public interface DemographicDetailSQL {
    
    public DemographicDetail insert( Connection conn, DemographicDetail detail) throws DataSourceException;
    
    public void update( Connection conn, DemographicDetail detail) throws DataSourceException;
    
    public void delete( Connection conn, DemographicDetail detail ) throws DataSourceException;
    
    public DemographicDetail findByPrimaryKey(Connection conn, Long id) throws DataSourceException;

    public DemographicDetail[] findByExample(Connection conn, DemographicDetail detailFragment) throws DataSourceException;

    /**
     * 
     */
   public DemographicDetail newDemographicDetail(Connection conn) throws DataSourceException;
 
    
}
