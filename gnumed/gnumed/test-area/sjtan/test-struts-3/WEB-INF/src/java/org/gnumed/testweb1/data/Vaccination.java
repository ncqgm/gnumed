/*
 * Vaccination.java
 *
 * Created on July 6, 2004, 4:52 AM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface Vaccination extends ClinRootItem {
    public Vaccine getVaccine();
    /**
     * Getter for property tradeName.
     * @return Value of property tradeName.
     */
    public String getSite();
    
    /**
     * Setter for property tradeName.
     * @param tradeName New value of property tradeName.
     */
    public void setSite(String site);
    
    /**
     * Getter for property shortName.
     * @return Value of property shortName.
     */
    public String getVaccineGiven();
    
    /**
     * Setter for property shortName.
     * @param shortName New value of property shortName.
     */
    public void setVaccineGiven(String shortName);
    
    /**
     * Getter for property descriptiveName.
     * @return Value of property descriptiveName.
     */
    public String getComments();
    
    /**
     * Setter for property descriptiveName.
     * @param descriptiveName New value of property descriptiveName.
     */
    public void setComments(String descriptiveName);
    
    /**
     * Getter for property lastBatchNo.
     * @return Value of property lastBatchNo.
     */
    public String getBatchNo();
    
    /**
     * Setter for property lastBatchNo.
     * @param lastBatchNo New value of property lastBatchNo.
     */
    public void setBatchNo(String lastBatchNo);
    
    /**
     * Getter for property dateGivenString.
     * @return Value of property dateGivenString.
     */
    public String getDateGivenString();
    
    /**
     * Setter for property dateGivenString.
     * @param dateGivenString New value of property dateGivenString.
     */
    public void setDateGivenString(String dateGivenString);
    
}
