/** Java class "link_drug_disease_interactions.java" generated from Poseidon for UML.
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
public class link_drug_disease_interactions {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String comment; 

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
    public interactions interactions; 
/**
 * <p>
 * 
 * </p>
 */
    public disease_code disease_code; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_element drug_element; 


   ///////////////////////////////////////
   // access methods for associations

    public interactions getInteractions() {
        return interactions;
    }
    public void setInteractions(interactions _interactions) {
        this.interactions = _interactions;
    }
    public disease_code getDisease_code() {
        return disease_code;
    }
    public void setDisease_code(disease_code _disease_code) {
        this.disease_code = _disease_code;
    }
    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        if (this.drug_element != _drug_element) {
            if (this.drug_element != null) this.drug_element.removeLink_drug_disease_interactions(this);
            this.drug_element = _drug_element;
            if (_drug_element != null) _drug_element.addLink_drug_disease_interactions(this);
        }
    }


  ///////////////////////////////////////
  // operations


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

} // end link_drug_disease_interactions





