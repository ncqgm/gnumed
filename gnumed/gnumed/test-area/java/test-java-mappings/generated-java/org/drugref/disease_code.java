/** Java class "disease_code.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
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


   ///////////////////////////////////////
   // access methods for associations

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
    } // end setDescription        

} // end disease_code





