/*
 * AllergyInputImpl1.java
 *
 * Created on September 26, 2004, 12:10 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class AllergyEntryImpl1 extends AllergyImpl1 implements AllergyEntry, EntryClinRootItem {
    private boolean definite, entered, linked;
    private String substance;
    ClinWhenEntryAdapter adapter = new ClinWhenEntryAdapter(this);
    
    /** Creates a new instance of AllergyInputImpl1 */
    public AllergyEntryImpl1() {
        setEntered(false);
        setLinkedToPreviousEpisode(false);
    }
    
    public String getSubstance() {
        return substance;
    }
    
    public boolean isDefinite() {
        return definite;
    }
    
    public void setDefinite(boolean definite) {
        this.definite = definite;
    }
    
    public void setSubstance(String substance) {
        this.substance = substance;
    }
    
   
    
    public String getClinWhenString() {
        return adapter.getClinWhenString();
    }
    
    public boolean isEntered() {
        return entered;
    }
    
    public void setClinWhenString(String clinWhenString) {
        adapter.setClinWhenString(clinWhenString);
    }
    
    public void setEntered(boolean entered) {
        this.entered = entered;
    }
    
    public boolean isLinkedToPreviousEpisode() {
      return   this.linked ;
    }
    
    public void setLinkedToPreviousEpisode(boolean linkedToPreviousEpisode) {
        this.linked = linkedToPreviousEpisode;
    }
    
}
