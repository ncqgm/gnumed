/*
 * ClinicalEncounter.java
 *
 * Created on July 6, 2004, 5:53 AM
 */

package org.gnumed.testweb1.data;

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
    
}
