/** Java class "package_size.java" generated from Poseidon for UML.
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
public class package_size {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double double; 

/**
 * <p>
 * Represents ...
 * </p>
 */
    private int id; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public product product; 


   ///////////////////////////////////////
   // access methods for associations

    public product getProduct() {
        return product;
    }
    public void setProduct(product _product) {
        if (this.product != _product) {
            if (this.product != null) this.product.removePackage_size(this);
            this.product = _product;
            if (_product != null) _product.addPackage_size(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public int getId() {        
        return id;
    } // end getId        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setId(int _id) {        
        id = _id;
    } // end setId        

} // end package_size





