/*
 * Vaccination.java
 *
 * Created on July 6, 2004, 12:32 AM
 */

package org.gnumed.testweb1.data;
import org.gnumed.testweb1.global.Util;
import java.util.Map;
/**
 *
 * @author  sjtan
 */
public class DefaultVaccination extends ClinRootItemImpl1 implements Vaccination, ClinRootItem {
    
    private Vaccine vaccine;
  
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
    public DefaultVaccination( ) {
        dateGivenString = Util.getShortNowString(false);
       
    }
    
    public DefaultVaccination(Long id, Integer vacc_id, 
    String siteGiven, String batchNo, 
    java.sql.Timestamp ts , Map vaccines) {
        this.id = id;
        this.vaccine = (Vaccine) vaccines.get( vacc_id);
        this.siteGiven = siteGiven;
        this.batchNo =batchNo;
        setDateGivenString( ts.toString());
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
    public String getSite() {
        return this.siteGiven;
    }
    
    /**
     * Setter for property siteGiven.
     * @param siteGiven New value of property siteGiven.
     */
    public void setSite(String siteGiven) {
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
        return vaccine == null ? this.vaccineGiven : vaccine.getShortName();
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

    
    public Vaccine getVaccine() {
        return vaccine;
    }
     
    public String getHealthIssueName() {
        String retValue;
        
        retValue = super.getHealthIssueName();
        return retValue;
    }    
    
    public void setHealthIssueName(String healthIssueName) {
        super.setHealthIssueName(healthIssueName);
    }
    
    public java.util.Date getClin_when() {
        java.util.Date retValue;
        
        retValue = super.getClin_when();
        return retValue;
    }
    
    public void setClin_when(java.util.Date clin_when) {
        super.setClin_when(clin_when);
    }
    
}
