/*
 * DefaultDataObjectFactory.java
 *
 * Created on June 19, 2004, 5:28 PM
 */

package org.gnumed.testweb1.data;
import java.util.Map;
import java.util.ResourceBundle;

import org.apache.commons.beanutils.PropertyUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.gnumed.testweb1.global.Constants;
/**
 *
 * @author  sjtan
 */
public class DefaultDataObjectFactory implements DataObjectFactory {
    static Log log = LogFactory.getLog(DefaultDataObjectFactory.class);
    
    public static int nEntry =4;
     
    public final static String[] itemTypes = new String[] { "narrative", "medication", "vaccination", "allergy", "vital" };
    public final static String[] factoryMethods = new String[]
    { "createEntryClinNarrative", "createEntryMedication",
      "createEntryVaccination", "createEntryAllergy",
      "createEntryVitals"
    };
    public final static int[] counts = { nEntry, nEntry * MEDS_PER_ITEM, 0, 0, 0 };
    
    private  ClinicalEncounter loadEntryObjects( ClinicalEncounter ce) {
        log.info( ce + "BEING LOADED");
        for (int i = 0; i < itemTypes.length ; ++i) {
            try {
                int  n = counts[i] != 0 ? counts[i] : nEntry;
            	for (int j = 0; j < n ; ++j) {
                	log.info("Setting property *" + itemTypes[i] + "* index " + j + " method " + factoryMethods[i]);
                    PropertyUtils.setIndexedProperty( ce, itemTypes[i], j,
                    getClass().getMethod( factoryMethods[i], new Class[0] ).invoke( this, new Object[0] ) );
                }
            } catch (Exception e) {
                log.error(e);
                log.info( "Error with " + factoryMethods[i] + " property " + ce);
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
        
        return ce;
    }
    
    
    public ClinicalEncounter createEntryClinicalEncounter() {
        return loadEntryObjects( createClinicalEncounter() );
        
        
    }
    
    
    
    public ClinNarrative createClinNarrative() {
        ClinNarrative cn =  new ClinNarrativeImpl1();
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
    
    public ClinicalEpisode createEntryClinicalEpisode() {
        ClinicalEpisode e = createClinicalEpisode();
        e.setHealthIssue(createHealthIssue());
        return e;
    }
    
    public Vitals createVitals() {
        return new VitalsImpl1();
    }
    
    public ClinNarrative createEntryClinNarrative() {
        ClinNarrative cn = new EntryClinNarrativeImpl1();
        cn.setEpisode(createEntryClinicalEpisode());
        return cn;
        
    }
    
   
    
    public AllergyEntry createEntryAllergy() {
        AllergyEntry a= new  AllergyEntryImpl1();
        a.setEpisode(createEntryClinicalEpisode());
        return a;
    }
    
    public EntryVitals createEntryVitals() {
        EntryVitals a= new  EntryVitalsImpl1();
        a.setEpisode(createEntryClinicalEpisode());
        return a;
    }
    
    public EntryVaccination createEntryVaccination () {
    	EntryVaccination v = new EntryVaccinationImpl1();
    	String issue = getBundle().getString(Constants.Schema.DEFAULT_VACCINATION_HEALTH_ISSUE_RESOURCE_KEY);
    	String defaultEpisodeName = getBundle().getString(Constants.Schema.DEFAULT_VACCINATION_EPISODE_RESOURCE_KEY);
    	String defaultNarrative = getBundle().getString(Constants.Schema.DEFAULT_VACCINATION_NARRATIVE_RESOURCE_KEY);
    	
    	
    	configureEntryItem(v, issue, defaultEpisodeName, defaultNarrative);
    	
    	return v;
    }

	/**
	 * @param v
	 * @param issue
	 * @param defaultEpisodeName
	 * @param defaultNarrative
	 */
	private void configureEntryItem(EntryClinRootItem v, String issue, String defaultEpisodeName, String defaultNarrative) {
		v.setEpisode(createEntryClinicalEpisode());
    	
    	HealthIssue healthIssue = v.getEpisode().getHealthIssue();
		healthIssue.setDescription(issue);
		v.getEpisode().setDescription(defaultEpisodeName);
    	v.setNarrative(defaultNarrative);
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DataObjectFactory#getResourceString(java.lang.String)
	 */
	public String getResourceString(String key) {
		return getBundle().getString(key);
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.DataObjectFactory#createEntryMedication()
	 */
	public EntryMedication createEntryMedication() {
		EntryMedication m = new EntryMedicationImpl1();
		configureEntryItem(m, "prescription", "script", "medication done"	);
		return m;
	}
    
    
}
