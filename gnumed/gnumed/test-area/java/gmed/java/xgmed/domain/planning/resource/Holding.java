/** Java class "Holding.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.resource;

import java.util.*;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *  table="holding"
 */
public class Holding {
    
    ///////////////////////////////////////
    // attributes
    
    
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
    public ConsumableType consumableType;
    /**
     * <p>
     *
     * </p>
     */
    public Collection consumableAllocation = new java.util.HashSet(); // of type ConsumableAllocation
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.many-to-one
     */
    public ConsumableType getConsumableType() {
        return consumableType;
    }
    public void setConsumableType(ConsumableType consumableType) {
        if (this.consumableType != consumableType) {
            if (this.consumableType != null) this.consumableType.removeHolding(this);
            this.consumableType = consumableType;
            if (consumableType != null) consumableType.addHolding(this);
        }
    }
    
    /**
     *
     * see custom hbm file for one-to-many mapping
     */
    
    public Collection getConsumableAllocations() {
        return consumableAllocation;
    }
    public void addConsumableAllocation(ConsumableAllocation consumableAllocation) {
        if (! this.consumableAllocation.contains(consumableAllocation)) {
            this.consumableAllocation.add(consumableAllocation);
            consumableAllocation.setHolding(this);
        }
    }
    public void removeConsumableAllocation(ConsumableAllocation consumableAllocation) {
        boolean removed = this.consumableAllocation.remove(consumableAllocation);
        if (removed) consumableAllocation.setHolding((Holding)null);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.id
     *  generator-class="hilo.long"
     *      type="long"
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
    
    /** Setter for property consumableAllocations.
     * @param consumableAllocations New value of property consumableAllocations.
     *
     */
    public void setConsumableAllocations(Collection consumableAllocations) {
    consumableAllocation=consumableAllocations;
    }
    
 // end setId
    
} // end Holding





