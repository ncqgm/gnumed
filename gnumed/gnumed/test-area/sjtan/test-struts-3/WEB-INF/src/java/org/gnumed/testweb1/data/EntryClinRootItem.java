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
    
    /**
     * Getter for property entered.
     * @return Value of property entered.
     */
    public boolean isEntered();
    
    /**
     * Setter for property entered.
     * @param entered New value of property entered.
     */
    public void setEntered(boolean entered);
    
}
