/** Java class "address_type.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class address_type {

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
    private Integer id; 



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
 * @hibernate.id
 *      generator-class="hilo"
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

    
    public boolean equals(Object obj) {
        if ( obj instanceof address_type) {
            address_type type = (address_type) obj;
            if (type.getId() != null && getId() != null)
                return getId().equals(type.getId());
            return  getName().equals(((address_type)obj).getName());
        }
        return super.equals(obj);
    }
} // end address_type





