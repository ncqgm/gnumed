/*
 * EntryClinNarrativeImpl1.java
 *
 * Created on September 25, 2004, 10:40 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class EntryClinNarrativeImpl1 extends ClinNarrativeImpl1 
implements EntryClinNarrative, ClinWhenHolder {
    ClinWhenEntryAdapter adapter;
    boolean entered;
    
    /**
     * Holds value of property linkedToPreviousEpisode.
     */
    private boolean linkedToPreviousEpisode = false;
    
    /** Creates a new instance of EntryClinNarrativeImpl1 */
    public EntryClinNarrativeImpl1() {
        super();
        adapter = new ClinWhenEntryAdapter(this);
    }
    
    public String getClinWhenString() {
        return adapter.getClinWhenString();
    }
    
    public void setClinWhenString(String clinWhenString) {
        adapter.setClinWhenString(clinWhenString);
    }
    
    public boolean isEntered() {
        return entered;
    }
    
    public void setNarrative(String narrative) {
        super.setNarrative(narrative);
        if (narrative != null && narrative.trim().length() > 0 )
        setEntered(true);
    }
    
    public void setEntered(boolean entered) {
        this.entered = entered;
    }
    
    /**
     * Getter for property linkedToPreviousEpisode.
     * @return Value of property linkedToPreviousEpisode.
     */
    public boolean isLinkedToPreviousEpisode() {
        return this.linkedToPreviousEpisode;
    }
    
    /**
     * Setter for property linkedToPreviousEpisode.
     * @param linkedToPreviousEpisode New value of property linkedToPreviousEpisode.
     */
    public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
        this.linkedToPreviousEpisode = linkedToPreviousEpisode;
    }
    
}
