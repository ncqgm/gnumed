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
 *
 * @hibernate.class
 *  mutable="false"
 */
public class package_size {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double size; 

   ///////////////////////////////////////
   // associations

/**
 * <p>
 * 
 * </p>
 */
    public product product; 

    /** Holds value of property audit_id. */
    private Integer audit_id;    

   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     *  column="id_product"
     */
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


 // end getId        

    /** Getter for property size.
     * @return Value of property size.
     * @hibernate.property
     */
    public Double getSize() {
        return this.size;
    }
    
    /** Setter for property size.
     * @param size New value of property size.
     *
     *
     */
    public void setSize(Double size) {
        this.size = size;
    }
    
    /** Getter for property audit_id.
     * @return Value of property audit_id.
     * @hibernate.id
     *  generator-class="assigned"
     */
    public Integer getAudit_id() {
        return this.audit_id;
    }
    
    /** Setter for property audit_id.
     * @param audit_id New value of property audit_id.
     *
     */
    public void setAudit_id(Integer audit_id) {
        this.audit_id = audit_id;
    }
    
 // end setId        

} // end package_size





