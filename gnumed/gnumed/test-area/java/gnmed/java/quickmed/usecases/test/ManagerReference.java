/*
 * ManagerReference.java
 *
 * Created on 17 August 2003, 00:43
 */

package quickmed.usecases.test;

/**
 *
 * @author  syan
 */
public interface ManagerReference {
    
    IdentityManager getIdentityManager();
    TestGISManager  getGISManager();
    TestProblemManager getProblemManager();
    TestScriptDrugManager getScriptDrugManager();
    
    /** Getter for property connected.
     * @return Value of property connected.
     *
     */
    public boolean isConnected();    
    
    /** Setter for property connected.
     * @param connected New value of property connected.
     *
     */
    public void setConnected(boolean connected) throws Exception;
    
}
