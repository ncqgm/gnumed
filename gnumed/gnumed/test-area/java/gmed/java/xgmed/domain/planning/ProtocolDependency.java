/** Java class "ProtocolDependency.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * dependents and consequents exist
 * as steps of one protocol
 */
public class ProtocolDependency {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public ProtocolRef consequentRef; 
/**
 * <p>
 * 
 * </p>
 */
    public ProtocolRef dependentRef; 
/**
 * <p>
 * 
 * </p>
 */
    public Protocol protocol; 


   ///////////////////////////////////////
   // access methods for associations

    public ProtocolRef getConsequentRef() {
        return consequentRef;
    }
    public void setConsequentRef(ProtocolRef protocolRef) {
        if (this.consequentRef != protocolRef) {
            if (this.consequentRef != null) this.consequentRef.removeDependent(this);
            this.consequentRef = protocolRef;
            if (protocolRef != null) protocolRef.addDependent(this);
        }
    }
    public ProtocolRef getDependentRef() {
        return dependentRef;
    }
    public void setDependentRef(ProtocolRef protocolRef) {
        if (this.dependentRef != protocolRef) {
            if (this.dependentRef != null) this.dependentRef.removeConsequent(this);
            this.dependentRef = protocolRef;
            if (protocolRef != null) protocolRef.addConsequent(this);
        }
    }
    public Protocol getProtocol() {
        return protocol;
    }
    public void setProtocol(Protocol protocol) {
        if (this.protocol != protocol) {
            if (this.protocol != null) this.protocol.removeProtocolDependency(this);
            this.protocol = protocol;
            if (protocol != null) protocol.addProtocolDependency(this);
        }
    }

} // end ProtocolDependency





