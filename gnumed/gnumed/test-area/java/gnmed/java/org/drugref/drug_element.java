/** Java class "drug_element.java" generated from Poseidon for UML.
 *  Poseidon for UML is developed by <A HREF="http://www.gentleware.com">Gentleware</A>.
 *  Generated with <A HREF="http://jakarta.apache.org/velocity/">velocity</A> template engine.
 */
package org.drugref;

import java.util.*;

/**
 * <p>
 * 
 * </p>
 * @hibernate.class
 *  mutable="false"
 *  
 */
public class drug_element {

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
    private char category; 

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
    public Collection atc = new java.util.HashSet(); // of type atc
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug = new java.util.HashSet(); // of type drug_element
/**
 * <p>
 * 
 * </p>
 */
    public static Collection drug_class = new java.util.HashSet(); // of type drug_element
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_warning = new java.util.HashSet(); // of type drug_warning
/**
 * <p>
 * 
 * </p>
 */
    public Collection drug_information = new java.util.HashSet(); // of type drug_information
/**
 * <p>
 * 
 * </p>
 */
    public Collection link_drug_interactions = new java.util.HashSet(); // of type link_drug_interactions
/**
 * <p>
 * 
 * </p>
 */
    public Collection link_drug_interactions_1 = new java.util.HashSet(); // of type link_drug_interactions
/**
 * <p>
 * 
 * </p>
 */
    public Collection link_drug_indication = new java.util.HashSet(); // of type link_drug_indication
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
    public Collection link_drug_disease_interactions = new java.util.ArrayList();
    
    /** Holds value of property audit_id. */
    private Integer audit_id;
    /**
 * <p>
 * 
 * </p>
 */
    public Collection toCompound = new java.util.HashSet(); // of type link_compound_generics
/**
 * <p>
 * 
 * </p>
 */
    public Collection toComponent = new java.util.HashSet();
    
    /** Holds value of property generic_name. */
    private Collection generic_name;
    
 // of type link_compound_generics
   
 // of type link_drug_disease_interactions


   ///////////////////////////////////////
   // access methods for associations

    /**
     *@hibernate.set
     *  table="link_drug_atc"
     *@hibernate.collection-key
     *  column="id_drug"
     *@hibernate.collection-many-to-many
     *  column="atccode"
     *  class="org.drugref.atc"
     *  
     */
    public Collection getAtcs() {
        return atc;
    }
    public void addAtc(atc _atc) {
        if (! this.atc.contains(_atc)) {
            this.atc.add(_atc);
            _atc.addDrug_element(this);
        }
    }
    public void removeAtc(atc _atc) {
        boolean removed = this.atc.remove(_atc);
        if (removed) _atc.removeDrug_element(this);
    }
    
      /** Setter for property atcs.
     * @param atcs New value of property atcs.
     *
     */
    public void setAtcs(Collection atcs) {
    atc = atcs;
    }    
    
    
    public Collection getDrugs() {
        return drug;
    }
    public void addDrug(drug_element _drug_element) {
        if (! this.drug.contains(_drug_element)) {
            this.drug.add(_drug_element);
            _drug_element.addDrug_class(this);
        }
    }
    public void removeDrug(drug_element _drug_element) {
        boolean removed = this.drug.remove(_drug_element);
        if (removed) _drug_element.removeDrug_class(this);
    }
    public static Collection getDrug_classs() {
        return drug_class;
    }
    public static void addDrug_class(drug_element _drug_element) {
        if (! drug_element.drug_class.contains(_drug_element)) {
            drug_element.drug_class.add(_drug_element);
        }
    }
    public static void removeDrug_class(drug_element _drug_element) {
        boolean removed = drug_element.drug_class.remove(_drug_element);
    }
    public Collection getDrug_warnings() {
        return drug_warning;
    }
    public void addDrug_warning(drug_warning _drug_warning) {
        if (! this.drug_warning.contains(_drug_warning)) {
            this.drug_warning.add(_drug_warning);
            _drug_warning.addDrug_element(this);
        }
    }
    public void removeDrug_warning(drug_warning _drug_warning) {
        boolean removed = this.drug_warning.remove(_drug_warning);
        if (removed) _drug_warning.removeDrug_element(this);
    }
    public Collection getDrug_informations() {
        return drug_information;
    }
    public void addDrug_information(drug_information _drug_information) {
        if (! this.drug_information.contains(_drug_information)) {
            this.drug_information.add(_drug_information);
            _drug_information.addDrug_element(this);
        }
    }
    public void removeDrug_information(drug_information _drug_information) {
        boolean removed = this.drug_information.remove(_drug_information);
        if (removed) _drug_information.removeDrug_element(this);
    }
    public Collection getLink_drug_interactionss() {
        return link_drug_interactions;
    }
    public void addLink_drug_interactions(link_drug_interactions _link_drug_interactions) {
        if (! this.link_drug_interactions.contains(_link_drug_interactions)) {
            this.link_drug_interactions.add(_link_drug_interactions);
            _link_drug_interactions.setInteractor(this);
        }
    }
    public void removeLink_drug_interactions(link_drug_interactions _link_drug_interactions) {
        boolean removed = this.link_drug_interactions.remove(_link_drug_interactions);
        if (removed) _link_drug_interactions.setInteractor((drug_element)null);
    }
    public Collection getLink_drug_interactions_1s() {
        return link_drug_interactions_1;
    }
    public void addLink_drug_interactions_1(link_drug_interactions _link_drug_interactions) {
        if (! this.link_drug_interactions_1.contains(_link_drug_interactions)) {
            this.link_drug_interactions_1.add(_link_drug_interactions);
            _link_drug_interactions.setDrug_element(this);
        }
    }
    public void removeLink_drug_interactions_1(link_drug_interactions _link_drug_interactions) {
        boolean removed = this.link_drug_interactions_1.remove(_link_drug_interactions);
        if (removed) _link_drug_interactions.setDrug_element((drug_element)null);
    }
    public Collection getLink_drug_indications() {
        return link_drug_indication;
    }
    public void addLink_drug_indication(link_drug_indication _link_drug_indication) {
        if (! this.link_drug_indication.contains(_link_drug_indication)) {
            this.link_drug_indication.add(_link_drug_indication);
            _link_drug_indication.setDrug_element(this);
        }
    }
    public void removeLink_drug_indication(link_drug_indication _link_drug_indication) {
        boolean removed = this.link_drug_indication.remove(_link_drug_indication);
        if (removed) _link_drug_indication.setDrug_element((drug_element)null);
    }
    
    /**
     *@hibernate.set
     *  cascade="none"
     *@hibernate.collection-key
     *  column="drug_element"
     *@hibernate.collection-one-to-many
     *  class="org.drugref.product"
     */
    public Collection getProducts() {
        return product;
    }
    public void addProduct(product _product) {
        if (! this.product.contains(_product)) {
            this.product.add(_product);
            _product.setDrug_element(this);
        }
    }
    public void removeProduct(product _product) {
        boolean removed = this.product.remove(_product);
        if (removed) _product.setDrug_element((drug_element)null);
    }
    
       
    /** Setter for property products.
     * @param products New value of property products.
     *
     */
    public void setProducts(Collection products) {
    product = products;
    }
    
    
    public Collection getLink_drug_disease_interactionss() {
        return link_drug_disease_interactions;
    }
    public void addLink_drug_disease_interactions(link_drug_disease_interactions _link_drug_disease_interactions) {
        if (! this.link_drug_disease_interactions.contains(_link_drug_disease_interactions)) {
            this.link_drug_disease_interactions.add(_link_drug_disease_interactions);
            _link_drug_disease_interactions.setDrug_element(this);
        }
    }
    public void removeLink_drug_disease_interactions(link_drug_disease_interactions _link_drug_disease_interactions) {
        boolean removed = this.link_drug_disease_interactions.remove(_link_drug_disease_interactions);
        if (removed) _link_drug_disease_interactions.setDrug_element((drug_element)null);
    }


  ///////////////////////////////////////
  // operations


/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.id
 *  generator-class="hilo"
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
 * @hibernate.property
 */
    public char getCategory() {        
        return category;
    } // end getCategory        

/**
 * <p>
 * Represents ...
 * </p>
 */
    public void setCategory(char _category) {        
        category = _category;
    } // end setCategory        

/**
 * <p>
 * Represents ...
 * </p>
 * @hibernate.property
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
    
 // end setDescription        
    
    /**
     *
     * @hibernate.set
     *  inverse="true"
     * @hibernate.collection-key
     *      column="id_component"
     * @hibernate.collection-one-to-many
     *      class="org.drugref.link_compound_generics"
     */
     public Collection getToCompounds() {
        return toCompound;
    }
    public void addToCompound(link_compound_generics _link_compound_generics) {
        if (! this.toCompound.contains(_link_compound_generics)) {
            this.toCompound.add(_link_compound_generics);
            _link_compound_generics.setComponent(this);
        }
    }
    public void removeToCompound(link_compound_generics _link_compound_generics) {
        boolean removed = this.toCompound.remove(_link_compound_generics);
        if (removed) _link_compound_generics.setComponent((drug_element)null);
    }
    
    
    /** Setter for property toCompounds.
     * @param toCompounds New value of property toCompounds.
     *
     */
    public void setToCompounds(Collection toCompounds) {
        toCompound = toCompounds;
    }
    
      /**
     *
     * @hibernate.set
       * inverse="true"
       * 
     * @hibernate.collection-key
     *      column="id_compound"
     * @hibernate.collection-one-to-many
     *      class="org.drugref.link_compound_generics"
     */
    public Collection getToComponents() {
        return toComponent;
    }
    public void addToComponent(link_compound_generics _link_compound_generics) {
        if (! this.toComponent.contains(_link_compound_generics)) {
            this.toComponent.add(_link_compound_generics);
            _link_compound_generics.setCompound(this);
        }
    }
    public void removeToComponent(link_compound_generics _link_compound_generics) {
        boolean removed = this.toComponent.remove(_link_compound_generics);
        if (removed) _link_compound_generics.setCompound((drug_element)null);
    }
    
    /** Setter for property toComponents.
     * @param toComponents New value of property toComponents.
     *
     */
    public void setToComponents(Collection toComponents) {
        toComponent = toComponents;
    }
    
    /** Getter for property generic_name.
     * @return Value of property generic_name.
     * @hibernate.set
     *      inverse="true"
     *@hibernate.collection-key
     *  column="id_drug"
     *@hibernate.collection-one-to-many
     *  class="org.drugref.generic_drug_name"
     */
    public Collection getGeneric_name() {
        return this.generic_name;
    }    
    
    /** Setter for property generic_name.
     * @param generic_name New value of property generic_name.
     *
     */
    public void setGeneric_name(Collection generic_name) {
        this.generic_name = generic_name;
    }
    
} // end drug_element





