/** Java class "atc.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  mutable="false"
 */
public class atc {

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
    private String text; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_element = new java.util.ArrayList(); // of type drug_element


   ///////////////////////////////////////
   // access methods for associations

    
    public Collection getDrug_elements() {
        return drug_element;
    }
    public void addDrug_element(drug_element _drug_element) {
        if (! this.drug_element.contains(_drug_element)) {
            this.drug_element.add(_drug_element);
            _drug_element.addAtc(this);
        }
    }
    public void removeDrug_element(drug_element _drug_element) {
        boolean removed = this.drug_element.remove(_drug_element);
        if (removed) _drug_element.removeAtc(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="assigned"
 *  type="string"
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
 * @hibernate.property
 *
 */
    public String getText() {        
        return text;
    } // end getText        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setText(String _text) {        
        text = _text;
    } // end setText        

} // end atc





