/** Java class "drug_routes.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 *  mutable="false"
 */
public class drug_routes {

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
    private String abbreviation; 

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
    private String comment; 



  ///////////////////////////////////////
  // operations


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
    } // end setId        

/**
 * <p>
 * Represents ...
 * </p>
 *@hibernate.property
 */
    public String getAbbreviation() {        
        return abbreviation;
    } // end getAbbreviation        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAbbreviation(String _abbreviation) {        
        abbreviation = _abbreviation;
    } // end setAbbreviation        

/**
 * <p>
 * Represents ...
 * </p>
 *@hibernate.property
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
 *@hibernate.property
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

} // end drug_routes





