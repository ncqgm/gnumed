/** Java class "Observation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.observation;

import java.util.*;
import xgmed.domain.accountability.Party;
import xgmed.domain.common.TimeRecord;
import xgmed.domain.planning.Action;
import xgmed.domain.planning.Plan;
import xgmed.helper.Visitable;
import  xgmed.helper.Visitor;
/**
 * <p>
 *
 * @hibernate.subclass
 *  discriminator-value="O"
 */
// *@hibernate.discriminator
// *  column="type"
// *  type="string"
// *  length="2"
// */
public class Observation  extends Action  implements Visitable {
    
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
    public ObservationProtocol observationProtocol;
    /**
     * <p>
     *
     * </p>
     */
    public TimeRecord recordTime;
    /**
     * <p>
     *
     * </p>
     */
    public TimeRecord applicableTime;
    /**
     * <p>
     *
     * </p>
     */
    public AssuranceLevel assuranceLevel;
    /**
     * <p>
     *
     * </p>
     */
    public Collection rejected = new java.util.HashSet(); // of type Observation
    /**
     * <p>
     *
     * </p>
     */
    public Observation accepted;
    /**
     * <p>
     *
     * </p>
     */
    public Party subject;
    /**
     * <p>
     *
     * </p>
     */
    protected Collection assertion = new java.util.HashSet(); // of type AssociatedObservationRole
    /**
     * <p>
     *
     * </p>
     */
    public Collection triggered = new java.util.HashSet(); // of type Plan
    /**
     * <p>
     *
     * </p>
     */
    public AssociatedObservationRole associatedObservationRole;
    /**
     * <p>
     *
     * </p>
     */
    public Action antecedent;
    /**
     * <p>
     *
     * </p>
     */
//    public Measurement measurement;
    
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     * @hibernate.many-to-one
     */
    public ObservationProtocol getObservationProtocol() {
        return observationProtocol;
    }
    public void setObservationProtocol(ObservationProtocol observationProtocol) {
        this.observationProtocol = observationProtocol;
    }
    
    /**
     *@hibernate.many-to-one
     */
    public TimeRecord getRecordTime() {
        return recordTime;
    }
    public void setRecordTime(TimeRecord timeRecord) {
        if (this.recordTime != timeRecord) {
            if (this.recordTime != null) this.recordTime.removeRecorded(this);
            this.recordTime = timeRecord;
            if (timeRecord != null) timeRecord.addRecorded(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public TimeRecord getApplicableTime() {
        return applicableTime;
    }
    public void setApplicableTime(TimeRecord timeRecord) {
        if (this.applicableTime != timeRecord) {
            if (this.applicableTime != null) this.applicableTime.removeApplied(this);
            this.applicableTime = timeRecord;
            if (timeRecord != null) timeRecord.addApplied(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public AssuranceLevel getAssuranceLevel() {
        return assuranceLevel;
    }
    public void setAssuranceLevel(AssuranceLevel assuranceLevel) {
        this.assuranceLevel = assuranceLevel;
    }
    
    /**
     *@hibernate.collection-one-to-many
     *  need a custom hbm for the bidirectional one-to-many association to itself.
     */
    public Collection getRejecteds() {
        return rejected;
    }
    public void addRejected(Observation observation) {
        if (! this.rejected.contains(observation)) {
            this.rejected.add(observation);
            observation.setAccepted(this);
        }
    }
    public void removeRejected(Observation observation) {
        boolean removed = this.rejected.remove(observation);
        if (removed) observation.setAccepted((Observation)null);
    }
    
    /**
     *  need a custom hbm for the bidirectional one-to-many association to itself.
     */
    public Observation getAccepted() {
        return accepted;
    }
    public void setAccepted(Observation observation) {
        if (this.accepted != observation) {
            if (this.accepted != null) this.accepted.removeRejected(this);
            this.accepted = observation;
            if (observation != null) observation.addRejected(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public Party getSubject() {
        return subject;
    }
    public void setSubject(Party party) {
        if (this.subject != party) {
            if (this.subject != null) this.subject.removeObservation(this);
            this.subject = party;
            if (party != null) party.addObservation(this);
        }
    }
    
    /**
     *
     * will need a custom hibernate set  bidirectional many-to-many mapping from observation to associationObservationRole
     */
    public Collection getAssertions() {
        return assertion;
    }
    public void addAssertion(AssociatedObservationRole associatedObservationRole) {
        if (! this.assertion.contains(associatedObservationRole)) {
            this.assertion.add(associatedObservationRole);
            associatedObservationRole.addEvidence(this);
        }
    }
    public void removeAssertion(AssociatedObservationRole associatedObservationRole) {
        boolean removed = this.assertion.remove(associatedObservationRole);
        if (removed) associatedObservationRole.removeEvidence(this);
    }
    
    /**
     * a hibernate many-to-many bidirectional
     */
    public Collection getTriggereds() {
        return triggered;
    }
    public void addTriggered(Plan plan) {
        if (! this.triggered.contains(plan)) {
            this.triggered.add(plan);
            plan.addTriggering(this);
        }
    }
    public void removeTriggered(Plan plan) {
        boolean removed = this.triggered.remove(plan);
        if (removed) plan.removeTriggering(this);
    }
    
    /**
     * @hibernate.one-to-one
     */
    public AssociatedObservationRole getAssociatedObservationRole() {
        return associatedObservationRole;
    }
    public void setAssociatedObservationRole(AssociatedObservationRole associatedObservationRole) {
        if (this.associatedObservationRole != associatedObservationRole) {
            this.associatedObservationRole = associatedObservationRole;
            if (associatedObservationRole != null) associatedObservationRole.setObservation(this);
        }
    }
    
    /**
     * an action association exists if this observation is an outcome of the action.
     *
     * @hibernate.many-to-one
     */
    public Action getAntecedent() {
        return antecedent;
    }
    public void setAntecedent(Action action) {
        if (this.antecedent != action) {
            if (this.antecedent != null) this.antecedent.removeOutcome(this);
            this.antecedent = action;
            if (action != null) action.addOutcome(this);
        }
    }
    
//    /**
//     * an observation may have a measurement.
//     * @hibernate.one-to-one
//     */
//    public Measurement getMeasurement() {
//        return measurement;
//    }
//    public void setMeasurement(Measurement measurement) {
//        if (this.measurement != measurement) {
//            this.measurement = measurement;
//            if (measurement != null) measurement.setObservation(this);
//        }
//    }
//    
    
    ///////////////////////////////////////
    // operations
    
    
    // end getId
    
    /** Setter for property assertions.
     * @param assertions New value of property assertions.
     *
     */
    public void setAssertions(Collection assertions) {
        assertion = assertions;
    }
    
    /** Setter for property rejecteds.
     * @param rejecteds New value of property rejecteds.
     *
     */
    public void setRejecteds(Collection rejecteds) {
        rejected = rejecteds;
    }
    
    /** Setter for property triggereds.
     * @param triggereds New value of property triggereds.
     *
     */
    public void setTriggereds(Collection triggereds) {
        triggered = triggereds;
    }
    
    public void accept(Visitor v) {
        v.visitObservation(this);
    }
    
//    
//    /**
//     * <p>
//     * Represents ...
//     * </p>
//     * @hibernate.id
//     *  generator-class="hilo.long"
//     *      type="long"
//     */
//    public Long getId() {
//        return id;
//    } // end getId
//    
//    /**
//     * <p>
//     * Represents ...
//     * </p>
//     */
//    public void setId(Long _id) {
//        id = _id;
//    }
//    // end setId
} // end Observation





