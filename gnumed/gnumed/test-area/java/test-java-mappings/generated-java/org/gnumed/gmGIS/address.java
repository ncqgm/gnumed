/** Java class "address.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmGIS;

import java.util.*;
import org.gnumed.gmClinical.clin_encouonter;

/**
 * <p>
 * 
 * </p>
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
/**
 * <p>
 * 
 * </p>
 */
    public Collection clin_encouonter = new java.util.HashSet(); // of type clin_encouonter


   ///////////////////////////////////////
   // access methods for associations

    public street getStreet() {
        return street;
    }
    public void setStreet(street _street) {
        this.street = _street;
    }
    public Collection getClin_encouonters() {
        return clin_encouonter;
    }
    public void addClin_encouonter(clin_encouonter _clin_encouonter) {
        if (! this.clin_encouonter.contains(_clin_encouonter)) {
            this.clin_encouonter.add(_clin_encouonter);
            _clin_encouonter.setLocation(this);
        }
    }
    public void removeClin_encouonter(clin_encouonter _clin_encouonter) {
        boolean removed = this.clin_encouonter.remove(_clin_encouonter);
        if (removed) _clin_encouonter.setLocation((address)null);
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





