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
/**
 *
 * @author  sjtan
 */
public class ClinicalUpdateForm extends ActionForm {
    static int updateBatch = 5;
    //List vaccinations = new ArrayList();
    Vaccination[] vaccinations ;
    ClinNarrative[] narratives;
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
    
    public ClinicalUpdateForm() {
        initVaccinations();
        setEncounter( factory.createEntryClinicalEncounter() );
        
    }
    
    /** Creates a new instance of ClinicalUpdateForm */
    public ClinicalUpdateForm(DataObjectFactory factory, Integer id) {
        setPatientId(id);
        initVaccinations();
        setEncounter( factory.createEntryClinicalEncounter() );
        
        
    }
    
    
    private void initNarratives() {
         narratives =  (ClinNarrative[])getEncounter().
        getNarratives().toArray(new ClinNarrative[0]);
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
    }
    
    /**
     * Getter for property narratives.
     * @return Value of property narratives.
     */
    public ClinNarrative[] getNarratives() {
        return narratives;
    }
    
    /**
     * Indexed getter for property narrative.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
      
    public ClinNarrative getNarrative(int index) {
        return narratives[index];
    }    
       
    /**
     * Indexed setter for property narrative.
     * @param index Index of the property.
     * @param narrative New value of the property at <CODE>index</CODE>.
     */
    public void setNarrative(int index, ClinNarrative narrative) {
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
    public boolean getLinkNarrative(int index) {
        return this.linkNarrative[index];
    }    
    
    /**
     * Indexed setter for property linkNarrative.
     * @param index Index of the property.
     * @param linkNarrative New value of the property at <CODE>index</CODE>.
     */
    public void setLinkNarrative(int index, boolean linkNarrative) {
        this.linkNarrative[index] = linkNarrative;
    }    
    
    public void copyPreviousEpisodeForLinkedNarrative() {
        for ( int i=1; i < narratives.length; ++i ) {
           if ( narratives[i].isLinkedToPreviousEpisode() ) {
               narratives[i].setNewHealthIssueName(narratives[i-1].getNewHealthIssueName());
                narratives[i].setHealthIssueName(narratives[i-1].getHealthIssueName());
             
               narratives[i].setEpisode(narratives[i-1].getEpisode());
                log.info(narratives[i] + " WAS LINKED");
           } else {
           log.info(narratives[i] + " is not Linked");
           }
        }
    }
}
