/** Java class "Asset.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.planning.resource;

import java.util.*;

/**
 * <p>
 *
 * </p>
 *  @hibernate.class
 *      table="asset"
 *      discriminator-value="A"
 *  @hibernate.discriminator
 *      column="class"
 *      type="string"
*/
public class Asset {
    
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
    public Collection assetType = new java.util.HashSet(); // of type AssetType
    /**
     * <p>
     *
     * </p>
     */
    public Collection timeAllocation = new java.util.HashSet(); // of type TimeAllocation
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    public Collection getAssetTypes() {
        return assetType;
    }
    public void addAssetType(AssetType assetType) {
        if (! this.assetType.contains(assetType)) {
            this.assetType.add(assetType);
            assetType.addAsset(this);
        }
    }
    public void removeAssetType(AssetType assetType) {
        boolean removed = this.assetType.remove(assetType);
        if (removed) assetType.removeAsset(this);
    }
    public Collection getTimeAllocations() {
        return timeAllocation;
    }
    public void addTimeAllocation(TimeAllocation timeAllocation) {
        if (! this.timeAllocation.contains(timeAllocation)) {
            this.timeAllocation.add(timeAllocation);
            timeAllocation.setAsset(this);
        }
    }
    public void removeTimeAllocation(TimeAllocation timeAllocation) {
        boolean removed = this.timeAllocation.remove(timeAllocation);
        if (removed) timeAllocation.setAsset((Asset)null);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.id
     *  generator-class="hilo.long"
     *      type="long"
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
    } // end setId
    
} // end Asset





