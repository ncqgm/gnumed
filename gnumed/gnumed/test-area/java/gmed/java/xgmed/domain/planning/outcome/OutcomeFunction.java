/** Java class "OutcomeFunction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.planning.outcome;

import java.util.*;
import xgmed.domain.observation.ObservationConcept;
import xgmed.domain.planning.Protocol;

/**
 * <p>
 * 
 * </p>
 * an outcome function takes observations and protocols as input.
 * Output is target and side-effect observation types.
 * A protocol may have many resulting outcome functions, depending
 * on what observations and other protocols are taken as input e.g. a modifying
 * disease condition, a modifying treatment regime.
 */
public class OutcomeFunction extends KnowledgeFunction {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection target = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public Collection side_effect = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public Protocol protocol; 


   ///////////////////////////////////////
   // access methods for associations

    public Collection getTargets() {
        return target;
    }
    public void addTarget(ObservationConcept observationConcept) {
        if (! this.target.contains(observationConcept)) {
            this.target.add(observationConcept);
            observationConcept.addOutcomeGenerator(this);
        }
    }
    public void removeTarget(ObservationConcept observationConcept) {
        boolean removed = this.target.remove(observationConcept);
        if (removed) observationConcept.removeOutcomeGenerator(this);
    }
    public Collection getSide_effects() {
        return side_effect;
    }
    public void addSide_effect(ObservationConcept observationConcept) {
        if (! this.side_effect.contains(observationConcept)) {
            this.side_effect.add(observationConcept);
            observationConcept.addSideEffectGenerator(this);
        }
    }
    public void removeSide_effect(ObservationConcept observationConcept) {
        boolean removed = this.side_effect.remove(observationConcept);
        if (removed) observationConcept.removeSideEffectGenerator(this);
    }
    public Protocol getProtocol() {
        return protocol;
    }
    public void setProtocol(Protocol protocol) {
        if (this.protocol != protocol) {
            if (this.protocol != null) this.protocol.removeResult(this);
            this.protocol = protocol;
            if (protocol != null) protocol.addResult(this);
        }
    }

} // end OutcomeFunction





