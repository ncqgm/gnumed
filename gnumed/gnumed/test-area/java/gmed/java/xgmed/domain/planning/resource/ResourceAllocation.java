/** Java class "ResourceAllocation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.resource;

import java.util.*;
import xgmed.domain.common.Quantity;
import xgmed.domain.planning.ExecutedAction;
import xgmed.domain.planning.ProposedAction;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *      table="resource_allocation"
 *      discriminator-value="R"
 * @hibernate.discriminator
 *      column="type"
 *      type="string"
 *      length="2"
 */
public class ResourceAllocation {
    
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
    public Quantity quantity;
    /**
     * <p>
     *
     * </p>
     */
    public ResourceType resourceType;
    /**
     * <p>
     *
     * </p>
     */
    public ExecutedAction executedAction;
    /**
     * <p>
     *
     * </p>
     */
    public ProposedAction proposedAction;
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.many-to-one
     */
    public Quantity getQuantity() {
        return quantity;
    }
    public void setQuantity(Quantity quantity) {
        if (this.quantity != quantity) {
            this.quantity = quantity;
            if (quantity != null) quantity.setResourceAllocation(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public ResourceType getResourceType() {
        return resourceType;
    }
    public void setResourceType(ResourceType resourceType) {
        if (this.resourceType != resourceType) {
            if (this.resourceType != null) this.resourceType.removeResourceAllocation(this);
            this.resourceType = resourceType;
            if (resourceType != null) resourceType.addResourceAllocation(this);
        }
    }
    
    /**
     *
     *@hibernate.many-to-one
     */
    public ExecutedAction getExecutedAction() {
        return executedAction;
    }
    public void setExecutedAction(ExecutedAction executedAction) {
        if (this.executedAction != executedAction) {
            if (this.executedAction != null) this.executedAction.removeResourceAllocation(this);
            this.executedAction = executedAction;
            if (executedAction != null) executedAction.addResourceAllocation(this);
        }
    }
    /**
     * @hibernate.many-to-one
     */
    public ProposedAction getProposedAction() {
        return proposedAction;
    }
    public void setProposedAction(ProposedAction proposedAction) {
        if (this.proposedAction != proposedAction) {
            if (this.proposedAction != null) this.proposedAction.removeResourceAllocation(this);
            this.proposedAction = proposedAction;
            if (proposedAction != null) proposedAction.addResourceAllocation(this);
        }
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
    } // end setId
    
} // end ResourceAllocation





