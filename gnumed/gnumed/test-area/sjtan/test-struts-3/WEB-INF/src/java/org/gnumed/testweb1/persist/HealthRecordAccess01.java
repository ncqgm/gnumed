/*
 * MedicalRecordAccess01.java
 *
 * Created on September 14, 2004, 12:13 AM
 */

package org.gnumed.testweb1.persist;
import java.util.List;

import org.gnumed.testweb1.data.HealthRecord01;
import org.gnumed.testweb1.data.HealthSummary01;
import org.gnumed.testweb1.data.ClinicalEncounter;
/**
 *
 * @author  sjtan
 */
public interface HealthRecordAccess01 extends DataSourceUsing, DataObjectFactoryUsing, ClinicalDataAccessUsing {
    public HealthRecord01 findHealthRecordByIdentityId( long patientId) throws DataSourceException;
    public void save(HealthRecord01 healthRecord) throws DataSourceException;
    
    /**
     * @param encounter - the encounter holding entry items to save.
     * @param summary - the health summary object holding reference data (e.g. encounter location)
     * @param nonFatalExceptions - exceptions during saving encounter items that are non-fatal, e.g. nonexistent physical exam test results
     * @throws DataSourceException - a fatal exception during the course of saving (e.g. non connection, the base encounter detail unable to be generated)
     */
    public void save(ClinicalEncounter encounter, HealthSummary01 summary, List nonFatalExceptions )throws DataSourceException;
}
