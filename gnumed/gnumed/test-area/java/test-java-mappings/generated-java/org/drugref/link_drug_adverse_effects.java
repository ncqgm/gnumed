/** Java class "link_drug_adverse_effects.java" generated from Poseidon for UML.
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
public class link_drug_adverse_effects {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private char frequency; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private boolean important; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String comment; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public adverse_effects adverse_effects; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_element drug_element; 


   ///////////////////////////////////////
   // access methods for associations

    public adverse_effects getAdverse_effects() {
        return adverse_effects;
    }
    public void setAdverse_effects(adverse_effects _adverse_effects) {
        this.adverse_effects = _adverse_effects;
    }
    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        this.drug_element = _drug_element;
    }


  ///////////////////////////////////////
  // operations


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

/**
 * <p>
 * Represents ...
 * </p>
 */
    public char getFrequency() {        
        return frequency;
    } // end getFrequency        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setFrequency(char _frequency) {        
        frequency = _frequency;
    } // end setFrequency        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public boolean isImportant() {        
        return important;
    } // end isImportant        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setImportant(boolean _important) {        
        important = _important;
    } // end setImportant        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getComment() {        
        return comment;
    } // end getComment        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setComment(String _comment) {        
        comment = _comment;
    } // end setComment        

} // end link_drug_adverse_effects





