/** Java class "ProtocolRef.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;

/**
 * <p>
 *
 * </p>
 */
public class ProtocolRef {
    
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
    public Collection actionRef = new java.util.HashSet(); // of type ActionRef
    /**
     * <p>
     *
     * </p>
     */
    public Protocol referred;
    /**
     * <p>
     *
     * </p>
     */
    public Protocol referring;
    /**
     * <p>
     *
     * </p>
     */
    public Collection dependent = new java.util.HashSet(); // of type ProtocolDependency
    /**
     * <p>
     *
     * </p>
     */
    public Collection consequent = new java.util.HashSet(); // of type ProtocolDependency
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getActionRefs() {
        return actionRef;
    }
    public void addActionRef(ActionRef actionRef) {
        if (! this.actionRef.contains(actionRef)) {
            this.actionRef.add(actionRef);
            actionRef.setProtocolRef(this);
        }
    }
    public void removeActionRef(ActionRef actionRef) {
        boolean removed = this.actionRef.remove(actionRef);
        if (removed) actionRef.setProtocolRef((ProtocolRef)null);
    }
    public Protocol getReferred() {
        return referred;
    }
    public void setReferred(Protocol protocol) {
        if (this.referred != protocol) {
            if (this.referred != null) this.referred.removeParentRef(this);
            this.referred = protocol;
            if (protocol != null) protocol.addParentRef(this);
        }
    }
    public Protocol getReferring() {
        return referring;
    }
    public void setReferring(Protocol protocol) {
        if (this.referring != protocol) {
            if (this.referring != null) this.referring.removeStep(this);
            this.referring = protocol;
            if (protocol != null) protocol.addStep(this);
        }
    }
    public Collection getDependents() {
        return dependent;
    }
    public void addDependent(ProtocolDependency protocolDependency) {
        if (! this.dependent.contains(protocolDependency)) {
            this.dependent.add(protocolDependency);
            protocolDependency.setConsequentRef(this);
        }
    }
    public void removeDependent(ProtocolDependency protocolDependency) {
        boolean removed = this.dependent.remove(protocolDependency);
        if (removed) protocolDependency.setConsequentRef((ProtocolRef)null);
    }
    public Collection getConsequents() {
        return consequent;
    }
    public void addConsequent(ProtocolDependency protocolDependency) {
        if (! this.consequent.contains(protocolDependency)) {
            this.consequent.add(protocolDependency);
            protocolDependency.setDependentRef(this);
        }
    }
    public void removeConsequent(ProtocolDependency protocolDependency) {
        boolean removed = this.consequent.remove(protocolDependency);
        if (removed) protocolDependency.setDependentRef((ProtocolRef)null);
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
    
    /** Setter for property actionRefs.
     * @param actionRefs New value of property actionRefs.
     *
     */
    public void setActionRefs(Collection actionRefs) {}
    
    /** Setter for property consequents.
     * @param consequents New value of property consequents.
     *
     */
    public void setConsequents(Collection consequents) {
        consequent=consequents;
    }
    
    /** Setter for property dependents.
     * @param dependents New value of property dependents.
     *
     */
    public void setDependents(Collection dependents) {
        dependent=dependents;
    }
    
    // end setId
    
} // end ProtocolRef





