/** Java class "drug_dosage.java" generated from Poseidon for UML.
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
public class drug_dosage {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String dosage_hints; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public drug_element drug_element; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_warning_categories drug_warning_categories; 
/**
 * <p>
 * 
 * </p>
 */
    public info_reference info_reference; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_routes drug_routes; 


   ///////////////////////////////////////
   // access methods for associations

    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        this.drug_element = _drug_element;
    }
    public drug_warning_categories getDrug_warning_categories() {
        return drug_warning_categories;
    }
    public void setDrug_warning_categories(drug_warning_categories _drug_warning_categories) {
        this.drug_warning_categories = _drug_warning_categories;
    }
    public info_reference getInfo_reference() {
        return info_reference;
    }
    public void setInfo_reference(info_reference _info_reference) {
        this.info_reference = _info_reference;
    }
    public drug_routes getDrug_routes() {
        return drug_routes;
    }
    public void setDrug_routes(drug_routes _drug_routes) {
        this.drug_routes = _drug_routes;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getDosage_hints() {        
        return dosage_hints;
    } // end getDosage_hints        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDosage_hints(String _dosage_hints) {        
        dosage_hints = _dosage_hints;
    } // end setDosage_hints        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Integer _id) {        
        id = _id;
    } // end setId        

} // end drug_dosage





