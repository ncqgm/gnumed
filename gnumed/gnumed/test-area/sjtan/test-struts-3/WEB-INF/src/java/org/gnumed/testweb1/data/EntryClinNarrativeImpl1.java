/*
 * EntryClinNarrativeImpl1.java
 *
 * Created on September 25, 2004, 10:40 PM
 */

package org.gnumed.testweb1.data;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;

/**
 *
 * @author  sjtan
 */
public class EntryClinNarrativeImpl1 extends ClinNarrativeImpl1 
implements EntryClinNarrative, ClinWhenHolder {
	
	Log log = LogFactory.getLog(this.getClass());
	
    ClinWhenEntryAdapter adapter;
    DateEntryAdapter issueStartedAdapter = new DateEntryAdapter(this, "healthIssueStart");
   EntryClinRootItem item = new EntryClinRootItemImpl1();
    /** Creates a new instance of EntryClinNarrativeImpl1 */
    public EntryClinNarrativeImpl1() {
        super();
        adapter = new ClinWhenEntryAdapter(this);
    }
    
    public String getHealthIssueStartString() {
        return issueStartedAdapter.getDateString();
    }
    
    public void setHealthIssueStartString(String start) {
        issueStartedAdapter.setDateString(start);
    }
    
    public String getClinWhenString() {
        return adapter.getClinWhenString();
    }
    
    public void setClinWhenString(String clinWhenString) {
        adapter.setClinWhenString(clinWhenString);
    }
    
    public boolean isEntered() {
        return item.isEntered();
    }
    
    public void setNarrative(String narrative) {
        super.setNarrative(narrative);
        if (narrative != null && narrative.trim().length() > 0 )
        setEntered(true);
        log.info( "narrative set to " + narrative + "entered = " + isEntered());
    }
    
    public void setEntered(boolean entered) {
        item.setEntered(entered);
    }
    
    /**
     * Getter for property linkedToPreviousEpisode.
     * @return Value of property linkedToPreviousEpisode.
     */
    public boolean isLinkedToPreviousEpisode() {
        return item.isLinkedToPreviousEpisode();
    }
    
    /**
     * Setter for property linkedToPreviousEpisode.
     * @param linkedToPreviousEpisode New value of property linkedToPreviousEpisode.
     */
    public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
        item.setLinkedToPreviousEpisode(linkedToPreviousEpisode);
    }
    
}
