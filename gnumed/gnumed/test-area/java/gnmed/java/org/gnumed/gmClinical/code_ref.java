/** Java class "code_ref.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;
import org.drugref.disease_code;

/**
 * <p>
 * 
 * </p>
  * @hibernate.class
 */
public class code_ref {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public disease_code disease_code; 
/**
 * <p>
 * 
 * </p>
 */
    public coding_systems coding_systems; 

    /** Holds value of property id. */
    private Integer id;
    
 // of type immunity


   ///////////////////////////////////////
   // access methods for associations

//    /**
//     *@hibernate.many-to-one
//     */
    public disease_code getDisease_code() {
        return disease_code;
    }
    public void setDisease_code(disease_code _disease_code) {
        if (this.disease_code != _disease_code) {
            this.disease_code = _disease_code;
            if (_disease_code != null) _disease_code.setCode_ref(this);
        }
    }
    /**
     *@hibernate.many-to-one
     */
    public coding_systems getCoding_systems() {
        return coding_systems;
    }
    public void setCoding_systems(coding_systems _coding_systems) {
        if (this.coding_systems != _coding_systems) {
            if (this.coding_systems != null) this.coding_systems.removeCode_ref(this);
            this.coding_systems = _coding_systems;
            if (_coding_systems != null) _coding_systems.addCode_ref(this);
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
   
    
} // end code_ref





