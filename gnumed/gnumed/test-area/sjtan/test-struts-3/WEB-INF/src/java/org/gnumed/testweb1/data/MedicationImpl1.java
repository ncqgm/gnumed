

/*
 * MedicationImpl1.java
 *
 * Created on September 18, 2004, 7:59 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class MedicationImpl1 extends ClinRootItemImpl1 implements Medication {
    
    private String brand, generic, shortDescription;
    private java.util.Date last, start;
    
    /** Creates a new instance of MedicationImpl1 */
    public MedicationImpl1() {
        last = new java.util.Date();
        start =new java.util.Date();
        
    }
    
    public String getBrandName() {
        return brand;
    }
    
    public String getGenericName() {
        return generic;
    }
    
    public java.util.Date getLast() {
        return last;
    }
    
    public String getShortDescription() {
        return shortDescription;
    }
    
    public java.util.Date getStart() {
        return start;
    }
    
    public void setBrandName(String b) {
        this.brand = b;
    }
    
    public void setGenericName(String n) {
        this.generic = n;
    }
    
    public void setShortDescription(String s) {
        this.shortDescription = s;
    }
    
    public void setStart(java.util.Date s) {
        this.start = s;
    }
    
    public void setLast(java.util.Date l) {
        this.last = l;
    }
    
}
