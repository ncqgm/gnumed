/*
 * ClinicalEncounter.java
 *
 * Created on July 6, 2004, 5:53 AM
 */

package org.gnumed.testweb1.data;
import java.util.Collection;
import java.util.List;
/**
 *
 * @author  sjtan
 */
public interface ClinicalEncounter {
    
    /**
     * Getter for property id.
     * @return Value of property id.
     */
    public Long getId();
    
    /**
     * Setter for property id.
     * @param id New value of property id.
     */
    public void setId(Long id);
    
    /**
     * Getter for property description.
     * @return Value of property description.
     */
    public String getDescription();
    
    /**
     * Setter for property description.
     * @param description New value of property description.
     */
    public void setDescription(String description);
    
    /**
     * Getter for property started.
     * @return Value of property started.
     */
    public java.util.Date getStarted();
    
    /**
     * Setter for property started.
     * @param started New value of property started.
     */
    public void setStarted(java.util.Date started);
    
    /**
     * Getter for property lastAffirmed.
     * @return Value of property lastAffirmed.
     */
    public java.util.Date getLastAffirmed();
    
    /**
     * Setter for property lastAffirmed.
     * @param lastAffirmed New value of property lastAffirmed.
     */
    public void setLastAffirmed(java.util.Date lastAffirmed);
    
    /**
     * Getter for property encounterType.
     * @return Value of property encounterType.
     */
    public String getEncounterType();
    
    /**
     * Setter for property encounterType.
     * @param encounterType New value of property encounterType.
     */
    public void setEncounterType(String encounterType);
    
    /**
     * Indexed getter for property vaccination.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public Vaccination getVaccination(int index);
    
    /**
     * Indexed setter for property vaccination.
     * @param index Index of the property.
     * @param vaccination New value of the property at <CODE>index</CODE>.
     */
    public void setVaccination(int index, Vaccination vaccination);
    
    /**
     * Indexed getter for property allergy.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public Allergy getAllergy(int index);
    
    /**
     * Indexed setter for property allergy.
     * @param index Index of the property.
     * @param allergy New value of the property at <CODE>index</CODE>.
     */
    public void setAllergy(int index, Allergy allergy);
    
    /**
     * Indexed getter for property medication.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public Medication getMedication(int index);
    
    /**
     * Indexed setter for property medication.
     * @param index Index of the property.
     * @param medication New value of the property at <CODE>index</CODE>.
     */
    public void setMedication(int index, Medication medication);
    
    /**
     * Getter for property location.
     * @return Value of property location.
     */
    public String getLocation();
    
    /**
     * Setter for property location.
     * @param location New value of property location.
     */
    public void setLocation(String location);
    
    /**
     * Indexed getter for property narrative.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public ClinNarrative getNarrative(int index);
    
    public List getVaccinations();

    public List getMedications();
    
    public List getNarratives();
    /**
     * Indexed setter for property narrative.
     * @param index Index of the property.
     * @param narrative New value of the property at <CODE>index</CODE>.
     */
    public void setNarrative(int index, ClinNarrative narrative);
    
    public void removeNarrative(ClinNarrative narrative);
    
    public void sortRootItems(final java.util.Comparator comparator) ;
    
    /**
     * Getter for property allergies.
     * @return Value of property allergies.
     */
    public java.util.List getAllergies();
    
    /**
     * Getter for property rootItems.
     * @return Value of property rootItems.
     */
    public ClinRootItem[] getRootItems();
    
    /**
     * Indexed getter for property vital.
     * @param index Index of the property.
     * @return Value of the property at <CODE>index</CODE>.
     */
    public EntryVitals getVital(int index);
    
    /**
     * Indexed setter for property vital.
     * @param index Index of the property.
     * @param vital New value of the property at <CODE>index</CODE>.
     */
    public void setVital(int index, EntryVitals vital);
    
    /**
     * Getter for property vitals.
     * @return Value of property vitals.
     */
    public java.util.List getVitals();
    
    public ClinNarrative[] findNarrativeByHealthIssueName(String issueName) ;
    
    public ClinNarrative[] findNarrativeBySoapCat(String issueName, String soapCat );


    public EntryClinRootItem[] getEntryRootItems();
    
    public boolean contains(ClinRootItem item);
    
    public boolean addClinRootItem(ClinRootItem item);
    
    public Collection getMappedIssues();
	public Collection getMappedEpisodes() ;
	public void mergeReferences() ;

	/**
	 * @param hi
	 */
	public void replaceMappedIssue(HealthIssue hi);

	
}
