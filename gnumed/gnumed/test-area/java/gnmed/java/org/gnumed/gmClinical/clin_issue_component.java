/** Java class "clin_issue_component.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  discriminator-value="C"
 * @hibernate.discriminator
 *  column="TYPE"
 */
public class clin_issue_component {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public clin_health_issue clin_health_issue; 


   ///////////////////////////////////////
   // access methods for associations
/** @hibernate.many-to-one
 */
    public clin_health_issue getClin_health_issue() {
        return clin_health_issue;
    }
    public void setClin_health_issue(clin_health_issue _clin_health_issue) {
        if (this.clin_health_issue != _clin_health_issue) {
            if (this.clin_health_issue != null) this.clin_health_issue.removeClin_issue_component(this);
            this.clin_health_issue = _clin_health_issue;
            if (_clin_health_issue != null) _clin_health_issue.addClin_issue_component(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo"
 */
    public Integer getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Integer _id) {        
        id = _id;
    } // end setId        

} // end clin_issue_component





