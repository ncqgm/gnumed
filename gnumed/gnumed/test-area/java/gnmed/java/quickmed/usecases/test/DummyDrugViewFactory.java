/*
 * DummyDrugViewFactory.java
 *
 * Created on 5 August 2003, 07:45
 */

package quickmed.usecases.test;
import org.gnumed.gmIdentity.identity;

import java.util.*;
import org.gnumed.gmClinical.*;
/**
 *
 * @author  sjtan
 */
/**
 *
 *  uses a inner class Factory of the original holder of identity in order
 * to return the most current identity reference.
 */
public class DummyDrugViewFactory implements Factory {
    
    /** Holds value of property identity. */
    private identity identity;
    
    /** Holds value of property identityRef. */
    private Ref identityRef;
    
    /** Creates a new instance of DummyDrugViewFactory */
    public DummyDrugViewFactory() {
    }
    
    public Object newInstance() {
        DummyDrugListView view = new DummyDrugListView();
//        view.setIdentity(getIdentity());
        view.setIdentityRef(getIdentityRef());
        return view;
    }
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     */
    public identity getIdentity() {
      if ( getIdentityRef() != null)
          return (identity) getIdentityRef().getRef();
        return this.identity;
    }
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(identity identity) {
        this.identity = identity;
    }
    
    
    
    public List getConvertedList() {
        List l2 = new ArrayList();
       Collection l = getIdentity().getScript_drugs();
        for (Iterator i = l.iterator(); i.hasNext(); ) {
            script_drug sd = (script_drug) i.next();
           DummyDrugListView view = (DummyDrugListView) newInstance();
           view.setUpdating(false);
           view.setScriptDrug(sd);
           view.setUpdating(true);
           l2.add(view);
        }
       return l2;
    }
    
    /** Getter for property identityRef.
     * @return Value of property identityRef.
     *
     */
    public Ref getIdentityRef() {
        return this.identityRef;
    }
    
    /** Setter for property identityRef.
     * @param identityRef New value of property identityRef.
     *
     */
    public void setIdentityRef(Ref identityRef) {
        this.identityRef = identityRef;
    }
    
}
