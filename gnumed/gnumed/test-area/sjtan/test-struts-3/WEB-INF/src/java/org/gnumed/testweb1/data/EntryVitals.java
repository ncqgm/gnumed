/*
 * EntryVitals.java
 *
 * Created on 26 October 2004, 07:45
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface EntryVitals extends Vitals, EntryClinRootItem {
    boolean isSet(String propertyName);
    
    /**
     * Getter for property heightString.
     * @return Value of property heightString.
     */
    public String getHeightString();    
    
    /**
     * Setter for property heightString.
     * @param heightString New value of property heightString.
     */
    public void setHeightString(String heightString);
    
    /**
     * Getter for property weightString.
     * @return Value of property weightString.
     */
    public String getWeightString();
    
    /**
     * Setter for property weightString.
     * @param weightString New value of property weightString.
     */
    public void setWeightString(String weightString);
    
}
