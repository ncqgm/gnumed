/** Java class "generic_drug_name.java" generated from Poseidon for UML.
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
 *      mutable="false"
 */
public class generic_drug_name {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String name; 

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
    public drug_element drug_element; 

    /** Holds value of property audit_id. */
    private Integer audit_id;    

   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     *  column="id_drug"
     */
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
 * @hibernate.property
 */
    public String getName() {        
        return name;
    } // end getName        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setName(String _name) {        
        name = _name;
    } // end setName        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
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
 * @hibernate.id
 *  generator-class="assigned"
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
    }
    
    /** Getter for property audit_id.
     * @return Value of property audit_id.
     * @hibernate.property
     */
    public Integer getAudit_id() {
        return this.audit_id;
    }
    
    /** Setter for property audit_id.
     * @param audit_id New value of property audit_id.
     *
     */
    public void setAudit_id(Integer audit_id) {
        this.audit_id = audit_id;
    }
    
 // end setId        

} // end generic_drug_name





