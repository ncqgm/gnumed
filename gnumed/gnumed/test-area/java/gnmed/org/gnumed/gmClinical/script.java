/** Java class "script.java" generated from Poseidon for UML.
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
public class script {

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
    public Collection link_script_drug = new java.util.HashSet();
    
    /** Holds value of property id. */
    private Integer id;
    
 // of type link_script_drug


   ///////////////////////////////////////
   // access methods for associations

    /**
     *
     *@hibernate.many-to-one
     */
    public clin_encounter getClin_encounter() {
        return clin_encounter;
    }
    public void setClin_encounter(clin_encounter _clin_encounter) {
        if (this.clin_encounter != _clin_encounter) {
            this.clin_encounter = _clin_encounter;
            if (_clin_encounter != null) _clin_encounter.setScript(this);
        }
    }
    
    /**
     *@hibernate.collection-one-to-many
     *  class="link_script_drugs"
     */
    public Collection getLink_script_drugs() {
        return link_script_drug;
    }
    
     /** Setter for property link_script_drugs.
     * @param link_script_drugs New value of property link_script_drugs.
     *
     */
    public void setLink_script_drugs(Collection link_script_drugs) {
        link_script_drug = link_script_drugs;
    }
    
    public void addLink_script_drug(link_script_drug _link_script_drug) {
        if (! this.link_script_drug.contains(_link_script_drug)) {
            this.link_script_drug.add(_link_script_drug);
            _link_script_drug.setScript(this);
        }
    }
    public void removeLink_script_drug(link_script_drug _link_script_drug) {
        boolean removed = this.link_script_drug.remove(_link_script_drug);
        if (removed) _link_script_drug.setScript((script)null);
    }

    /** Getter for property id.
     * @return Value of property id.
     *
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
    
} // end script





