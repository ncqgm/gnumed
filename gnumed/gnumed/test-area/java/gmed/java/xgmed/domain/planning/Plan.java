/** Java class "Plan.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.observation.Observation;

/**
 * <p>
 * 
 * </p>
 */
public class Plan extends Action {

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
    public Collection triggering = new java.util.HashSet(); // of type Observation


   ///////////////////////////////////////
   // access methods for associations

    public Collection getActionRefs() {
        return actionRef;
    }
    public void addActionRef(ActionRef actionRef) {
        if (! this.actionRef.contains(actionRef)) {
            this.actionRef.add(actionRef);
            actionRef.setPlan(this);
        }
    }
    public void removeActionRef(ActionRef actionRef) {
        boolean removed = this.actionRef.remove(actionRef);
        if (removed) actionRef.setPlan((Plan)null);
    }
    public Collection getTriggerings() {
        return triggering;
    }
    public void addTriggering(Observation observation) {
        if (! this.triggering.contains(observation)) {
            this.triggering.add(observation);
            observation.addTriggered(this);
        }
    }
    public void removeTriggering(Observation observation) {
        boolean removed = this.triggering.remove(observation);
        if (removed) observation.removeTriggered(this);
    }

    /** Setter for property actionRefs.
     * @param actionRefs New value of property actionRefs.
     *
     */
    public void setActionRefs(Collection actionRefs) {
    actionRef = actionRefs;
    }
    
    /** Setter for property triggerings.
     * @param triggerings New value of property triggerings.
     *
     */
    public void setTriggerings(Collection triggerings) {
    triggering= triggerings;
    }
    
} // end Plan





