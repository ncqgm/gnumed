/** Java class "clin_root_item.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  org.gnumed.gmClinical;

import java.util.*;
import org.gnumed.audit.audit_fields;

/**
 * <p>
 * 
 * </p>
 *  @hibernate.class
 *  discriminator-value="R"
 * @hibernate.discriminator
 *  column="TYPE"
 *  type="string"
 *  length="2"
 */
public class clin_root_item {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String narrative; 

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
    public clin_encounter clin_encounter; 
/**
 * <p>
 * 
 * </p>
 */
    public clin_episode clin_episode; 
/**
 * <p>
 * 
 * </p>
 */
    public audit_fields audit_fields; 


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
            if (this.clin_encounter != null) this.clin_encounter.removeClin_root_item(this);
            this.clin_encounter = _clin_encounter;
            if (_clin_encounter != null) _clin_encounter.addClin_root_item(this);
        }
    }
    
    /**
     *
     *@hibernate.many-to-one
     */
    public clin_episode getClin_episode() {
        return clin_episode;
    }
    public void setClin_episode(clin_episode _clin_episode) {
        if (this.clin_episode != _clin_episode) {
            if (this.clin_episode != null) this.clin_episode.removeClin_root_item(this);
            this.clin_episode = _clin_episode;
            if (_clin_episode != null) _clin_episode.addClin_root_item(this);
        }
    }
    
//    /**
//     *@hibernate.one-to-one
//     */
    public audit_fields getAudit_fields() {
        return audit_fields;
    }
    public void setAudit_fields(audit_fields _audit_fields) {
        if (this.audit_fields != _audit_fields) {
            if (this.audit_fields != null) this.audit_fields.removeClin_root_item(this);
            this.audit_fields = _audit_fields;
            if (_audit_fields != null) _audit_fields.addClin_root_item(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getNarrative() {        
        return narrative;
    } // end getNarrative        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setNarrative(String _narrative) {        
        narrative = _narrative;
    } // end setNarrative        

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

} // end clin_root_item





