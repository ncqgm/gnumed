/*
 * ScriptedSQLClinicalAccess.java
 *
 * Created on July 5, 2004, 7:37 PM
 */

package org.gnumed.testweb1.persist.scripted;
import   org.gnumed.testweb1.persist.ClinicalDataAccess;
import org.gnumed.testweb1.persist.scripted.ClinicalSQL;
import org.gnumed.testweb1.global.Util;
import org.gnumed.testweb1.persist.DataSourceException;

import javax.sql.DataSource;

import org.gnumed.testweb1.data.Vaccination;
/**
 *
 * @author  sjtan
 */
public class ScriptedSQLClinicalAccess implements ClinicalDataAccess {
    
    DataSource dataSource;
    ClinicalSQL sqlProvider;
    /** Creates a new instance of ScriptedSQLClinicalAccess */
    public ScriptedSQLClinicalAccess() {
    }
    
    public java.util.List getVaccines() throws DataSourceException {
        try {
         return sqlProvider.getVaccines(getDataSource().getConnection());
        } catch (Exception e) {
            throw new DataSourceException( Util.getStaceTraceN(e, 8));
        }
        
    }    
    
    public void setClinicalSQL( ClinicalSQL sqlProvider) {
        this.sqlProvider = sqlProvider;
    }
    /**
     * Getter for property dataSource.
     * @return Value of property dataSource.
     */
    public DataSource getDataSource() {
        return dataSource;
    }
    
    /**
     * Setter for property dataSource.
     * @param dataSource New value of property dataSource.
     */
    public void setDataSource(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    public void updateVaccinations(Long patientId, Vaccination[] vaccinations) throws DataSourceException {
    }
    
}
