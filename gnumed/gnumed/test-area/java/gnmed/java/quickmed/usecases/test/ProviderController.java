/*
 * ProviderController.java
 *
 * Created on 19 August 2003, 16:26
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.*;

/**
 *
 * @author  syan
 */
public interface ProviderController {
    public ProviderView getView();
    public void setView( ProviderView view);
    public identity getProvider();
    public void setProvider(identity id);
    public void modelToUi();
    public void uiToModel();
    public void save();
    public identity_role createOrFindRole(final java.lang.String name);
    public void changeProvider(identity i);
    /** Getter for property managerReference.
     * @return Value of property managerReference.
     *
     */
    public ManagerReference getManagerReference();
    
}
