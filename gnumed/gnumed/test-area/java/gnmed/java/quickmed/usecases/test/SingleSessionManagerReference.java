/*
 * SingleSessionManagerReference.java
 *
 * Created on 17 August 2003, 00:46
 */

package quickmed.usecases.test;
import net.sf.hibernate.*;

/**
 *
 * @author  syan
 */
public class SingleSessionManagerReference extends SessionHolder implements ManagerReference {
    
    
    TestGISManager GISManager;
    IdentityManager idManager;
    TestProblemManager problemManager;
    TestScriptDrugManager scriptDrugManager;
    
    
    /** Creates a new instance of SingleSessionManagerReference */
    public SingleSessionManagerReference() {
        super();
        Session s = null;
        try {
            s = gnmed.test.HibernateInit.openSession();
              setSession(s);
        } catch (Exception e) {
         e.printStackTrace();   
        }
      
        
    }
    
    
    
    public TestGISManager getGISManager() {
        if (GISManager == null) {
            GISManager = new TestGISManager();
            GISManager.setSessionHolder(this);
         }
        return GISManager;
    }
    
    public IdentityManager getIdentityManager() {
        if (idManager == null) {
            idManager = new IdentityManager();
            idManager.setSessionHolder(this);
        }
        return idManager;
    }
    
    public TestProblemManager getProblemManager() {
        if (problemManager == null) {
            problemManager = new TestProblemManager();
            problemManager.setSessionHolder(this);
        }
        return problemManager;
    }
    
    public TestScriptDrugManager getScriptDrugManager() {
        if (scriptDrugManager == null) {
             scriptDrugManager = new TestScriptDrugManager();
            scriptDrugManager.setSessionHolder(this);
        }
        return scriptDrugManager;
    }
    
    
 
      
}
