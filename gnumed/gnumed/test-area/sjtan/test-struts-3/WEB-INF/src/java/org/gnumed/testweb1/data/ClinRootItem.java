/*
 * ClinRootItem.java
 *
 * Created on July 6, 2004, 6:00 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface ClinRootItem {
    
    /**
     * Getter for property narrative.
     * @return Value of property narrative.
     */
    public String getNarrative();
    
    /**
     * Setter for property narrative.
     * @param narrative New value of property narrative.
     */
    public void setNarrative(String narrative);
    
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
     * Getter for property soapCat.
     * @return Value of property soapCat.
     */
    public String getSoapCat();
    
    /**
     * Setter for property soapCat.
     * @param soapCat New value of property soapCat.
     */
    public void setSoapCat(String soapCat);
    
    /**
     * Getter for property encounter.
     * @return Value of property encounter.
     */
    public ClinicalEncounter getEncounter();
    
    /**
     * Setter for property encounter.
     * @param encounter New value of property encounter.
     */
    public void setEncounter(ClinicalEncounter encounter);
    
    /**
     * Getter for property episode.
     * @return Value of property episode.
     */
    public ClinicalEpisode getEpisode();
    
    /**
     * Setter for property episode.
     * @param episode New value of property episode.
     */
    public void setEpisode(ClinicalEpisode episode);
    
}
