/** Java class "ObservationConcept.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;
import xgmed.domain.planning.outcome.KnowledgeFunction;
import xgmed.domain.planning.outcome.OutcomeFunction;
import xgmed.helper.Visitable;
import xgmed.helper.Visitor;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  table="observation_concept"
 *  discriminator-value="O"
 *  @hibernate.discriminator
 *      column="type"
 *      type="string"
 *      length="2"
 */
public class ObservationConcept implements Visitable {

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
    public Collection subtype = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public Collection supertype = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public Coding coding; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection associativeFunction = new java.util.HashSet(); // of type AssociativeFunction
/**
 * <p>
 * 
 * </p>
 */
    public Collection producer = new java.util.HashSet(); // of type AssociativeFunction
/**
 * <p>
 * 
 * </p>
 */
    public Collection knowledgeFunction = new java.util.HashSet(); // of type KnowledgeFunction
/**
 * <p>
 * 
 * </p>
 */
    public Collection outcomeGenerator = new java.util.HashSet(); // of type OutcomeFunction
/**
 * <p>
 * 
 * </p>
 */
    public Collection sideEffectGenerator = new java.util.HashSet(); // of type OutcomeFunction


   ///////////////////////////////////////
   // access methods for associations

    public Collection getSubtypes() {
        return subtype;
    }
    public void addSubtype(ObservationConcept observationConcept) {
        if (! this.subtype.contains(observationConcept)) {
            this.subtype.add(observationConcept);
            observationConcept.addSupertype(this);
        }
    }
    public void removeSubtype(ObservationConcept observationConcept) {
        boolean removed = this.subtype.remove(observationConcept);
        if (removed) observationConcept.removeSupertype(this);
    }
    public Collection getSupertypes() {
        return supertype;
    }
    public void addSupertype(ObservationConcept observationConcept) {
        if (! this.supertype.contains(observationConcept)) {
            this.supertype.add(observationConcept);
            observationConcept.addSubtype(this);
        }
    }
    public void removeSupertype(ObservationConcept observationConcept) {
        boolean removed = this.supertype.remove(observationConcept);
        if (removed) observationConcept.removeSubtype(this);
    }
    
    /**
     *@hibernate.one-to-one
     */
    public Coding getCoding() {
        return coding;
    }
    public void setCoding(Coding coding) {
        if (this.coding != coding) {
            this.coding = coding;
            if (coding != null) coding.setObservationConcept(this);
        }
    }
    
    
    public Collection getAssociativeFunctions() {
        return associativeFunction;
    }
    public void addAssociativeFunction(AssociativeFunction associativeFunction) {
        if (! this.associativeFunction.contains(associativeFunction)) {
            this.associativeFunction.add(associativeFunction);
            associativeFunction.addArgument(this);
        }
    }
    public void removeAssociativeFunction(AssociativeFunction associativeFunction) {
        boolean removed = this.associativeFunction.remove(associativeFunction);
        if (removed) associativeFunction.removeArgument(this);
    }
    public Collection getProducers() {
        return producer;
    }
    public void addProducer(AssociativeFunction associativeFunction) {
        if (! this.producer.contains(associativeFunction)) {
            this.producer.add(associativeFunction);
            associativeFunction.setProduct(this);
        }
    }
    public void removeProducer(AssociativeFunction associativeFunction) {
        boolean removed = this.producer.remove(associativeFunction);
        if (removed) associativeFunction.setProduct((ObservationConcept)null);
    }
    
    public Collection getKnowledgeFunctions() {
        return knowledgeFunction;
    }
    public void addKnowledgeFunction(KnowledgeFunction knowledgeFunction) {
        if (! this.knowledgeFunction.contains(knowledgeFunction)) {
            this.knowledgeFunction.add(knowledgeFunction);
            knowledgeFunction.addArgConcept(this);
        }
    }
    public void removeKnowledgeFunction(KnowledgeFunction knowledgeFunction) {
        boolean removed = this.knowledgeFunction.remove(knowledgeFunction);
        if (removed) knowledgeFunction.removeArgConcept(this);
    }
    public Collection getOutcomeGenerators() {
        return outcomeGenerator;
    }
    public void addOutcomeGenerator(OutcomeFunction outcomeFunction) {
        if (! this.outcomeGenerator.contains(outcomeFunction)) {
            this.outcomeGenerator.add(outcomeFunction);
            outcomeFunction.addTarget(this);
        }
    }
    public void removeOutcomeGenerator(OutcomeFunction outcomeFunction) {
        boolean removed = this.outcomeGenerator.remove(outcomeFunction);
        if (removed) outcomeFunction.removeTarget(this);
    }
    public Collection getSideEffectGenerators() {
        return sideEffectGenerator;
    }
    public void addSideEffectGenerator(OutcomeFunction outcomeFunction) {
        if (! this.sideEffectGenerator.contains(outcomeFunction)) {
            this.sideEffectGenerator.add(outcomeFunction);
            outcomeFunction.addSide_effect(this);
        }
    }
    public void removeSideEffectGenerator(OutcomeFunction outcomeFunction) {
        boolean removed = this.sideEffectGenerator.remove(outcomeFunction);
        if (removed) outcomeFunction.removeSide_effect(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 *  @hibernate.property
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
 *  @hibernate.id
 *      generator-class="hilo.long"
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
    
    /** Setter for property associativeFunctions.
     * @param associativeFunctions New value of property associativeFunctions.
     *
     */
    public void setAssociativeFunctions(Collection associativeFunctions) {
     associativeFunction = associativeFunctions;
    }
    
    /** Setter for property knowledgeFunctions.
     * @param knowledgeFunctions New value of property knowledgeFunctions.
     *
     */
    public void setKnowledgeFunctions(Collection knowledgeFunctions) {
        knowledgeFunction = knowledgeFunctions;
    }
    
    /** Setter for property outcomeGenerators.
     * @param outcomeGenerators New value of property outcomeGenerators.
     *
     */
    public void setOutcomeGenerators(Collection outcomeGenerators) {
        outcomeGenerator = outcomeGenerators;
    }
    
    /** Setter for property producers.
     * @param producers New value of property producers.
     *
     */
    public void setProducers(Collection producers) {
        producer = producers;
    }
    
    /** Setter for property sideEffectGenerators.
     * @param sideEffectGenerators New value of property sideEffectGenerators.
     *
     */
    public void setSideEffectGenerators(Collection sideEffectGenerators) {
        sideEffectGenerator = sideEffectGenerators;
    }
    
    /** Setter for property subtypes.
     * @param subtypes New value of property subtypes.
     *
     */
    public void setSubtypes(Collection subtypes) {
        subtype = subtypes;
    }
    
    public void accept(Visitor v) {
        v.visitObservationConcept(this);
    }
    
 // end setId        

} // end ObservationConcept





