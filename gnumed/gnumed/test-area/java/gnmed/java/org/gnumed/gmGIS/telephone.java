
/** Java class "telephone.java" generated from Poseidon for UML.
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
 *  @hibernate.class
 *      
 */
public class telephone {

  
  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String number; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

   ///////////////////////////////////////
   // associations

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
    public enum_telephone_role enum_telephone_role; // of type enum_telephone_role
/**
 * <p>
 * 
 * </p>
 */
    public Collection identity = new java.util.HashSet();
    
 // of type identity


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     */
    public address getAddress() {
        return address;
    }
    public void setAddress(address _address) {
        if (this.address != _address) {
            if (this.address != null) this.address.removeTelephone(this);
            this.address = _address;
            if (_address != null) _address.addTelephone(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
       public enum_telephone_role getEnum_telephone_role() {
        return enum_telephone_role;
    }
    public void setEnum_telephone_role(enum_telephone_role _enum_telephone_role) {
        if (this.enum_telephone_role != _enum_telephone_role) {
          
            this.enum_telephone_role = _enum_telephone_role;
           
        }
    }
    
    /**
     *
     *@hibernate.set
     *@hibernate.collection-key
     *  column="mobile"
     *@hibernate.collection-one-to-many
     *  class="org.gnumed.gmIdentity.identity"
     */
    public Collection getIdentitys() {
        return identity;
    }
    
    /** Setter for property identitys.
     * @param identitys New value of property identitys.
     *
     */
    public void setIdentitys(Collection identitys) {
    identity = identitys;
    }    
  
    public void addIdentity(identity _identity) {
        if (! this.identity.contains(_identity)) {
            this.identity.add(_identity);
            _identity.setMobile(this);
        }
    }
    public void removeIdentity(identity _identity) {
        boolean removed = this.identity.remove(_identity);
        if (removed) _identity.setMobile((telephone)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *@hibernate.property
 */
    public String getNumber() {        
        return number;
    } // end getNumber        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setNumber(String _number) {        
        number = _number;
    } // end setNumber        

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
    }
    
      
    public final static telephone NULL ;
    static {
        NULL = new telephone();
        NULL.setId( new Long(0));
        NULL.setNumber("");
    }
 // end setId        

} // end telephone



