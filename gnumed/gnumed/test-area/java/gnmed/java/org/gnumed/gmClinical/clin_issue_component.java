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
    private Long id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public clin_health_issue clin_health_issue; 

/**
 * <p>
 * 
 * </p>
 */
    public code_ref code_ref; 


   ///////////////////////////////////////
   // access methods for associations

    /** 
     *
     *@hibernate.many-to-one
     *  cascade="all"
     */
    public code_ref getCode_ref() {
        return code_ref;
    }
    public void setCode_ref(code_ref _code_ref) {
        if (this.code_ref != _code_ref) {
     //if (this.code_ref != null) this.code_ref.setClin_diagnosis(this);
            this.code_ref = _code_ref;
   //  if (_code_ref != null) _code_ref.addClin_diagnosis(this);
        }
    }


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

} // end clin_issue_component





