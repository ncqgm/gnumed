/** Java class "Protocol.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.planning.outcome.KnowledgeFunction;
import xgmed.domain.planning.outcome.OutcomeFunction;
import xgmed.domain.planning.outcome.StartFunction;

/**
 * <p>
 *
 * </p>
 */
public class Protocol {
    
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
    public Collection parentRef = new java.util.HashSet(); // of type ProtocolRef
    /**
     * <p>
     *
     * </p>
     */
    public Collection step = new java.util.HashSet(); // of type ProtocolRef
    /**
     * <p>
     *
     * </p>
     */
    public Collection protocolDependency = new java.util.HashSet(); // of type ProtocolDependency
    /**
     * <p>
     *
     * </p>
     */
    public Collection indicator = new java.util.HashSet(); // of type StartFunction
    /**
     * <p>
     *
     * </p>
     */
    public Collection knowledgeFunction = new java.util.HashSet(); // of type KnowledgeFunction
    /**
     * <p>
     *
     * </p>
     */
    public Collection result = new java.util.HashSet(); // of type OutcomeFunction
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getParentRefs() {
        return parentRef;
    }
    public void addParentRef(ProtocolRef protocolRef) {
        if (! this.parentRef.contains(protocolRef)) {
            this.parentRef.add(protocolRef);
            protocolRef.setReferred(this);
        }
    }
    public void removeParentRef(ProtocolRef protocolRef) {
        boolean removed = this.parentRef.remove(protocolRef);
        if (removed) protocolRef.setReferred((Protocol)null);
    }
    public Collection getSteps() {
        return step;
    }
    public void addStep(ProtocolRef protocolRef) {
        if (! this.step.contains(protocolRef)) {
            this.step.add(protocolRef);
            protocolRef.setReferring(this);
        }
    }
    public void removeStep(ProtocolRef protocolRef) {
        boolean removed = this.step.remove(protocolRef);
        if (removed) protocolRef.setReferring((Protocol)null);
    }
    public Collection getProtocolDependencys() {
        return protocolDependency;
    }
    public void addProtocolDependency(ProtocolDependency protocolDependency) {
        if (! this.protocolDependency.contains(protocolDependency)) {
            this.protocolDependency.add(protocolDependency);
            protocolDependency.setProtocol(this);
        }
    }
    public void removeProtocolDependency(ProtocolDependency protocolDependency) {
        boolean removed = this.protocolDependency.remove(protocolDependency);
        if (removed) protocolDependency.setProtocol((Protocol)null);
    }
    public Collection getIndicators() {
        return indicator;
    }
    public void addIndicator(StartFunction startFunction) {
        if (! this.indicator.contains(startFunction)) {
            this.indicator.add(startFunction);
            startFunction.setIndication(this);
        }
    }
    public void removeIndicator(StartFunction startFunction) {
        boolean removed = this.indicator.remove(startFunction);
        if (removed) startFunction.setIndication((Protocol)null);
    }
    public Collection getKnowledgeFunctions() {
        return knowledgeFunction;
    }
    public void addKnowledgeFunction(KnowledgeFunction knowledgeFunction) {
        if (! this.knowledgeFunction.contains(knowledgeFunction)) {
            this.knowledgeFunction.add(knowledgeFunction);
            knowledgeFunction.addArgProtocol(this);
        }
    }
    public void removeKnowledgeFunction(KnowledgeFunction knowledgeFunction) {
        boolean removed = this.knowledgeFunction.remove(knowledgeFunction);
        if (removed) knowledgeFunction.removeArgProtocol(this);
    }
    public Collection getResults() {
        return result;
    }
    public void addResult(OutcomeFunction outcomeFunction) {
        if (! this.result.contains(outcomeFunction)) {
            this.result.add(outcomeFunction);
            outcomeFunction.setProtocol(this);
        }
    }
    public void removeResult(OutcomeFunction outcomeFunction) {
        boolean removed = this.result.remove(outcomeFunction);
        if (removed) outcomeFunction.setProtocol((Protocol)null);
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
    
    /** Setter for property indicators.
     * @param indicators New value of property indicators.
     *
     */
    public void setIndicators(Collection indicators) {}
    
    /** Setter for property knowledgeFunctions.
     * @param knowledgeFunctions New value of property knowledgeFunctions.
     *
     */
    public void setKnowledgeFunctions(Collection knowledgeFunctions) {}
    
    /** Setter for property parentRefs.
     * @param parentRefs New value of property parentRefs.
     *
     */
    public void setParentRefs(Collection parentRefs) {}
    
    /** Setter for property protocolDependencys.
     * @param protocolDependencys New value of property protocolDependencys.
     *
     */
    public void setProtocolDependencys(Collection protocolDependencys) {}
    
    /** Setter for property results.
     * @param results New value of property results.
     *
     */
    public void setResults(Collection results) {
        result=results;
    }
    
    /** Setter for property steps.
     * @param steps New value of property steps.
     *
     */
    public void setSteps(Collection steps) {
        step=steps;
    }
    
    // end setId
    
} // end Protocol





