/** Java class "substance_dosage.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class substance_dosage {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private char dosage_type; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double dosage_start; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double dosage_max; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public drug_dosage drug_dosage; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_units drug_units; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_element component; 


   ///////////////////////////////////////
   // access methods for associations

    public drug_dosage getDrug_dosage() {
        return drug_dosage;
    }
    public void setDrug_dosage(drug_dosage _drug_dosage) {
        this.drug_dosage = _drug_dosage;
    }
    public drug_units getDrug_units() {
        return drug_units;
    }
    public void setDrug_units(drug_units _drug_units) {
        this.drug_units = _drug_units;
    }
    public drug_element getComponent() {
        return component;
    }
    public void setComponent(drug_element _drug_element) {
        this.component = _drug_element;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public char getDosage_type() {        
        return dosage_type;
    } // end getDosage_type        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDosage_type(char _dosage_type) {        
        dosage_type = _dosage_type;
    } // end setDosage_type        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Double getDosage_start() {        
        return dosage_start;
    } // end getDosage_start        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDosage_start(Double _dosage_start) {        
        dosage_start = _dosage_start;
    } // end setDosage_start        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Double getDosage_max() {        
        return dosage_max;
    } // end getDosage_max        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDosage_max(Double _dosage_max) {        
        dosage_max = _dosage_max;
    } // end setDosage_max        

} // end substance_dosage





