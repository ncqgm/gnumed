/** Java class "clin_history.java" generated from Poseidon for UML.
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
 *  discriminator-value="H"
 */
public class clin_history extends clin_root_item {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public enum_hx_source enum_hx_source; 
/**
 * <p>
 * 
 * </p>
 */
    public enum_hx_type enum_hx_type; 


   ///////////////////////////////////////
   // access methods for associations

    /** 
     *@hibernate.many-to-one
     */
    public enum_hx_source getEnum_hx_source() {
        return enum_hx_source;
    }
    
   
    public void setEnum_hx_source(enum_hx_source _enum_hx_source) {
        this.enum_hx_source = _enum_hx_source;
    }
    
     /**
     *@hibernate.many-to-one
     */
    public enum_hx_type getEnum_hx_type() {
        return enum_hx_type;
    }
    public void setEnum_hx_type(enum_hx_type _enum_hx_type) {
        this.enum_hx_type = _enum_hx_type;
    }

} // end clin_history





