/** Java class "Coding.java" generated from Poseidon for UML.
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
 *  @hibernate.class
 *      table="coding"
 */
public class Coding  implements Visitable {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String code; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public ObservationConcept observationConcept; 
/**
 * <p>
 * 
 * </p>
 */
    public PhenomenonType phenomenonType; 
/**
 * <p>
 * 
 * </p>
 */
    public CodeScheme codeScheme; 
/**
 * <p>
 * 
 * </p>
 */
    public IdentityObservation identityObservation; 

    /** Holds value of property id. */
    private Long id;    

   ///////////////////////////////////////
   // access methods for associations
 /**
     *  @hibernate.many-to-one
     */
    public ObservationConcept getObservationConcept() {
        return observationConcept;
    }
    public void setObservationConcept(ObservationConcept observationConcept) {
        if (this.observationConcept != observationConcept) {
            this.observationConcept = observationConcept;
            if (observationConcept != null) observationConcept.setCoding(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public PhenomenonType getPhenomenonType() {
        return phenomenonType;
    }
    public void setPhenomenonType(PhenomenonType phenomenonType) {
        if (this.phenomenonType != phenomenonType) {
            this.phenomenonType = phenomenonType;
            if (phenomenonType != null) phenomenonType.setCoding(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     */
    public CodeScheme getCodeScheme() {
        return codeScheme;
    }
    public void setCodeScheme(CodeScheme codeScheme) {
        if (this.codeScheme != codeScheme) {
            if (this.codeScheme != null) this.codeScheme.removeCoding(this);
            this.codeScheme = codeScheme;
            if (codeScheme != null) codeScheme.addCoding(this);
        }
    }
     /**
     *@hibernate.many-to-one
     */
    public IdentityObservation getIdentityObservation() {
        return identityObservation;
    }
    public void setIdentityObservation(IdentityObservation identityObservation) {
        if (this.identityObservation != identityObservation) {
            this.identityObservation = identityObservation;
            if (identityObservation != null) identityObservation.setCoding(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public String getCode() {        
        return code;
    } // end getCode        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setCode(String _code) {        
        code = _code;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     *
     *@hibernate.id
     *  generator-class="hilo.long"
     *  type="long"
     */
    public Long getId() {
        return this.id;
    }
    
    /** Setter for property id.
     * @param id New value of property id.
     *
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    public void accept(Visitor v) {
        v.visitCoding(this);
    }
    
 // end setCode        

} // end Coding





