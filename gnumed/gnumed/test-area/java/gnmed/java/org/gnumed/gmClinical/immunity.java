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
   
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public code_ref code_ref;
    
    
    ///////////////////////////////////////
    // access methods for associations
    /** 
     *
     *@hibernate.many-to-one
     */
    public code_ref getCode_ref() {
        return code_ref;
    }
    public void setCode_ref(code_ref _code_ref) {
        if (this.code_ref != _code_ref) {
        //    if (this.code_ref != null) this.code_ref.removeImmunity(this);
            this.code_ref = _code_ref;
         //   if (_code_ref != null) _code_ref.addImmunity(this);
        }
    }
    
  
    
} // end immunity





