/** Java class "immunity.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 *
 * </p>
 * @hibernate.subclass
 *      discriminator-value="I"
 */
public class immunity extends clin_issue_component {
   
    /** Holds value of property notes. */
    private String notes;    

    /** Getter for property notes.
     * @return Value of property notes.
     *
     * @hibernate.property
     */
    public String getNotes() {
        return this.notes;
    }    
        
    /** Setter for property notes.
     * @param notes New value of property notes.
     *
     */
    public void setNotes(String notes) {
        this.notes = notes;
    }    
  
    
} // end immunity





