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
    
    
}
