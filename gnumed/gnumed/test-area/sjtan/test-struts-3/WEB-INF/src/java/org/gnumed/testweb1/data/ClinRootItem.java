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
public interface ClinRootItem extends ClinWhenHolder {
    
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
    
    /**
     * Getter for property pk.
     * @return Value of property pk.
     */
    public Integer getPk();
    
    /**
     * Setter for property pk.
     * @param pk New value of property pk.
     */
    public void setPk(Integer pk);
    
    /**
     * Getter for property healthIssueName.
     * @return Value of property healthIssueName.
     */
    public String getHealthIssueName();
    
    /**
     * Setter for property healthIssueName.
     * @param healthIssueName New value of property healthIssueName.
     */
    public void setHealthIssueName(String healthIssueName);
    
    /**
     * Getter for property clin_when.
     * @return Value of property clin_when.
     */
    public java.util.Date getClin_when();
    
    /**
     * Setter for property clin_when.
     * @param clin_when New value of property clin_when.
     */
    public void setClin_when(java.util.Date clin_when);
    
    /**
     * Getter for property newHealthIssueName.
     * @return Value of property newHealthIssueName.
     */
    public String getNewHealthIssueName();
    
    /**
     * Setter for property newHealthIssueName.
     * @param newHealthIssueName New value of property newHealthIssueName.
     */
    public void setNewHealthIssueName(String newHealthIssueName);
    
    public void normalizeHealthIssueName( ) ;
}
