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
    public AllergyImpl1() {
        super();
    }
     
    
    public String getGenerics() {
        return generics;
    } 
    
    public String getSubstance() {
        return substance;
    }
    
    public boolean isDefinite() {
        return definite;
    }
    
    public void setDefinite(boolean definite) {
        this.definite = definite;
    }
     
    
    public void setGenerics(String generics) {
        this.generics= generics;
    }
     
     
     
    
    public void setSubstance(String substance) {
        this.substance = substance;
    }
    
    public void setHealthIssueName(String healthIssueName) {
        super.setHealthIssueName(healthIssueName);
    }
    
}

