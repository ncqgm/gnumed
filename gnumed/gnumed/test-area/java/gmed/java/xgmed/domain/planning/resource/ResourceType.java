/** Java class "ResourceType.java" generated from Poseidon for UML.
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
 *  table="resourceType"
 *  discriminator-value="R"
 * @hibernate.discriminator
 *      column="type"
 *      type="string"
 *      length="2"
 */
public class ResourceType {
    
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
    public Collection resourceAllocation = new java.util.HashSet(); // of type ResourceAllocation
    
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     *
     * see custom hbm 1-many mapping
     */
    public Collection getResourceAllocations() {
        return resourceAllocation;
    }
    public void addResourceAllocation(ResourceAllocation resourceAllocation) {
        if (! this.resourceAllocation.contains(resourceAllocation)) {
            this.resourceAllocation.add(resourceAllocation);
            resourceAllocation.setResourceType(this);
        }
    }
    public void removeResourceAllocation(ResourceAllocation resourceAllocation) {
        boolean removed = this.resourceAllocation.remove(resourceAllocation);
        if (removed) resourceAllocation.setResourceType((ResourceType)null);
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
    
    /** Setter for property resourceAllocations.
     * @param resourceAllocations New value of property resourceAllocations.
     *
     */
    public void setResourceAllocations(Collection resourceAllocations) {
        resourceAllocation=resourceAllocations;
        
    }
    
    // end setId
    
} // end ResourceType





