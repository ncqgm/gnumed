
/** Java class "measurement.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="m"
 */
public class measurement extends clin_attribute {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double value; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public quantified_type quantified_type; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     * @hibernate.many-to-one
     */
    public quantified_type getQuantified_type() {
        return quantified_type;
    }
    public void setQuantified_type(quantified_type _quantified_type) {
        this.quantified_type = _quantified_type;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public Double getValue() {        
        return value;
    } // end getValue        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setValue(Double _value) {        
        value = _value;
    } // end setValue        

} // end measurement



