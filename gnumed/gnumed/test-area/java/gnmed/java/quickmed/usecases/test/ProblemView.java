/*
 * ProblemView.java
 *
 * Created on 11 August 2003, 07:36
 */

package quickmed.usecases.test;
import java.util.Date;
/**
 *
 * @author  sjtan
 */
public interface ProblemView {
    
    /** Getter for property date.
     * @return Value of property date.
     *
     */
    public Date getDate();
    
    /** Setter for property date.
     * @param date New value of property date.
     *
     */
    public void setDate(Date date);
    
    /** Getter for property description.
     * @return Value of property description.
     *
     */
    public Object getSignificantProblem();
    
    /** Setter for property description.
     * @param description New value of property description.
     *
     */
    public void setSignificantProblem(Object description);
    
}
