/** Java class "drug_warning.java" generated from Poseidon for UML.
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
public class drug_warning {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String code; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

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
    public drug_warning_categories drug_warning_categories; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_element = new java.util.HashSet(); // of type drug_element


   ///////////////////////////////////////
   // access methods for associations

    public drug_warning_categories getDrug_warning_categories() {
        return drug_warning_categories;
    }
    public void setDrug_warning_categories(drug_warning_categories _drug_warning_categories) {
        this.drug_warning_categories = _drug_warning_categories;
    }
    public Collection getDrug_elements() {
        return drug_element;
    }
    public void addDrug_element(drug_element _drug_element) {
        if (! this.drug_element.contains(_drug_element)) {
            this.drug_element.add(_drug_element);
            _drug_element.addDrug_warning(this);
        }
    }
    public void removeDrug_element(drug_element _drug_element) {
        boolean removed = this.drug_element.remove(_drug_element);
        if (removed) _drug_element.removeDrug_warning(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getCode() {        
        return code;
    } // end getCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setCode(String _code) {        
        code = _code;
    } // end setCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getDescription() {        
        return description;
    } // end getDescription        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDescription(String _description) {        
        description = _description;
    } // end setDescription        

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

} // end drug_warning





