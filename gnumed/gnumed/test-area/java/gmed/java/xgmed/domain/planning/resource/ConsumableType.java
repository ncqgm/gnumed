/** Java class "ConsumableType.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.resource;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.subclass
 *  discriminator-value="C"
 */
public class ConsumableType extends ResourceType {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection holding = new java.util.HashSet(); // of type Holding


   ///////////////////////////////////////
   // access methods for associations

    /**
     *
     * see custom hbm for 1-many mapping
     */
    public Collection getHoldings() {
        return holding;
    }
    public void addHolding(Holding holding) {
        if (! this.holding.contains(holding)) {
            this.holding.add(holding);
            holding.setConsumableType(this);
        }
    }
    public void removeHolding(Holding holding) {
        boolean removed = this.holding.remove(holding);
        if (removed) holding.setConsumableType((ConsumableType)null);
    }

} // end ConsumableType





