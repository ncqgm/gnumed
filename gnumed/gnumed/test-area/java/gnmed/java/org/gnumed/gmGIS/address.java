/** Java class "address.java" generated from Poseidon for UML.
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
public class address {

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

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String addendum; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public street street; 

    
    Collection telephone= new java.util.HashSet();

   ///////////////////////////////////////
   // access methods for associations
/** 
 *@hibernate.many-to-one
 *  cascade="save-update"
 *  lazy="false"
 */
    public street getStreet() {
        return street;
    }
    public void setStreet(street _street) {
        this.street = _street;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *
 *@hibernate.id
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
 *
 * @hibernate.property
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
 * @hibernate.property
 */
    public String getAddendum() {        
        return addendum;
    } // end getAddendum        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAddendum(String _addendum) {        
        addendum = _addendum;
    } // end setAddendum        

     public Collection getTelephones() {
        return telephone;
    }
    public void addTelephone(telephone _telephone) {
        if (! this.telephone.contains(_telephone)) {
            this.telephone.add(_telephone);
            _telephone.setAddress(this);
        }
    }
    public void removeTelephone(telephone _telephone) {
        boolean removed = this.telephone.remove(_telephone);
        if (removed) _telephone.setAddress((address)null);
    }

    /** Setter for property telephones.
     * @param telephones New value of property telephones.
     *
     */
    public void setTelephones(Collection telephones) {
    telephone = telephones;
    }    
    
    
    /**
     *finds the telephone by role
     */
    public telephone findTelephone( enum_telephone_role role) {
        Iterator i = getTelephones().iterator();
        while (i.hasNext()) {
            telephone t = (telephone) i.next();
            if (t.getEnum_telephone_role().equals(role))
                return t;
        }
        return null;
    }
    
} // end address





