/** Java class "disease_code.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;
import org.gnumed.gmClinical.code_ref;

/**
 * <p>
 * 
 * </p>
 * was commented out to let access to drugref's original disease code table.
 * But now trying to match fields to drugref org.
 *@hibernate.class
 */
public class disease_code {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String code; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public code_systems code_systems; 

    /** Holds value of property id. */
    private Integer id;
    
    /** Holds value of property id_system. */
    private Integer id_system;
    
   ///////////////////////////////////////
   // access methods for associations

    /**
     * 
     */
    public code_systems getCode_systems() {
        return code_systems;
    }
    public void setCode_systems(code_systems _code_systems) {
        this.code_systems = _code_systems;
    }

  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
// * @hibernate.id
// *  generator-class="assigned"
 * @hibernate.property
 */
    public String getCode() {        
        return code;
    } // end getCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setCode(String _code) {        
        code = _code;
    } // end setCode        

/**
 * <p>
 * Represents ...
 * </p>
 *
  * @hibernate.property
 */
    public String getDescription() {        
        return description;
    } // end getDescription        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setDescription(String _description) {        
        description = _description;
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
    
    /** Getter for property id_code_systems.
     * @return Value of property id_code_systems.
     * @hibernate.property
     */
    public Integer getId_system() {
        return this.id_system;
    }
    
    /** Setter for property id_code_systems.
     * @param id_code_systems New value of property id_code_systems.
     *
     */
    public void setId_system(Integer id_system) {
        this.id_system = id_system;
    }
    
    public String toString() {
        return getDescription()+": "+getCode();
    }
    
 // end setDescription        

} // end disease_code





