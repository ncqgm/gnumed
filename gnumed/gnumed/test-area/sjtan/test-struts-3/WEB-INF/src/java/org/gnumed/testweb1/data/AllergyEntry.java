/*
 * AllergyInput.java
 *
 * Created on September 26, 2004, 12:09 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface AllergyEntry {
    
    /**
     * Getter for property definite.
     * @return Value of property definite.
     */
    public boolean isDefinite();
    
    /**
     * Setter for property definite.
     * @param definite New value of property definite.
     */
    public void setDefinite(boolean definite);
    
    /**
     * Getter for property substance.
     * @return Value of property substance.
     */
    public String getSubstance();
    
    /**
     * Setter for property substance.
     * @param substance New value of property substance.
     */
    public void setSubstance(String substance);
    
    /**
     * Getter for property selected.
     * @return Value of property selected.
     */
    public boolean isSelected();
    
    /**
     * Setter for property selected.
     * @param selected New value of property selected.
     */
    public void setSelected(boolean selected);
    
}
