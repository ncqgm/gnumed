/** Java class "CategoryObservation.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;
import xgmed.helper.Visitable;
import  xgmed.helper.Visitor;
/**
 * <p>
 *
 * </p>
 *  @hibernate.subclass
 *      discriminator-value="C"
 */
public class CategoryObservation extends Observation {
    
    ///////////////////////////////////////
    // associations
    
    /**
     * <p>
     *
     * </p>
     */
    public Occurence occurence;
    /**
     * <p>
     *
     * </p>
     */
    public ObservationConcept observationConcept;
    
    
    ///////////////////////////////////////
    // access methods for associations
    /**
     *@hibernate.many-to-one
     */
    public Occurence getOccurence() {
        return occurence;
    }
    public void setOccurence(Occurence occurence) {
        this.occurence = occurence;
    }
    
    /**
     *@hibernate.many-to-one
     */
    public ObservationConcept getObservationConcept() {
        return observationConcept;
    }
    public void setObservationConcept(ObservationConcept observationConcept) {
        this.observationConcept = observationConcept;
    }
    
    public void accept(Visitor v) {
        
        v.visitCategoryObservation(this);
//        super.accept(v);
    }
    
} // end CategoryObservation





