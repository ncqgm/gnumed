/** Java class "coding_systems.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;
import org.drugref.code_systems;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 */
public class coding_systems {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public enum_coding_systems enum_coding_systems; 
/**
 * <p>
 * 
 * </p>
 */
    public code_systems code_systems; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection code_ref = new java.util.HashSet();
    
    /** Holds value of property id. */
    private Integer id;
    
 // of type code_ref


   ///////////////////////////////////////
   // access methods for associations

    public enum_coding_systems getEnum_coding_systems() {
        return enum_coding_systems;
    }
    public void setEnum_coding_systems(enum_coding_systems _enum_coding_systems) {
        if (this.enum_coding_systems != _enum_coding_systems) {
            if (this.enum_coding_systems != null) this.enum_coding_systems.removeCoding_systems(this);
            this.enum_coding_systems = _enum_coding_systems;
            if (_enum_coding_systems != null) _enum_coding_systems.addCoding_systems(this);
        }
    }
    public code_systems getCode_systems() {
        return code_systems;
    }
    public void setCode_systems(code_systems _code_systems) {
        if (this.code_systems != _code_systems) {
            this.code_systems = _code_systems;
            if (_code_systems != null) _code_systems.setCoding_systems(this);
        }
    }
    public Collection getCode_refs() {
        return code_ref;
    }
    public void addCode_ref(code_ref _code_ref) {
        if (! this.code_ref.contains(_code_ref)) {
            this.code_ref.add(_code_ref);
            _code_ref.setCoding_systems(this);
        }
    }
    public void removeCode_ref(code_ref _code_ref) {
        boolean removed = this.code_ref.remove(_code_ref);
        if (removed) _code_ref.setCoding_systems((coding_systems)null);
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
    
} // end coding_systems





