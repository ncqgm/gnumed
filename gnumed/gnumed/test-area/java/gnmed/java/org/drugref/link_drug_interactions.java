/** Java class "link_drug_interactions.java" generated from Poseidon for UML.
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
public class link_drug_interactions {

  ///////////////////////////////////////
  // attributes


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
    public severity_level severity_level; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_element interactor; 
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
    public interactions interactions; 


   ///////////////////////////////////////
   // access methods for associations

    public severity_level getSeverity_level() {
        return severity_level;
    }
    public void setSeverity_level(severity_level _severity_level) {
        this.severity_level = _severity_level;
    }
    public drug_element getInteractor() {
        return interactor;
    }
    public void setInteractor(drug_element _drug_element) {
        if (this.interactor != _drug_element) {
            if (this.interactor != null) this.interactor.removeLink_drug_interactions(this);
            this.interactor = _drug_element;
            if (_drug_element != null) _drug_element.addLink_drug_interactions(this);
        }
    }
    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        if (this.drug_element != _drug_element) {
            if (this.drug_element != null) this.drug_element.removeLink_drug_interactions_1(this);
            this.drug_element = _drug_element;
            if (_drug_element != null) _drug_element.addLink_drug_interactions_1(this);
        }
    }
    public interactions getInteractions() {
        return interactions;
    }
    public void setInteractions(interactions _interactions) {
        this.interactions = _interactions;
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

} // end link_drug_interactions





