/** Java class "clin_aux_note.java" generated from Poseidon for UML.
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
 *  discriminator-value="X"
*/
public class clin_aux_note extends clin_root_item {
    
    /** Holds value of property description. */
    private String description;
    
    /** Getter for property description.
     * @return Value of property description.
     * @hibernate.property
     */
    public String getDescription() {
        return this.description;
    }
    
    /** Setter for property description.
     * @param description New value of property description.
     *
     */
    public void setDescription(String description) {
        this.description = description;
    }
    
} // end clin_aux_note





