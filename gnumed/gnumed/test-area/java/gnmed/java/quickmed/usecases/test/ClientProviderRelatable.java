/*
 * ClientProviderRelatable.java
 *
 * Created on 22 August 2003, 11:00
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;
/**
 *
 * @author  sjtan
 */
public interface ClientProviderRelatable {
    
    /** Getter for property client.
     * @return Value of property client.
     *
     */
    public identity getClient();
    
    /** Setter for property client.
     * @param client New value of property client.
     *
     */
    public void setClient(identity client);
    
    /** Getter for property provider.
     * @return Value of property provider.
     *
     */
    public identity getProvider();
    
    /** Setter for property provider.
     * @param provider New value of property provider.
     *
     */
    public void setProvider(identity provider);
    
}
