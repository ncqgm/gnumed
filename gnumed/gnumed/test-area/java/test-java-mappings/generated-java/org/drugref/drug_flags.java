/** Java class "drug_flags.java" generated from Poseidon for UML.
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
public class drug_flags {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Integer id; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private String description; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection product = new TreeSet(); // of type product


   ///////////////////////////////////////
   // access methods for associations

    public Collection getProducts() {
        return product;
    }
    public void addProduct(product _product) {
        if (! this.product.contains(_product)) {
            this.product.add(_product);
            _product.addDrug_flags(this);
        }
    }
    public void removeProduct(product _product) {
        boolean removed = this.product.remove(_product);
        if (removed) _product.removeDrug_flags(this);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public Integer getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(Integer _id) {        
        id = _id;
    } // end setId        

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

} // end drug_flags





