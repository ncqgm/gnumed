/** Java class "Quantity.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;
import xgmed.domain.planning.resource.ResourceAllocation;
import xgmed.helper.Visitable;
import  xgmed.helper.Visitor; 
/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="quantity"
 */
public class Quantity implements Visitable {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double number; 

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
    public Unit unit; 
/**
 * <p>
 * 
 * </p>
 */
    public ResourceAllocation resourceAllocation; 


   ///////////////////////////////////////
   // access methods for associations
/**
 *@hibernate.many-to-one
 */
    public Unit getUnit() {
        return unit;
    }
    public void setUnit(Unit unit) {
        this.unit = unit;
    }
    
    /**
     *@hibernate.one-to-one
     */
      public ResourceAllocation getResourceAllocation() {
        return resourceAllocation;
    }
    public void setResourceAllocation(ResourceAllocation resourceAllocation) {
        if (this.resourceAllocation != resourceAllocation) {
            this.resourceAllocation = resourceAllocation;
            if (resourceAllocation != null) resourceAllocation.setQuantity(this);
        }
    }


  ///////////////////////////////////////
  // operations



    /** Getter for property id.
     * @return Value of property id.
     *
     * @hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /** Getter for property number.
     * @return Value of property number.
     *
     * @hibernate.property
     */
    public Double getNumber() {
        return this.number;
    }    

    /** Setter for property number.
     * @param number New value of property number.
     *
     */
    public void setNumber(Double number) {
        this.number = number;
    }
    
    public void accept(Visitor v) {
        v.visitQuantity(this);
    }
    
} // end Quantity





