/** Java class "urb.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class urb {

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
    public state state; 


   ///////////////////////////////////////
   // access methods for associations

    public state getState() {
        return state;
    }
    public void setState(state _state) {
        this.state = _state;
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
    } // end setPostcode        

} // end urb





