/** Java class "ExecutedAction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.planning.resource.ResourceAllocation;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="E"
 */
public class ExecutedAction extends Action {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection resourceAllocation = new java.util.HashSet(); // of type ResourceAllocation
/**
 * <p>
 * 
 * </p>
 */
    public ProposedAction proposedAction; 


   ///////////////////////////////////////
   // access methods for associations

    public Collection getResourceAllocations() {
        return resourceAllocation;
    }
    public void addResourceAllocation(ResourceAllocation resourceAllocation) {
        if (! this.resourceAllocation.contains(resourceAllocation)) {
            this.resourceAllocation.add(resourceAllocation);
            resourceAllocation.setExecutedAction(this);
        }
    }
    public void removeResourceAllocation(ResourceAllocation resourceAllocation) {
        boolean removed = this.resourceAllocation.remove(resourceAllocation);
        if (removed) resourceAllocation.setExecutedAction((ExecutedAction)null);
    }
    
    /**
     * @hibernate.one-to-one
     */
    public ProposedAction getProposedAction() {
        return proposedAction;
    }
    public void setProposedAction(ProposedAction proposedAction) {
        if (this.proposedAction != proposedAction) {
            this.proposedAction = proposedAction;
            if (proposedAction != null) proposedAction.setExecutedAction(this);
        }
    }

    /** Setter for property resourceAllocations.
     * @param resourceAllocations New value of property resourceAllocations.
     *
     */
    public void setResourceAllocations(Collection resourceAllocations) {
    resourceAllocation= resourceAllocations;
    }
    
} // end ExecutedAction





