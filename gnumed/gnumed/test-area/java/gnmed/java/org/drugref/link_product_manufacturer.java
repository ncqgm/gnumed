/** Java class "link_product_manufacturer.java" generated from Poseidon for UML.
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
public class link_product_manufacturer {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private String brandname; 

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
    public product product; 
/**
 * <p>
 * 
 * </p>
 */
    public manufacturer manufacturer; 


   ///////////////////////////////////////
   // access methods for associations

    public product getProduct() {
        return product;
    }
    public void setProduct(product _product) {
        this.product = _product;
    }
    public manufacturer getManufacturer() {
        return manufacturer;
    }
    public void setManufacturer(manufacturer _manufacturer) {
        if (this.manufacturer != _manufacturer) {
            if (this.manufacturer != null) this.manufacturer.removeLink_product_manufacturer(this);
            this.manufacturer = _manufacturer;
            if (_manufacturer != null) _manufacturer.addLink_product_manufacturer(this);
        }
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public String getBrandname() {        
        return brandname;
    } // end getBrandname        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setBrandname(String _brandname) {        
        brandname = _brandname;
    } // end setBrandname        

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

} // end link_product_manufacturer





