/*
 * Vaccination.java
 *
 * Created on July 6, 2004, 12:32 AM
 */

package org.gnumed.testweb1.data;
import org.gnumed.testweb1.global.Util;
/**
 *
 * @author  sjtan
 */
public class DefaultVaccination implements Vaccination {
    
    /**
     * Holds value of property dateGivenString.
     */
    private String dateGivenString;
    
    /**
     * Holds value of property siteGiven.
     */
    private String siteGiven;
    
    /**
     * Holds value of property comments.
     */
    private String comments;
    
    /**
     * Holds value of property vaccineGiven.
     */
    private String vaccineGiven;
    
    private String batchNo;
    
    /** Creates a new instance of Vaccination */
    public DefaultVaccination() {
        dateGivenString = Util.getShortNowString(false);
    }
    
    /**
     * Getter for property dateGivenString.
     * @return Value of property dateGivenString.
     */
    public String getDateGivenString() {
        return this.dateGivenString;
    }
    
    /**
     * Setter for property dateGivenString.
     * @param dateGivenString New value of property dateGivenString.
     */
    public void setDateGivenString(String dateGivenString) {
        this.dateGivenString = dateGivenString;
    }
    
    /**
     * Getter for property siteGiven.
     * @return Value of property siteGiven.
     */
    public String getSiteGiven() {
        return this.siteGiven;
    }
    
    /**
     * Setter for property siteGiven.
     * @param siteGiven New value of property siteGiven.
     */
    public void setSiteGiven(String siteGiven) {
        this.siteGiven = siteGiven;
    }
    
    /**
     * Getter for property comments.
     * @return Value of property comments.
     */
    public String getComments() {
        return this.comments;
    }
    
    /**
     * Setter for property comments.
     * @param comments New value of property comments.
     */
    public void setComments(String comments) {
        this.comments = comments;
    }
    
    /**
     * Getter for property vaccineGiven.
     * @return Value of property vaccineGiven.
     */
    public String getVaccineGiven() {
        return this.vaccineGiven;
    }
    
    /**
     * Setter for property vaccineGiven.
     * @param vaccineGiven New value of property vaccineGiven.
     */
    public void setVaccineGiven(String vaccineGiven) {
        this.vaccineGiven = vaccineGiven;
    }
    
    /**
     * Getter for property batchNo.
     * @return Value of property batchNo.
     */
    public String getBatchNo() {
        return this.batchNo;
    }
    
    /**
     * Setter for property batchNo.
     * @param batchNo New value of property batchNo.
     */
    public void setBatchNo(String batchNo) {
        this.batchNo = batchNo;
    }
    
}
