/** Java class "StartFunction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.outcome;

import java.util.*;
import xgmed.domain.planning.Protocol;

/**
 * <p>
 * 
 * </p>
 */
public class StartFunction extends KnowledgeFunction {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Protocol indication; 


   ///////////////////////////////////////
   // access methods for associations

    public Protocol getIndication() {
        return indication;
    }
    public void setIndication(Protocol protocol) {
        if (this.indication != protocol) {
            if (this.indication != null) this.indication.removeIndicator(this);
            this.indication = protocol;
            if (protocol != null) protocol.addIndicator(this);
        }
    }

} // end StartFunction





