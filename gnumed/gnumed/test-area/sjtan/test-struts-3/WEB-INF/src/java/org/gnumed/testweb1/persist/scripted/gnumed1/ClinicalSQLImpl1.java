/*
 * ClinicalSQLImpl1.java
 *
 * Created on July 5, 2004, 9:59 PM
 */

package org.gnumed.testweb1.persist.scripted.gnumed1;
import org.gnumed.testweb1.persist.ResourceBundleUsing;
import org.gnumed.testweb1.persist.DataObjectFactoryUsing;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.persist.scripted.ClinicalSQL;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;
import java.util.ResourceBundle;
import java.util.Collections;
import java.sql.SQLException;

import org.gnumed.testweb1.data.Vaccine;
import org.gnumed.testweb1.data.Vaccination;
/**
 *
 * @author  sjtan
 */

public class ClinicalSQLImpl1 implements ClinicalSQL ,
        DataObjectFactoryUsing, ResourceBundleUsing {
            
    ResourceBundle bundle;
    DataObjectFactory factory;
    List vaccines = null;
    /** Creates a new instance of ClinicalSQLImpl1 */
    public ClinicalSQLImpl1() {
    }
    
    public synchronized void refreshVaccineList(Connection conn) throws SQLException {
            PreparedStatement stmt = conn.prepareStatement(
                "select id, trade_name, short_name, last_batch_no, is_live from vaccine order by short_name"
                );
                stmt.execute();
                ResultSet rs = stmt.getResultSet();
                vaccines = new java.util.ArrayList();
                while (rs.next() ) {
                    Vaccine vaccine  = getDataObjectFactory()
                    .createVaccine(new Integer(rs.getInt(1)), rs.getString(2), rs.getString(3), rs.getBoolean(5),  rs.getString(4));
                    vaccines.add(vaccine);
                }
                
    }
    
    
    
    public List getVaccines(Connection conn) throws SQLException {
        synchronized(this) {
            if (vaccines == null) {
                 refreshVaccineList(conn);
            }
        }
       
        return new java.util.ArrayList( Collections.synchronizedList(vaccines));
        
    }
    
    public org.gnumed.testweb1.data.DataObjectFactory getDataObjectFactory() {
        return factory;
    }
    
    public void setDataObjectFactory(org.gnumed.testweb1.data.DataObjectFactory dataObjectFactory) {
        factory = dataObjectFactory;
    }
    
    public java.util.ResourceBundle getResourceBundle() {
        return bundle;
    }
    
    public void setResourceBundle(java.util.ResourceBundle resourceBundle) {
        bundle = resourceBundle;
    }
    
    public void updateVaccinations(Connection conn, java.lang.Long patientId, Vaccination[] vaccinations) throws SQLException {
        PreparedStatement stmt = conn.prepareStatement("insert into ");
    }
    
    public void updateVaccinations(java.lang.Long patientId, Vaccination[] vaccinations) throws java.sql.SQLException {
    }
    
}
