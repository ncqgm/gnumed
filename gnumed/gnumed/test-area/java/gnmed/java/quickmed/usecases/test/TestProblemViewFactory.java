/*
 * TestProblemViewFactory.java
 *
 * Created on 11 August 2003, 10:42
 */

package quickmed.usecases.test;
import java.util.*;
import org.gnumed.gmClinical.*;
import org.gnumed.gmIdentity.*;

/**
 *
 * @author  sjtan
 */
public class TestProblemViewFactory implements Factory {
    
    /** Holds value of property idRef. */
    private Ref idRef;
    
    /** Creates a new instance of TestProblemViewFactory */
    public TestProblemViewFactory() {
    }
    
    TestProblemView createViewFromDiagnosis( clin_diagnosis diagnosis) {
        TestProblemView view = (TestProblemView ) newInstance();
        view.setUpdating(false);
        view.setDiagnosis(diagnosis);
        view.setUpdating(true);
        return view;
    }
    
    public List getConvertedList() {
        List list = new ArrayList();
        if (getIdRef() == null)
            return list;
        Collection c = ((identity)getIdRef().getRef()).getClin_health_issues();
        for (Iterator i = c.iterator(); i.hasNext(); ) {
            clin_health_issue issue = (clin_health_issue) i.next();
           List comps = issue.findComponentOfType(clin_diagnosis.class);
            for (int j = 0; j< comps.size(); ++j) {
                list.add(createViewFromDiagnosis((clin_diagnosis) comps.get(j)));
            }
        }
        return list;
    }
    
    public Object newInstance() {
        TestProblemView view = new TestProblemView();
        view.setIdentityRef(getIdRef());
        return view;
    }
    
    /** Getter for property idRef.
     * @return Value of property idRef.
     *
     */
    public Ref getIdRef() {
        return this.idRef;
    }
    
    /** Setter for property idRef.
     * @param idRef New value of property idRef.
     *
     */
    public void setIdRef(Ref idRef) {
        this.idRef = idRef;
    }
    
}
