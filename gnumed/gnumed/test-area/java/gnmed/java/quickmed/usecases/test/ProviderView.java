/*
 * ProviderView.java
 *
 * Created on 19 August 2003, 01:16
 */

package quickmed.usecases.test;
import java.util.Collection;

/**
 *
 * @author  syan
 */
public interface ProviderView {
    
    /** Getter for property lastNames.
     * @return Value of property lastNames.
     *
     */
    public String getLastNames();
    
    /** Setter for property lastNames.
     * @param lastNames New value of property lastNames.
     *
     */
    public void setLastNames(String lastNames);
    
    /** Getter for property firstNames.
     * @return Value of property firstNames.
     *
     */
    public String getFirstNames();
    
    /** Setter for property firstNames.
     * @param firstNames New value of property firstNames.
     *
     */
    public void setFirstNames(String firstNames);
    
    /** Getter for property address.
     * @return Value of property address.
     *
     */
    public String getAddress();
    
    /** Setter for property address.
     * @param address New value of property address.
     *
     */
    public void setAddress(String address);
    
    /** Getter for property telephone.
     * @return Value of property telephone.
     *
     */
    public String getTelephone();
    
    /** Setter for property telephone.
     * @param telephone New value of property telephone.
     *
     */
    public void setTelephone(String telephone);
    
    /** Getter for property fax.
     * @return Value of property fax.
     *
     */
    public String getFax();
    
    /** Setter for property fax.
     * @param fax New value of property fax.
     *
     */
    public void setFax(String fax);
    
    /** Getter for property mobile.
     * @return Value of property mobile.
     *
     */
    public String getMobile();
    
    /** Setter for property mobile.
     * @param mobile New value of property mobile.
     *
     */
    public void setMobile(String mobile);
    
    /** Getter for property pager.
     * @return Value of property pager.
     *
     */
    public String getPager();
    
    /** Setter for property pager.
     * @param pager New value of property pager.
     *
     */
    public void setPager(String pager);
    
    /** Getter for property identity_role_info.
     * @return Value of property identity_role_info.
     *
     */
    public Collection getIdentity_role_info();
    
    /** Setter for property identity_role_info.
     * @param identity_role_info New value of property identity_role_info.
     *
     */
    public void setIdentity_role_info(Collection identity_role_info);
    
}
