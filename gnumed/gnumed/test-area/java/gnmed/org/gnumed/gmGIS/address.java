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
    private Integer id; 

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


   ///////////////////////////////////////
   // access methods for associations
/** 
 *@hibernate.many-to-one
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

} // end address





