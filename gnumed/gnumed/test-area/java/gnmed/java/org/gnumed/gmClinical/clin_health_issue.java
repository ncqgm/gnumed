/** Java class "clin_health_issue.java" generated from Poseidon for UML.
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
 */
public class clin_health_issue {
    
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
    public identity identity;
    /**
     * <p>
     *
     * </p>
     */
    public Collection clin_episode = new java.util.HashSet(); // of type clin_episode
    /**
     * <p>
     *
     * </p>
     */
    public Collection clin_issue_component = new java.util.HashSet(); // of type clin_issue_component
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.many-to-one
     */
    public identity getIdentity() {
        return identity;
    }
    public void setIdentity(identity _identity) {
        if (this.identity != _identity) {
            if (this.identity != null) this.identity.removeClin_health_issue(this);
            this.identity = _identity;
            if (_identity != null) _identity.addClin_health_issue(this);
        }
    }
    
    /**
     * @hibernate.set
     *  cascade="all"
     * @hibernate.collection-key
     *  column="clin_health_issue"
     * @hibernate.collection-one-to-many
     *  class="org.gnumed.gmClinical.clin_episode"
     */
    public Collection getClin_episodes() {
        return clin_episode;
    }
    /** Setter for property clin_episodes.
     * @param clin_episodes New value of property clin_episodes.
     *
     */
    public void setClin_episodes(Collection clin_episodes) {
        clin_episode=clin_episodes;
    }
    
    public void addClin_episode(clin_episode _clin_episode) {
        if (! this.clin_episode.contains(_clin_episode)) {
            this.clin_episode.add(_clin_episode);
            _clin_episode.setClin_health_issue(this);
        }
    }
    public void removeClin_episode(clin_episode _clin_episode) {
        boolean removed = this.clin_episode.remove(_clin_episode);
        if (removed) _clin_episode.setClin_health_issue((clin_health_issue)null);
    }
    
    /**
     *
     *@hibernate.set
     *  cascade="all"
     *  inverse="true"
     *@hibernate.collection-key
     *  column="clin_health_issue"
     *@hibernate.collection-one-to-many
     *      class="org.gnumed.gmClinical.clin_issue_component"
     */
    public Collection getClin_issue_components() {
        return clin_issue_component;
    }
    /** Setter for property clin_issue_components.
     * @param clin_issue_components New value of property clin_issue_components.
     *
     */
    public void setClin_issue_components(Collection clin_issue_components) {
        clin_issue_component= clin_issue_components;
    }
    
    
    public void addClin_issue_component(clin_issue_component _clin_issue_component) {
        if (! this.clin_issue_component.contains(_clin_issue_component)) {
            this.clin_issue_component.add(_clin_issue_component);
            _clin_issue_component.setClin_health_issue(this);
        }
    }
    public void removeClin_issue_component(clin_issue_component _clin_issue_component) {
        boolean removed = this.clin_issue_component.remove(_clin_issue_component);
        if (removed) _clin_issue_component.setClin_health_issue((clin_health_issue)null);
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
    
    
    // end setId
    
} // end clin_health_issue





