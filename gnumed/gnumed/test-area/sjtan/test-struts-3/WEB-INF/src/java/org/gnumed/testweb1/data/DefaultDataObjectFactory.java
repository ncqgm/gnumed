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
import org.apache.commons.beanutils.PropertyUtils;
/**
 *
 * @author  sjtan
 */
public class DefaultDataObjectFactory implements DataObjectFactory {
    
    
    public static int nEntryVaccs =10, nEntryMeds =20, nEntryNarratives=6, nEntryAllergies=5;
    
    public final static String[] itemTypes = new String[] { "narrative", "medication", "vaccination", "allergy" };
    public final static String[] factoryMethods = new String[] { "createClinNarrative", "createMedication", "createVaccination", "createAllergy" };
   
    final static int[] nEntries = new int[] {nEntryNarratives, nEntryMeds, nEntryVaccs, nEntryAllergies };
    
    private  ClinicalEncounter loadEntryObjects( ClinicalEncounter ce, ClinNarrative n, Medication m, Vaccination v, Allergy a) {
         Object[] oo = new Object[] { n, m, v, a };
        for (int i = 0; i < nEntries.length; ++i) {
            try {
                for (int j = 0; j < nEntries[i]; ++j) {
                    PropertyUtils.setIndexedProperty( ce, itemTypes[i], j, 
                    getClass().getMethod( factoryMethods[i], new Class[0] ).invoke( this, new Object[0] ) );
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
            
        }
        return ce;
    }
    
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
        return new HealthIssueImpl1();
    }
    
    public Allergy createAllergy() {
        return new AllergyImpl1();
    }
    
    public HealthRecord01 createHealthRecord(HealthSummary01 hs) {
        return new HealthRecordImpl01(hs);
    }
    
    public Vaccination createVaccination(Long id, Integer vacc_id, String siteGiven, String batchNo, java.sql.Timestamp ts, Map vaccines) {
        return new DefaultVaccination( id, vacc_id, siteGiven, batchNo, ts, vaccines);
    }
    
    public ClinicalEncounter createClinicalEncounter() {
        ClinicalEncounter ce =  new ClinicalEncounterImpl1();
        Vitals vitals = createVitals();
        ce.setVitals(vitals);
        return ce;
    }
    
    
    public ClinicalEncounter createEntryClinicalEncounter() {
        return loadEntryObjects( createClinicalEncounter(),
        createClinNarrative(), createMedication(), createVaccination(), createAllergy() );
        
       
    }
     
    
    
    public ClinNarrative createClinNarrative() {
        ClinNarrative cn =  new ClinNarrativeImpl1();
        cn.setEpisode(createClinicalEpisode());
        return cn;
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
    
    public Vitals createVitals() {
        return new VitalsImpl1();
    }
    
    
}
