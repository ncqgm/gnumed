/*
 * MedicalRecordAccess01.java
 *
 * Created on September 14, 2004, 12:13 AM
 */

package org.gnumed.testweb1.persist;
import org.gnumed.testweb1.data.HealthRecord01;
/**
 *
 * @author  sjtan
 */
public interface HealthRecordAccess01 extends DataSourceUsing, DataObjectFactoryUsing, ClinicalDataAccessUsing {
    public HealthRecord01 findHealthRecordByIdentityId( long patientId) throws DataSourceException;
    public void save(HealthRecord01 healthRecord) throws DataSourceException;
     
}
