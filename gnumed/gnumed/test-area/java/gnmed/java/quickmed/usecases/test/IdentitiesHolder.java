/*
 * IdentityHolder.java
 *
 * Created on 7 August 2003, 06:33
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;

/**
 *
 * @author  sjtan
 */
public interface IdentitiesHolder {
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity[] getIdentities();
    
    public void addIdentity(identity identity);
    
}
