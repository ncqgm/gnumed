/** Java class "KnowledgeFunction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.outcome;

import java.util.*;
import xgmed.domain.observation.ObservationConcept;
import xgmed.domain.planning.Protocol;

/**
 * <p>
 * 
 * </p>
 */
public class KnowledgeFunction {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection argConcept = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public Collection argProtocol = new java.util.HashSet(); // of type Protocol


   ///////////////////////////////////////
   // access methods for associations

    /** many concepts can be arguments to many protocols
     * hibernate mapping in addon file.
     */
    public Collection getArgConcepts() {
        return argConcept;
    }
    
    public void addArgConcept(ObservationConcept observationConcept) {
        if (! this.argConcept.contains(observationConcept)) {
            this.argConcept.add(observationConcept);
            observationConcept.addKnowledgeFunction(this);
        }
    }
    public void removeArgConcept(ObservationConcept observationConcept) {
        boolean removed = this.argConcept.remove(observationConcept);
        if (removed) observationConcept.removeKnowledgeFunction(this);
    }
    
    /** many protocols can be arguments to many knowledge functions 
     */
    public Collection getArgProtocols() {
        return argProtocol;
    }
    public void addArgProtocol(Protocol protocol) {
        if (! this.argProtocol.contains(protocol)) {
            this.argProtocol.add(protocol);
            protocol.addKnowledgeFunction(this);
        }
    }
    public void removeArgProtocol(Protocol protocol) {
        boolean removed = this.argProtocol.remove(protocol);
        if (removed) protocol.removeKnowledgeFunction(this);
    }

} // end KnowledgeFunction





