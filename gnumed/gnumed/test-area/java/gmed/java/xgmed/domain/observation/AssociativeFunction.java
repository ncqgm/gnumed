/** Java class "AssociativeFunction.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package xgmed.domain.observation;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * describes which combination of observationConcepts have
 * observations which can produce the associated observation.
 *
 *@hibernate.class
 *  table="associative_function"
 */
public class AssociativeFunction {

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection aProduct = new java.util.HashSet(); // of type AssociatedObservationRole
/**
 * <p>
 * 
 * </p>
 */
    public Collection arguments = new java.util.HashSet(); // of type ObservationConcept
/**
 * <p>
 * 
 * </p>
 */
    public ObservationConcept product; 

    /** Holds value of property id. */
    private Long id;    

   ///////////////////////////////////////
   // access methods for associations

    /**
     * xdoclet tag - custom one-to-many bidirectional
     */
    public Collection getAProducts() {
        return aProduct;
    }
    public void addAProduct(AssociatedObservationRole associatedObservationRole) {
        if (! this.aProduct.contains(associatedObservationRole)) {
            this.aProduct.add(associatedObservationRole);
            associatedObservationRole.setDescriber(this);
        }
    }
    public void removeAProduct(AssociatedObservationRole associatedObservationRole) {
        boolean removed = this.aProduct.remove(associatedObservationRole);
        if (removed) associatedObservationRole.setDescriber((AssociativeFunction)null);
    }
    
    /**
     * xdoclet tag - custom many-to-many
     */
    public Collection getArguments() {
        return arguments;
    }
    public void addArgument(ObservationConcept observationConcept) {
        if (! this.arguments.contains(observationConcept)) {
            this.arguments.add(observationConcept);
            observationConcept.addAssociativeFunction(this);
        }
    }
    public void removeArgument(ObservationConcept observationConcept) {
        boolean removed = this.arguments.remove(observationConcept);
        if (removed) observationConcept.removeAssociativeFunction(this);
    }
    
    /**
     *@hibernate.many-to-one
     */
    public ObservationConcept getProduct() {
        return product;
    }
    public void setProduct(ObservationConcept observationConcept) {
        if (this.product != observationConcept) {
            if (this.product != null) this.product.removeProducer(this);
            this.product = observationConcept;
            if (observationConcept != null) observationConcept.addProducer(this);
        }
    }

    /** Setter for property argumentss.
     * @param argumentss New value of property argumentss.
     *
     */
    public void setArguments(Collection arguments ) {
       this.arguments = arguments;
    }
    
    /** Setter for property AProducts.
     * @param AProducts New value of property AProducts.
     *
     */
    public void setAProducts(Collection AProducts) {
        aProduct = AProducts;
    }
    
    /** Getter for property id.
     * @return Value of property id.
     *
     * @hibernate.id
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
    
} // end AssociativeFunction





