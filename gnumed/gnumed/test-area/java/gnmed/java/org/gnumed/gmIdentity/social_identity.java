
/** Java class "social_identity.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmIdentity;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class social_identity {

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
    private String number; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public enum_social_id enum_social_id; 
/**
 * <p>
 * 
 * </p>
 */
    public identity identity; 

    /** Holds value of property expiry. */
    private java.util.Date expiry;    

   ///////////////////////////////////////
   // access methods for associations
/**
 *@hibernate.many-to-one
 */
    public enum_social_id getEnum_social_id() {
        return enum_social_id;
    }
    public void setEnum_social_id(enum_social_id _enum_social_id) {
        this.enum_social_id = _enum_social_id;
    }
    
    /**
     *@hibernate.many-to-one
     */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        if (this.identity != _identity) {
            if (this.identity != null) this.identity.removeSocial_identity(this);
            this.identity = _identity;
            if (_identity != null) _identity.addSocial_identity(this);
        }
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
    public String getNumber() {        
        return number ;
    } // end getNumber        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setNumber(String _number) {        
      number = _number;
    }
    
    /** Getter for property expiry.
     * @return Value of property expiry.
     * 
     * @hibernate.property
     */
    public java.util.Date getExpiry() {
        return this.expiry;
    }
    
    /** Setter for property expiry.
     * @param expiry New value of property expiry.
     *
     */
    public void setExpiry(java.util.Date expiry) {
        this.expiry = expiry;
    }
    
 // end setNumber        

} // end social_identity



