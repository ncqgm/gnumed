/*
 * ClinicalUpdateForm.java
 *
 * Created on July 6, 2004, 12:30 AM
 */

package org.gnumed.testweb1.forms;

import java.util.Iterator;
import java.util.List;

import org.apache.commons.beanutils.BeanUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.struts.validator.ValidatorActionForm;
import org.gnumed.testweb1.data.Allergy;
import org.gnumed.testweb1.data.AllergyEntry;
import org.gnumed.testweb1.data.ClinNarrative;
import org.gnumed.testweb1.data.ClinRootItem;
import org.gnumed.testweb1.data.ClinicalEncounter;
import org.gnumed.testweb1.data.DataObjectFactory;
import org.gnumed.testweb1.data.EntryClinNarrative;
import org.gnumed.testweb1.data.EntryClinRootItem;
import org.gnumed.testweb1.data.EntryVaccination;
import org.gnumed.testweb1.data.Vaccination;
import org.gnumed.testweb1.data.Medication;

import sun.security.action.GetBooleanAction;
/**
 *
 * @author  sjtan
 */
public class ClinicalUpdateForm extends  /*org.apache.struts.action.ActionForm */
                                    BaseClinicalUpdateForm
{
    static int updateBatch = 5;
 
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
         setEncounter( factory.createEntryClinicalEncounter() );
        
        
    }
    
    public ClinicalUpdateForm(DataObjectFactory factory) {
        setEncounter(factory.createEntryClinicalEncounter() );
        setDataObjectFactory(factory);
    }
    
    
    
    /** Creates a new instance of ClinicalUpdateForm */
    public ClinicalUpdateForm(DataObjectFactory factory, Integer id) {
        
        this(factory);
        setPatientId(id);
        
        
        
    }
    
    
    public Vaccination getVaccination(int index) {
        
        return (Vaccination)getEncounter().getVaccinations().get(index);
    }
    
    
    
    
    public void setVaccination( int index, Vaccination v) {
        //Vaccination vo = (Vaccination) vaccinations.get(index);
        try {
            BeanUtils.copyProperties(getEncounter().getVaccinations().get(index), v);
        } catch (Exception e) {
            e.printStackTrace();
            
        }
         
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
         
    }
    
    
    /**
     * Indexed getter for property narrative.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    
    public EntryClinNarrative getNarrative(int index) {
        return (EntryClinNarrative)  getEncounter().getNarratives().get(index);
    }
    
    /**
     * Indexed setter for property narrative.
     * @param index Index of the property.
     * @param narrative New value of the property at <CODE>index</CODE>.
     */
    public void setNarrative(int index, EntryClinNarrative narrative) {
        //Vaccination vo = (Vaccination) vaccinations.get(index);
        try {
            BeanUtils.copyProperties(getEncounter().getNarratives().get(index), narrative);
        } catch (Exception e) {
            e.printStackTrace();
            
        }
       
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
    
    /**
     * Try to stick to form related problems.e.g
     * split new and current healthIssue names, 
     * linking of narratives
     *
     */
    public void linkObjects() {
    	normalizeHealthIssueNames();
    	
        copyPreviousEpisodeForLinkedNarrative();
      
        getEncounter().mergeReferences();
      
        transferNarrativeDetailToEnteredAllergies();
    }
   
	

	/**
	 * 
	 */
	private void normalizeHealthIssueNames() {
		// TODO Auto-generated method stub
		Iterator i = getNarratives().iterator();
		while (i.hasNext()) {
			ClinNarrative cn= (ClinNarrative) i.next();
			cn.normalizeHealthIssueName();
		}
	}




	/**
	 * @param vaccinations
	 */
	private void copyMatchingNarrativeLinksToRootItems(List vaccinations) {
		// TODO Auto-generated method stub
		Iterator i = vaccinations.iterator();
		while (i.hasNext() ) {
			
			EntryVaccination v = (EntryVaccination) i.next();
			String description = v.getHealthIssueName();
			ClinNarrative[] ns = getEncounter().findNarrativeBySoapCat(description, "p");
			if (ns.length ==0) {
				ns = getEncounter().findNarrativeByHealthIssueName(description);
			}
			if (ns.length > 0) {
				copyOverEpisodeAndEncounter(ns[0], v, v.getVaccineGiven() );
			} else {
				v.getEpisode().setDescription("vaccination");
				
			}
		}
	}




	void copyPreviousEpisodeForLinkedNarrative() {
        for ( int i=1; i < getEncounter().getNarratives().size(); ++i ) {
            log.info("Checking narrative :healthIssue" 
                    + getNarrative(i).getHealthIssueName() + " , is linked is "
                    + getNarrative(i).isLinkedToPreviousEpisode() );
            if ( getNarrative(i).isLinkedToPreviousEpisode() ) {
            	getNarrative(i).setEpisode(getNarrative(i-1).getEpisode());
                log.info(getNarrative(i)+ " :"+ getNarrative(i).getNarrative() +  "#"+i+" WAS LINKED");
            } else {
                log.info(getNarrative(i) +" :"+ getNarrative(i).getNarrative()+ "*** #"+i+" is NOT Linked **");
            }
        }
    }
    
    void copyLinksToClinRootItems(java.util.List items) {
        if (items == null)
            return;
        for ( int i= 0; i < getEncounter().getNarratives().size(); ++i ) {
            ClinRootItem n = getNarrative(i);
            if ( i >= items.size()) { 
                log.info("number of narratives "+ i + " exceeds "+ items.size());
                continue;
            }
                  log.info("copying from #" + n + " to " + items.get(i));
       
            EntryClinRootItem p = (EntryClinRootItem) items.get(i);
            String label = String.valueOf(i);
            copyOverEpisodeAndEncounter(n, p, label);
            
        }
    }
    
    
    /**
	 * @param n
	 * @param p
	 * @param label
	 */
	private void copyOverEpisodeAndEncounter(ClinRootItem n, EntryClinRootItem p, String label) {
		if (p.isEntered() ) {
		   log.info(p.getClass()+"#"+ label + " is EDITED");
		    try {
		        BeanUtils.copyProperties( p, n);
		        n.setId(new Long(-1));
		    } catch (Exception e) {
		        log.error(e.getLocalizedMessage(), e);
		        
		    }
		} else {
		    log.info(p.getClass()+"#"+label + " was not edited");
		}
	}




	void transferNarrativeDetailToEnteredAllergies() {
        for ( int i = 0; i < getEncounter().getNarratives().size() ; ++i) {
            
            ClinNarrative n = ( ClinNarrative) getNarrative(i);
            
            if (getAllergy(i).isEntered()) {
            	getAllergy(i).setClin_when(n.getClin_when());
                getAllergy(i).setNarrative(n.getNarrative());
                
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
        return (AllergyEntry)getAllergies().get(index);
    }
    
    /**
     * Indexed setter for property allergyEntry.
     * @param index Index of the property.
     * @param allergyEntry New value of the property at <CODE>index</CODE>.
     */
    public void setAllergy(int index, Allergy allergyEntry) {
        getEncounter().setAllergy(index, allergyEntry);
    }
    
    /**
     * Getter for property allergies.
     * @return Value of property allergies.
     */
    public  List getAllergies() {
        return getEncounter().getAllergies();
    }
    
    /**
     * Getter for property vitals.
     * @return Value of property vitals.
     */
    public  List getVitals() {
        return getEncounter().getVitals();
    }
     
    public List getNarratives() {
    	return getEncounter().getNarratives();
    }
    
    public  List getVaccinations() {
        return getEncounter().getVaccinations();
    }
     
    /**
     * Indexed getter for property medication.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public Medication getMedication(int index) {
        return getEncounter().getMedication(index);
    }
    
    /**
     * Indexed setter for property medication.
     * @param index Index of the property.
     * @param medication New value of the property at <CODE>index</CODE>.
     */
    public void setMedication(int index, Medication medication) {
        getEncounter().setMedication(index, medication);
    }
    
    public List getMedications() {
        return getEncounter().getMedications();
        
    }
    
}
