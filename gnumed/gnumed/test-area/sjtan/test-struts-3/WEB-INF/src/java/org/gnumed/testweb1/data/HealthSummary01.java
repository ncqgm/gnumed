/*
 * HealthSummary.java
 *
 * Created on September 18, 2004, 1:04 PM
 */

package org.gnumed.testweb1.data;
import java.util.List;
/**
 *
 * @author  sjtan
 */
public interface HealthSummary01 {
    public List getHealthIssues();
    public List getMedications( );
    public List getAllergys( );
    public List  getVaccinations();
    public List getClinEpisodes();
    Long getIdentityId();
    
    /**
     * Getter for property encounters.
     * @return Value of property encounters.
     */
    public List getEncounters();
    
    /**
     * Setter for property encounters.
     * @param encounters New value of property encounters.
     */
    public void setEncounters(List encounters);
    
    public boolean hasHealthIssue(final HealthIssue issue);
    public boolean addHealthIssue(  HealthIssue issue);
}
    
