/** Java class "identities_addresses.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;
import org.gnumed.gmIdentity.identity;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class identities_addresses {

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
    private String address_source; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public address_type address_type; 
/**
 * <p>
 * 
 * </p>
 */
    public address address; 
/**
 * <p>
 * 
 * </p>
 */
    public identity identity; 


   ///////////////////////////////////////
   // access methods for associations
   /**
    *@hibernate.many-to-one
    */
    public address_type getAddress_type() {
        return address_type;
    }
    public void setAddress_type(address_type _address_type) {
        this.address_type = _address_type;
    }
    
      /**
    *@hibernate.many-to-one
       *    cascade="save-update"
    */
    public address getAddress() {
        return address;
    }
    public void setAddress(address _address) {
        this.address = _address;
    }
    
      /**
    *@hibernate.many-to-one
    */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        this.identity = _identity;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo"
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
    public String getAddress_source() {        
        return address_source;
    } // end getAddress_source        

/**
 * <p>
 * Represents ...
 * </p>
 * 
 */
    public void setAddress_source(String _address_source) {        
        address_source = _address_source;
    } // end setAddress_source        

} // end identities_addresses





