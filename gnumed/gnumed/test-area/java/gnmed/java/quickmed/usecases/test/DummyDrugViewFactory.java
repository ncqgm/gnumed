/*
 * DummyDrugViewFactory.java
 *
 * Created on 5 August 2003, 07:45
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;
/**
 *
 * @author  sjtan
 */
/**
 *
 *  uses a inner class Factory of the original holder of identity in order
 * to return the most current identity reference.
 */
public class DummyDrugViewFactory implements Factory {
    
    /** Holds value of property identity. */
    private identity identity;
    
    /** Holds value of property identityFactory. */
    private Factory identityFactory;
    
    /** Creates a new instance of DummyDrugViewFactory */
    public DummyDrugViewFactory() {
    }
    
    public Object newInstance() {
        DummyDrugListView view = new DummyDrugListView();
//        view.setIdentity(getIdentity());
        view.setIdentityRef(getIdentityFactory());
        return view;
    }
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity() {
      
        return this.identity;
    }
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity identity) {
        this.identity = identity;
    }
    
    /** Getter for property identityFactory.
     * @return Value of property identityFactory.
     *
     */
    public Factory getIdentityFactory() {
        return this.identityFactory;
    }
    
    /** Setter for property identityFactory.
     * @param identityFactory New value of property identityFactory.
     *
     */
    public void setIdentityFactory(Factory identityFactory) {
        this.identityFactory = identityFactory;
    }
    
}
