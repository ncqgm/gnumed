/** Java class "TimeAllocation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning.resource;

import java.util.*;

/**
 * <p>
 *
 *
 * </p>
 * @hibernate.subclass
 *      discriminator-value="T"
 */
public class TimeAllocation extends SpecificAllocation {
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Asset asset;
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Asset getAsset() {
        return asset;
    }
    public void setAsset(Asset asset) {
        if (this.asset != asset) {
            if (this.asset != null) this.asset.removeTimeAllocation(this);
            this.asset = asset;
            if (asset != null) asset.addTimeAllocation(this);
        }
    }
    
} // end TimeAllocation





