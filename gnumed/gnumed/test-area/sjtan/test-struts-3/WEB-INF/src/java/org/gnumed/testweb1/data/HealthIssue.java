/*
 * HealthIssue.java
 *
 * Created on July 6, 2004, 5:22 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface HealthIssue {
    
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
     * Getter for property clinicalEpisodes.
     * @return Value of property clinicalEpisodes.
     */
    public ClinicalEpisode[] getClinicalEpisodes();
    
    /**
     * Setter for property clinicalEpisodes.
     * @param clinicalEpisodes New value of property clinicalEpisodes.
     */
    public void setClinicalEpisodes(ClinicalEpisode[] clinicalEpisodes);
    
}
