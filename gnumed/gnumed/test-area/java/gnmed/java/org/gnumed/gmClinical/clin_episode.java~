/** Java class "clin_episode.java" generated from Poseidon for UML.
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
 */
public class clin_episode {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 *
 */
    private String description; 

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
/**
 * <p>
 * 
 * </p>
 */
    public last_act_episode last_act_episode; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection clin_root_item = new java.util.HashSet(); // of type clin_root_item


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     */
    public clin_health_issue getClin_health_issue() {
        return clin_health_issue;
    }
    public void setClin_health_issue(clin_health_issue _clin_health_issue) {
        if (this.clin_health_issue != _clin_health_issue) {
            if (this.clin_health_issue != null) this.clin_health_issue.removeClin_episode(this);
            this.clin_health_issue = _clin_health_issue;
            if (_clin_health_issue != null) _clin_health_issue.addClin_episode(this);
        }
    }
    
    /**
     *@hibernate.one-to-one
     */
    public last_act_episode getLast_act_episode() {
        return last_act_episode;
    }
    public void setLast_act_episode(last_act_episode _last_act_episode) {
        if (this.last_act_episode != _last_act_episode) {
            this.last_act_episode = _last_act_episode;
            if (_last_act_episode != null) _last_act_episode.setClin_episode(this);
        }
    }
    
    /**
     *
     *@hibernate.collection-one-to-many
     *      class="org.gnumed.clin_root_item"
     */
    public Collection getClin_root_items() {
        return clin_root_item;
    }
       /** Setter for property clin_root_items.
     * @param clin_root_items New value of property clin_root_items.
     *
     */
    public void setClin_root_items(Collection clin_root_items) {
     clin_root_item = clin_root_items;
    }
    
    public void addClin_root_item(clin_root_item _clin_root_item) {
        if (! this.clin_root_item.contains(_clin_root_item)) {
            this.clin_root_item.add(_clin_root_item);
            _clin_root_item.setClin_episode(this);
        }
    }
    public void removeClin_root_item(clin_root_item _clin_root_item) {
        boolean removed = this.clin_root_item.remove(_clin_root_item);
        if (removed) _clin_root_item.setClin_episode((clin_episode)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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
    } // end setDescription        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *      generator-class="hilo"
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
    }
    
 
 // end setId        

} // end clin_episode





