/** Java class "drug_information.java" generated from Poseidon for UML.
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
public class drug_information {

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
    private String text; 

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
    public info_reference info_reference; 
/**
 * <p>
 * 
 * </p>
 */
    public information_topic information_topic; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_element = new java.util.HashSet(); // of type drug_element


   ///////////////////////////////////////
   // access methods for associations

    public info_reference getInfo_reference() {
        return info_reference;
    }
    public void setInfo_reference(info_reference _info_reference) {
        this.info_reference = _info_reference;
    }
    public information_topic getInformation_topic() {
        return information_topic;
    }
    public void setInformation_topic(information_topic _information_topic) {
        this.information_topic = _information_topic;
    }
    public Collection getDrug_elements() {
        return drug_element;
    }
    public void addDrug_element(drug_element _drug_element) {
        if (! this.drug_element.contains(_drug_element)) {
            this.drug_element.add(_drug_element);
            _drug_element.addDrug_information(this);
        }
    }
    public void removeDrug_element(drug_element _drug_element) {
        boolean removed = this.drug_element.remove(_drug_element);
        if (removed) _drug_element.removeDrug_information(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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

} // end drug_information





