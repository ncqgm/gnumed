/** Java class "Abandoned.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *  hibernate - is specified as component of Action.
 */
public class Abandoned {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Action action; 


   ///////////////////////////////////////
   // access methods for associations

    public Action getAction() {
        return action;
    }
    public void setAction(Action action) {
        if (this.action != action) {
            this.action = action;
            if (action != null) action.setAbandoned(this);
        }
    }

} // end Abandoned





