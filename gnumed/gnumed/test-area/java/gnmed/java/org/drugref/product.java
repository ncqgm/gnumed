
/** Java class "product.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;
import org.gnumed.gmClinical.script_drug;

/**
 * <p>
 * 
 * </p>
 *@hibernate.class
 *  mutable="false"
 */
public class product {

  ///////////////////////////////////////
  // attributes


/**
 * <p>
 * Represents ...
 * </p>
 */
    private Double amount; 

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
    public drug_element drug_element; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_formulations drug_formulations; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_units drug_units; 
/**
 * <p>
 * 
 * </p>
 */
    public drug_routes drug_routes; 
/**
 * <p>
 * 
 * </p>
 */
    public Collection package_size = new java.util.HashSet(); // of type package_size
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_flags = new java.util.HashSet(); // of type drug_flags
/**
 * <p>
 * 
 * </p>
 */
    public Collection available = new java.util.HashSet(); // of type available
/**
 * <p>
 * 
 * </p>
 */
    public Collection link_product_manufacturer = new java.util.HashSet(); // of type link_product_manufacturer
/**
 * <p>
 * 
 * </p>
 */
    public Collection subsidized_products = new java.util.HashSet(); // of type subsidized_products
/**
 * <p>
 * 
 * </p>
 */
    public Collection script_drug = new java.util.HashSet();
    
    /** Holds value of property audit_id. */
    private Integer audit_id;
    
    /** Holds value of property link_product_component. */
    private link_product_component link_product_component;
    
 // of type script_drug


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.many-to-one
     *  column="id_drug"
     */
    public drug_element getDrug_element() {
        return drug_element;
    }
    public void setDrug_element(drug_element _drug_element) {
        if (this.drug_element != _drug_element) {
            if (this.drug_element != null) this.drug_element.removeProduct(this);
            this.drug_element = _drug_element;
            if (_drug_element != null) _drug_element.addProduct(this);
        }
    }
    
    /**
     *@hibernate.many-to-one
     *  column="id_formulation"
     */
    public drug_formulations getDrug_formulations() {
        return drug_formulations;
    }
    public void setDrug_formulations(drug_formulations _drug_formulations) {
        if (this.drug_formulations != _drug_formulations) {
            if (this.drug_formulations != null) this.drug_formulations.removeProduct(this);
            this.drug_formulations = _drug_formulations;
            if (_drug_formulations != null) _drug_formulations.addProduct(this);
        }
    }
    
    /**
     *  @hibernate.many-to-one
     *      column="id_packing_unit"
     */
    public drug_units getDrug_units() {
        return drug_units;
    }
    public void setDrug_units(drug_units _drug_units) {
        this.drug_units = _drug_units;
    }
    
    /**
     * @hibernate.many-to-one
     *     column="id_route"
     */
    public drug_routes getDrug_routes() {
        return drug_routes;
    }
    public void setDrug_routes(drug_routes _drug_routes) {
        this.drug_routes = _drug_routes;
    }
    
    /**
     *@hibernate.set
     *  
     *@hibernate.collection-key
     *  column="id_product"
     *@hibernate.collection-one-to-many
     *  class="org.drugref.package_size"
     */
    public Collection getPackage_sizes() {
        return package_size;
    }
      /** Setter for property package_sizes.
     * @param package_sizes New value of property package_sizes.
     *
     */
    public void setPackage_sizes(Collection package_sizes) {
        package_size = package_sizes;
    }
    
    public void addPackage_size(package_size _package_size) {
        if (! this.package_size.contains(_package_size)) {
            this.package_size.add(_package_size);
            _package_size.setProduct(this);
        }
    }
    public void removePackage_size(package_size _package_size) {
        boolean removed = this.package_size.remove(_package_size);
        if (removed) _package_size.setProduct((product)null);
    }
    public Collection getDrug_flagss() {
        return drug_flags;
    }
    public void addDrug_flags(drug_flags _drug_flags) {
        if (! this.drug_flags.contains(_drug_flags)) {
            this.drug_flags.add(_drug_flags);
            _drug_flags.addProduct(this);
        }
    }
    public void removeDrug_flags(drug_flags _drug_flags) {
        boolean removed = this.drug_flags.remove(_drug_flags);
        if (removed) _drug_flags.removeProduct(this);
    }
    public Collection getAvailables() {
        return available;
    }
    public void addAvailable(available _available) {
        if (! this.available.contains(_available)) {
            this.available.add(_available);
            _available.setProduct(this);
        }
    }
    public void removeAvailable(available _available) {
        boolean removed = this.available.remove(_available);
        if (removed) _available.setProduct((product)null);
    }
    public Collection getLink_product_manufacturers() {
        return link_product_manufacturer;
    }
    public void addLink_product_manufacturer(link_product_manufacturer _link_product_manufacturer) {
        if (! this.link_product_manufacturer.contains(_link_product_manufacturer)) {
            this.link_product_manufacturer.add(_link_product_manufacturer);
            _link_product_manufacturer.setProduct(this);
        }
    }
    public void removeLink_product_manufacturer(link_product_manufacturer _link_product_manufacturer) {
        boolean removed = this.link_product_manufacturer.remove(_link_product_manufacturer);
        if (removed) _link_product_manufacturer.setProduct((product)null);
    }
    
    /**
     *@hibernate.set
     *  inverse="true"
     *@hibernate.collection-key
     *  column="id_product"
     *@hibernate.collection-one-to-many
     *  class="org.drugref.subsidized_products"
     */
    
    public Collection getSubsidized_productss() {
        return subsidized_products;
    }
     /** Setter for property subsidized_productss.
     * @param subsidized_productss New value of property subsidized_productss.
     *
     */
    public void setSubsidized_productss(Collection subsidized_productss) {
        subsidized_products = subsidized_productss;
    }
    
    public void addSubsidized_products(subsidized_products _subsidized_products) {
        if (! this.subsidized_products.contains(_subsidized_products)) {
            this.subsidized_products.add(_subsidized_products);
            _subsidized_products.setProduct(this);
        }
    }
    public void removeSubsidized_products(subsidized_products _subsidized_products) {
        boolean removed = this.subsidized_products.remove(_subsidized_products);
        if (removed) _subsidized_products.setProduct((product)null);
    }
    
//    
//    /**
//     *
//     */
//    public Collection getScript_drugs() {
//        return script_drug;
//    }
//    
//    public void addScript_drug(script_drug _script_drug) {
//        if (! this.script_drug.contains(_script_drug)) {
//            this.script_drug.add(_script_drug);
//            _script_drug.setProduct(this);
//        }
//    }
//    public void removeScript_drug(script_drug _script_drug) {
//        boolean removed = this.script_drug.remove(_script_drug);
//        if (removed) _script_drug.setProduct((product)null);
//    }
//
//      
//    /** Setter for property script_drugs.
//     * @param script_drugs New value of property script_drugs.
//     *
//     */
//    public void setScript_drugs(Collection script_drugs) {
//    script_drug =script_drugs;
//    }
//    

  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
 */
    public Double getAmount() {        
        return amount;
    } // end getAmount        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setAmount(Double _amount) {        
        amount = _amount;
    } // end setAmount        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
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

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *      generator-class="hilo"
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
    }
  
    /** Getter for property audit_id.
     * @return Value of property audit_id.
     * @hibernate.property
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
    
    /** Getter for property link_product_component.
     * @return Value of property link_product_component.
     *
     */
    public link_product_component getLink_product_component() {
        return this.link_product_component;
    }    
  
    /** Setter for property link_product_component.
     * @param link_product_component New value of property link_product_component.
     *
     */
    public void setLink_product_component(link_product_component link_product_component) {
    }    
    
 // end setId        

    public String toString() {
       org.drugref.generic_drug_name n =(org.drugref.generic_drug_name) getDrug_element().getGeneric_name().iterator().next();
       StringBuffer sb = new StringBuffer();
       sb.append(n.getName());
       sb.append(": ");
       sb.append(getComment());
       return sb.toString();
    }
    
   
    
} // end product



