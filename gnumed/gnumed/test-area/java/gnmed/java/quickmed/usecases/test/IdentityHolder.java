/*
 * IdentityHolder.java
 *
 * Created on 3 September 2003, 23:17
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;
/**
 *
 * @author  syan
 */
public interface IdentityHolder {
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity();
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity identity);
    
}
