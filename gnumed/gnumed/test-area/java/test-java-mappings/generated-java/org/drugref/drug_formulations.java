/** Java class "drug_formulations.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 */
public class drug_formulations {

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
    private String comment; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection product = new java.util.HashSet(); // of type product


   ///////////////////////////////////////
   // access methods for associations

    public Collection getProducts() {
        return product;
    }
    public void addProduct(product _product) {
        if (! this.product.contains(_product)) {
            this.product.add(_product);
            _product.setDrug_formulations(this);
        }
    }
    public void removeProduct(product _product) {
        boolean removed = this.product.remove(_product);
        if (removed) _product.setDrug_formulations((drug_formulations)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
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
 */
    public String getComment() {        
        return comment;
    } // end getComment        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setComment(String _comment) {        
        comment = _comment;
    } // end setComment        

} // end drug_formulations





