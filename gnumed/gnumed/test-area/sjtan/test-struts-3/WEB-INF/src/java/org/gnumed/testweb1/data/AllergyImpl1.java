/*
 * AllergyImpl.java
 *
 * Created on September 18, 2004, 1:20 PM
 */

package org.gnumed.testweb1.data;

/**
 *
 * @author  sjtan
 */
public class AllergyImpl1 extends ClinRootItemImpl1 implements Allergy {
    
    
    String substance,   generics;
      
     boolean definite;
    /** Creates a new instance of AllergyImpl */
    protected AllergyImpl1() {
        super();
    }
     
    
    /**
     * database property
     * @return
     */    
    public String getGenerics() {
        return generics;
    } 
    
    /**
     *
     * @return
     */    
    public String getSubstance() {
        return substance;
    }
    
    /**
     *
     * @return
     */    
    public boolean isDefinite() {
        return definite;
    }
    
    /**
     *
     * @param definite
     */    
    public void setDefinite(boolean definite) {
        this.definite = definite;
    }
     
    
    /**
     *
     * @param generics
     */    
    public void setGenerics(String generics) {
        this.generics= generics;
    }
     
     
     
    
    /**
     *
     * @param substance
     */    
    public void setSubstance(String substance) {
        this.substance = substance;
    }
    
    /**
     *
     * @param healthIssueName
     */    
    public void setHealthIssueName(String healthIssueName) {
        super.setHealthIssueName(healthIssueName);
    }
    
    /**
     *
     * @param newHealthIssueName
     */    
    public void setNewHealthIssueName(String newHealthIssueName) {
        super.setNewHealthIssueName(newHealthIssueName);
    }
    
    
}

