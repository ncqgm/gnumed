/** Java class "AssuranceLevel.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="assurance_level"
 *  discriminator-value="1"
 *  @hibernate.discriminator
 *  column="type"
 *  type="string"
 *  length=2   
 *      
 */
public class AssuranceLevel {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Long id; 



  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *      generator-class="hilo.long"
 *      type="long"
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

} // end AssuranceLevel





