/** Java class "clin_encounter.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.gnumed.gmClinical;

import java.util.*;
import org.gnumed.gmGIS.address;
import org.gnumed.gmIdentity.identity;

/**
 * <p>
 *
 * </p>
 * @hibernate.class
 *      proxy="org.gnumed.gmClinical.clin_encounter"
// *      dynamic_update="true"
// *      dynamic_insert="true"
 */
public class clin_encounter {
    
    ///////////////////////////////////////
    // attributes
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     */
    private String description;
    
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
    public address location;
    /**
     * <p>
     *
     * </p>
     */
    public identity provider;
    /**
     * <p>
     *
     * </p>
     */
    public enum_encounter_type enum_encounter_type;
    /**
     * <p>
     *
     * </p>
     */
    public curr_encounter curr_encounter;
    /**
     * <p>
     *
     * </p>
     */
    public Collection clin_root_item = new java.util.HashSet(); // of type clin_root_item
    /**
     * <p>
     *
     * </p>
     */
    public script script;
    
    /** Holds value of property identity. */
    private org.gnumed.gmIdentity.identity identity;    
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     * @hibernate.many-to-one
     *  cascade="none"
     */
    public address getLocation() {
        return location;
    }
    public void setLocation(address _address) {
        this.location = _address;
    }
    
    /**
     *@hibernate.many-to-one
     *  cascade="none"
     */
    public identity getProvider() {
        return provider;
    }
    public void setProvider(identity _identity) {
        if (this.provider != _identity) {
            //if (this.provider != null) this.provider.removeClin_encounter(this);
            this.provider = _identity;
            //if (_identity != null) _identity.addClin_encounter(this);
        }
    }
    
    /**
     *
     * @hibernate.many-to-one
     */
    public enum_encounter_type getEnum_encounter_type() {
        return enum_encounter_type;
    }
    public void setEnum_encounter_type(enum_encounter_type _enum_encounter_type) {
        this.enum_encounter_type = _enum_encounter_type;
    }
    
    /**
     * @hibernate.many-to-one
     */
    public curr_encounter getCurr_encounter() {
        return curr_encounter;
    }
    public void setCurr_encounter(curr_encounter _curr_encounter) {
        if (this.curr_encounter != _curr_encounter) {
            this.curr_encounter = _curr_encounter;
            if (_curr_encounter != null) _curr_encounter.setClin_encounter(this);
        }
    }
    
    /**
     *
     * @hibernate.set
     *      cascade="all"
     *      lazy="false"
     * @hibernate.collection-key
     *      column="clin_encounter"
     *@hibernate.collection-one-to-many
     *      class="org.gnumed.gmClinical.clin_root_item"
     */
    public Collection getClin_root_items() {
        return clin_root_item;
    }
    /** Setter for property clin_root_items.
     * @param clin_root_items New value of property clin_root_items.
     *
     */
    public void setClin_root_items(Collection clin_root_items) {
        clin_root_item= clin_root_items;
        
    }
    public void addClin_root_item(clin_root_item _clin_root_item) {
        if (! this.clin_root_item.contains(_clin_root_item)) {
            this.clin_root_item.add(_clin_root_item);
            _clin_root_item.setClin_encounter(this);
        }
    }
    public void removeClin_root_item(clin_root_item _clin_root_item) {
        boolean removed = this.clin_root_item.remove(_clin_root_item);
        if (removed) _clin_root_item.setClin_encounter((clin_encounter)null);
    }
    
//    /**
//     *@hibernate.many-to-one
//     */
//    public script getScript() {
//        return script;
//    }
//    public void setScript(script _script) {
//        if (this.script != _script) {
//            this.script = _script;
//            if (_script != null) _script.setClin_encounter(this);
//        }
//    }
    
    
    ///////////////////////////////////////
    // operations
    
    
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
    } // end setDescription
    
    /**
     * <p>
     * Represents ...
     * </p>
     *
     * @hibernate.id
     *      generator-class="hilo"
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
    }
    
    /** Getter for property identity.
     * @return Value of property identity.
     *
     * @hibernate.many-to-one
     *  cascade="none"
     */
    public org.gnumed.gmIdentity.identity getIdentity() {
        return this.identity;
    }    
    
    /** Setter for property identity.
     * @param identity New value of property identity.
     *
     */
    public void setIdentity(org.gnumed.gmIdentity.identity identity) {
        if (this.identity != identity) {
             if (this.identity != null) this.identity.removeClin_encounter(this);
            this.identity = identity;
            if (this.identity != null) identity.addClin_encounter(this);
        }
        this.identity = identity;
    }    
    
    // end setId
    
} // end clin_encounter





