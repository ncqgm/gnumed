/*
 * VitalsImpl1.java
 *
 * Created on September 19, 2004, 6:23 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class VitalsImpl1 extends ClinRootItemImpl1 implements Vitals {
    private int diastolic,systolic, pr, rr, pefr,postpefr;
    private double wt, ht, temp;
    private String rhythm;
    /** Creates a new instance of VitalsImpl1 */
    public VitalsImpl1() {
        diastolic = 0;
        systolic = 0;
        pr = 0;
        rr = 0;
        pefr = 0;
        postpefr = 0;
        wt =  0.0;
        ht =  0.0;
        temp =  0.0;
    }
    
    public int getDiastolic() {
        return diastolic;
        
    }
    
    public double getHeight() {
        return ht;
    }
    
    public int getPrepefr() {
        return pefr;
    }
    
    public int getPr() {
        return pr;
    }
    
    public int getRr() {
        return rr;
    }
    
    public int getSystolic() {
        return systolic;
    }
    
    public double getTemp() {
        return temp;
    }
    
    public double getWeight() {
        return wt;
    }
    
    public void setDiastolic(int diastolic) {
        this.diastolic = diastolic;
    }
    
    public void setHeight(double height) {
        this.ht = height;
    }
    
    public void setPrepefr(int pefr) {
        this.pefr = pefr;
    }
    
    public void setPr(int pr) {
        this.pr = pr;
    }
    
    public void setRr(int rr) {
        this.rr = rr;
    }
    
    public void setSystolic(int systolic) {
        this.systolic = systolic;
    }
    
    public void setTemp(double temp) {
        this.temp = temp;
    }
    
    public void setWeight(double weight) {
        this.wt = weight;
        
    }
    
    public String getRhythm() {
        return rhythm;
    }
    
    public void setRhythm(String rhytm) {
        this.rhythm = rhythm;
    }
    
    public int getPostpefr() {
        return postpefr;
    }
    
    public void setPostpefr(int postpefr) {
        this.postpefr = postpefr;
    }
    
}
