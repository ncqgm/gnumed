/*
 * ClinicalSQL.java
 *
 * Created on July 5, 2004, 7:42 PM
 */

package org.gnumed.testweb1.persist.scripted;
import java.sql.Connection;
import org.gnumed.testweb1.persist.DataSourceException;
import org.gnumed.testweb1.data.Vaccine;
import org.gnumed.testweb1.data.Vaccination;
import java.util.List;

/**
 *
 * @author  sjtan
 */
public interface ClinicalSQL  {
    public List getVaccines(Connection conn) throws java.sql.SQLException;
    
    public void updateVaccinations(final java.lang.Long patientId, final Vaccination[] vaccinations) throws java.sql.SQLException;
    
}
