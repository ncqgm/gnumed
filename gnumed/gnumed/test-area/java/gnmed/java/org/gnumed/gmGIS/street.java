/** Java class "street.java" generated from Poseidon for UML.
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
public class street {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

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
    private String postcode; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public urb urb; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *
     * @hibernate.many-to-one
     */
    public urb getUrb() {
        return urb;
    }
    public void setUrb(urb _urb) {
        this.urb = _urb;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *  @hibernate.id
 *      generator-class="hilo"
 */
    public Long getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Long _id) {        
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
    } // end setName        

/**
 * <p>
 * Represents ...
 * </p>
 *
 * @hibernate.property
 */
    public String getPostcode() {        
        return postcode;
    } // end getPostcode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setPostcode(String _postcode) {        
        postcode = _postcode;
    }
  
    public String toString() {
          StringBuffer sb = new StringBuffer();
          sb.append(getName());
          if (getUrb() != null) {
              sb.append(", ").append(getUrb());
          }
          return sb.toString();
    }
    
 // end setPostcode        

} // end street





