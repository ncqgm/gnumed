/*
 * identifiable.java
 *
 * Created on 8 September 2003, 00:50
 */

package org.gnumed.gmIdentity;
import java.util.Date;
import java.util.Collection;
import org.gnumed.gmGIS.identities_addresses;
/**
 *
 * @author  syan
 */
public interface identifiable {
    
    /** Getter for property dob.
     * @return Value of property dob.
     *
     */
    public Date getDob();
    
    /** Setter for property dob.
     * @param dob New value of property dob.
     *
     */
    public void setDob(Date dob);
    
    /** Getter for property id.
     * @return Value of property id.
     *
     */
    public Long getId();
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id);
    
    /** Getter for property identities_addressess.
     * @return Value of property identities_addressess.
     *
     */
    public Collection getIdentities_addressess();
    
    /** Setter for property identities_addressess.
     * @param identities_addressess New value of property identities_addressess.
     *
     */
    public void setIdentities_addressess(Collection identities_addressess);
    
    /** Getter for property karyotype.
     * @return Value of property karyotype.
     *
     */
    public String getKaryotype();
    
    /** Setter for property karyotype.
     * @param karyotype New value of property karyotype.
     *
     */
    public void setKaryotype(String karyotype);
    
    /** Getter for property names.
     * @return Value of property names.
     *
     */
    public Collection getNamess();
    
    /** Setter for property names.
     * @param names New value of property names.
     *
     */
    public void setNamess(Collection names);
    
}
