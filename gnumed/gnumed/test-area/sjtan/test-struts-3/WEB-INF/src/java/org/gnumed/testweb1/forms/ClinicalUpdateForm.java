/*
 * ClinicalUpdateForm.java
 *
 * Created on July 6, 2004, 12:30 AM
 */

package org.gnumed.testweb1.forms;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.action.ActionForm;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinicalEncounter;
import org.gnumed.testweb1.data.ClinicalEncounterImpl1;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.DefaultVaccination;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.data.AllergyEntry;
import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.EntryClinRootItem;
import org.gnumed.testweb1.data.EntryClinNarrative;
import org.gnumed.testweb1.data.Vitals;
import java.util.ListIterator;
/**
 *
 * @author  sjtan
 */
public class ClinicalUpdateForm extends ActionForm {
    static int updateBatch = 5;
    //List vaccinations = new ArrayList();
    Vaccination[] vaccinations ;
    EntryClinNarrative[] narratives;
    String test;
    Log log = LogFactory.getLog(this.getClass());
    
    static DataObjectFactory factory;
    
    public static void setDataObjectFactory(DataObjectFactory _factory ) {
        factory = _factory;
        
    }
    
    /**
     * Holds value of property encounter.
     */
    private ClinicalEncounter encounter;
    
    /**
     * Holds value of property patientId.
     */
    private Integer patientId;
    
    /**
     * Holds value of property linkNarrative.
     */
    private boolean[] linkNarrative;
    
    
    /**
     * Holds value of property allergyEntry.
     */
    private AllergyEntry[] allergyEntry;
    
    /**
     * Holds value of property allergies.
     */
    private java.util.List allergies  ;
    
    private java.util.List vitals;
    
    public ClinicalUpdateForm() {
        initVaccinations();
        setEncounter( factory.createEntryClinicalEncounter() );
        
        
    }
    
    
    
    
    /** Creates a new instance of ClinicalUpdateForm */
    public ClinicalUpdateForm(DataObjectFactory factory, Integer id) {
        this();
        setPatientId(id);
        
        
        
    }
    
    
    private void initAllergies() {
        allergies = getEncounter().getAllergies();
    }
    
    private void initNarratives() {
        narratives =  (EntryClinNarrative[])getEncounter().
        getNarratives().toArray(new EntryClinNarrative[0]);
        //    narratives = new ClinNarrative[nn.length];
        //    System.arraycopy(nn, 0, narratives, 0, nn.length);
        
    }
    
    private void initVaccinations() {
        vaccinations = new Vaccination[updateBatch];
        for (int i =0; i < updateBatch; ++i) {
            vaccinations[i] = new DefaultVaccination() ;
        }
        log.info("ClinicalForm was initialized");
        
    }
    
    
    public Vaccination[] getVaccinations() {
        return (Vaccination[]) vaccinations;
    }
  /*
    public DefaultVaccination getVaccination(int index) {
        return (DefaultVaccination) vaccinations.get(index);
    }
   */
    
    public Vaccination getVaccination(int index) {
        
        return vaccinations[index];
    }
    
    
    
    
    public void setVaccination( int index, Vaccination v) {
        //Vaccination vo = (Vaccination) vaccinations.get(index);
        try {
            BeanUtils.copyProperties(vaccinations[index], v);
        } catch (Exception e) {
            e.printStackTrace();
            
        }
        log.info("COPIED vaccine="+ vaccinations[index]);
    }
    
    public String getTest() {
        return test;
    }
    public void setTest(String test) {
        this.test=test;
    }
    
    /**
     * Getter for property encounter.
     * @return Value of property encounter.
     */
    public ClinicalEncounter getEncounter() {
        return this.encounter;
        
    }
    
    /**
     * Setter for property encounter.
     * @param encounter New value of property encounter.
     */
    public void setEncounter(ClinicalEncounter encounter) {
        this.encounter = encounter;
        initNarratives();
        initAllergies();
    }
    
    /**
     * Getter for property narratives.
     * @return Value of property narratives.
     */
    public EntryClinNarrative[] getNarratives() {
        return narratives;
    }
    
    /**
     * Indexed getter for property narrative.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    
    public EntryClinNarrative getNarrative(int index) {
        return narratives[index];
    }
    
    /**
     * Indexed setter for property narrative.
     * @param index Index of the property.
     * @param narrative New value of the property at <CODE>index</CODE>.
     */
    public void setNarrative(int index, EntryClinNarrative narrative) {
        //Vaccination vo = (Vaccination) vaccinations.get(index);
        try {
            BeanUtils.copyProperties(narratives[index], narrative);
        } catch (Exception e) {
            e.printStackTrace();
            
        }
        log.info("COPIED narratives="+ narratives[index]);
    }
    
    /**
     * Getter for property patientId.
     * @return Value of property patientId.
     */
    public Integer getPatientId() {
        return this.patientId;
    }
    
    /**
     * Setter for property patientId.
     * @param patientId New value of property patientId.
     */
    public void setPatientId(Integer patientId) {
        this.patientId = patientId;
    }
    
    /**
     * Indexed getter for property linkNarrative.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public boolean getLinkedToPreviousEpisode(int index) {
        return this.linkNarrative[index];
    }
    
    /**
     * Indexed setter for property linkNarrative.
     * @param index Index of the property.
     * @param linkNarrative New value of the property at <CODE>index</CODE>.
     */
    public void setLinkedToPreviousEpisode(int index, boolean linkNarrative) {
        this.linkNarrative[index] = linkNarrative;
    }
    
    public void linkObjects() {
        copyPreviousEpisodeForLinkedNarrative();
        
        copyLinksToClinRootItems(getEncounter().getAllergies());
        
        copyLinksToClinRootItems(getEncounter().getVitals());
        
        
        alterAllergyMarkedNarratives();
    }
    
    void copyPreviousEpisodeForLinkedNarrative() {
        for ( int i=1; i < narratives.length; ++i ) {
            if ( narratives[i].isLinkedToPreviousEpisode() ) {
                narratives[i].setNewHealthIssueName(narratives[i-1].getNewHealthIssueName());
                narratives[i].setHealthIssueName(narratives[i-1].getHealthIssueName());
                
                narratives[i].setEpisode(narratives[i-1].getEpisode());
                log.info(narratives[i] +  "#"+i+" WAS LINKED");
            } else {
                log.info(narratives[i] + "*** #"+i+" is not Linked **");
            }
        }
    }
    
    void copyLinksToClinRootItems(java.util.List items) {
        if (items == null)
            return;
        for ( int i= 0; i < narratives.length; ++i ) {
            ClinRootItem n = (ClinRootItem) narratives[i];
            if ( i >= items.size()) { 
                log.info("number of narratives "+ i + " exceeds "+ items.size());
                continue;
            }
                  log.info("copying from #" + n + " to " + items.get(i));
       
            EntryClinRootItem p = (EntryClinRootItem) items.get(i);
            
            if (p.isEntered() ) {
                log.debug(p.getClass()+"#"+ i + " is EDITED");
                try {
                    BeanUtils.copyProperties( p, n);
                    n.setId(new Long(-1));
                } catch (Exception e) {
                    log.error(e.getLocalizedMessage(), e);
                    
                }
            } else {
                log.info(p.getClass()+"#"+i + " was not edited");
            }
            
        }
    }
    
    
    void alterAllergyMarkedNarratives() {
        for ( int i = 0; i < narratives.length ; ++i) {
            
            ClinNarrative n = ( ClinNarrative) narratives[i];
            
            if (getAllergy(i).isEntered()) {
                String title = "ALLERGY:" + getAllergy(i).getSubstance() + " definite:" +
                String.valueOf( getAllergy(i).isDefinite()) + ".  \n\r";
                n.setNarrative(title +( n.getNarrative() != null ? n.getNarrative(): "" ) );
                log.info("ALLERGY COPIED TO NARRATIVE:" + i + getAllergy(i).getSubstance());
                n.setId(null);
            }
            
            
        }
    }
    
    /**
     * Indexed getter for property allergyEntry.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public AllergyEntry getAllergy(int index) {
        return (AllergyEntry)this.allergies.get(index);
    }
    
    /**
     * Indexed setter for property allergyEntry.
     * @param index Index of the property.
     * @param allergyEntry New value of the property at <CODE>index</CODE>.
     */
    public void setAllergy(int index, Allergy allergyEntry) {
        this.allergies.set(index, allergyEntry);
    }
    
    /**
     * Getter for property allergies.
     * @return Value of property allergies.
     */
    public java.util.List getAllergies() {
        return this.allergies;
    }
    
    /**
     * Getter for property vitals.
     * @return Value of property vitals.
     */
    public java.util.List getVitals() {
        return vitals;
    }
    
    /**
     * Setter for property vitals.l
     * @param vitals New value of property vitals.
     */
    public void setVitals(java.util.List vitals) {
        this.vitals = vitals;
    }
    
}
