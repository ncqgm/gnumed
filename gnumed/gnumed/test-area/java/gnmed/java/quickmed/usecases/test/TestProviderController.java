/*
 * TestProviderController.java
 *
 * Created on 19 August 2003, 16:54
 */

package quickmed.usecases.test;
import java.util.*;
import org.gnumed.gmIdentity.*;
/**
 *
 * @author  syan
 */
public class TestProviderController implements ProviderController , ProviderView {
    
     
    private org.gnumed.gmIdentity.identity id;
    private ProviderView view;
    private InterfaceTransfer transferer;
    private DemographicIdentityModel model;
    /** Creates a new instance of TestProviderController */
    public TestProviderController() {
        try {
            model = new DemographicIdentityModel();
        } catch (Exception e) {
            e.printStackTrace();
        }
        try {
            transferer = new InterfaceTransfer( ProviderView.class, new String[] { "class" } );
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public org.gnumed.gmIdentity.identity getProvider() {
        return id;
    }
    
    public ProviderView getView() {
        return view;
    }
    
    public void modelToUi() {
        try {
            transferer.transfer(this, view);
        } catch (Exception e) {
        e.printStackTrace();
        }
    }
    
    public void setProvider(org.gnumed.gmIdentity.identity id) {
        this.id = id;
        setIdentity(id);
    }
    
    public void setView(ProviderView view) {
        this.view = view;
    }
    
    public void uiToModel() {
        try {
            transferer.transfer(view, this);
        } catch (Exception e) {
        }
        
    }
    
    public String getAddress() {
        return model.getAddress();
    }
    
    public String getFax() {
        return model.getTelephone(TestGISManager.fax );
    }
    
    public String getFirstNames() {
        return model.getFirstNames();
    }
    
    public java.util.Collection getIdentity_role_info() {
        return model.getIdentity().getRoles();
    }
    
    public String getLastNames() {
        return model.getLastNames();
    }
    
    public String getMobile() {
        return model.getMobilePhone();
    }
    
    public String getPager() {
        return model.getTelephone(TestGISManager.pager   );
    }
    
    public String getTelephone() {
        return model.getWorkTelephone();
    }
    
    public void setAddress(String address) {
        model.setAddress(address);
    }
    
    public void setFax(String fax) {
        model.setTelephone(fax,  TestGISManager.fax );
    }
    
    public void setFirstNames(String firstNames) {
        model.setFirstNames(firstNames);
    }
    
    
    public void setIdentity_role_info(java.util.Collection identity_role_info) {
        model.getIdentity().getRoles().addAll(identity_role_info);
    }
    
    public void setLastNames(String lastNames) {
        model.setLastNames(lastNames);
    }
    
    public void setMobile(String mobile) {
        model.setMobilePhone(mobile);
    }
    
    public void setPager(String pager) {
        model.setTelephone(pager,  TestGISManager.pager);
    }
    
    public void setTelephone(String telephone) {
        model.setHomeTelephone(telephone);
    }
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity() {
        return model.getIdentity();
    }
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity id) {
        model.setIdentity(id);
    }
    
    public identity_role createOrFindRole(String name) {
        
        return getManagerReference().getIdentityManager().createOrFindRole(  name);
        
        
    }
    
    public ManagerReference getManagerReference() {
        return   (ManagerReference) model.getIdentity().getPersister();
    }
    
    public void save() {
        try {
        getManagerReference().getIdentityManager().save(getIdentity());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
}
