/** Java class "AssetType.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.planning.resource;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *  @hibernate.subclass
 *      discriminator-value="A"
 */
public class AssetType extends ResourceType {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection asset = new java.util.HashSet(); // of type Asset


   ///////////////////////////////////////
   // access methods for associations

    
    public Collection getAssets() {
        return asset;
    }
    public void addAsset(Asset asset) {
        if (! this.asset.contains(asset)) {
            this.asset.add(asset);
            asset.addAssetType(this);
        }
    }
    public void removeAsset(Asset asset) {
        boolean removed = this.asset.remove(asset);
        if (removed) asset.removeAssetType(this);
    }

} // end AssetType





