
/** Java class "enum_social_id.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmIdentity;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 */
public class enum_social_id {

    public enum_social_id() {
    }
    
    public enum_social_id(String type) {
        setName(type);
    }
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
    private String name; 



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
    }
    
    public boolean equals(enum_social_id  esid) {
        
        return getId().equals(esid.getId());
    }
    
    public boolean equals( Object other) {
        if (other instanceof enum_social_id)
            return equals( (enum_social_id) other);
        return super.equals(other);
    }
    
 // end setName        

} // end enum_social_id



