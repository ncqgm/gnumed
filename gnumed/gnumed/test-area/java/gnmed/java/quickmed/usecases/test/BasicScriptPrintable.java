/*
 * BasicScriptPrintable.java
 *
 * Created on 29 August 2003, 14:00
 */

package quickmed.usecases.test;

/**
 *
 * @author  syan
 */
public interface BasicScriptPrintable {
    
    /** Getter for property scriptItems.
     * @return Value of property scriptItems.
     *
     */
    public java.util.List getScriptItems();
    
    /** Setter for property scriptItems.
     * @param scriptItems New value of property scriptItems.
     *
     */
    public void setScriptItems(java.util.List scriptItems);
    
    /** Getter for property pageable.
     * @return Value of property pageable.
     *
     */
    public java.awt.print.Pageable getPageable();
    
    /** Getter for property prescriber.
     * @return Value of property prescriber.
     *
     */
    public Object getPrescriber();    
   
    /** Setter for property prescriber.
     * @param prescriber New value of property prescriber.
     *
     */
    public void setPrescriber(Object prescriber);    
    
    /** Getter for property scriptDate.
     * @return Value of property scriptDate.
     *
     */
    public java.util.Date getScriptDate();
    
    /** Setter for property scriptDate.
     * @param scriptDate New value of property scriptDate.
     *
     */
    public void setScriptDate(java.util.Date scriptDate);
    
    /** Getter for property patient.
     * @return Value of property patient.
     *
     */
    public Object getPatient();
    
    /** Setter for property patient.
     * @param patient New value of property patient.
     *
     */
    public void setPatient(Object patient);
    
    public BasicScriptFormLayoutAdjustable getAdjustableLayout();
}
