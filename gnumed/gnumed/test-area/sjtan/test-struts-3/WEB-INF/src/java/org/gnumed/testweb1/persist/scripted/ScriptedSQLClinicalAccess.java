/*
 * ScriptedSQLClinicalAccess.java
 *
 * Created on July 5, 2004, 7:37 PM
 */

package org.gnumed.testweb1.persist.scripted;
import   org.gnumed.testweb1.persist.ClinicalDataAccess;
import org.gnumed.testweb1.persist.CredentialUsing;
import org.gnumed.testweb1.persist.ThreadLocalCredentialUsing;
import org.gnumed.testweb1.persist.scripted.ClinicalSQL;
import org.gnumed.testweb1.persist.DataSourceException;

import javax.sql.DataSource;
import org.gnumed.testweb1.data.Vaccine;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.global.Util;

import java.security.Principal;
import java.util.Map;
import java.util.Iterator;
/**
 *
 * @author  sjtan
 */
public class ScriptedSQLClinicalAccess implements ClinicalDataAccess , CredentialUsing{
    
    DataSource dataSource;
    ClinicalSQL sqlProvider;
    Map vaccMap;
    static ThreadLocalCredentialUsing threadCredential;
    static {
        threadCredential = new ThreadLocalCredentialUsing();
    }
    /** Creates a new instance of ScriptedSQLClinicalAccess */
    public ScriptedSQLClinicalAccess() {
    }
    
    public java.util.List getVaccines() throws DataSourceException {
        java.sql.Connection conn = null;
        try {
           conn = getDataSource().getConnection();
           
           Util.setSessionAuthentication(conn, (Principal)threadCredential.getCredential());
           
            return sqlProvider.getVaccines(conn);
        } catch (Exception e) {
            throw new DataSourceException( e);//Util.getStaceTraceN(e, 8));
        } finally {
            try {
               conn.close();
            }catch (Exception e) {
             throw new DataSourceException(e); //Util.getStaceTraceN(e, 8));
        }
        }
        
        
    }
    
    public Map getVaccineMap() throws DataSourceException {
        if ( vaccMap == null) {
            vaccMap = new java.util.HashMap();
            Iterator i = getVaccines().iterator();
            while (i.hasNext()) {
                Vaccine v = (Vaccine)i.next();
                System.err.println("VACCINE=" + v.getTradeName() + " id =" + v.getId());
                vaccMap.put(v.getId(), v);
                
            }
            
        }
        return vaccMap;
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

    /* (non-Javadoc)
     * @see org.gnumed.testweb1.persist.CredentialUsing#setCredential(java.lang.Object)
     */
    public  void setCredential(Object o) {
        // TODO Auto-generated method stub
        threadCredential.setCredential(o);
    }
    
}
