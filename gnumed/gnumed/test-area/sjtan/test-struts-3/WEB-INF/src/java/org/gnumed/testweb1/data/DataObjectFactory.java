/*
 * DataObjectFactory.java
 *
 * Created on June 19, 2004, 5:24 PM
 */

package org.gnumed.testweb1.data;
import java.util.Map;
import java.util.ResourceBundle;
/**
 *
 * @author  sjtan
 */
public interface DataObjectFactory {
    public final static int MEDS_PER_ITEM=4;
    
    DemographicDetail createDemographicDetail();
    
    
    
    Vaccine createVaccine(Integer id, String tradeName, String shortName, boolean isLive, 
        String lastBatchNo ) ;
    
    
    public Vaccination createVaccination(Long id, Integer vacc_id, 
    String siteGiven, String batchNo, 
    java.sql.Timestamp ts , Map vaccines) ;
     
          
    
    HealthIssue createHealthIssue( PatientIdentifiable pi, String description );
    
    ClinicalEncounter createClinicalEncounter( );
     
     public Allergy createAllergy();
     public Vaccination createVaccination();
     public ClinNarrative createClinNarrative();
     public Medication createMedication();
     public HealthIssue createHealthIssue();
     public ClinicalEpisode createClinicalEpisode();
     public Vitals createVitals();
     HealthRecord01 createHealthRecord(HealthSummary01 hs);
     
     public ClinicalEncounter createEntryClinicalEncounter();
     public ClinNarrative createEntryClinNarrative();
     public AllergyEntry createEntryAllergy();
     public EntryVitals createEntryVitals();
     public EntryMedication createEntryMedication();
     
     public void setBundle(ResourceBundle bundle);
     public ResourceBundle getBundle();
     public String getResourceString(String key);
	}
