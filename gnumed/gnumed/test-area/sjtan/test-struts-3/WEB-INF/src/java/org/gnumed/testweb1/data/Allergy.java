/*
 * Allergy.java
 *
 * Created on July 12, 2004, 7:00 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface Allergy extends ClinRootItem {
   
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
     * Getter for property generics.
     * @return Value of property generics.
     */
    public String getGenerics();
    
    /**
     * Setter for property generics.
     * @param generics New value of property generics.
     */
    public void setGenerics(String generics);
    
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
    
}
