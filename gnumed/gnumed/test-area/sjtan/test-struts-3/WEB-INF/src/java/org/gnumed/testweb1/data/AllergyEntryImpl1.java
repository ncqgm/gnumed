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
public class AllergyEntryImpl1 implements AllergyEntry {
    private boolean definite, selected = false;
    private String substance;
    
    /** Creates a new instance of AllergyInputImpl1 */
    public AllergyEntryImpl1() {
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
    
    public boolean isSelected() {
        return selected;
        
    }
    
    public void setSelected(boolean selected) {
        this.selected= selected;
    }
    
}
