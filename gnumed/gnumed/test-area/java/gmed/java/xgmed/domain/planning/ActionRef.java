/** Java class "ActionRef.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * 
 */
public class ActionRef {

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
    public Plan plan; 
/**
 * <p>
 * 
 * </p>
 */
    public ProposedAction proposedAction; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection dependent = new java.util.HashSet(); // of type PlanDependency
/**
 * <p>
 * 
 * </p>
 */
    public Collection consequent = new java.util.HashSet(); // of type PlanDependency
/**
 * <p>
 * 
 * </p>
 */
    public ProtocolRef protocolRef; 


   ///////////////////////////////////////
   // access methods for associations

    public Plan getPlan() {
        return plan;
    }
    public void setPlan(Plan plan) {
        if (this.plan != plan) {
            if (this.plan != null) this.plan.removeActionRef(this);
            this.plan = plan;
            if (plan != null) plan.addActionRef(this);
        }
    }
    public ProposedAction getProposedAction() {
        return proposedAction;
    }
    public void setProposedAction(ProposedAction proposedAction) {
        if (this.proposedAction != proposedAction) {
            if (this.proposedAction != null) this.proposedAction.removeActionRef(this);
            this.proposedAction = proposedAction;
            if (proposedAction != null) proposedAction.addActionRef(this);
        }
    }
    public Collection getDependents() {
        return dependent;
    }
    public void addDependent(PlanDependency planDependency) {
        if (! this.dependent.contains(planDependency)) {
            this.dependent.add(planDependency);
            planDependency.setDependantActionRef(this);
        }
    }
    public void removeDependent(PlanDependency planDependency) {
        boolean removed = this.dependent.remove(planDependency);
        if (removed) planDependency.setDependantActionRef((ActionRef)null);
    }
    public Collection getConsequents() {
        return consequent;
    }
    public void addConsequent(PlanDependency planDependency) {
        if (! this.consequent.contains(planDependency)) {
            this.consequent.add(planDependency);
            planDependency.setConsequentActionRef(this);
        }
    }
    public void removeConsequent(PlanDependency planDependency) {
        boolean removed = this.consequent.remove(planDependency);
        if (removed) planDependency.setConsequentActionRef((ActionRef)null);
    }
    public ProtocolRef getProtocolRef() {
        return protocolRef;
    }
    public void setProtocolRef(ProtocolRef protocolRef) {
        if (this.protocolRef != protocolRef) {
            if (this.protocolRef != null) this.protocolRef.removeActionRef(this);
            this.protocolRef = protocolRef;
            if (protocolRef != null) protocolRef.addActionRef(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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
    
    /** Setter for property consequents.
     * @param consequents New value of property consequents.
     *
     */
    public void setConsequents(Collection consequents) {
    consequent= consequents;
    
    }
    
    /** Setter for property dependents.
     * @param dependents New value of property dependents.
     *
     */
    public void setDependents(Collection dependents) {
    dependent = dependents;
    }
    
 // end setId        

} // end ActionRef





