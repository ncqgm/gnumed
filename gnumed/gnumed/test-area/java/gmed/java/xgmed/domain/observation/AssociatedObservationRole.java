/** Java class "AssociatedObservationRole.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package  xgmed.domain.observation;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *      table="associated_observation_role"
 */
public class AssociatedObservationRole {

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
    public Collection evidence = new java.util.HashSet(); // of type Observation
/**
 * <p>
 * 
 * </p>
 */
    public AssociativeFunction describer; 
/**
 * <p>
 * 
 * </p>
 */
    public Observation observation; 


   ///////////////////////////////////////
   // access methods for associations

    /**
     * @return
     *  xdoclet tag - see custom hibernate many-to-many
     */    
    public Collection getEvidences() {
        return evidence;
    }
    /**
     * @param observation
     */    
    public void addEvidence(Observation observation) {
        if (! this.evidence.contains(observation)) {
            this.evidence.add(observation);
            observation.addAssertion(this);
        }
    }
    /**
     * @param observation
     */    
    public void removeEvidence(Observation observation) {
        boolean removed = this.evidence.remove(observation);
        if (removed) observation.removeAssertion(this);
    }
    /**
     * @return the describing associative function that
     * produces this associated observation.
     * @see
     *
     * @hibernate.many-to-one
     */    
    public AssociativeFunction getDescriber() {
        return describer;
    }
    /**
     * @param associativeFunction
     */    
    public void setDescriber(AssociativeFunction associativeFunction) {
        if (this.describer != associativeFunction) {
            if (this.describer != null) this.describer.removeAProduct(this);
            this.describer = associativeFunction;
            if (associativeFunction != null) associativeFunction.addAProduct(this);
        }
    }
    /**
     * @return
     * @hibernate.many-to-one
     */    
    public Observation getObservation() {
        return observation;
    }
    /**
     * @param observation
     */    
    public void setObservation(Observation observation) {
        if (this.observation != observation) {
            this.observation = observation;
            if (observation != null) observation.setAssociatedObservationRole(this);
        }
    }


  ///////////////////////////////////////
  // operations


    /** <p>
     * Represents persistent id
     * </p>
     * xdoclet tag
     * @hibernate.id     
     * generator-class="hilo.long"
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
    
    /** Setter for property evidences.
     * @param evidences New value of property evidences.
     *
     */
    public void setEvidences(Collection evidences) {
        evidence = evidences;
    }
    
 // end setId        

} // end AssociatedObservationRole





