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
implements EntryClinRootItem, ClinWhenHolder {
    ClinWhenEntryAdapter adapter;
    boolean entered;
    
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
    
}
