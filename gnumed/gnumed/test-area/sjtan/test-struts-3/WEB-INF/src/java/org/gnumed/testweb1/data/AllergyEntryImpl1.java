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
    private boolean marked = false;
    
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
    
   
    
    public boolean isEntered() {
        return !("".equals(substance));
    }
    

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.AllergyEntry#isMarked()
	 */
	public boolean isMarked() {
		return marked;
	}

	/* (non-Javadoc)
	 * @see org.gnumed.testweb1.data.AllergyEntry#setMarked(boolean)
	 */
	public void setMarked(boolean marked) {
		this.marked = marked;
	}
    
}
