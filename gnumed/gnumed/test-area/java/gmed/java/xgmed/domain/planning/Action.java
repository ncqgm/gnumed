/** Java class "Action.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.planning;

import java.util.*;
import xgmed.domain.accountability.Accountability;
import xgmed.domain.common.Location;
import xgmed.domain.common.TimeRecord;
import xgmed.domain.observation.Observation;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *      table="action"
 *      discriminator-value="A'
 *@hibernate.discriminator
 *      column="type"
 *      type="string"
 *      length="255"
 */
public class Action {

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
    public Collection suspension = new java.util.HashSet(); // of type Suspension
/**
 * <p>
 * 
 * </p>
 */
    public Collection component = new java.util.HashSet(); // of type Action
/**
 * <p>
 * 
 * </p>
 */
    public Action parent; 
/**
 * <p>
 * 
 * </p>
 */
    public Abandoned abandoned; 
/**
 * <p>
 * 
 * </p>
 */
    public TimeRecord timeRecord; 
/**
 * <p>
 * 
 * </p>
 */
    public Location location; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection accountability = new java.util.HashSet(); // of type Accountability
/**
 * <p>
 * 
 * </p>
 */
    public Collection outcome = new java.util.HashSet(); // of type Observation


   ///////////////////////////////////////
   // access methods for associations

    
    public Collection getSuspensions() {
        return suspension;
    }
    public void addSuspension(Suspension suspension) {
        if (! this.suspension.contains(suspension)) {
            this.suspension.add(suspension);
            suspension.setAction(this);
        }
    }
    public void removeSuspension(Suspension suspension) {
        boolean removed = this.suspension.remove(suspension);
        if (removed) suspension.setAction((Action)null);
    }
    
    /**
     *
     */
    public Collection getComponents() {
        return component;
    }
    public void addComponent(Action action) {
        if (! this.component.contains(action)) {
            this.component.add(action);
            action.setParent(this);
        }
    }
    public void removeComponent(Action action) {
        boolean removed = this.component.remove(action);
        if (removed) action.setParent((Action)null);
    }
    
    /**
     *@hibernate.many-to-one
     */
    public Action getParent() {
        return parent;
    }
    public void setParent(Action action) {
        if (this.parent != action) {
            if (this.parent != null) this.parent.removeComponent(this);
            this.parent = action;
            if (action != null) action.addComponent(this);
        }
    }
    
    /**
     *@hibernate.component
     *
     */
    public Abandoned getAbandoned() {
        return abandoned;
    }
    public void setAbandoned(Abandoned abandoned) {
        if (this.abandoned != abandoned) {
            this.abandoned = abandoned;
            if (abandoned != null) abandoned.setAction(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public TimeRecord getTimeRecord() {
        return timeRecord;
    }
    public void setTimeRecord(TimeRecord timeRecord) {
        this.timeRecord = timeRecord;
    }
    
    /**
     *
     *@hibernate.many-to-one
     */
    public Location getLocation() {
        return location;
    }
    public void setLocation(Location location) {
        this.location = location;
    }
    
    /**
     *
     */
    public Collection getAccountabilitys() {
        return accountability;
    }
    public void addAccountability(Accountability accountability) {
        if (! this.accountability.contains(accountability)) {
            this.accountability.add(accountability);
            accountability.addAction(this);
        }
    }
    public void removeAccountability(Accountability accountability) {
        boolean removed = this.accountability.remove(accountability);
        if (removed) accountability.removeAction(this);
    }
    
    
    public Collection getOutcomes() {
        return outcome;
    }
    public void addOutcome(Observation observation) {
        if (! this.outcome.contains(observation)) {
            this.outcome.add(observation);
            observation.setAntecedent(this);
        }
    }
    public void removeOutcome(Observation observation) {
        boolean removed = this.outcome.remove(observation);
        if (removed) observation.setAntecedent((Action)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo.long"
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
    }
    
    /** Setter for property accountabilitys.
     * @param accountabilitys New value of property accountabilitys.
     *
     */
    public void setAccountabilitys(Collection accountabilitys) {
        accountability= accountabilitys;
    }
    
    /** Setter for property components.
     * @param components New value of property components.
     *
     */
    public void setComponents(Collection components) {
        component = components;
    }
    
    /** Setter for property outcomes.
     * @param outcomes New value of property outcomes.
     *
     */
    public void setOutcomes(Collection outcomes) {
        outcome = outcomes;
    }
    
    /** Setter for property suspensions.
     * @param suspensions New value of property suspensions.
     *
     */
    public void setSuspensions(Collection suspensions) {
        suspension = suspensions;
    }
    
 // end setId        

} // end Action





