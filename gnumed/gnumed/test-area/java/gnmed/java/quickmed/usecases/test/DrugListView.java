/*
 * DrugListView.java
 *
 * Created on 4 August 2003, 02:23
 */

package quickmed.usecases.test;

/**
 *
 * @author  sjtan
 */
public interface DrugListView {
    
    /** Getter for property drug.
     * @return Value of property drug.
     *
     */
    public Object getDrug();
    
    /** Setter for property drug.
     * @param drug New value of property drug.
     *
     */
    public void setDrug(Object drug);
    
    /** Getter for property directions.
     * @return Value of property directions.
     *
     */
    public String getDirections();
    
    /** Setter for property directions.
     * @param directions New value of property directions.
     *
     */
    public void setDirections(String directions);
    
    /** Getter for property qty.
     * @return Value of property qty.
     *
     */
    public Integer getQty();
    
    /** Setter for property qty.
     * @param qty New value of property qty.
     *
     */
    public void setQty(Integer qty);
    
    /** Getter for property repeats.
     * @return Value of property repeats.
     *
     */
    public Integer getRepeats();
    
    /** Setter for property repeats.
     * @param repeats New value of property repeats.
     *
     */
    public void setRepeats(Integer repeats);
    
    /** Getter for property last.
     * @return Value of property last.
     *
     */
    public java.util.Date getLast();
    
    /** Setter for property last.
     * @param last New value of property last.
     *
     */
    public void setLast(java.util.Date last);
    
    /** Getter for property constructed.
     * @return Value of property constructed.
     *
     */
    public Object getConstructed();
    
    /** Setter for property constructed.
     * @param constructed New value of property constructed.
     *
     */
    public void setConstructed(Object constructed);
    
    /** Getter for property print.
     * @return Value of property print.
     *
     */
    public boolean isPrint();
    
    /** Setter for property print.
     * @param print New value of property print.
     *
     */
    public void setPrint(boolean print);
    
}
