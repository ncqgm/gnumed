/** Java class "ConsumableAllocation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.resource;

import java.util.*;

/**
 *
 * @hibernate.subclass
 *  discriminator-value="C"
 */
public class ConsumableAllocation extends SpecificAllocation {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Holding holding; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     *
     *@hibernate.many-to-one
     */
    public Holding getHolding() {
        return holding;
    }
    public void setHolding(Holding holding) {
        if (this.holding != holding) {
            if (this.holding != null) this.holding.removeConsumableAllocation(this);
            this.holding = holding;
            if (holding != null) holding.addConsumableAllocation(this);
        }
    }

} // end ConsumableAllocation





