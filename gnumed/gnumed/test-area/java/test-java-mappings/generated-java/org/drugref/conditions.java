/** Java class "conditions.java" generated from Poseidon for UML.
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
public class conditions {

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
    private String title; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Boolean authority; 

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
    public subsidies subsidies; 


   ///////////////////////////////////////
   // access methods for associations

    public subsidies getSubsidies() {
        return subsidies;
    }
    public void setSubsidies(subsidies _subsidies) {
        this.subsidies = _subsidies;
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
    public String getTitle() {        
        return title;
    } // end getTitle        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setTitle(String _title) {        
        title = _title;
    } // end setTitle        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public Boolean getAuthority() {        
        return authority;
    } // end getAuthority        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAuthority(Boolean _authority) {        
        authority = _authority;
    } // end setAuthority        

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

} // end conditions





