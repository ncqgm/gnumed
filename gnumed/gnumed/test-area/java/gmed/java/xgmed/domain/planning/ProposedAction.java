/** Java class "ProposedAction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.planning.resource.ResourceAllocation;

/**
 * <p>
 * 
 * </p>]
 * @hibernate.subclass
 *  discriminator-value="P"
 */
public class ProposedAction extends Action {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection actionRef = new java.util.HashSet(); // of type ActionRef
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
    public ExecutedAction executedAction; 


   ///////////////////////////////////////
   // access methods for associations

    public Collection getActionRefs() {
        return actionRef;
    }
    public void addActionRef(ActionRef actionRef) {
        if (! this.actionRef.contains(actionRef)) {
            this.actionRef.add(actionRef);
            actionRef.setProposedAction(this);
        }
    }
    public void removeActionRef(ActionRef actionRef) {
        boolean removed = this.actionRef.remove(actionRef);
        if (removed) actionRef.setProposedAction((ProposedAction)null);
    }
    public Collection getResourceAllocations() {
        return resourceAllocation;
    }
    public void addResourceAllocation(ResourceAllocation resourceAllocation) {
        if (! this.resourceAllocation.contains(resourceAllocation)) {
            this.resourceAllocation.add(resourceAllocation);
            resourceAllocation.setProposedAction(this);
        }
    }
    public void removeResourceAllocation(ResourceAllocation resourceAllocation) {
        boolean removed = this.resourceAllocation.remove(resourceAllocation);
        if (removed) resourceAllocation.setProposedAction((ProposedAction)null);
    }
    public ExecutedAction getExecutedAction() {
        return executedAction;
    }
    public void setExecutedAction(ExecutedAction executedAction) {
        if (this.executedAction != executedAction) {
            this.executedAction = executedAction;
            if (executedAction != null) executedAction.setProposedAction(this);
        }
    }

    /** Setter for property actionRefs.
     * @param actionRefs New value of property actionRefs.
     *
     */
    public void setActionRefs(Collection actionRefs) {
    actionRef=actionRefs;
    }
    
    /** Setter for property resourceAllocations.
     * @param resourceAllocations New value of property resourceAllocations.
     *
     */
    public void setResourceAllocations(Collection resourceAllocations) {
    resourceAllocation= resourceAllocations;
    }
    
} // end ProposedAction





