/** Java class "Measurement.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;
import xgmed.domain.common.Quantity;
import  xgmed.helper.Visitor; 
/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value
 */
public class Measurement extends Observation {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Quantity quantity;

   ///////////////////////////////////////
   // associations


/**
 * <p>
 * 
 * </p>
 */
    public PhenomenonType phenomenonType; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.one-to-one
     */
    public Quantity getQuantity() {
        return quantity;
    }
    public void setQuantity(Quantity quantity) {
        this.quantity = quantity;
    }
    
    /**
     *@hibernate.many-to-one
     */
    public PhenomenonType getPhenomenonType() {
        return phenomenonType;
    }
    public void setPhenomenonType(PhenomenonType phenomenonType) {
        this.phenomenonType = phenomenonType;
    }


  ///////////////////////////////////////
  // operations
  public void accept(Visitor v) {
        v.visitMeasurement(this);
    }


} // end Measurement





