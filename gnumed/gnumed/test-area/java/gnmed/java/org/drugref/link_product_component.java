/** Java class "link_product_component.java" generated from Poseidon for UML.
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
public class link_product_component {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double strength; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public Collection product = new java.util.HashSet(); // of type product
/**
 * <p>
 * 
 * </p>
 */
    public drug_element drug_element; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_units drug_units; 


   ///////////////////////////////////////
   // access methods for associations

    public Collection getProducts() {
        return product;
    }
    public void addProduct(product _product) {
        if (! this.product.contains(_product)) {
            this.product.add(_product);
            _product.setLink_product_component(this);
        }
    }
    public void removeProduct(product _product) {
        boolean removed = this.product.remove(_product);
        if (removed) _product.setLink_product_component((link_product_component)null);
    }
    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        this.drug_element = _drug_element;
    }
    public drug_units getDrug_units() {
        return drug_units;
    }
    public void setDrug_units(drug_units _drug_units) {
        this.drug_units = _drug_units;
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 */
    public Double getStrength() {        
        return strength;
    } // end getStrength        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setStrength(Double _strength) {        
        strength = _strength;
    } // end setStrength        

} // end link_product_component





