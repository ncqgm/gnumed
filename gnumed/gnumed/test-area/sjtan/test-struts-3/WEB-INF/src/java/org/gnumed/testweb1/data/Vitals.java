/*
 * Vitals.java
 *
 * Created on September 19, 2004, 6:20 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public interface Vitals extends ClinRootItem {
    
    /**
     * Getter for property systolic.
     * @return Value of property systolic.
     */
    public int getSystolic();
    
    /**
     * Setter for property systolic.
     * @param systolic New value of property systolic.
     */
    public void setSystolic(int systolic);
    
    /**
     * Getter for property diastolic.
     * @return Value of property diastolic.
     */
    public int getDiastolic();
    
    /**
     * Setter for property diastolic.
     * @param diastolic New value of property diastolic.
     */
    public void setDiastolic(int diastolic);
    
    /**
     * Getter for property rr.
     * @return Value of property rr.
     */
    public int getRr();
    
    /**
     * Setter for property rr.
     * @param rr New value of property rr.
     */
    public void setRr(int rr);
    
    /**
     * Getter for property pr.
     * @return Value of property pr.
     */
    public int getPr();
    
    /**
     * Setter for property pr.
     * @param pr New value of property pr.
     */
    public void setPr(int pr);
    
    /**
     * Getter for property temp.
     * @return Value of property temp.
     */
    public double getTemp();
    
    /**
     * Setter for property temp.
     * @param temp New value of property temp.
     */
    public void setTemp(double temp);
    
    /**
     * Getter for property weight.
     * @return Value of property weight.
     */
    public double getWeight();
    
    /**
     * Setter for property weight.
     * @param weight New value of property weight.
     */
    public void setWeight(double weight);
    
    /**
     * Getter for property height.
     * @return Value of property height.
     */
    public double getHeight();
    
    /**
     * Setter for property height.
     * @param height New value of property height.
     */
    public void setHeight(double height);
    
    /**
     * Getter for property pefr.
     * @return Value of property pefr.
     */
    public int getPrepefr();
    
    /**
     * Setter for property pefr.
     * @param pefr New value of property pefr.
     */
    public void setPrepefr(int pefr);
    
    /**
     * Getter for property rhytm.
     * @return Value of property rhytm.
     */
    public String getRhythm();
    
    /**
     * Setter for property rhytm.
     * @param rhytm New value of property rhytm.
     */
    public void setRhythm(String rhytm);
    
    /**
     * Getter for property postpefr.
     * @return Value of property postpefr.
     */
    public int getPostpefr();
    
    /**
     * Setter for property postpefr.
     * @param postpefr New value of property postpefr.
     */
    public void setPostpefr(int postpefr);
    
}
