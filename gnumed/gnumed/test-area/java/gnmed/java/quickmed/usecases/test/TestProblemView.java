/*
 * TestProblemView.java
 *
 * Created on 11 August 2003, 07:43
 */

package quickmed.usecases.test;
import java.util.Date;
import java.text.DateFormat;
import org.gnumed.gmIdentity.identity;
import org.drugref.disease_code;
import org.gnumed.gmClinical.clin_diagnosis;
/**
 *
 * @author  sjtan
 *
 *converts between view and domain for clinical problems / clinical diagnosis.
 */
public class TestProblemView implements ProblemView , LimitedViewable, Removable {
    static java.util.logging.Logger logger =  java.util.logging.Logger.global;
    final static String[] LIMITED_VIEW = new String[] { "date", "significantProblem" };
    
    Object problem = "";
    Object oldProblem;
    
    Date date = new Date();
    
    /** Holds value of property identityRef. */
    private Ref identityRef;
    
    /** Holds value of property updating. */
    private boolean updating = true;
    
    /** Holds value of property diagnosis. */
    private clin_diagnosis diagnosis;
    
    /** Holds value of property problemManager. */
    private TestProblemManager problemManager;
    
    /** Creates a new instance of TestProblemView */
    public TestProblemView() {
    }
    
    public java.util.Date getDate() {
        return date;
    }
    
    public Object getSignificantProblem() {
        return problem;
    }
    
    public void setDate(java.util.Date date) {
        this.date = date;
        updateIdentity();
    }
    
    public void setSignificantProblem(Object problem) {
        oldProblem = problem;
        this.problem = problem;
        updateIdentity();
    }
    
    public String[] getLimitedView() {
        return LIMITED_VIEW;
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
    
    void updateIdentity() {
        logger.fine("updating with " + getDate() + " and sign prob="+ getSignificantProblem());
        if (!isUpdating() )
            return;
        if (getDiagnosis() == null && !(getSignificantProblem() instanceof String)) {
            clin_diagnosis diagnosis = getProblemManager().createProblem((identity)getIdentityRef().getRef(),
            getDate(), (disease_code) getSignificantProblem());
            setDiagnosis(diagnosis);
            return;
        }
        logger.info("**** significantProblem = " + getSignificantProblem() + "type" + getSignificantProblem().getClass() );
        clin_diagnosis diagnosis =  getProblemManager().updateProblem( (identity)getIdentityRef().getRef(),
        getDate(), (disease_code) getSignificantProblem() , getDiagnosis());
        setDiagnosis(diagnosis);
    }
    
    /** Getter for property updating.
     * @return Value of property updating.
     *
     */
    public boolean isUpdating() {
        return this.updating;
    }
    
    /** Setter for property updating.
     * @param updating New value of property updating.
     *
     */
    public void setUpdating(boolean updating) {
        this.updating = updating;
    }
    
    /** Getter for property diagnosis.
     * @return Value of property diagnosis.
     *
     */
    public clin_diagnosis getDiagnosis() {
        return this.diagnosis;
    }
    
    /** Setter for property diagnosis.
     * @param diagnosis New value of property diagnosis.
     *
     */
    public void setDiagnosis(clin_diagnosis diagnosis) {
        if ( this.diagnosis != null && this.diagnosis.getText().equals(diagnosis.getText()))
            return;
        this.diagnosis = diagnosis;
        try {
            setDate((Date) DateFormat.getDateInstance(DateFormat.SHORT).parse(diagnosis.getApprox_start()));
        } catch (Exception e) {
            try {
                setDate((Date) new java.text.SimpleDateFormat("yyyy").parse(diagnosis.getApprox_start()));
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
        setSignificantProblem(diagnosis.getCode_ref().getDisease_code());
      
    }
    
    public void remove() {
        try {
            getProblemManager().removeDiagnosis( (identity)getIdentityRef().getRef(), getDiagnosis());
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    /** Getter for property problemManager.
     * @return Value of property problemManager.
     *
     */
    public TestProblemManager getProblemManager() {
         return ((ManagerReference)((identity)getIdentityRef().getRef() ).getPersister()).getProblemManager();
    }
    
}
