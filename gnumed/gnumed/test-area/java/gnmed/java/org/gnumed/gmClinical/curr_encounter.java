/** Java class "curr_encounter.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
  * @hibernate.class
 */
public class curr_encounter {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public clin_encounter clin_encounter; 

    /** Holds value of property id. */
    private Integer id;    

   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     */
    public clin_encounter getClin_encounter() {
        return clin_encounter;
    }
    public void setClin_encounter(clin_encounter _clin_encounter) {
        if (this.clin_encounter != _clin_encounter) {
            this.clin_encounter = _clin_encounter;
            if (_clin_encounter != null) _clin_encounter.setCurr_encounter(this);
        }
    }

    /** Getter for property id.
     * @return Value of property id.
      * @hibernate.id
     *  generator-class="hilo"
     */
    public Integer getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Integer id) {
        this.id = id;
    }
    
} // end curr_encounter





