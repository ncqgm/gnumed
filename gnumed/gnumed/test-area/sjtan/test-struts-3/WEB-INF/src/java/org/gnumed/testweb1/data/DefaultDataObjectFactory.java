/*
 * DefaultDataObjectFactory.java
 *
 * Created on June 19, 2004, 5:28 PM
 */

package org.gnumed.testweb1.data;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DefaultDemographicDetail;
import org.gnumed.testweb1.data.DemographicDetail;
import org.apache.struts.config.PlugInConfig;
import java.util.Map;
import java.util.ResourceBundle;
/**
 *
 * @author  sjtan
 */
public class DefaultDataObjectFactory implements DataObjectFactory {
    
    /**
     * Holds value of property bundle.
     */
    private ResourceBundle bundle;
    
    /** Creates a new instance of DefaultDataObjectFactory */
    public DefaultDataObjectFactory() {
    }
    
    public DemographicDetail createDemographicDetail() {
        DemographicDetail detail = new DefaultDemographicDetail() ;
        return detail;
    }
    
    /**
     * Getter for property bundle.
     * @return Value of property bundle.
     */
    public ResourceBundle getBundle() {
        return this.bundle;
    }
    
    /**
     * Setter for property bundle.
     * @param bundle New value of property bundle.
     */
    public void setBundle(ResourceBundle bundle) {
        this.bundle = bundle;
    }
    
    public Vaccine createVaccine(Integer id, String tradeName, String shortName, boolean isLive, String lastBatchNo) {
        Vaccine vaccine = new DefaultVaccine( id, tradeName, shortName, isLive, lastBatchNo);
        return vaccine;
    }
    
    public HealthIssue createHealthIssue(PatientIdentifiable pi, String description) {
    return null;
    }
    
    public Allergy createAllergy() {
        return null;
    }
    
    public HealthRecord01 createHealthRecord(HealthSummary01 hs) {
        return new HealthRecordImpl01(hs);
    } 
    
    public Vaccination createVaccination(Long id, Integer vacc_id, String siteGiven, String batchNo, java.sql.Timestamp ts, Map vaccines) {
        return new DefaultVaccination( id, vacc_id, siteGiven, batchNo, ts, vaccines);
    }
    
    public ClinicalEncounter createClinicalEncounter() {
        return new ClinicalEncounterImpl1();
    }    
    
    public ClinNarrative createClinNarrative() {
        return new ClinNarrativeImpl1();
    }
    
    public Medication createMedication() {
        return new MedicationImpl1();
    }
    
    public Vaccination createVaccination() {
        return new DefaultVaccination();
    }
    
    public HealthIssue createHealthIssue() {
        return new HealthIssueImpl1();
    }
    
    public ClinicalEpisode createClinicalEpisode() {
        return new ClinicalEpisodeImpl1();
    }
    
}
