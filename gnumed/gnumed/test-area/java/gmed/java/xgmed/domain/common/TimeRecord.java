/** Java class "TimeRecord.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.common;

import java.util.*;
import xgmed.domain.observation.Observation;

import xgmed.helper.Visitable;
import  xgmed.helper.Visitor; 
/**
 * <p>
 *
 * </p>
 *  @hibernate.class
 *      table="timeRecord"
 *      discriminator-value="R"
 * @hibernate.discriminator
 *  column="type"
 *  type="string"
 *  length="2"
 */
public class TimeRecord implements  Visitable {
    
    
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
    public Collection recorded = new java.util.HashSet(); // of type Observation
    /**
     * <p>
     *
     * </p>
     */
    public Collection applied = new java.util.HashSet(); // of type Observation
    
    
    ///////////////////////////////////////
    // access methods for associations
    
    /**
     *@hibernate.collection.one-to-many
     *  class="xgmed.domain.observation.Observation"
     */
    public Collection getRecordeds() {
        return recorded;
    }
    public void addRecorded(Observation observation) {
        if (! this.recorded.contains(observation)) {
            this.recorded.add(observation);
            observation.setRecordTime(this);
        }
    }
    public void removeRecorded(Observation observation) {
        boolean removed = this.recorded.remove(observation);
        if (removed) observation.setRecordTime((TimeRecord)null);
    }
    
    /**
     *@hibernate.collection.one-to-many
     *  class="xgmed.domain.observation.Observation"
     */
    public Collection getApplieds() {
        return applied;
    }
    public void addApplied(Observation observation) {
        if (! this.applied.contains(observation)) {
            this.applied.add(observation);
            observation.setApplicableTime(this);
        }
    }
    public void removeApplied(Observation observation) {
        boolean removed = this.applied.remove(observation);
        if (removed) observation.setApplicableTime((TimeRecord)null);
    }
    
    
    ///////////////////////////////////////
    // operations
    
    
    /**
     * <p>
     * Represents ...
     * </p>
     * @hibernate.id
     *    generator-class="hilo.long"
     *    type="long"
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
    
    /** Setter for property applieds.
     * @param applieds New value of property applieds.
     *
     */
    public void setApplieds(Collection applieds) {
        applied = applieds;
    }
    
    /** Setter for property recordeds.
     * @param recordeds New value of property recordeds.
     *
     */
    public void setRecordeds(Collection recordeds) {
        recorded= recordeds;
    }
    
    public void accept(Visitor v) {
        v.visitTimeRecord(this);
    }
    
    // end setId
    
} // end TimeRecord





