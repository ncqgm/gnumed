
/** Java class "quantified_type.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.subclass
 *  discriminator-value="q"
 */
public class quantified_type extends category_type {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String unit; 



  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getUnit() {        
        return unit;
    } // end getUnit        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setUnit(String _unit) {        
        unit = _unit;
    } // end setUnit        

} // end quantified_type



