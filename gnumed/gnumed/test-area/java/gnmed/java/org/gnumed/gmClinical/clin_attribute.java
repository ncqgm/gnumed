
/** Java class "clin_attribute.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;
import org.gnumed.gmIdentity.identity;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  discriminator-value="a"
 *
 * @hibernate.discriminator
 *  column="type"
 *  type="string"
 *  length="2"
 *
 */
public class clin_attribute {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public identity identity; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     * @hibernate.many-to-one
     */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        if (this.identity != _identity) {
            if (this.identity != null) this.identity.removeClin_attribute(this);
            this.identity = _identity;
            if (_identity != null) _identity.addClin_attribute(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *@hibernate.id
 *  generator-class="hilo"
 */
    public Long getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Long _id) {        
        id = _id;
    } // end setId        

} // end clin_attribute



