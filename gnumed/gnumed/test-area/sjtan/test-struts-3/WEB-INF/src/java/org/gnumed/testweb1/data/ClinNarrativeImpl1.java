/*
 * ClinNarrativeImpl1.java
 *
 * Created on September 18, 2004, 7:27 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class ClinNarrativeImpl1 extends ClinRootItemImpl1 implements ClinNarrative {
     private boolean aoe, rfe;
    
    
    /** Creates a new instance of ClinNarrativeImpl1 */
    public ClinNarrativeImpl1() {
    }
     
     
    
    public boolean isAoe() {
        return aoe;
    }
    
    public boolean isRfe() {
        return rfe;
    }
    
    public void setAoe(boolean isAoe) {
        aoe = isAoe();
    }
     
    
    public void setRfe(boolean isRfe) {
        rfe = isRfe;
    }
     
    
}
