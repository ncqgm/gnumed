/*
 * EntryClinRootItem.java
 *
 * Created on September 25, 2004, 9:56 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface EntryClinRootItem extends ClinRootItem, ClinWhenEntryHolder {
    
    /**
     * Getter for property clinWhenString.
     * @return Value of property clinWhenString.
     */
    public String getClinWhenString();    
    
    /**
     * Setter for property clinWhenString.
     * @param clinWhenString New value of property clinWhenString.
     */
    public void setClinWhenString(String clinWhenString);
    
}
