/** Java class "clin_diagnosis.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 *@hibernate.subclass
 *  discriminator-value="D"
 */
public class clin_diagnosis extends clin_issue_component {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String approx_start; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String text; 

   ///////////////////////////////////////
   // associations


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getApprox_start() {        
        return approx_start;
    } // end getApprox_start        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setApprox_start(String _approx_start) {        
        approx_start = _approx_start;
    } // end setApprox_start        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getText() {        
        return text;
    } // end getText        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setText(String _text) {        
        text = _text;
    } // end setText        

} // end clin_diagnosis





